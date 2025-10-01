
import time
import math
from typing import Dict
from contract.adas_actor_event import AdasActorEvent
from contract.mqtt.topics import Topics
from nav_app.publishers import publish_actor_event_created
from nav_app.publishers import publish_actor_event_deleted
import uuid

# Global state for event tracking
events_dict: Dict[int, AdasActorEvent] = {}  # key: event_counter, value: EventDetails
current_event = None
event_counter = 0
VehicleStillNearEvent = 0
distance_threshold = 50  # meters

def distance(loc1, loc2):
    # Euclidean distance in 3D
    return math.sqrt(
        (loc1[0] - loc2[0]) ** 2 +
        (loc1[1] - loc2[1]) ** 2 +
        (loc1[2] - loc2[2]) ** 2
    )

def handle_vehicle_adas_actor_seen(payload: AdasActorEvent):
    global events_dict, current_event, event_counter, VehicleStillNearEvent

    print(f"Actor Event - Tag: {payload.actor_tag}, Visible: {payload.is_visible}, "
          f"Timestamp: {payload.timestamp}, Location: {payload.location}")

    is_new_event = False
    list_of_relevant_events = [(key, ev) for key, ev in events_dict.items() if ev.actor_tag == payload.actor_tag]
    if payload.is_visible:
        # Check if this event is far from all existing events (>50m)
        is_far = True
        for _, ev in list_of_relevant_events:
            if distance(payload.location, ev.location) <= distance_threshold:
                is_far = False
                break
        if is_far:
            # New event, add to dictionary with a unique UUID
            payload.UUID = str(uuid.uuid4())
            current_event = payload
            event_counter += 1
            events_dict[event_counter] = current_event
            VehicleStillNearEvent = 1
            is_new_event = True
            print(f"Started new event #{event_counter}: {current_event.dict()}")
            publish_actor_event_created(current_event)
        else:
            # No need to update EventStop, just print info for all close events
            for key, ev in list_of_relevant_events:
                if distance(payload.location, ev.location) <= distance_threshold:
                    print(f"Event #{key} is still active: {ev.dict()}")
                    # Check if vehicle moves away from this event
                    if distance(payload.location, ev.location) > distance_threshold:
                        VehicleStillNearEvent = 0
                        print(f"Vehicle is now further than {distance_threshold}m from event location of event #{key}.")
    else:
        # Remove events that become passive (vehicle is close and not visible)
        to_remove = []
        for key, ev in events_dict.items():
            if VehicleStillNearEvent == 0 and distance(payload.location, ev.location) <= distance_threshold:
                print(f"Event #{key} ended and will be removed: {ev.dict()}")
                to_remove.append(key)
                # Publish the deleted event before removing
                publish_actor_event_deleted(ev)
        for key in to_remove:
            print(f"Removing event #{key} from dictionary.")
            del events_dict[key]



#    event_created_payload = create_event_created_payload(payload)
#    if is_new_event:
#        publish_actor_event_created(event_created_payload)
#
#def create_event_created_payload(payload: AdasActorEvent) -> AdasActorEvent:
#    # Fill this function with logic to create the payload for publishing
#    return payload