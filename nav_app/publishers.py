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
    print()
    CLIENT.publish(Topics.VEHICLE_ADAS_ACTOR_SHOULD_MONITOR,
                   should_monitor_payload.model_dump_json())


def publish_actor_event_created(payload: AdasActorEvent):
    print("Publishing actor event created:", payload)
    print()
    CLIENT.publish(Topics.VEHICLE_ADAS_ACTOR_EVENT_CREATED,
                   payload.model_dump_json())


def publish_actor_event_deleted(payload: AdasActorEvent):
    print("Publishing actor event deleted:", payload)
    print()
    CLIENT.publish(Topics.VEHICLE_ADAS_ACTOR_EVENT_DELETED,
                   payload.model_dump_json())
