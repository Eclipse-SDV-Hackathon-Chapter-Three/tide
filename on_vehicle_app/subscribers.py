from contract.mqtt.client import CLIENT
from contract.mqtt.topics import Topics

def start_listening_to_topics():
    CLIENT.subscribe(Topics.VEHICLE_ADAS_ACTOR_SHOULD_MONITOR)
