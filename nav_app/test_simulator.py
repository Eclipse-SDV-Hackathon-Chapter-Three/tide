#!/usr/bin/env python3
"""
Test Simulator for FASLit Nav-App
Simulates ADAS events and vehicle data to test the complete nav_app flow.
"""
import json
import time
import random
from datetime import datetime
import paho.mqtt.client as mqtt


class TestSimulator:
    """Simulates ADAS events and vehicle data for testing"""

    def __init__(self, config_path: str = "mqtt_config.json"):
        """Initialize test simulator"""

        # Load configuration
        with open(config_path) as f:
            config = json.load(f)

        self.broker = config["broker"]
        self.port = config["port"]
        self.keepalive = config.get("keepalive", 60)

        # MQTT client
        self.mqtt_client = mqtt.Client(client_id="test_simulator")
        self.mqtt_client.on_connect = self._on_connect

        # Topics
        self.ADAS_TOPIC = "adas_actor_event"
        self.VEHICLE_DATA_TOPIC = "vehicle/data"
        self.PASSENGER_EXIT_TOPIC = "passenger_exit"

        # Simulation state
        self.current_location = [1000.0, 500.0, 0.0]
        self.current_speed = 60.0
        self.simulation_running = False

    def connect(self):
        """Connect to MQTT broker"""
        print(f"\n[Simulator] Connecting to MQTT broker at {self.broker}:{self.port}...")
        self.mqtt_client.connect(self.broker, self.port, self.keepalive)
        self.mqtt_client.loop_start()
        time.sleep(1)  # Give it time to connect

    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected"""
        if rc == 0:
            print(f"[Simulator] ✓ Connected to MQTT broker")
        else:
            print(f"[Simulator] ✗ Connection failed with code {rc}")

    def publish_adas_event(self, actor_tag: str, location: tuple, is_visible: bool = True):
        """Publish an ADAS actor detection event"""
        event = {
            "actor_tag": actor_tag,
            "location": list(location),
            "is_visible": is_visible,
            "timestamp": datetime.now().isoformat()
        }

        self.mqtt_client.publish(self.ADAS_TOPIC, json.dumps(event))
        print(f"\n[Simulator] 📸 Published ADAS event: {actor_tag} at {location}")

    def publish_vehicle_data(self, location: tuple, speed: float):
        """Publish vehicle data update"""
        data = {
            "location": list(location),
            "speed": speed
        }

        self.mqtt_client.publish(self.VEHICLE_DATA_TOPIC, json.dumps(data))

    def publish_passenger_exit(self, location: tuple):
        """Publish passenger exit event"""
        event = {
            "location": list(location),
            "timestamp": datetime.now().isoformat()
        }

        self.mqtt_client.publish(self.PASSENGER_EXIT_TOPIC, json.dumps(event))
        print(f"\n[Simulator] 🚪 Published passenger exit event at {location}")

    def simulate_approaching_hazard(self):
        """Simulate approaching a hazard (should trigger reroute)"""
        print("\n" + "="*70)
        print("TEST SCENARIO 1: Approaching Hazard (FIRST AVOID)")
        print("="*70)

        # Vehicle is far from hazard (800m ahead)
        self.current_location = [1000.0, 500.0, 0.0]
        self.current_speed = 60.0

        print(f"\n[Simulator] Vehicle location: {self.current_location}")
        print(f"[Simulator] Vehicle speed: {self.current_speed} km/h")

        # Update vehicle data
        self.publish_vehicle_data(self.current_location, self.current_speed)
        time.sleep(1)

        # Detect police ahead (800m away)
        hazard_location = (1800.0, 500.0, 0.0)
        print(f"\n[Simulator] Detecting hazard ahead at {hazard_location}...")
        self.publish_adas_event("vehicle.police.car", hazard_location)

        print(f"\n[Simulator] ✓ Expected: Nav-app should REROUTE (First Avoid)")
        print(f"[Simulator] ✓ Frontend should show: Reroute notification")

    def simulate_affected_by_hazard(self):
        """Simulate being stuck in traffic due to hazard (should suggest alternatives)"""
        print("\n" + "="*70)
        print("TEST SCENARIO 2: Stuck in Traffic (SECOND LEAVE IT)")
        print("="*70)

        # Vehicle is very close to hazard and stuck
        self.current_location = [2000.0, 1000.0, 0.0]
        self.current_speed = 5.0  # Very slow

        print(f"\n[Simulator] Vehicle location: {self.current_location}")
        print(f"[Simulator] Vehicle speed: {self.current_speed} km/h (STUCK)")

        # Update vehicle data to show we're stuck
        for i in range(3):
            self.publish_vehicle_data(self.current_location, self.current_speed)
            time.sleep(0.5)

        # Detect accident very close
        hazard_location = (2050.0, 1000.0, 0.0)
        print(f"\n[Simulator] Detecting accident nearby at {hazard_location}...")
        self.publish_adas_event("static.prop.trafficcone01", hazard_location)

        print(f"\n[Simulator] ✓ Expected: Nav-app should SUGGEST ALTERNATIVES (Second Leave It)")
        print(f"[Simulator] ✓ Frontend should show: Alternative transportation options")

    def simulate_critical_hazard(self):
        """Simulate critical hazard detection"""
        print("\n" + "="*70)
        print("TEST SCENARIO 3: Critical Hazard - Emergency Vehicle")
        print("="*70)

        # Vehicle moving normally
        self.current_location = [3000.0, 1500.0, 0.0]
        self.current_speed = 80.0

        print(f"\n[Simulator] Vehicle location: {self.current_location}")
        print(f"[Simulator] Vehicle speed: {self.current_speed} km/h")

        self.publish_vehicle_data(self.current_location, self.current_speed)
        time.sleep(1)

        # Detect emergency vehicle nearby
        hazard_location = (3400.0, 1500.0, 0.0)
        print(f"\n[Simulator] Detecting emergency vehicle at {hazard_location}...")
        self.publish_adas_event("vehicle.carlamotors.firetruck", hazard_location)

        print(f"\n[Simulator] ✓ Expected: Nav-app should detect CRITICAL severity")
        print(f"[Simulator] ✓ Frontend should show: Critical hazard alert (RED)")

    def run_full_test_sequence(self):
        """Run complete test sequence"""
        print("\n" + "="*70)
        print("FASLIT NAV-APP FULL TEST SEQUENCE")
        print("="*70)
        print("This will simulate 3 test scenarios:")
        print("1. Approaching hazard → Reroute (First Avoid)")
        print("2. Stuck in traffic → Alternative suggestions (Second Leave It)")
        print("3. Critical hazard → Emergency alert")
        print("="*70)

        input("\nPress Enter to start test sequence...")

        # Test 1: Approaching hazard
        self.simulate_approaching_hazard()
        print(f"\n[Simulator] Waiting 5 seconds before next test...\n")
        time.sleep(5)

        # Test 2: Stuck in traffic
        self.simulate_affected_by_hazard()
        print(f"\n[Simulator] Waiting 5 seconds before next test...\n")
        time.sleep(5)

        # Test 3: Critical hazard
        self.simulate_critical_hazard()

        print(f"\n\n[Simulator] ✓ Test sequence complete!")
        print(f"[Simulator] Check your test frontend to verify all messages were displayed correctly.\n")

    def interactive_mode(self):
        """Interactive mode for manual testing"""
        print("\n" + "="*70)
        print("INTERACTIVE TEST MODE")
        print("="*70)

        while True:
            print("\nAvailable test scenarios:")
            print("1. Approaching hazard (triggers reroute)")
            print("2. Stuck in traffic (suggests alternatives)")
            print("3. Critical emergency vehicle")
            print("4. Run full sequence")
            print("5. Custom ADAS event")
            print("6. Update vehicle data")
            print("0. Exit")

            choice = input("\nSelect option (0-6): ").strip()

            if choice == "0":
                print("\n[Simulator] Exiting...")
                break
            elif choice == "1":
                self.simulate_approaching_hazard()
            elif choice == "2":
                self.simulate_affected_by_hazard()
            elif choice == "3":
                self.simulate_critical_hazard()
            elif choice == "4":
                self.run_full_test_sequence()
            elif choice == "5":
                self._custom_adas_event()
            elif choice == "6":
                self._update_vehicle_data()
            else:
                print(f"\n[Simulator] Invalid option. Please try again.")

    def _custom_adas_event(self):
        """Create custom ADAS event"""
        print("\nCustom ADAS Event Creator")
        print("Common actor tags:")
        print("  - vehicle.police.car")
        print("  - static.prop.trafficcone01 (accident)")
        print("  - vehicle.carlamotors.firetruck")
        print("  - static.prop.constructioncone")

        actor_tag = input("Actor tag: ").strip()
        if not actor_tag:
            actor_tag = "vehicle.police.car"

        try:
            x = float(input(f"X coordinate (current: {self.current_location[0]}): ") or self.current_location[0])
            y = float(input(f"Y coordinate (current: {self.current_location[1]}): ") or self.current_location[1])
            z = float(input(f"Z coordinate (current: {self.current_location[2]}): ") or self.current_location[2])

            location = (x, y, z)
            self.publish_adas_event(actor_tag, location)
        except ValueError:
            print("[Simulator] Invalid coordinates")

    def _update_vehicle_data(self):
        """Update vehicle data"""
        print("\nUpdate Vehicle Data")
        try:
            x = float(input(f"X coordinate (current: {self.current_location[0]}): ") or self.current_location[0])
            y = float(input(f"Y coordinate (current: {self.current_location[1]}): ") or self.current_location[1])
            z = float(input(f"Z coordinate (current: {self.current_location[2]}): ") or self.current_location[2])
            speed = float(input(f"Speed km/h (current: {self.current_speed}): ") or self.current_speed)

            self.current_location = [x, y, z]
            self.current_speed = speed

            self.publish_vehicle_data(self.current_location, self.current_speed)
            print(f"\n[Simulator] ✓ Published vehicle data")
        except ValueError:
            print("[Simulator] Invalid input")


def main():
    """Main entry point"""
    import sys

    simulator = TestSimulator()
    simulator.connect()

    print("\n[Simulator] Ready to send test events")

    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # Run full test sequence automatically
        simulator.run_full_test_sequence()
    else:
        # Interactive mode
        simulator.interactive_mode()

    simulator.mqtt_client.loop_stop()
    print("\n[Simulator] Goodbye!")


if __name__ == "__main__":
    main()
