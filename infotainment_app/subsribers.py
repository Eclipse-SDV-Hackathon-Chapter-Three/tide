import json
from contract.mqtt.client import CLIENT
from contract.mqtt.topics import Topics
from infotainment_app.handlers import handle_actor_event_created, handle_actor_event_deleted

def on_message(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode("utf-8"))
        topic = message.topic

        if topic == Topics.VEHICLE_ADAS_ACTOR_EVENT_CREATED:
            handle_actor_event_created(payload)
        elif topic == Topics.VEHICLE_ADAS_ACTOR_EVENT_DELETED:
            handle_actor_event_deleted(payload)
    except Exception as e:
        print(f"Error processing message: {e}")

# Subscribe to relevant topics
CLIENT.subscribe(Topics.VEHICLE_ADAS_ACTOR_EVENT_CREATED)
CLIENT.subscribe(Topics.VEHICLE_ADAS_ACTOR_EVENT_DELETED)
CLIENT.on_message = on_message