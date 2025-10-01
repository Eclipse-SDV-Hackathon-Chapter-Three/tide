import json
import os
from contract.mqtt.topic_handlers import TOPIC_HANDLERS
import paho.mqtt.client as mqtt

CLIENT: mqtt.Client

def initialize_mqtt_client():
    DEFAULT_HANDLER = lambda payload: print("No handler for this topic")

    # Callback when a message is received
    def on_message(client, userdata, message):
        try:
            payload = json.loads(message.payload.decode())
            print(f"Received message on {message.topic}: {json.dumps(payload, indent=2)}")
            topic = message.topic
            topic_handler = TOPIC_HANDLERS.get(topic, DEFAULT_HANDLER)
            topic_handler(payload)
            
        except json.JSONDecodeError:
            print(f"Received non-JSON message: {message.payload}")

    # Create MQTT client
    CLIENT = mqtt.Client()
    CLIENT.on_message = on_message

def start_mqtt_client():
    # Load configuration
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir, "mqtt_config.json")) as f:
        config = json.load(f)

    broker = config["broker"]
    port = config["port"]
    keepalive = config.get("keepalive", 60)
    
    # Connect and subscribe
    CLIENT.connect(broker, port, keepalive)

    # Keep listening
    CLIENT.loop_forever()
