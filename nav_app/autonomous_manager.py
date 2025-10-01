"""
Autonomous vehicle management for passenger handoff scenarios.
Handles vehicle behavior when passenger exits for alternative transport.
"""
from enum import Enum
from dataclasses import dataclass
from typing import Tuple, Optional
from datetime import datetime


class AutonomousMode(Enum):
    """Autonomous driving modes after passenger exit"""
    CONTINUE_TO_DESTINATION = "continue_to_destination"
    RETURN_HOME = "return_home"
    PARK_NEARBY = "park_nearby"
    AWAIT_INSTRUCTIONS = "await_instructions"


class VehicleStatus(Enum):
    """Current status of autonomous vehicle"""
    PASSENGER_PRESENT = "passenger_present"
    AUTONOMOUS_DRIVING = "autonomous_driving"
    PARKED = "parked"
    WAITING = "waiting"


@dataclass
class PassengerExitRequest:
    """Request from passenger to exit and enable autonomous mode"""
    exit_location: Tuple[float, float, float]
    chosen_transport_mode: str
    preferred_autonomous_mode: AutonomousMode
    vehicle_destination: Tuple[float, float, float]
    parking_preference: Optional[Tuple[float, float, float]] = None


@dataclass
class AutonomousSession:
    """Details of an autonomous driving session"""
    session_id: str
    start_time: datetime
    start_location: Tuple[float, float, float]
    target_location: Tuple[float, float, float]
    mode: AutonomousMode
    status: VehicleStatus
    passenger_transport_mode: str
    estimated_arrival: datetime


