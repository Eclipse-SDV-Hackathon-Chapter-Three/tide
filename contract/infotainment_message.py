"""
Data contracts for communication between nav_app (backend) and
Android infotainment display (frontend).
"""
from datetime import datetime
from typing import List, Optional, Tuple
from pydantic import BaseModel


class AlertLevel(BaseModel):
    """Alert level for notifications"""
    level: str  # "info", "warning", "critical"
    color: str  # Hex color code for UI


class TransportAlternative(BaseModel):
    """Alternative transportation option for display"""
    mode: str  # "walk", "public_transit", "taxi", "rideshare"
    icon: str  # Icon identifier
    estimated_time_minutes: int
    estimated_cost: float
    distance_km: float
    description: str
    instructions: List[str]


class HazardNotification(BaseModel):
    """Hazard detection notification for display"""
    message_type: str = "hazard_notification"
    title: str
    description: str
    hazard_type: str
    severity: str  # "low", "medium", "high", "critical"
    distance_meters: float
    alert_level: str  # "info", "warning", "critical"
    icon: str  # Icon identifier for hazard type
    timestamp: datetime
    show_duration_seconds: int = 10


class RerouteNotification(BaseModel):
    """Reroute notification for approaching drivers"""
    message_type: str = "reroute_notification"
    title: str
    description: str
    old_eta_minutes: int
    new_eta_minutes: int
    time_saved_minutes: int
    reason: str
    timestamp: datetime
    show_duration_seconds: int = 8
    auto_accept: bool = True  # Auto-accept reroute


class AlternativeSuggestion(BaseModel):
    """Alternative transportation suggestions for affected drivers"""
    message_type: str = "alternative_suggestion"
    title: str
    description: str
    current_eta_minutes: int
    delay_estimate_minutes: int
    alternatives: List[TransportAlternative]
    timestamp: datetime
    requires_user_action: bool = True
    timeout_seconds: int = 60  # How long to show before dismissing


class AutonomousConfirmation(BaseModel):
    """Confirmation when vehicle enters autonomous mode"""
    message_type: str = "autonomous_confirmation"
    title: str
    description: str
    chosen_transport_mode: str
    vehicle_destination: Tuple[float, float, float]
    autonomous_mode: str  # "continue_to_destination", "return_home", etc.
    estimated_arrival_time: datetime
    tracking_url: str
    timestamp: datetime


class VehicleStatusUpdate(BaseModel):
    """Vehicle status update for continuous monitoring"""
    message_type: str = "vehicle_status"
    current_speed: float
    current_location: Tuple[float, float, float]
    destination: Optional[Tuple[float, float, float]]
    has_passenger: bool
    autonomous_active: bool
    timestamp: datetime


class CentralScreenCommand(BaseModel):
    """Command to change what's displayed on central screen"""
    message_type: str = "screen_command"
    screen_state: str  # "MODES", "MAP", "SENSORS_FORWARD", "HAZARD_ALERT", "ALTERNATIVES"
    data: Optional[dict] = None  # Additional data for the screen
