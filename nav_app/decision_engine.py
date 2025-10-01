"""
Decision engine for FASLit system.
Determines whether vehicle should:
1. Reroute (approaching vehicle - FIRST AVOID)
2. Suggest alternatives (affected vehicle - SECOND LEAVE IT THERE)
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

from nav_app.hazard_classifier import HazardSeverity, HazardType
from nav_app.alternative_transport import TransportOption, RouteInfo
from nav_app.route_manager import HazardZone


class VehicleState(Enum):
    """Current state of the vehicle relative to hazard"""
    UNAFFECTED = "unaffected"  # No hazards on route
    APPROACHING = "approaching"  # Hazard ahead, can reroute (FIRST AVOID)
    AFFECTED = "affected"  # Already at hazard, stuck (SECOND LEAVE IT)
    REROUTING = "rerouting"  # Currently changing route
    PASSENGER_EXITING = "passenger_exiting"  # Passenger choosing alternative


class ActionType(Enum):
    """Types of actions the system can recommend"""
    NO_ACTION = "no_action"
    REROUTE = "reroute"  # Find alternative route
    SUGGEST_ALTERNATIVES = "suggest_alternatives"  # Offer transport options
    MONITOR = "monitor"  # Watch situation
    AUTONOMOUS_HANDOFF = "autonomous_handoff"  # Passenger exited, vehicle autonomous


@dataclass
class DecisionContext:
    """Context information for decision making"""
    current_location: tuple
    current_speed_kmh: float
    hazard_location: tuple
    hazard_severity: HazardSeverity
    hazard_type: HazardType
    distance_to_hazard_m: float
    time_stuck_minutes: int
    route_info: Optional[RouteInfo]
    has_passenger: bool


@dataclass
class Decision:
    """Decision output from the engine"""
    action: ActionType
    vehicle_state: VehicleState
    reasoning: str
    alternatives: Optional[List[TransportOption]] = None
    reroute_available: bool = False
    time_saved_minutes: int = 0
    confidence: float = 0.0


class DecisionEngine:
    """Core decision engine implementing FASLit logic"""

    # Thresholds for decision making
    APPROACHING_THRESHOLD_M = 500.0  # Consider reroute if > 500m away
    AFFECTED_SPEED_THRESHOLD_KMH = 10.0  # Stuck if speed < 10 km/h
    STUCK_TIME_THRESHOLD_MIN = 5  # Stuck if slow for > 5 minutes
    MIN_TIME_SAVINGS_MIN = 5  # Only suggest if saves >= 5 minutes

    def __init__(self):
        self.last_decision: Optional[Decision] = None
        self.decision_history: List[Decision] = []

    def make_decision(self, context: DecisionContext) -> Decision:
        """
        Main decision-making logic.

        Implements FASLit strategy:
        1. FIRST AVOID: If approaching hazard, reroute
        2. SECOND LEAVE IT: If affected, suggest alternatives

        Args:
            context: Current situation context

        Returns:
            Decision with recommended action
        """
        # Determine vehicle state
        vehicle_state = self._determine_vehicle_state(context)

        # Make decision based on state
        if vehicle_state == VehicleState.UNAFFECTED:
            decision = self._handle_unaffected(context)

        elif vehicle_state == VehicleState.APPROACHING:
            decision = self._handle_approaching(context)

        elif vehicle_state == VehicleState.AFFECTED:
            decision = self._handle_affected(context)

        else:
            decision = Decision(
                action=ActionType.NO_ACTION,
                vehicle_state=vehicle_state,
                reasoning="Monitoring situation",
                confidence=0.5
            )

        # Store decision
        self.last_decision = decision
        self.decision_history.append(decision)

        return decision

    def _determine_vehicle_state(self, context: DecisionContext) -> VehicleState:
        """Determine current vehicle state"""

        # Check if affected (stuck at hazard)
        is_slow = context.current_speed_kmh < self.AFFECTED_SPEED_THRESHOLD_KMH
        is_stuck_long = context.time_stuck_minutes >= self.STUCK_TIME_THRESHOLD_MIN
        is_at_hazard = context.distance_to_hazard_m < 100  # Within 100m

        if is_at_hazard and (is_slow or is_stuck_long):
            return VehicleState.AFFECTED

        # Check if approaching (can still reroute)
        if context.distance_to_hazard_m > self.APPROACHING_THRESHOLD_M:
            if context.hazard_severity in [HazardSeverity.HIGH, HazardSeverity.CRITICAL]:
                return VehicleState.APPROACHING

        # Otherwise unaffected or just monitoring
        return VehicleState.UNAFFECTED

    def _handle_unaffected(self, context: DecisionContext) -> Decision:
        """Handle unaffected vehicle"""
        if context.hazard_severity == HazardSeverity.LOW:
            return Decision(
                action=ActionType.NO_ACTION,
                vehicle_state=VehicleState.UNAFFECTED,
                reasoning="Hazard detected but severity is low. Continue on current route.",
                confidence=0.9
            )
        else:
            return Decision(
                action=ActionType.MONITOR,
                vehicle_state=VehicleState.UNAFFECTED,
                reasoning="Monitoring hazard. Will reroute if it affects planned route.",
                confidence=0.8
            )

    def _handle_approaching(self, context: DecisionContext) -> Decision:
        """
        Handle approaching vehicle - FIRST AVOID strategy.

        Try to reroute around the hazard.
        """
        reasoning = (
            f"Hazard detected {int(context.distance_to_hazard_m)}m ahead. "
            f"Severity: {context.hazard_severity.value}, Type: {context.hazard_type.value}. "
            f"Attempting to find alternative route to avoid delay."
        )

        # Estimate time saved by rerouting
        delay_estimate = self._estimate_delay(context.hazard_severity)
        reroute_penalty = 5  # Assume 5 min penalty for reroute
        time_saved = delay_estimate - reroute_penalty

        return Decision(
            action=ActionType.REROUTE,
            vehicle_state=VehicleState.APPROACHING,
            reasoning=reasoning,
            reroute_available=True,
            time_saved_minutes=max(0, time_saved),
            confidence=0.85
        )

    def _handle_affected(self, context: DecisionContext) -> Decision:
        """
        Handle affected vehicle - SECOND LEAVE IT strategy.

        Suggest alternative transportation options.
        """
        reasoning = (
            f"Vehicle is affected by {context.hazard_type.value}. "
            f"Current speed: {context.current_speed_kmh:.1f} km/h, "
            f"Stuck for: {context.time_stuck_minutes} minutes. "
            f"Analyzing alternative transportation options that may be faster."
        )

        # Only suggest alternatives if it will save significant time
        if context.hazard_severity in [HazardSeverity.HIGH, HazardSeverity.CRITICAL]:
            return Decision(
                action=ActionType.SUGGEST_ALTERNATIVES,
                vehicle_state=VehicleState.AFFECTED,
                reasoning=reasoning,
                reroute_available=False,
                confidence=0.9
            )
        else:
            return Decision(
                action=ActionType.MONITOR,
                vehicle_state=VehicleState.AFFECTED,
                reasoning="Affected by hazard but situation may improve. Monitoring...",
                confidence=0.7
            )

    def _estimate_delay(self, severity: HazardSeverity) -> int:
        """Estimate delay in minutes based on hazard severity"""
        delay_map = {
            HazardSeverity.LOW: 5,
            HazardSeverity.MEDIUM: 15,
            HazardSeverity.HIGH: 30,
            HazardSeverity.CRITICAL: 60
        }
        return delay_map.get(severity, 10)

    def should_notify_driver(self, decision: Decision) -> bool:
        """Determine if driver should be notified"""
        notify_actions = {
            ActionType.REROUTE,
            ActionType.SUGGEST_ALTERNATIVES,
            ActionType.AUTONOMOUS_HANDOFF
        }
        return decision.action in notify_actions

    def format_decision_for_display(self, decision: Decision) -> str:
        """Format decision for display to driver"""
        action_titles = {
            ActionType.NO_ACTION: "✓ All Clear",
            ActionType.REROUTE: "🔄 Reroute Recommended",
            ActionType.SUGGEST_ALTERNATIVES: "🚶 Alternative Options Available",
            ActionType.MONITOR: "👁 Monitoring Situation",
            ActionType.AUTONOMOUS_HANDOFF: "🤖 Autonomous Mode Active"
        }

        state_icons = {
            VehicleState.UNAFFECTED: "✓",
            VehicleState.APPROACHING: "⚠",
            VehicleState.AFFECTED: "🚫",
            VehicleState.REROUTING: "🔄",
            VehicleState.PASSENGER_EXITING: "🚶"
        }

        title = action_titles.get(decision.action, "Status")
        icon = state_icons.get(decision.vehicle_state, "•")

        output = f"\n{'='*60}\n"
        output += f"{icon} {title}\n"
        output += f"{'='*60}\n\n"
        output += f"{decision.reasoning}\n\n"

        if decision.time_saved_minutes > 0:
            output += f"Estimated Time Saved: {decision.time_saved_minutes} minutes\n"

        if decision.reroute_available:
            output += f"Alternative Routes: Available\n"

        output += f"\nConfidence: {decision.confidence*100:.0f}%\n"
        output += f"{'='*60}\n"

        return output
