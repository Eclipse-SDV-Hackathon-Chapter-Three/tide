import json
from typing import Dict
from contract.adas_actor_event import AdasActorEvent
from nav_app.publishers import publish_actor_event_created
import math
from infotainment_app.notification_manager import update_notification_message

# Dictionary to store currently active events
active_events: Dict[str, AdasActorEvent] = {}

def distance(loc1, loc2):
    # Euclidean distance in 3D
    return math.sqrt(
        (loc1[0] - loc2[0]) ** 2 +
        (loc1[1] - loc2[1]) ** 2 +
        (loc1[2] - loc2[2]) ** 2
    )

def handle_actor_event_created(payload: dict):
    global active_events

    event = AdasActorEvent(**payload)
    if event.UUID not in active_events:
        active_events[event.UUID] = event
        print(f"Added new active event: {event.UUID}")
        # Check if the car is close enough to the event
        car_location = payload.get("location", (0, 0, 0))  # Use payload.location as the car's location
        if distance(car_location, event.location) <= 50:  # Threshold distance in meters
            notification_message = f"Event Location: {event.location}"
            update_notification_message(notification_message)

def handle_actor_event_deleted(payload: dict):
    global active_events

    event = AdasActorEvent(**payload)
    if event.UUID in active_events:
        del active_events[event.UUID]
        print(f"Removed active event: {event.UUID}")