class AutonomousManager:
    """Manages autonomous vehicle operations after passenger exit"""

    def __init__(self, vehicle_id: str):
        self.vehicle_id = vehicle_id
        self.current_session: Optional[AutonomousSession] = None
        self.default_home_location: Optional[Tuple[float, float, float]] = None
        self.autonomous_capable = True  # Assume vehicle has autonomous capability

    def set_home_location(self, location: Tuple[float, float, float]):
        """Set the default home/parking location for the vehicle"""
        self.default_home_location = location
        print(f"[AutonomousManager] Home location set to {location}")

    def validate_exit_request(
        self, request: PassengerExitRequest
    ) -> Tuple[bool, str]:
        """
        Validate if passenger exit request can be fulfilled.

        Returns:
            (is_valid, message)
        """
        if not self.autonomous_capable:
            return False, "Vehicle does not support autonomous driving"

        if request.preferred_autonomous_mode == AutonomousMode.RETURN_HOME:
            if self.default_home_location is None:
                return False, "Home location not set. Please configure home address."

        # Check if location is safe for passenger exit
        # In production, this would check traffic, parking zones, etc.
        if not self._is_safe_exit_location(request.exit_location):
            return False, "Current location not safe for passenger exit"

        return True, "Exit request validated"

    def initiate_passenger_exit(
        self, request: PassengerExitRequest
    ) -> AutonomousSession:
        """
        Initiate passenger exit and autonomous driving.

        Args:
            request: PassengerExitRequest with details

        Returns:
            AutonomousSession tracking the autonomous operation
        """
        # Determine target location based on mode
        if request.preferred_autonomous_mode == AutonomousMode.CONTINUE_TO_DESTINATION:
            target = request.vehicle_destination
        elif request.preferred_autonomous_mode == AutonomousMode.RETURN_HOME:
            target = self.default_home_location
        elif request.preferred_autonomous_mode == AutonomousMode.PARK_NEARBY:
            target = self._find_nearby_parking(request.exit_location)
        else:
            target = request.exit_location  # Stay and wait

        session_id = f"auto_{self.vehicle_id}_{datetime.now().timestamp()}"

        session = AutonomousSession(
            session_id=session_id,
            start_time=datetime.now(),
            start_location=request.exit_location,
            target_location=target,
            mode=request.preferred_autonomous_mode,
            status=VehicleStatus.AUTONOMOUS_DRIVING,
            passenger_transport_mode=request.chosen_transport_mode,
            estimated_arrival=self._estimate_arrival(request.exit_location, target)
        )

        self.current_session = session

        print(f"\n{'='*60}")
        print(f"🤖 AUTONOMOUS MODE ACTIVATED")
        print(f"{'='*60}")
        print(f"Session ID: {session_id}")
        print(f"Mode: {request.preferred_autonomous_mode.value}")
        print(f"Passenger chose: {request.chosen_transport_mode}")
        print(f"Vehicle destination: {target}")
        print(f"Estimated arrival: {session.estimated_arrival.strftime('%H:%M')}")
        print(f"{'='*60}\n")

        return session

    def get_vehicle_status(self) -> dict:
        """Get current vehicle status for passenger tracking"""
        if not self.current_session:
            return {
                "status": VehicleStatus.PASSENGER_PRESENT.value,
                "location": None,
                "destination": None
            }

        return {
            "status": self.current_session.status.value,
            "session_id": self.current_session.session_id,
            "mode": self.current_session.mode.value,
            "start_time": self.current_session.start_time.isoformat(),
            "destination": self.current_session.target_location,
            "estimated_arrival": self.current_session.estimated_arrival.isoformat()
        }

    def update_autonomous_status(self, new_status: VehicleStatus):
        """Update the status of autonomous operation"""
        if self.current_session:
            self.current_session.status = new_status
            print(f"[AutonomousManager] Status updated to: {new_status.value}")

    def end_autonomous_session(self):
        """End the current autonomous session"""
        if self.current_session:
            print(f"\n{'='*60}")
            print(f"🤖 AUTONOMOUS SESSION ENDED")
            print(f"{'='*60}")
            print(f"Session ID: {self.current_session.session_id}")
            print(f"Duration: {(datetime.now() - self.current_session.start_time).seconds // 60} minutes")
            print(f"Final status: {self.current_session.status.value}")
            print(f"{'='*60}\n")

            self.current_session = None

    def format_exit_confirmation(
        self, request: PassengerExitRequest
    ) -> str:
        """Format passenger exit confirmation message"""
        mode_descriptions = {
            AutonomousMode.CONTINUE_TO_DESTINATION:
                "Your vehicle will continue to the original destination autonomously.",
            AutonomousMode.RETURN_HOME:
                "Your vehicle will return home and park autonomously.",
            AutonomousMode.PARK_NEARBY:
                "Your vehicle will find nearby parking and wait.",
            AutonomousMode.AWAIT_INSTRUCTIONS:
                "Your vehicle will stay here and await further instructions."
        }

        output = f"""
╔══════════════════════════════════════════════════════════════╗
║                    PASSENGER EXIT CONFIRMED                  ║
╠══════════════════════════════════════════════════════════════╣
║
║ You have chosen: {request.chosen_transport_mode.upper()}
║
║ Vehicle Autonomous Mode: {request.preferred_autonomous_mode.value.upper()}
║ {mode_descriptions.get(request.preferred_autonomous_mode, '')}
║
║ You can track your vehicle's location via the mobile app.
║ The vehicle will notify you when it reaches its destination.
║
║ Safe travels!
║
╚══════════════════════════════════════════════════════════════╝
"""
        return output

    def _is_safe_exit_location(self, location: Tuple[float, float, float]) -> bool:
        """Check if location is safe for passenger exit"""
        # In production: check traffic, parking zones, road types, etc.
        # For demo: always return True
        return True

    def _find_nearby_parking(
        self, current_location: Tuple[float, float, float]
    ) -> Tuple[float, float, float]:
        """Find nearby parking location"""
        # In production: query parking API
        # For demo: offset location slightly
        x, y, z = current_location
        return (x + 100, y + 50, z)  # 100m away

    def _estimate_arrival(
        self,
        start: Tuple[float, float, float],
        end: Tuple[float, float, float]
    ) -> datetime:
        """Estimate arrival time at destination"""
        # Simple estimate: assume 30 km/h average for autonomous driving
        x1, y1, z1 = start
        x2, y2, z2 = end
        distance_m = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        distance_km = distance_m / 1000.0

        hours = distance_km / 30.0  # 30 km/h
        minutes = int(hours * 60)

        from datetime import timedelta
        return datetime.now() + timedelta(minutes=minutes)

    def generate_qr_code_for_tracking(self) -> str:
        """
        Generate QR code data for passenger to track vehicle.

        Returns:
            URL or data string for QR code
        """
        if not self.current_session:
            return ""

        # In production: return actual tracking URL
        tracking_url = (
            f"https://vehicle-tracking.app/track/"
            f"{self.vehicle_id}/"
            f"{self.current_session.session_id}"
        )

        return tracking_url
