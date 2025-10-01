import json
from contract.adas_actor_event import AdasActorEvent
from contract.mqtt.client import CLIENT
from contract.mqtt.topics import Topics

def publish_should_monitor_event(adas_actor_seen_event: AdasActorEvent):
    print("Publishing should monitor event for actor:", adas_actor_seen_event.actor_tag)
    payload = json.dumps(adas_actor_seen_event)
    CLIENT.publish(Topics.VEHICLE_ADAS_ACTOR_SEEN, payload)
