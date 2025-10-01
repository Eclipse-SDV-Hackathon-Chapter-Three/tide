"""
Hazard classification system for real-time event assessment.
Determines severity and impact of detected road events.
"""
from enum import Enum
from typing import Tuple
from datetime import datetime


class HazardSeverity(Enum):
    """Severity levels for road hazards"""
    LOW = "low"  # Minor slowdown, can navigate around
    MEDIUM = "medium"  # Significant delay, consider alternatives
    HIGH = "high"  # Major blockage, strongly recommend alternatives
    CRITICAL = "critical"  # Complete road closure


class HazardType(Enum):
    """Types of road events that can be detected"""
    POLICE = "police"
    ACCIDENT = "accident"
    CONSTRUCTION = "construction"
    TRAFFIC_JAM = "traffic_jam"
    EMERGENCY_VEHICLE = "emergency_vehicle"
    ROAD_HAZARD = "road_hazard"
    WEATHER = "weather"
    UNKNOWN = "unknown"


class HazardClassifier:
    """Classifies detected actors and determines severity"""

    # Mapping of actor tags to hazard types
    ACTOR_TAG_MAPPING = {
        "police": HazardType.POLICE,
        "police_car": HazardType.POLICE,
        "ambulance": HazardType.EMERGENCY_VEHICLE,
        "fire_truck": HazardType.EMERGENCY_VEHICLE,
        "construction": HazardType.CONSTRUCTION,
        "construction_vehicle": HazardType.CONSTRUCTION,
        "accident": HazardType.ACCIDENT,
        "vehicle_stopped": HazardType.ROAD_HAZARD,
        "debris": HazardType.ROAD_HAZARD,
    }

    # Base severity for each hazard type
    BASE_SEVERITY = {
        HazardType.POLICE: HazardSeverity.LOW,
        HazardType.ACCIDENT: HazardSeverity.HIGH,
        HazardType.CONSTRUCTION: HazardSeverity.MEDIUM,
        HazardType.TRAFFIC_JAM: HazardSeverity.MEDIUM,
        HazardType.EMERGENCY_VEHICLE: HazardSeverity.MEDIUM,
        HazardType.ROAD_HAZARD: HazardSeverity.MEDIUM,
        HazardType.WEATHER: HazardSeverity.LOW,
        HazardType.UNKNOWN: HazardSeverity.LOW,
    }

    @staticmethod
    def classify_actor(actor_tag: str) -> HazardType:
        """Convert actor tag to hazard type"""
        actor_tag_lower = actor_tag.lower()

        for tag, hazard_type in HazardClassifier.ACTOR_TAG_MAPPING.items():
            if tag in actor_tag_lower:
                return hazard_type

        return HazardType.UNKNOWN

    @staticmethod
    def assess_severity(
        hazard_type: HazardType,
        is_visible: bool,
        distance_to_vehicle: float,
        current_speed: float = 0.0
    ) -> HazardSeverity:
        """
        Assess the severity of a hazard based on multiple factors.

        Args:
            hazard_type: Type of hazard detected
            is_visible: Whether the hazard is currently visible
            distance_to_vehicle: Distance in meters
            current_speed: Current vehicle speed in km/h

        Returns:
            HazardSeverity level
        """
        base_severity = HazardClassifier.BASE_SEVERITY.get(
            hazard_type, HazardSeverity.LOW
        )

        # If not visible, downgrade severity
        if not is_visible:
            return HazardSeverity.LOW

        # Distance factor: closer = more severe
        if distance_to_vehicle < 50:  # Very close
            if base_severity == HazardSeverity.LOW:
                base_severity = HazardSeverity.MEDIUM
            elif base_severity == HazardSeverity.MEDIUM:
                base_severity = HazardSeverity.HIGH
        elif distance_to_vehicle < 200:  # Moderate distance
            # Keep base severity
            pass
        else:  # Far away
            if base_severity == HazardSeverity.HIGH:
                base_severity = HazardSeverity.MEDIUM
            elif base_severity == HazardSeverity.CRITICAL:
                base_severity = HazardSeverity.HIGH

        # Speed factor: if vehicle is stopped or very slow, increase severity
        if current_speed < 5.0 and base_severity != HazardSeverity.LOW:
            if base_severity == HazardSeverity.MEDIUM:
                base_severity = HazardSeverity.HIGH
            elif base_severity == HazardSeverity.HIGH:
                base_severity = HazardSeverity.CRITICAL

        return base_severity

    @staticmethod
    def should_suggest_alternatives(severity: HazardSeverity) -> bool:
        """Determine if alternative transportation should be suggested"""
        return severity in [HazardSeverity.HIGH, HazardSeverity.CRITICAL]

    @staticmethod
    def should_reroute(severity: HazardSeverity, distance_to_hazard: float) -> bool:
        """Determine if vehicle should be rerouted"""
        # Reroute if severe and far enough to change route
        if severity in [HazardSeverity.HIGH, HazardSeverity.CRITICAL]:
            return distance_to_hazard > 100  # More than 100m away
        elif severity == HazardSeverity.MEDIUM:
            return distance_to_hazard > 500  # More than 500m away
        return False
