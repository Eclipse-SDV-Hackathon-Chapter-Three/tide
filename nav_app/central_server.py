"""
Central server communication for event sharing across vehicle network.
Implements V2V (Vehicle-to-Vehicle) communication via central hub.
"""
from dataclasses import dataclass, asdict
from typing import List, Optional, Tuple
from datetime import datetime
import json
import paho.mqtt.client as mqtt
from contract.adas_actor_event import AdasActorEvent
from contract.passenger_leaving_event import PassengerLeftEvent


@dataclass
class SharedHazardEvent:
    """Hazard event shared across vehicle network"""
    event_id: str
    vehicle_id: str
    hazard_type: str
    severity: str
    location: Tuple[float, float, float]
    timestamp: datetime
    is_confirmed: bool
    confirmation_count: int
    description: str
    image_url: Optional[str] = None
    affects_routes: List[str] = None  # List of road/route IDs affected

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "event_id": self.event_id,
            "vehicle_id": self.vehicle_id,
            "hazard_type": self.hazard_type,
            "severity": self.severity,
            "location": self.location,
            "timestamp": self.timestamp.isoformat(),
            "is_confirmed": self.is_confirmed,
            "confirmation_count": self.confirmation_count,
            "description": self.description,
            "image_url": self.image_url,
            "affects_routes": self.affects_routes or []
        }


@dataclass
class PassengerExitEvent:
    """Event when passenger exits vehicle for alternative transport"""
    event_id: str
    vehicle_id: str
    exit_location: Tuple[float, float, float]
    timestamp: datetime
    chosen_transport_mode: str
    vehicle_destination: Tuple[float, float, float]
    autonomous_mode: str  # "CONTINUE_TO_DESTINATION" or "RETURN_HOME"
    reason: str

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "event_id": self.event_id,
            "vehicle_id": self.vehicle_id,
            "exit_location": self.exit_location,
            "timestamp": self.timestamp.isoformat(),
            "chosen_transport_mode": self.chosen_transport_mode,
            "vehicle_destination": self.vehicle_destination,
            "autonomous_mode": self.autonomous_mode,
            "reason": self.reason
        }


class CentralServerClient:
    """Client for communicating with central event sharing server"""

    def __init__(self, broker: str, port: int, vehicle_id: str):
        """
        Initialize central server client.

        Args:
            broker: MQTT broker address
            port: MQTT broker port
            vehicle_id: Unique identifier for this vehicle
        """
        self.broker = broker
        self.port = port
        self.vehicle_id = vehicle_id
        self.client = mqtt.Client(client_id=f"vehicle_{vehicle_id}")

        # Topics
        self.hazard_publish_topic = "v2v/hazards/report"
        self.hazard_subscribe_topic = "v2v/hazards/broadcast"
        self.passenger_exit_topic = "v2v/passenger_exit"
        self.vehicle_status_topic = f"v2v/vehicle/{vehicle_id}/status"

        # Callbacks
        self.on_hazard_received = None
        self.on_passenger_exit_received = None

        self.client.on_message = self._on_message
        self.client.on_connect = self._on_connect

    def connect(self):
        """Connect to central server"""
        self.client.connect(self.broker, self.port, keepalive=60)
        self.client.loop_start()

    def disconnect(self):
        """Disconnect from central server"""
        self.client.loop_stop()
        self.client.disconnect()

    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to broker"""
        if rc == 0:
            print(f"[CentralServer] Connected to server at {self.broker}:{self.port}")
            # Subscribe to broadcast topics
            self.client.subscribe(self.hazard_subscribe_topic)
            self.client.subscribe(self.passenger_exit_topic)
            print(f"[CentralServer] Subscribed to V2V hazard broadcasts")
        else:
            print(f"[CentralServer] Connection failed with code {rc}")

    def _on_message(self, client, userdata, message):
        """Callback when message received"""
        try:
            data = json.loads(message.payload.decode())

            if message.topic == self.hazard_subscribe_topic:
                self._handle_hazard_broadcast(data)
            elif message.topic == self.passenger_exit_topic:
                self._handle_passenger_exit(data)

        except json.JSONDecodeError as e:
            print(f"[CentralServer] Failed to decode message: {e}")

    def _handle_hazard_broadcast(self, data: dict):
        """Handle incoming hazard broadcast"""
        # Ignore our own broadcasts
        if data.get("vehicle_id") == self.vehicle_id:
            return

        print(f"[CentralServer] Received hazard from vehicle {data.get('vehicle_id')}")
        print(f"  Type: {data.get('hazard_type')}, Severity: {data.get('severity')}")
        print(f"  Location: {data.get('location')}")

        if self.on_hazard_received:
            self.on_hazard_received(data)

    def _handle_passenger_exit(self, data: dict):
        """Handle passenger exit event"""
        print(f"[CentralServer] Passenger exit event from vehicle {data.get('vehicle_id')}")
        print(f"  Transport mode: {data.get('chosen_transport_mode')}")
        print(f"  Autonomous mode: {data.get('autonomous_mode')}")

        if self.on_passenger_exit_received:
            self.on_passenger_exit_received(data)

    def report_hazard(self, event: SharedHazardEvent):
        """
        Report a detected hazard to the central server for sharing.

        Args:
            event: SharedHazardEvent to share with other vehicles
        """
        payload = json.dumps(event.to_dict())
        self.client.publish(self.hazard_publish_topic, payload)

        print(f"[CentralServer] Reported hazard: {event.hazard_type} at {event.location}")
        print(f"  Severity: {event.severity}, ID: {event.event_id}")

    def report_passenger_exit(self, event: PassengerExitEvent):
        """
        Report passenger exit event (for city usage statistics).

        Args:
            event: PassengerExitEvent with details
        """
        payload = json.dumps(event.to_dict())
        self.client.publish(self.passenger_exit_topic, payload)

        print(f"[CentralServer] Reported passenger exit")
        print(f"  Mode: {event.chosen_transport_mode}")
        print(f"  Vehicle action: {event.autonomous_mode}")

    def update_vehicle_status(
        self,
        current_location: Tuple[float, float, float],
        speed: float,
        destination: Optional[Tuple[float, float, float]],
        has_passenger: bool
    ):
        """
        Update vehicle status for network awareness.

        Args:
            current_location: Current position
            speed: Current speed in km/h
            destination: Target destination if any
            has_passenger: Whether vehicle has a passenger
        """
        status = {
            "vehicle_id": self.vehicle_id,
            "timestamp": datetime.now().isoformat(),
            "location": current_location,
            "speed": speed,
            "destination": destination,
            "has_passenger": has_passenger,
            "autonomous_active": not has_passenger
        }

        payload = json.dumps(status)
        self.client.publish(self.vehicle_status_topic, payload, retain=True)

    def confirm_hazard(self, event_id: str, confirmation: bool):
        """
        Confirm or deny a hazard reported by another vehicle.

        Args:
            event_id: ID of the hazard event
            confirmation: True if confirmed, False if not present
        """
        confirmation_data = {
            "vehicle_id": self.vehicle_id,
            "event_id": event_id,
            "confirmed": confirmation,
            "timestamp": datetime.now().isoformat()
        }

        payload = json.dumps(confirmation_data)
        self.client.publish("v2v/hazards/confirm", payload)

        status = "confirmed" if confirmation else "denied"
        print(f"[CentralServer] {status.capitalize()} hazard {event_id}")
