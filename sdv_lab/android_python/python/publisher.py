import json
import time
import paho.mqtt.client as mqtt

# Load configuration
with open("mqtt_config.json") as f:
    config = json.load(f)

broker = config["broker"]
port = config["port"]
keepalive = config.get("keepalive", 60)
topic1 = config["topics"]["vehicle_parameters"]
topic2 = config["topics"]["rider_status"]

# Load payload from data.json file
with open("data.json") as f:
    payload = json.load(f)
print("Loaded payload from data.json")

# Create MQTT client
client = mqtt.Client()
client.connect(broker, port, keepalive)
client.loop_start()  # Start network loop

# Variables for speed control
speed = payload.get("Speed", 0)
rider_in_vehicle = payload.get("Rider_in_vehicle", True)
direction = 1  # 1 = increasing, -1 = decreasing

try:
    while True:
        # Update speed
        speed += 5 * direction

        # Reverse direction if limits reached
        if speed >= 100:
            direction = -1
        elif speed <= 0:
            direction = 1
            rider_in_vehicle = False    # Simulate rider leaving the vehicle at speed 0

        # Update payload
        payload["Speed"] = speed
        payload["Rider_in_vehicle"] = rider_in_vehicle

        # Publish updated payload
        client.publish(topic1, json.dumps(payload["Speed"]))
        client.publish(topic2, json.dumps(payload["Rider_in_vehicle"]))
        print(f"Published Speed={speed} to {topic1}")
        print(f"Published Rider In Vehicle={rider_in_vehicle} to {topic2}")
        time.sleep(1)  # Wait 1 second

except KeyboardInterrupt:
    print("\nStopped by user")

finally:
    client.loop_stop()
    client.disconnect()