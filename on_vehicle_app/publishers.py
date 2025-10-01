import json
from contract.adas_actor_event import AdasActorEvent
from contract.mqtt.client import CLIENT
from contract.mqtt.topics import Topics
from contract.passenger_leaving_event import PassengerLeftEvent

def publish_actor_seen_event(adas_actor_seen_event: AdasActorEvent):
    print("Publishing actor seen event for actor:", adas_actor_seen_event.actor_tag)
    payload = json.dumps(adas_actor_seen_event)
    CLIENT.publish(Topics.VEHICLE_ADAS_ACTOR_SEEN, payload)

def publish_passenger_left_vehicle_event(passenger_left_event: PassengerLeftEvent):
    print("Publishing passenger left vehicle event")
    payload = json.dumps(passenger_left_event)
    CLIENT.publish(Topics.VEHICLE_PASSENGER_LEFT, payload)
