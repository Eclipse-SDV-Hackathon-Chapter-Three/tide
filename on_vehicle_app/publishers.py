import json
from contract.adas_actor_event import AdasActorEvent
from contract.mqtt.client import CLIENT, initialize_mqtt_client
from contract.mqtt.topics import Topics
from contract.passenger_leaving_event import PassengerLeftEvent
from on_vehicle_app.constants import ONLY_PRINT


def publish(topic: str, payload: str):
    if ONLY_PRINT:
        print(payload)
        print()
        return

    print("Publishing topic '{}' with data {}".format(topic, payload))
    CLIENT.publish(topic, payload)


def publish_actor_seen_event(adas_actor_seen_event: AdasActorEvent):
    payload: str = adas_actor_seen_event.model_dump_json()
    publish(Topics.VEHICLE_ADAS_ACTOR_SEEN, payload)


def publish_passenger_left_vehicle_event(passenger_left_event: PassengerLeftEvent):
    payload: str = passenger_left_event.model_dump_json()
    publish(Topics.VEHICLE_PASSENGER_LEFT, payload)
