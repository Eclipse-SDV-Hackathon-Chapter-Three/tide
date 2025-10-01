import json
from contract.adas_actor_event import AdasActorEvent
from contract.mqtt.client import CLIENT, IS_INITIALIZED
from contract.mqtt.topics import Topics
from contract.passenger_leaving_event import PassengerLeftEvent

def publish(topic: str, payload: str):
    """
    Publish message to MQTT broker.
    Prints payload for visibility and publishes to broker if initialized.
    """
    # Always print for visibility
    print(payload)
    print()

    # Attempt to publish to MQTT
    global IS_INITIALIZED
    if not IS_INITIALIZED:
        try:
            import contract.mqtt.client
            contract.mqtt.client.initialize_mqtt_client()
            IS_INITIALIZED = True
            print(f"✅ Connected to MQTT broker\n")
        except Exception as e:
            print(f"⚠️  Note: MQTT not connected - {e}")
            print(f"   (Make sure you're on team WiFi and broker at 192.168.41.250 is running)")
            print(f"   Messages are printed above for visibility.\n")
            return

    try:
        CLIENT.publish(topic, payload)
    except Exception as e:
        print(f"⚠️  Failed to publish to MQTT: {e}\n")

def publish_actor_seen_event(adas_actor_seen_event: AdasActorEvent):
    print("Publishing actor seen event for actor:", adas_actor_seen_event.actor_tag)
    payload: str = adas_actor_seen_event.model_dump_json()
    publish(Topics.VEHICLE_ADAS_ACTOR_SEEN, payload)

def publish_passenger_left_vehicle_event(passenger_left_event: PassengerLeftEvent):
    print("Publishing passenger left vehicle event")
    payload: str = passenger_left_event.model_dump_json()
    publish(Topics.VEHICLE_PASSENGER_LEFT, payload)
