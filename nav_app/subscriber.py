"""
FASLit Navigation Application - Main Subscriber
Implements "First Avoid, Second Leave it there" strategy

Handles:
1. Real-time hazard detection from ADAS
2. Decision making: reroute (approaching) or suggest alternatives (affected)
3. Alternative transportation suggestions with ETA
4. Passenger exit and autonomous vehicle handoff
5. V2V communication for hazard sharing
"""
import json
import uuid
from datetime import datetime
from typing import Optional
import paho.mqtt.client as mqtt

from contract.adas_actor_event import AdasActorEvent
from contract.passenger_leaving_event import PassengerLeftEvent

from nav_app.hazard_classifier import HazardClassifier, HazardSeverity, HazardType
from nav_app.alternative_transport import (
	AlternativeTransportSuggester, RouteInfo, TransportOption
)
from nav_app.route_manager import RouteManager, HazardZone
from nav_app.decision_engine import DecisionEngine, DecisionContext, ActionType
from nav_app.autonomous_manager import (
	AutonomousManager, PassengerExitRequest, AutonomousMode
)
from nav_app.central_server import (
	CentralServerClient, SharedHazardEvent, PassengerExitEvent
)
from nav_app.infotainment_publisher import InfotainmentPublisher


class FASlitNavigationApp:
	"""Main application implementing FASLit strategy"""
	
	# loc_amb_seen = []

	def __init__(self, config_path: str = "mqtt_config.json"):
		"""Initialize the navigation application"""

		# Load configuration
		with open(config_path) as f:
			config = json.load(f)

		self.broker = config["broker"]
		self.port = config["port"]
		self.keepalive = config.get("keepalive", 60)

		# Generate unique vehicle ID
		self.vehicle_id = f"vehicle_{uuid.uuid4().hex[:8]}"

		# Initialize core modules
		self.hazard_classifier = HazardClassifier()
		self.route_manager = RouteManager()
		self.decision_engine = DecisionEngine()
		self.autonomous_manager = AutonomousManager(self.vehicle_id)
		self.central_server = CentralServerClient(
			self.broker, self.port, self.vehicle_id
		)

		# Vehicle state
		self.current_location = (0.0, 0.0, 0.0)  # Will be updated from vehicle data
		self.current_speed = 0.0  # km/h
		self.destination = None
		self.has_passenger = True
		self.time_stuck_minutes = 0
		self.last_speed_check = datetime.now()

		# MQTT client for ADAS events
		self.mqtt_client = mqtt.Client(client_id=f"faslit_{self.vehicle_id}")
		self.mqtt_client.on_message = self._on_adas_message
		self.mqtt_client.on_connect = self._on_connect

		# Topics
		self.adas_actor_event_topic = "adas_actor_event"
		self.passenger_exit_topic = "passenger_exit"
		self.vehicle_data_topic = "vehicle/data"
		self.user_action_topic = "user/action"  # From infotainment display

		# Set up central server callbacks
		self.central_server.on_hazard_received = self._on_shared_hazard
		self.central_server.on_passenger_exit_received = self._on_other_vehicle_exit

		# Initialize infotainment publisher (frontend communication)
		self.infotainment = None  # Will be initialized after MQTT connects

		print(f"\n{'='*70}")
		print(f"🚗 FASLit Navigation System Initialized")
		print(f"{'='*70}")
		print(f"Vehicle ID: {self.vehicle_id}")
		print(f"Strategy: First Avoid, Second Leave it there")
		print(f"{'='*70}\n")

	def start(self):
		"""Start the navigation application"""
		print("[FASLit] Starting navigation system...")

		# Connect to MQTT broker for ADAS events
		self.mqtt_client.connect(self.broker, self.port, self.keepalive)
		self.mqtt_client.subscribe(self.adas_actor_event_topic)
		self.mqtt_client.subscribe(self.passenger_exit_topic)
		self.mqtt_client.subscribe(self.vehicle_data_topic)
		self.mqtt_client.subscribe(self.user_action_topic)

		print(f"[FASLit] Subscribed to ADAS events: {self.adas_actor_event_topic}")

		# Connect to central server for V2V
		self.central_server.connect()

		# Set example destination (in production, this comes from nav input)
		self.set_destination((5000.0, 3000.0, 0.0))

		# Keep listening
		print("[FASLit] System ready. Monitoring for events...\n")
		self.mqtt_client.loop_forever()

	def set_destination(self, destination: tuple):
		"""Set navigation destination"""
		self.destination = destination
		route = self.route_manager.set_destination(self.current_location, destination)
		print(f"[FASLit] Destination set: {destination}")
		print(f"[FASLit] Route calculated: {route.total_distance_km:.1f} km, "
			f"ETA: {route.estimated_time_minutes} minutes\n")

	def _on_connect(self, client, userdata, flags, rc):
		"""Callback when connected to MQTT broker"""
		if rc == 0:
			print(f"[FASLit] Connected to MQTT broker at {self.broker}:{self.port}")
			# Initialize infotainment publisher after MQTT connection
			self.infotainment = InfotainmentPublisher(self.mqtt_client, self.vehicle_id)
			print(f"[FASLit] Infotainment display integration ready")
		else:
			print(f"[FASLit] Connection failed with code {rc}")

	def _on_adas_message(self, client, userdata, message):
		"""Handle incoming ADAS messages"""
		try:
			data = json.loads(message.payload.decode())

			if message.topic == self.adas_actor_event_topic:
				event = AdasActorEvent(**data)
				self._handle_adas_event(event)

			elif message.topic == self.passenger_exit_topic:
				event = PassengerLeftEvent(**data)
				self._handle_passenger_exit_event(event)

			elif message.topic == self.vehicle_data_topic:
				self._handle_vehicle_data(data)

			elif message.topic == self.user_action_topic:
				self._handle_user_action(data)

		except Exception as e:
			print(f"[FASLit] Error processing message: {e}")

	def _handle_adas_event(self, event: AdasActorEvent):
		"""
		Handle ADAS actor detection event.
		Core of FASLit strategy implementation.
		"""
		print(f"\n{'─'*70}")
		print(f"📸 ADAS Event Detected")
		print(f"{'─'*70}")
		print(f"Actor: {event.actor_tag}")
		print(f"Visible: {event.is_visible}")
		print(f"Location: {event.location}")
		print(f"Time: {event.timestamp}")

		# Classify the hazard
		hazard_type = self.hazard_classifier.classify_actor(event.actor_tag)
		distance_to_hazard = self._calculate_distance(
			self.current_location, event.location
		)

		severity = self.hazard_classifier.assess_severity(
			hazard_type,
			event.is_visible,
			distance_to_hazard,
			self.current_speed
		)

		print(f"\n🔍 Hazard Classification:")
		print(f"  Type: {hazard_type.value}")
		print(f"  Severity: {severity.value}")
		print(f"  Distance: {distance_to_hazard:.0f}m")

		# Send hazard notification to infotainment display
		if self.infotainment:
			description = f"{hazard_type.value.replace('_', ' ').title()} detected {distance_to_hazard:.0f}m ahead"
			self.infotainment.publish_hazard_detected(
				hazard_type, severity, distance_to_hazard, description
			)

		# Create hazard zone
		hazard_zone = HazardZone(
			center=event.location,
			radius_meters=100.0,
			severity=severity.value,
			hazard_type=hazard_type.value,
			reported_at=event.timestamp
		)

		# Add to route manager
		affects_route = self.route_manager.add_hazard(hazard_zone)

		# Share hazard with other vehicles via V2V
		self._share_hazard_with_network(event, hazard_type, severity)

		# Make decision
		decision = self._make_decision(event.location, hazard_type, severity)

		# Display decision
		print(self.decision_engine.format_decision_for_display(decision))

		# Execute decision
		if decision.action == ActionType.REROUTE:
			self._execute_reroute()

		elif decision.action == ActionType.SUGGEST_ALTERNATIVES:
			self._suggest_alternatives(decision)

	def _make_decision(
		self,
		hazard_location: tuple,
		hazard_type: HazardType,
		severity: HazardSeverity
	):
		"""Make decision using decision engine"""

		distance_to_hazard = self._calculate_distance(
			self.current_location, hazard_location
		)

		# Build route info
		route_info = None
		if self.route_manager.current_route:
			route = self.route_manager.current_route
			route_info = RouteInfo(
				current_location=self.current_location,
				destination=self.destination,
				remaining_distance_km=route.total_distance_km,
				original_eta_minutes=route.estimated_time_minutes
			)

		# Create decision context
		context = DecisionContext(
			current_location=self.current_location,
			current_speed_kmh=self.current_speed,
			hazard_location=hazard_location,
			hazard_severity=severity,
			hazard_type=hazard_type,
			distance_to_hazard_m=distance_to_hazard,
			time_stuck_minutes=self.time_stuck_minutes,
			route_info=route_info,
			has_passenger=self.has_passenger
		)

		return self.decision_engine.make_decision(context)

	def _execute_reroute(self):
		"""Execute rerouting - FIRST AVOID strategy"""
		print(f"\n{'═'*70}")
		print(f"🔄 EXECUTING REROUTE (First Avoid Strategy)")
		print(f"{'═'*70}")

		old_route = self.route_manager.current_route
		new_route = self.route_manager.recalculate_route(self.current_location)

		if new_route:
			print(f"✓ New route calculated:")
			print(f"  Distance: {new_route.total_distance_km:.1f} km")
			print(f"  ETA: {new_route.estimated_time_minutes} minutes")
			print(f"  Hazards avoided: {len(new_route.hazards_avoided)}")
			print(f"\n📍 Rerouting navigation...")

			# Send reroute notification to infotainment
			if self.infotainment and old_route:
				hazard_names = [h.hazard_type for h in new_route.hazards_avoided[:2]]
				reason = ", ".join(hazard_names) if hazard_names else "hazard"
				self.infotainment.publish_reroute(
					reason=reason,
					old_eta_minutes=old_route.estimated_time_minutes,
					new_eta_minutes=new_route.estimated_time_minutes,
					auto_accept=True
				)
		else:
			print(f"⚠ No better route found. Continuing on current route.")

		print(f"{'═'*70}\n")

	def _suggest_alternatives(self, decision):
		"""Suggest alternative transportation - SECOND LEAVE IT strategy"""
		print(f"\n{'═'*70}")
		print(f"🚶 SUGGESTING ALTERNATIVES (Second Leave It Strategy)")
		print(f"{'═'*70}")

		route_info = RouteInfo(
			current_location=self.current_location,
			destination=self.destination,
			remaining_distance_km=self.route_manager.current_route.total_distance_km,
			original_eta_minutes=self.route_manager.current_route.estimated_time_minutes
		)

		# Generate suggestions
		suggestions = AlternativeTransportSuggester.generate_suggestions(
			route_info,
			self.current_speed,
			self.time_stuck_minutes
		)

		print(f"\n📊 Alternative Transportation Options:\n")

		for i, option in enumerate(suggestions[:3], 1):  # Show top 3
			print(AlternativeTransportSuggester.format_suggestion_for_display(option))
			print()

		# Show comparison
		current_eta = route_info.original_eta_minutes
		delay_estimate = 20  # Estimated delay from hazard

		print(f"\n⏱  Time Comparison:")
		print(f"  Staying in vehicle: ~{current_eta + delay_estimate} minutes")
		print(f"  Best alternative: ~{suggestions[0].estimated_time_minutes} minutes")
		print(f"  Time saved: {(current_eta + delay_estimate) - suggestions[0].estimated_time_minutes} minutes")

		# Send alternatives to infotainment display
		if self.infotainment:
			self.infotainment.publish_alternatives(
				current_eta_minutes=current_eta,
				delay_estimate_minutes=delay_estimate,
				alternatives=suggestions
			)

		print(f"\n{'═'*70}\n")

		# In production, this would wait for driver input from infotainment
		# For demo, show what happens if driver chooses an option
		print("💡 Driver can now choose an alternative and exit vehicle.")
		print("   Vehicle will then enter autonomous mode.\n")

	def handle_passenger_choice(self, transport_mode: str, autonomous_mode: str):
		"""
		Handle passenger's choice of alternative transport.
		Initiates autonomous vehicle handoff.
		"""
		print(f"\n{'═'*70}")
		print(f"👤 PASSENGER CHOOSING ALTERNATIVE TRANSPORT")
		print(f"{'═'*70}")

		# Create exit request
		request = PassengerExitRequest(
			exit_location=self.current_location,
			chosen_transport_mode=transport_mode,
			preferred_autonomous_mode=AutonomousMode(autonomous_mode),
			vehicle_destination=self.destination
		)

		# Validate request
		is_valid, message = self.autonomous_manager.validate_exit_request(request)

		if not is_valid:
			print(f"❌ Exit request denied: {message}")
			return

		# Display confirmation
		print(self.autonomous_manager.format_exit_confirmation(request))

		# Initiate autonomous session
		session = self.autonomous_manager.initiate_passenger_exit(request)

		# Update state
		self.has_passenger = False

		# Report to central server
		exit_event = PassengerExitEvent(
			event_id=str(uuid.uuid4()),
			vehicle_id=self.vehicle_id,
			exit_location=self.current_location,
			timestamp=datetime.now(),
			chosen_transport_mode=transport_mode,
			vehicle_destination=self.destination,
			autonomous_mode=autonomous_mode,
			reason="hazard_avoidance"
		)
		self.central_server.report_passenger_exit(exit_event)

		# Send autonomous confirmation to infotainment
		if self.infotainment:
			tracking_url = self.autonomous_manager.generate_qr_code_for_tracking()
			self.infotainment.publish_autonomous_confirmation(
				chosen_transport_mode=transport_mode,
				vehicle_destination=self.destination,
				autonomous_mode=autonomous_mode,
				estimated_arrival=session.estimated_arrival,
				tracking_url=tracking_url
			)

		print(f"{'═'*70}\n")

	def _share_hazard_with_network(
		self,
		event: AdasActorEvent,
		hazard_type: HazardType,
		severity: HazardSeverity
	):
		"""Share detected hazard with other vehicles via V2V"""

		shared_event = SharedHazardEvent(
			event_id=str(uuid.uuid4()),
			vehicle_id=self.vehicle_id,
			hazard_type=hazard_type.value,
			severity=severity.value,
			location=event.location,
			timestamp=event.timestamp,
			is_confirmed=True,
			confirmation_count=1,
			description=f"{hazard_type.value} detected by ADAS"
		)

		self.central_server.report_hazard(shared_event)

	def _on_shared_hazard(self, data: dict):
		"""Handle hazard shared by another vehicle"""
		print(f"\n📡 Received Shared Hazard from V2V Network")
		print(f"  From vehicle: {data.get('vehicle_id')}")
		print(f"  Type: {data.get('hazard_type')}")
		print(f"  Severity: {data.get('severity')}")
		print(f"  Location: {data.get('location')}\n")

		# Add to known hazards
		hazard_zone = HazardZone(
			center=tuple(data.get('location')),
			radius_meters=150.0,
			severity=data.get('severity'),
			hazard_type=data.get('hazard_type'),
			reported_at=datetime.fromisoformat(data.get('timestamp'))
		)

		affects_route = self.route_manager.add_hazard(hazard_zone)

		if affects_route:
			print("⚠ Shared hazard affects your route. Recalculating...")
			self._execute_reroute()

	def _on_other_vehicle_exit(self, data: dict):
		"""Handle passenger exit event from another vehicle"""
		print(f"\n📊 City Statistics: Vehicle {data.get('vehicle_id')} "
			f"passenger switched to {data.get('chosen_transport_mode')}")

	def _handle_vehicle_data(self, data: dict):
		"""Update vehicle state from vehicle data"""
		self.current_location = tuple(data.get('location', self.current_location))
		new_speed = data.get('speed', self.current_speed)
		
		# Track if vehicle is stuck
		if new_speed < 10.0:  # Less than 10 km/h
			time_diff = (datetime.now() - self.last_speed_check).seconds / 60
			self.time_stuck_minutes += time_diff
		else:
			self.time_stuck_minutes = 0

		self.current_speed = new_speed
		self.last_speed_check = datetime.now()

		# Update central server
		self.central_server.update_vehicle_status(
			self.current_location,
			self.current_speed,
			self.destination,
			self.has_passenger
		)

		# Update infotainment display
		if self.infotainment:
			self.infotainment.publish_vehicle_status(
				current_speed=self.current_speed,
				current_location=self.current_location,
				destination=self.destination,
				has_passenger=self.has_passenger,
				autonomous_active=not self.has_passenger
			)

	def _handle_passenger_exit_event(self, event: PassengerLeftEvent):
		"""Handle passenger exit event from CARLA/sensor"""
		print(f"\n🚪 Passenger Exit Detected")
		print(f"  Location: {event.location}")
		print(f"  Time: {event.timestamp}\n")

	def _handle_user_action(self, data: dict):
		"""
		Handle user action from infotainment display.
		User selections (e.g., choosing alternative transport) are sent here.
		"""
		action_type = data.get("action", "unknown")
		action_data = data.get("data", {})

		print(f"\n{'─'*70}")
		print(f"👤 User Action from Infotainment Display")
		print(f"{'─'*70}")
		print(f"Action: {action_type}")
		print(f"Data: {action_data}")

		if action_type == "select_alternative":
			# User selected an alternative transport mode from infotainment
			transport_mode = action_data.get("transport_mode", "walk")
			autonomous_mode = action_data.get("autonomous_mode", "return_home")

			print(f"\n🚶 User selected: {transport_mode}")
			print(f"🤖 Vehicle will: {autonomous_mode}")

			# Handle the passenger choice
			self.handle_passenger_choice(transport_mode, autonomous_mode)

		elif action_type == "accept_reroute":
			# User accepted the reroute (usually auto-accepted)
			print(f"\n✓ User accepted reroute")

		elif action_type == "dismiss_alert":
			# User dismissed an alert
			print(f"\n✓ User dismissed alert")

		elif action_type == "cancel_autonomous":
			# User cancelled autonomous mode request
			print(f"\n⚠ User cancelled autonomous mode")
			self.has_passenger = True

		else:
			print(f"\n⚠ Unknown user action: {action_type}")

		print(f"{'─'*70}\n")

	@staticmethod
	def _calculate_distance(point1: tuple, point2: tuple) -> float:
		"""Calculate distance in meters between two points"""
		import math
		x1, y1, z1 = point1
		x2, y2, z2 = point2
		return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def main():
	"""Main entry point"""
	app = FASlitNavigationApp()

	# Set home location for autonomous return
	app.autonomous_manager.set_home_location((1000.0, 1000.0, 0.0))

	try:
		app.start()
	except KeyboardInterrupt:
		print("\n\n[FASLit] Shutting down...")
		app.central_server.disconnect()
		print("[FASLit] Goodbye!")


if __name__ == "__main__":
	main()
