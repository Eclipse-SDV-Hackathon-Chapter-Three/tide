"""
Route management and dynamic rerouting system.
Handles route calculations and hazard avoidance for approaching vehicles.
"""
from dataclasses import dataclass
from typing import List, Tuple, Optional, Set
from datetime import datetime, timedelta
import math


@dataclass
class Waypoint:
    """Represents a point on a route"""
    location: Tuple[float, float, float]
    timestamp: datetime
    distance_from_start: float


@dataclass
class HazardZone:
    """Represents a hazard area to avoid"""
    center: Tuple[float, float, float]
    radius_meters: float
    severity: str
    hazard_type: str
    reported_at: datetime
    expires_at: Optional[datetime] = None


@dataclass
class Route:
    """Represents a navigation route"""
    waypoints: List[Waypoint]
    total_distance_km: float
    estimated_time_minutes: int
    hazards_avoided: List[HazardZone]
    is_optimal: bool
    route_id: str


class RouteManager:
    """Manages route calculation and rerouting"""

    def __init__(self):
        self.current_route: Optional[Route] = None
        self.destination: Optional[Tuple[float, float, float]] = None
        self.known_hazards: List[HazardZone] = []
        self.avoided_zones: Set[Tuple[float, float, float]] = set()

    def set_destination(
        self,
        current_location: Tuple[float, float, float],
        destination: Tuple[float, float, float]
    ) -> Route:
        """
        Set a new destination and calculate initial route.

        Args:
            current_location: Current vehicle position
            destination: Target destination

        Returns:
            Calculated Route
        """
        self.destination = destination
        self.current_route = self._calculate_route(
            current_location, destination, []
        )
        return self.current_route

    def add_hazard(self, hazard: HazardZone) -> bool:
        """
        Add a newly detected or shared hazard.

        Returns:
            True if hazard affects current route and reroute is needed
        """
        self.known_hazards.append(hazard)

        if not self.current_route:
            return False

        # Check if hazard intersects with current route
        if self._hazard_affects_route(hazard, self.current_route):
            return True

        return False

    def recalculate_route(
        self, current_location: Tuple[float, float, float]
    ) -> Optional[Route]:
        """
        Recalculate route avoiding known hazards.

        Returns:
            New Route if successful, None if no better route found
        """
        if not self.destination:
            return None

        # Filter out expired hazards
        now = datetime.now()
        active_hazards = [
            h for h in self.known_hazards
            if h.expires_at is None or h.expires_at > now
        ]

        new_route = self._calculate_route(
            current_location, self.destination, active_hazards
        )

        # Only switch if new route is better (shorter time)
        if self.current_route:
            time_saved = (
                self.current_route.estimated_time_minutes -
                new_route.estimated_time_minutes
            )
            if time_saved >= 3:  # At least 3 minutes saved
                self.current_route = new_route
                return new_route
            return None

        self.current_route = new_route
        return new_route

    def _calculate_route(
        self,
        start: Tuple[float, float, float],
        end: Tuple[float, float, float],
        hazards_to_avoid: List[HazardZone]
    ) -> Route:
        """
        Calculate route from start to end, avoiding hazards.

        This is a simplified implementation. In production, this would
        call a real routing API (Google Maps, OpenStreetMap, etc.)
        """
        # Simple straight-line route for demo
        distance_km = self._calculate_distance(start, end)

        # Check if direct route intersects hazards
        must_reroute = any(
            self._point_in_hazard_zone(start, h) or
            self._point_in_hazard_zone(end, h)
            for h in hazards_to_avoid
        )

        if must_reroute:
            # Add detour penalty (simplified)
            distance_km *= 1.3  # 30% longer
            time_penalty = 10  # 10 extra minutes
        else:
            time_penalty = 0

        # Assume 50 km/h average speed
        estimated_time = int((distance_km / 50.0) * 60) + time_penalty

        # Generate waypoints (simplified)
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        mid_z = (start[2] + end[2]) / 2

        waypoints = [
            Waypoint(start, datetime.now(), 0.0),
            Waypoint(
                (mid_x, mid_y, mid_z),
                datetime.now() + timedelta(minutes=estimated_time // 2),
                distance_km / 2
            ),
            Waypoint(
                end,
                datetime.now() + timedelta(minutes=estimated_time),
                distance_km
            )
        ]

        return Route(
            waypoints=waypoints,
            total_distance_km=distance_km,
            estimated_time_minutes=estimated_time,
            hazards_avoided=hazards_to_avoid,
            is_optimal=not must_reroute,
            route_id=f"route_{datetime.now().timestamp()}"
        )

    def _hazard_affects_route(
        self, hazard: HazardZone, route: Route
    ) -> bool:
        """Check if hazard intersects with route"""
        for waypoint in route.waypoints:
            if self._point_in_hazard_zone(waypoint.location, hazard):
                return True
        return False

    def _point_in_hazard_zone(
        self, point: Tuple[float, float, float], hazard: HazardZone
    ) -> bool:
        """Check if point is within hazard zone"""
        distance = self._calculate_distance(point, hazard.center)
        return (distance * 1000) <= hazard.radius_meters

    @staticmethod
    def _calculate_distance(
        point1: Tuple[float, float, float],
        point2: Tuple[float, float, float]
    ) -> float:
        """Calculate distance in km between two points"""
        x1, y1, z1 = point1
        x2, y2, z2 = point2
        distance_meters = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return distance_meters / 1000.0

    def get_distance_to_hazard(
        self,
        current_location: Tuple[float, float, float],
        hazard: HazardZone
    ) -> float:
        """Get distance in meters from current location to hazard"""
        return self._calculate_distance(current_location, hazard.center) * 1000

    def estimate_delay_from_hazard(
        self, hazard: HazardZone
    ) -> int:
        """
        Estimate delay in minutes caused by hazard.

        Based on hazard severity and type.
        """
        severity_delays = {
            "low": 5,
            "medium": 15,
            "high": 30,
            "critical": 60
        }

        type_multipliers = {
            "accident": 1.5,
            "construction": 1.2,
            "traffic_jam": 1.3,
            "police": 1.0,
            "emergency_vehicle": 1.1,
            "road_hazard": 1.2
        }

        base_delay = severity_delays.get(hazard.severity, 10)
        multiplier = type_multipliers.get(hazard.hazard_type, 1.0)

        return int(base_delay * multiplier)

    def get_alternative_routes_count(self) -> int:
        """
        Get number of alternative routes available.

        In production, this would query a routing API.
        """
        if not self.current_route or not self.destination:
            return 0

        # Simplified: assume 2-3 alternative routes usually available
        return 2 if len(self.known_hazards) > 0 else 3
