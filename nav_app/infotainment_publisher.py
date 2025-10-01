"""
Infotainment Publisher - Backend to Frontend Communication
Publishes navigation decisions and alerts to Android infotainment display via MQTT.
"""
import json
from datetime import datetime
from typing import List
import paho.mqtt.client as mqtt

from contract.infotainment_message import (
    HazardNotification,
    RerouteNotification,
    AlternativeSuggestion,
    AutonomousConfirmation,
    VehicleStatusUpdate,
    CentralScreenCommand,
    TransportAlternative
)
from nav_app.alternative_transport import TransportOption
from nav_app.decision_engine import Decision, ActionType
from nav_app.hazard_classifier import HazardType, HazardSeverity


class InfotainmentPublisher:
    """Publishes messages to Android infotainment display"""

    def __init__(self, mqtt_client: mqtt.Client, vehicle_id: str):
        """
        Initialize infotainment publisher.

        Args:
            mqtt_client: MQTT client for publishing
            vehicle_id: Unique vehicle identifier
        """
        self.mqtt_client = mqtt_client
        self.vehicle_id = vehicle_id

        # MQTT Topics for infotainment communication
        self.HAZARD_TOPIC = "infotainment/hazard"
        self.REROUTE_TOPIC = "infotainment/reroute"
        self.ALTERNATIVES_TOPIC = "infotainment/alternatives"
        self.AUTONOMOUS_TOPIC = "infotainment/autonomous"
        self.STATUS_TOPIC = "infotainment/status"
        self.SCREEN_COMMAND_TOPIC = "infotainment/screen_command"

        # Map hazard types to icon identifiers (Android will have these icons)
        self.HAZARD_ICONS = {
            HazardType.POLICE: "ic_police",
            HazardType.ACCIDENT: "ic_accident",
            HazardType.CONSTRUCTION: "ic_construction",
            HazardType.TRAFFIC_JAM: "ic_traffic",
            HazardType.EMERGENCY_VEHICLE: "ic_emergency",
            HazardType.ROAD_HAZARD: "ic_warning",
            HazardType.WEATHER: "ic_weather",
            HazardType.UNKNOWN: "ic_alert"
        }

        # Map transport modes to icons
        self.TRANSPORT_ICONS = {
            "walk": "ic_walk",
            "public_transit": "ic_bus",
            "taxi": "ic_taxi",
            "rideshare": "ic_car_share",
            "bike": "ic_bike"
        }

    def publish_hazard_detected(
        self,
        hazard_type: HazardType,
        severity: HazardSeverity,
        distance_meters: float,
        description: str
    ):
        """
        Publish hazard detection notification to infotainment.

        Args:
            hazard_type: Type of hazard detected
            severity: Severity level
            distance_meters: Distance to hazard
            description: Human-readable description
        """
        # Determine alert level and title
        if severity == HazardSeverity.CRITICAL:
            alert_level = "critical"
            title = "⚠️ CRITICAL HAZARD AHEAD"
        elif severity == HazardSeverity.HIGH:
            alert_level = "warning"
            title = "⚠️ Hazard Detected"
        else:
            alert_level = "info"
            title = "ℹ️ Road Information"

        notification = HazardNotification(
            title=title,
            description=description,
            hazard_type=hazard_type.value,
            severity=severity.value,
            distance_meters=distance_meters,
            alert_level=alert_level,
            icon=self.HAZARD_ICONS.get(hazard_type, "ic_alert"),
            timestamp=datetime.now(),
            show_duration_seconds=10 if severity != HazardSeverity.LOW else 5
        )

        self._publish(self.HAZARD_TOPIC, notification.dict())

        # Also command the screen to show hazard alert
        self.set_screen_mode("HAZARD_ALERT", {
            "hazard_type": hazard_type.value,
            "severity": severity.value,
            "distance": distance_meters
        })

    def publish_reroute(
        self,
        reason: str,
        old_eta_minutes: int,
        new_eta_minutes: int,
        auto_accept: bool = True
    ):
        """
        Publish reroute notification to infotainment (FIRST AVOID).

        Args:
            reason: Reason for reroute
            old_eta_minutes: Original ETA
            new_eta_minutes: New ETA after reroute
            auto_accept: Whether to auto-accept the reroute
        """
        time_saved = old_eta_minutes - new_eta_minutes

        notification = RerouteNotification(
            title="🔄 Route Updated",
            description=f"New route calculated to avoid {reason}",
            old_eta_minutes=old_eta_minutes,
            new_eta_minutes=new_eta_minutes,
            time_saved_minutes=time_saved,
            reason=reason,
            timestamp=datetime.now(),
            show_duration_seconds=8,
            auto_accept=auto_accept
        )

        self._publish(self.REROUTE_TOPIC, notification.dict())

        # Switch to map view to show new route
        self.set_screen_mode("MAP", {
            "show_reroute": True,
            "highlight_hazard": True
        })

    def publish_alternatives(
        self,
        current_eta_minutes: int,
        delay_estimate_minutes: int,
        alternatives: List[TransportOption]
    ):
        """
        Publish alternative transport suggestions to infotainment (SECOND LEAVE IT).

        Args:
            current_eta_minutes: Current ETA in vehicle
            delay_estimate_minutes: Estimated delay
            alternatives: List of TransportOption objects
        """
        # Convert TransportOption to TransportAlternative for infotainment
        transport_alternatives = []
        for alt in alternatives:
            transport_alternatives.append(TransportAlternative(
                mode=alt.mode.value,
                icon=self.TRANSPORT_ICONS.get(alt.mode.value, "ic_walk"),
                estimated_time_minutes=alt.estimated_time_minutes,
                estimated_cost=alt.estimated_cost,
                distance_km=alt.distance_km,
                description=alt.description,
                instructions=alt.instructions
            ))

        suggestion = AlternativeSuggestion(
            title="🚶 Alternative Options Available",
            description=(
                f"You may be stuck for ~{delay_estimate_minutes} minutes. "
                f"Consider these faster alternatives:"
            ),
            current_eta_minutes=current_eta_minutes,
            delay_estimate_minutes=delay_estimate_minutes,
            alternatives=transport_alternatives,
            timestamp=datetime.now(),
            requires_user_action=True,
            timeout_seconds=60
        )

        self._publish(self.ALTERNATIVES_TOPIC, suggestion.dict())

        # Command screen to show alternatives
        self.set_screen_mode("ALTERNATIVES", {
            "alternative_count": len(alternatives),
            "best_option": alternatives[0].mode.value if alternatives else None
        })

    def publish_autonomous_confirmation(
        self,
        chosen_transport_mode: str,
        vehicle_destination: tuple,
        autonomous_mode: str,
        estimated_arrival: datetime,
        tracking_url: str
    ):
        """
        Publish autonomous mode confirmation to infotainment.

        Args:
            chosen_transport_mode: Transport mode passenger chose
            vehicle_destination: Where vehicle will go
            autonomous_mode: Autonomous driving mode
            estimated_arrival: When vehicle will arrive
            tracking_url: URL for tracking vehicle
        """
        confirmation = AutonomousConfirmation(
            title="🤖 Autonomous Mode Active",
            description=(
                f"You chose {chosen_transport_mode}. "
                f"Your vehicle will {autonomous_mode.replace('_', ' ')}."
            ),
            chosen_transport_mode=chosen_transport_mode,
            vehicle_destination=vehicle_destination,
            autonomous_mode=autonomous_mode,
            estimated_arrival_time=estimated_arrival,
            tracking_url=tracking_url,
            timestamp=datetime.now()
        )

        self._publish(self.AUTONOMOUS_TOPIC, confirmation.dict())

        # Show confirmation screen
        self.set_screen_mode("AUTONOMOUS_ACTIVE", {
            "mode": autonomous_mode,
            "tracking_url": tracking_url
        })

    def publish_vehicle_status(
        self,
        current_speed: float,
        current_location: tuple,
        destination: tuple,
        has_passenger: bool,
        autonomous_active: bool
    ):
        """
        Publish vehicle status update to infotainment.

        Args:
            current_speed: Current speed in km/h
            current_location: Current position
            destination: Target destination
            has_passenger: Whether passenger is in vehicle
            autonomous_active: Whether autonomous mode is active
        """
        status = VehicleStatusUpdate(
            current_speed=current_speed,
            current_location=current_location,
            destination=destination,
            has_passenger=has_passenger,
            autonomous_active=autonomous_active,
            timestamp=datetime.now()
        )

        self._publish(self.STATUS_TOPIC, status.dict())

    def set_screen_mode(self, screen_state: str, data: dict = None):
        """
        Command infotainment to change central screen display.

        Args:
            screen_state: Screen mode (MAP, HAZARD_ALERT, ALTERNATIVES, etc.)
            data: Additional data for the screen
        """
        command = CentralScreenCommand(
            screen_state=screen_state,
            data=data
        )

        self._publish(self.SCREEN_COMMAND_TOPIC, command.dict())

    def _publish(self, topic: str, payload: dict):
        """
        Publish message to MQTT topic.

        Args:
            topic: MQTT topic
            payload: Message payload as dictionary
        """
        # Add vehicle ID to all messages
        payload["vehicle_id"] = self.vehicle_id

        # Convert datetime objects to ISO format strings
        payload = self._serialize_datetime(payload)

        json_payload = json.dumps(payload)
        self.mqtt_client.publish(topic, json_payload)

        print(f"[Infotainment] Published to {topic}")
        print(f"  Message type: {payload.get('message_type', 'unknown')}")

    def _serialize_datetime(self, obj):
        """Recursively serialize datetime objects to ISO format"""
        if isinstance(obj, dict):
            return {k: self._serialize_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_datetime(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, tuple):
            return list(obj)  # Convert tuples to lists for JSON
        else:
            return obj
