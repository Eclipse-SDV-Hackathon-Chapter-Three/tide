"""
Vehicle Data Simulator
Publishes periodic vehicle status updates (speed, location) to simulate real vehicle telemetry.
This simulates the vehicle's onboard computer publishing data.
"""
import json
import time
import random
import math
from datetime import datetime
import paho.mqtt.client as mqtt


class VehicleSimulator:
    """Simulates vehicle telemetry data"""

    def __init__(self, config_path: str = "mqtt_config.json"):
        """Initialize vehicle simulator"""
        # Load MQTT config
        with open(config_path) as f:
            config = json.load(f)

        self.broker = config["broker"]
        self.port = config["port"]

        # Vehicle state
        self.location = [0.0, 0.0, 0.0]  # x, y, z
        self.speed = 60.0  # km/h
        self.has_passenger = True

        # Topics
        self.vehicle_data_topic = "vehicle/data"

        # MQTT client
        self.client = mqtt.Client(client_id="vehicle_simulator")
        self.client.on_connect = self._on_connect
        self.running = False

    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected"""
        if rc == 0:
            print(f"✅ [VehicleSim] Connected to broker at {self.broker}:{self.port}")
            print(f"📡 [VehicleSim] Publishing to: {self.vehicle_data_topic}")
        else:
            print(f"❌ [VehicleSim] Connection failed with code {rc}")
            print(f"   Make sure you're connected to the team WiFi network")
            print(f"   and the MQTT broker at {self.broker} is running")

    def update_vehicle_state(self):
        """Simulate vehicle movement and state changes"""
        # Simulate realistic driving
        # Random speed variation (50-70 km/h for normal driving)
        speed_change = random.uniform(-2.0, 2.0)
        self.speed = max(0.0, min(70.0, self.speed + speed_change))

        # Calculate distance traveled (speed in km/h, time in seconds)
        # distance = speed * time / 3600 (convert to meters per second)
        distance_per_second = (self.speed * 1000) / 3600

        # Move forward in X direction
        self.location[0] += distance_per_second

        # Add small lateral movement
        self.location[1] += random.uniform(-0.1, 0.1)

    def publish_vehicle_data(self):
        """Publish current vehicle status"""
        data = {
            "location": self.location,
            "speed": self.speed,
            "has_passenger": self.has_passenger,
            "timestamp": datetime.utcnow().isoformat()
        }

        payload = json.dumps(data)
        self.client.publish(self.vehicle_data_topic, payload)

        # Print compact status
        print(f"[VehicleSim] Position: {self.location[0]:7.1f}m | Speed: {self.speed:5.1f} km/h | Passenger: {self.has_passenger}")

    def run(self, update_interval_seconds: float = 1.0):
        """
        Run vehicle simulator with periodic updates.

        Args:
            update_interval_seconds: Time between status updates (default: 1 second)
        """
        print("\n" + "🚗 "*20)
        print("🚗  VEHICLE DATA SIMULATOR")
        print("🚗 "*20)
        print(f"\nUpdate Interval: {update_interval_seconds} seconds")
        print(f"Initial Location: {self.location}")
        print(f"Initial Speed: {self.speed} km/h")
        print(f"MQTT Broker: {self.broker}:{self.port}")
        print(f"\n⚠️  Make sure you're on the team WiFi network!")
        print("\n" + "🚗 "*20 + "\n")

        try:
            # Connect to MQTT broker
            print(f"Connecting to MQTT broker at {self.broker}:{self.port}...")
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()

            # Wait a moment for connection
            time.sleep(1)

            self.running = True
            while self.running:
                # Update vehicle state
                self.update_vehicle_state()

                # Publish to MQTT
                self.publish_vehicle_data()

                # Wait for next update
                time.sleep(update_interval_seconds)

        except KeyboardInterrupt:
            print("\n\n[VehicleSim] Shutting down...")
        finally:
            self.client.loop_stop()
            self.client.disconnect()
            print("[VehicleSim] Disconnected\n")

    def stop(self):
        """Stop the simulator"""
        self.running = False


def main():
    """Main entry point"""
    simulator = VehicleSimulator()

    # Run with 1-second updates (realistic for vehicle telemetry)
    simulator.run(update_interval_seconds=1.0)


if __name__ == "__main__":
    main()
