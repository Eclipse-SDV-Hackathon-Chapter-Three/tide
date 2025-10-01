import json
import time
from contract.adas_actor_event import AdasActorEvent
from contract.adas_actor_monitor_event import AdasActorMonitorEvent
from contract.mqtt.client import CLIENT
from contract.mqtt.topics import Topics

def publish_should_monitor_event():
    should_monitor_payload = AdasActorMonitorEvent(
        actor_tag="pedestrian", should_monitor=True
    )
    print("Publishing should monitor event:", should_monitor_payload)
    CLIENT.publish(Topics.VEHICLE_ADAS_ACTOR_SHOULD_MONITOR, json.dumps(should_monitor_payload))

def publish_actor_event_created(payload: AdasActorEvent):
    print("Publishing actor event created:", payload)
    CLIENT.publish(Topics.VEHICLE_ADAS_ACTOR_EVENT_CREATED, json.dumps(payload))

def publish_actor_event_deleted(payload: AdasActorEvent):
    print("Publishing actor event deleted:", payload)
    CLIENT.publish(Topics.VEHICLE_ADAS_ACTOR_EVENT_DELETED, json.dumps(payload))

