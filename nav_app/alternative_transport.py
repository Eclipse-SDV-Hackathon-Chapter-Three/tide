"""
Alternative transportation suggestion system.
Provides multi-modal transport options with estimated times.
"""
from dataclasses import dataclass
from typing import List, Tuple, Optional
from datetime import datetime, timedelta
from enum import Enum
import math


class TransportMode(Enum):
    """Available transportation modes"""
    WALK = "walk"
    PUBLIC_TRANSIT = "public_transit"
    TAXI = "taxi"
    RIDESHARE = "rideshare"
    BIKE = "bike"


@dataclass
class TransportOption:
    """Represents an alternative transportation option"""
    mode: TransportMode
    estimated_time_minutes: int
    estimated_cost: float
    distance_km: float
    description: str
    instructions: List[str]
    confidence: float  # 0.0 to 1.0


@dataclass
class RouteInfo:
    """Current route information"""
    current_location: Tuple[float, float, float]
    destination: Tuple[float, float, float]
    remaining_distance_km: float
    original_eta_minutes: int


class AlternativeTransportSuggester:
    """Suggests alternative transportation options"""

    # Average speeds in km/h for different modes
    AVERAGE_SPEEDS = {
        TransportMode.WALK: 5.0,
        TransportMode.BIKE: 15.0,
        TransportMode.PUBLIC_TRANSIT: 25.0,
        TransportMode.TAXI: 40.0,
        TransportMode.RIDESHARE: 40.0,
    }

    # Base costs per km (in currency units)
    BASE_COSTS = {
        TransportMode.WALK: 0.0,
        TransportMode.BIKE: 0.1,  # Bike rental
        TransportMode.PUBLIC_TRANSIT: 0.3,
        TransportMode.TAXI: 2.5,
        TransportMode.RIDESHARE: 2.0,
    }

    # Fixed costs (e.g., base fare)
    FIXED_COSTS = {
        TransportMode.WALK: 0.0,
        TransportMode.BIKE: 2.0,
        TransportMode.PUBLIC_TRANSIT: 2.5,
        TransportMode.TAXI: 5.0,
        TransportMode.RIDESHARE: 3.5,
    }

    @staticmethod
    def calculate_distance(
        point1: Tuple[float, float, float],
        point2: Tuple[float, float, float]
    ) -> float:
        """Calculate approximate distance in km between two points"""
        x1, y1, z1 = point1
        x2, y2, z2 = point2

        # Simple Euclidean distance (in real implementation, use proper geo calculations)
        distance_meters = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return distance_meters / 1000.0  # Convert to km

    @staticmethod
    def calculate_eta(distance_km: float, mode: TransportMode) -> int:
        """Calculate estimated time in minutes"""
        speed = AlternativeTransportSuggester.AVERAGE_SPEEDS[mode]
        hours = distance_km / speed
        return int(hours * 60)

    @staticmethod
    def calculate_cost(distance_km: float, mode: TransportMode) -> float:
        """Calculate estimated cost"""
        base_cost = AlternativeTransportSuggester.BASE_COSTS[mode]
        fixed_cost = AlternativeTransportSuggester.FIXED_COSTS[mode]
        return fixed_cost + (base_cost * distance_km)

    @staticmethod
    def generate_suggestions(
        route_info: RouteInfo,
        current_speed_kmh: float,
        stuck_duration_minutes: int = 0
    ) -> List[TransportOption]:
        """
        Generate alternative transportation suggestions.

        Args:
            route_info: Current route information
            current_speed_kmh: Current vehicle speed
            stuck_duration_minutes: How long vehicle has been stuck

        Returns:
            List of TransportOption sorted by estimated time
        """
        suggestions = []
        distance = route_info.remaining_distance_km

        # Walking option (always available for short distances)
        if distance <= 5.0:  # Only suggest walking for <= 5km
            walk_time = AlternativeTransportSuggester.calculate_eta(
                distance, TransportMode.WALK
            )
            suggestions.append(TransportOption(
                mode=TransportMode.WALK,
                estimated_time_minutes=walk_time,
                estimated_cost=0.0,
                distance_km=distance,
                description=f"Walk to destination ({distance:.1f} km)",
                instructions=[
                    "Exit vehicle and enable autonomous return mode",
                    "Follow pedestrian route to destination",
                    f"Estimated walk time: {walk_time} minutes"
                ],
                confidence=0.95
            ))

        # Public transit option
        transit_time = AlternativeTransportSuggester.calculate_eta(
            distance, TransportMode.PUBLIC_TRANSIT
        )
        transit_cost = AlternativeTransportSuggester.calculate_cost(
            distance, TransportMode.PUBLIC_TRANSIT
        )
        # Add wait time (assume average 10 min wait)
        transit_total_time = transit_time + 10 + stuck_duration_minutes

        suggestions.append(TransportOption(
            mode=TransportMode.PUBLIC_TRANSIT,
            estimated_time_minutes=transit_total_time,
            estimated_cost=transit_cost,
            distance_km=distance,
            description=f"Public transit to destination",
            instructions=[
                "Exit vehicle and enable autonomous parking mode",
                "Walk to nearest transit station (150m)",
                "Take Line 2 towards Central Station",
                "Transfer at Central Station to Line 5",
                f"Estimated total time: {transit_total_time} minutes"
            ],
            confidence=0.85
        ))

        # Taxi option
        taxi_time = AlternativeTransportSuggester.calculate_eta(
            distance, TransportMode.TAXI
        )
        taxi_cost = AlternativeTransportSuggester.calculate_cost(
            distance, TransportMode.TAXI
        )
        # Add pickup time
        taxi_total_time = taxi_time + 5 + stuck_duration_minutes

        suggestions.append(TransportOption(
            mode=TransportMode.TAXI,
            estimated_time_minutes=taxi_total_time,
            estimated_cost=taxi_cost,
            distance_km=distance,
            description=f"Taxi to destination",
            instructions=[
                "Exit vehicle and enable autonomous parking mode",
                "Taxi will arrive in 5 minutes",
                f"Direct route to destination",
                f"Estimated cost: ${taxi_cost:.2f}"
            ],
            confidence=0.90
        ))

        # Rideshare option
        rideshare_time = AlternativeTransportSuggester.calculate_eta(
            distance, TransportMode.RIDESHARE
        )
        rideshare_cost = AlternativeTransportSuggester.calculate_cost(
            distance, TransportMode.RIDESHARE
        )
        rideshare_total_time = rideshare_time + 7 + stuck_duration_minutes

        suggestions.append(TransportOption(
            mode=TransportMode.RIDESHARE,
            estimated_time_minutes=rideshare_total_time,
            estimated_cost=rideshare_cost,
            distance_km=distance,
            description=f"Rideshare to destination",
            instructions=[
                "Exit vehicle and enable autonomous parking mode",
                "Uber driver will arrive in 7 minutes",
                "Vehicle: Honda Accord (ABC-123)",
                f"Estimated cost: ${rideshare_cost:.2f}"
            ],
            confidence=0.88
        ))

        # Sort by estimated time
        suggestions.sort(key=lambda x: x.estimated_time_minutes)

        return suggestions

    @staticmethod
    def format_suggestion_for_display(option: TransportOption) -> str:
        """Format a transport option for display to driver"""
        cost_str = f"${option.estimated_cost:.2f}" if option.estimated_cost > 0 else "Free"

        return f"""
╔══════════════════════════════════════════════════════╗
║ {option.mode.value.upper().replace('_', ' ')}
╠══════════════════════════════════════════════════════╣
║ Estimated Time: {option.estimated_time_minutes} minutes
║ Cost: {cost_str}
║ Distance: {option.distance_km:.1f} km
║
║ {option.description}
║
║ Instructions:
"""[1:] + "\n".join(f"║  {i+1}. {instr}" for i, instr in enumerate(option.instructions)) + "\n╚══════════════════════════════════════════════════════╝"

    @staticmethod
    def compare_to_staying(
        suggestions: List[TransportOption],
        current_eta_minutes: int,
        delay_estimate_minutes: int
    ) -> List[Tuple[TransportOption, int]]:
        """
        Compare alternatives to staying in vehicle.

        Returns:
            List of (option, time_saved_minutes) tuples for options that are faster
        """
        staying_time = current_eta_minutes + delay_estimate_minutes
        better_options = []

        for option in suggestions:
            time_saved = staying_time - option.estimated_time_minutes
            if time_saved > 5:  # Only suggest if saves at least 5 minutes
                better_options.append((option, time_saved))

        return better_options
