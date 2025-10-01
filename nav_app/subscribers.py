import json
from contract.adas_actor_event import AdasActorEvent
from contract.mqtt.client import CLIENT
from contract.mqtt.topic_handlers import TOPIC_HANDLERS
from contract.mqtt.topics import Topics
from nav_app.handlers import handle_vehicle_adas_actor_seen


def start_listening_to_topics():
    TOPIC_HANDLERS[Topics.VEHICLE_ADAS_ACTOR_SEEN] = lambda payload: handle_vehicle_adas_actor_seen(AdasActorEvent(
        **payload))
    CLIENT.subscribe(Topics.VEHICLE_ADAS_ACTOR_SEEN)
