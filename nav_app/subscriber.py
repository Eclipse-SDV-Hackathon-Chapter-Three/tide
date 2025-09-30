import json
from contract.adas_actor_event import AdasActorEvent
import paho.mqtt.client as mqtt

# Load configuration
with open("mqtt_config.json") as f:
    config = json.load(f)

broker = config["broker"]
port = config["port"]
keepalive = config.get("keepalive", 60)
adas_actor_event_topic = "adas_actor_event"

# Track previous CruiseControl state
previous_cruise_control = None

# Callback when a message is received
def on_message(client, userdata, message):
    global previous_cruise_control
    
    try:
        data = json.loads(message.payload.decode())
        print(f"Received message on {message.topic}: {json.dumps(data, indent=2)}")
        if message.topic == adas_actor_event_topic:
			event = AdasActorEvent(**data)
			on_actor_event(event)
        
    except json.JSONDecodeError:
        print(f"Received non-JSON message: {message.payload}")

def on_actor_event(event: AdasActorEvent):
	print(f"Actor Event - Tag: {event.actor_tag}, Visible: {event.is_visible}, "
		  f"Timestamp: {event.timestamp}, Location: {event.location}")

# Create MQTT client
client = mqtt.Client()
client.on_message = on_message

# Connect and subscribe
client.connect(broker, port, keepalive)
client.subscribe(topic)
print(f"Subscribed to topic: {topic}")

# Keep listening
client.loop_forever()
