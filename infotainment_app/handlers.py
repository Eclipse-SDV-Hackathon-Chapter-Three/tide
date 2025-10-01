from typing import Dict
from contract.adas_actor_event import AdasActorEvent
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

def handle_actor_event_created(payload: AdasActorEvent):
    global active_events

    if payload.UUID not in active_events:
        active_events[payload.UUID] = payload
        print(f"Added new active event: {payload.UUID}")
        # Check if the car is close enough to the event
        car_location = payload.location
        if distance(car_location, payload.location) <= 50:  # Threshold distance in meters
            print("Event is in of range")
            notification_message = f"Event Location: {payload.location}"
            update_notification_message(notification_message)
        else:
            print("Event is out of range")

def handle_actor_event_deleted(payload: AdasActorEvent):
    global active_events

    if payload.UUID in active_events:
        del active_events[payload.UUID]
        print(f"Removed active event: {payload.UUID}")