
import time
from contract.adas_actor_event import AdasActorEvent
from nav_app.publishers import publish_actor_event_created

def handle_vehicle_adas_actor_seen(payload: AdasActorEvent):
    is_new_event = determine_if_new_event(payload)
    event_created_payload = create_event_created_payload(payload)
    if is_new_event:
        publish_actor_event_created(payload)
    
def determine_if_new_event(payload: AdasActorEvent) -> bool: ...

def create_event_created_payload(payload: AdasActorEvent) -> AdasActorEvent:
    ...