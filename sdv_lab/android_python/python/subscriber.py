import json
import paho.mqtt.client as mqtt

# Load configuration
with open("mqtt_config.json") as f:
    config = json.load(f)

broker = config["broker"]
port = config["port"]
keepalive = config.get("keepalive", 60)
topic1 = config["topics"]["vehicle_parameters"]
topic2 = config["topics"]["rider_status"]

# Callback when a message is received
def on_message(client, userdata, message):    
    try:
        data = json.loads(message.payload.decode())
        print(f"Received message on {message.topic}: {json.dumps(data, indent=2)}")

        # Handle messages from topic1 (vehicle_parameters)
        if message.topic == topic1:
            speed = data.get("Speed", 0)
            print(f"Speed: {speed}")

        # Handle messages from topic2 (rider_status)
        elif message.topic == topic2:
            rider_in_vehicle = data
            print(f"Rider in Vehicle: {rider_in_vehicle}")

    except json.JSONDecodeError:
        print(f"Received non-JSON message: {message.payload}")

# Create MQTT client
client = mqtt.Client()
client.on_message = on_message

# Connect and subscribe
client.connect(broker, port, keepalive)
client.subscribe(topic1)
client.subscribe(topic2)
print(f"Subscribed to topics: {topic1}, {topic2}")

# Keep listening
client.loop_forever()
