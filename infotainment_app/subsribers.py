import json
from contract.adas_actor_event import AdasActorEvent
from contract.mqtt.client import CLIENT
from contract.mqtt.topic_handlers import TOPIC_HANDLERS
from contract.mqtt.topics import Topics
from infotainment_app.handlers import handle_actor_event_created, handle_actor_event_deleted

def start_listening_to_topics():
        print("Listening to topics for infotainment")
        TOPIC_HANDLERS[Topics.VEHICLE_ADAS_ACTOR_EVENT_CREATED] = lambda payload: handle_actor_event_created(AdasActorEvent(
                **payload))
        TOPIC_HANDLERS[Topics.VEHICLE_ADAS_ACTOR_EVENT_DELETED] = lambda payload: handle_actor_event_deleted(AdasActorEvent(
                **payload))
        CLIENT.subscribe(Topics.VEHICLE_ADAS_ACTOR_EVENT_CREATED)
        CLIENT.subscribe(Topics.VEHICLE_ADAS_ACTOR_EVENT_DELETED)
