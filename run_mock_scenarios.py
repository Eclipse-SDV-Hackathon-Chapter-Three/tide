"""
Mock CARLA Sensor Data Generator with Various Scenarios
Generates diverse hazard scenarios for testing the FASLit navigation system.
Runs with 10-second intervals between scenarios.
"""
import time
import random
from datetime import datetime
from typing import Tuple

from contract.adas_actor_event import AdasActorEvent
from contract.passenger_leaving_event import PassengerLeftEvent
from on_vehicle_app.publishers import publish_actor_seen_event, publish_passenger_left_vehicle_event


class ScenarioSimulator:
    """Simulates various driving scenarios with ADAS events"""

    def __init__(self):
        self.ego_location = [0.0, 0.0, 0.0]  # Starting location
        self.ego_speed = 60.0  # km/h
        self.scenario_count = 0

    def update_ego_position(self, distance_meters: float = 100.0):
        """Simulate ego vehicle movement"""
        # Move forward in X direction
        self.ego_location[0] += distance_meters

    def get_location_ahead(self, distance_meters: float) -> Tuple[float, float, float]:
        """Get a location ahead of ego vehicle"""
        return (
            self.ego_location[0] + distance_meters,
            self.ego_location[1],
            self.ego_location[2]
        )

    def get_location_side(self, distance_meters: float, side_offset: float) -> Tuple[float, float, float]:
        """Get a location to the side of ego vehicle"""
        return (
            self.ego_location[0] + distance_meters,
            self.ego_location[1] + side_offset,
            self.ego_location[2]
        )

    def create_event(
        self,
        actor_tag: str,
        is_visible: bool,
        location: Tuple[float, float, float]
    ) -> AdasActorEvent:
        """Create an ADAS actor event"""
        return AdasActorEvent(
            UUID=None,
            actor_tag=actor_tag,
            is_visible=is_visible,
            timestamp=datetime.utcnow(),
            location=location
        )

    # ==================== SCENARIO DEFINITIONS ====================

    def scenario_police_ahead(self):
        """Scenario 1: Police car 200m ahead - should trigger reroute"""
        print("\n" + "="*70)
        print("🚨 SCENARIO 1: Police Car Ahead")
        print("="*70)
        print("📍 Location: 200m ahead on same lane")
        print("⚡ Expected: High severity, trigger reroute for approaching vehicles")
        print("="*70 + "\n")

        location = self.get_location_ahead(200.0)
        event = self.create_event("Police", True, location)
        publish_actor_seen_event(event)

    def scenario_accident_close(self):
        """Scenario 2: Traffic accident 50m ahead - critical severity"""
        print("\n" + "="*70)
        print("🚧 SCENARIO 2: Traffic Accident Close By")
        print("="*70)
        print("📍 Location: 50m ahead - CRITICAL")
        print("⚡ Expected: Critical severity, immediate reroute or suggest alternatives")
        print("="*70 + "\n")

        # Multiple vehicles involved
        location1 = self.get_location_ahead(50.0)
        location2 = self.get_location_ahead(55.0)

        event1 = self.create_event("Car", True, location1)
        event2 = self.create_event("Car", True, location2)

        publish_actor_seen_event(event1)
        time.sleep(0.5)
        publish_actor_seen_event(event2)

    def scenario_pedestrian_crossing(self):
        """Scenario 3: Pedestrians crossing road"""
        print("\n" + "="*70)
        print("🚶 SCENARIO 3: Pedestrians Crossing Road")
        print("="*70)
        print("📍 Location: 80m ahead, multiple pedestrians")
        print("⚡ Expected: Medium severity, slow down warning")
        print("="*70 + "\n")

        # Multiple pedestrians
        for i in range(3):
            location = self.get_location_side(80.0, random.uniform(-5.0, 5.0))
            event = self.create_event("Pedestrian", True, location)
            publish_actor_seen_event(event)
            time.sleep(0.3)

    def scenario_construction_zone(self):
        """Scenario 4: Construction zone with traffic signs"""
        print("\n" + "="*70)
        print("🏗️  SCENARIO 4: Construction Zone Ahead")
        print("="*70)
        print("📍 Location: 300m ahead with warning signs")
        print("⚡ Expected: Medium severity, suggest reroute")
        print("="*70 + "\n")

        # Traffic signs first
        sign_location = self.get_location_ahead(250.0)
        sign_event = self.create_event("TrafficSigns", True, sign_location)
        publish_actor_seen_event(sign_event)

        time.sleep(0.5)

        # Construction area
        construction_location = self.get_location_ahead(300.0)
        construction_event = self.create_event("Static", True, construction_location)
        publish_actor_seen_event(construction_event)

    def scenario_emergency_vehicle(self):
        """Scenario 5: Ambulance approaching from behind"""
        print("\n" + "="*70)
        print("🚑 SCENARIO 5: Emergency Vehicle (Ambulance)")
        print("="*70)
        print("📍 Location: Behind ego vehicle, moving fast")
        print("⚡ Expected: High priority, pull over suggestion")
        print("="*70 + "\n")

        # Ambulance behind (negative distance)
        location = self.get_location_ahead(-50.0)
        event = self.create_event("Police", True, location)  # Using Police tag for emergency
        publish_actor_seen_event(event)

    def scenario_traffic_jam(self):
        """Scenario 6: Heavy traffic jam ahead - multiple stopped vehicles"""
        print("\n" + "="*70)
        print("🚗🚙🚕 SCENARIO 6: Heavy Traffic Jam")
        print("="*70)
        print("📍 Location: 150m ahead, multiple stopped vehicles")
        print("⚡ Expected: High severity, suggest alternatives if stuck")
        print("="*70 + "\n")

        # Multiple cars in jam
        for i in range(5):
            distance = 150.0 + (i * 10.0)
            location = self.get_location_ahead(distance)
            event = self.create_event("Car", True, location)
            publish_actor_seen_event(event)
            time.sleep(0.2)

    def scenario_truck_breakdown(self):
        """Scenario 7: Large truck broken down on road"""
        print("\n" + "="*70)
        print("🚛 SCENARIO 7: Broken Down Truck")
        print("="*70)
        print("📍 Location: 120m ahead, blocking lane")
        print("⚡ Expected: High severity, lane change or reroute")
        print("="*70 + "\n")

        location = self.get_location_ahead(120.0)
        event = self.create_event("Truck", True, location)
        publish_actor_seen_event(event)

    def scenario_cyclist_on_road(self):
        """Scenario 8: Cyclist sharing the road"""
        print("\n" + "="*70)
        print("🚴 SCENARIO 8: Cyclist on Road")
        print("="*70)
        print("📍 Location: 60m ahead, slow moving")
        print("⚡ Expected: Low-medium severity, maintain safe distance")
        print("="*70 + "\n")

        location = self.get_location_ahead(60.0)
        event = self.create_event("Bicycle", True, location)
        publish_actor_seen_event(event)

    def scenario_bus_stop(self):
        """Scenario 9: Bus stopped at bus stop"""
        print("\n" + "="*70)
        print("🚌 SCENARIO 9: Bus at Bus Stop")
        print("="*70)
        print("📍 Location: 100m ahead on right side")
        print("⚡ Expected: Low severity, watch for pedestrians")
        print("="*70 + "\n")

        location = self.get_location_side(100.0, 5.0)
        event = self.create_event("Bus", True, location)
        publish_actor_seen_event(event)

    def scenario_motorcycle_weaving(self):
        """Scenario 10: Motorcycle weaving through traffic"""
        print("\n" + "="*70)
        print("🏍️  SCENARIO 10: Motorcycle in Traffic")
        print("="*70)
        print("📍 Location: Multiple positions, moving fast")
        print("⚡ Expected: Medium severity, unpredictable movement")
        print("="*70 + "\n")

        # Motorcycle appears at different positions
        positions = [90.0, 95.0, 100.0]
        for pos in positions:
            location = self.get_location_side(pos, random.uniform(-3.0, 3.0))
            event = self.create_event("Motorcycle", True, location)
            publish_actor_seen_event(event)
            time.sleep(0.4)

    def scenario_passenger_exit(self):
        """Scenario 11: Passenger decides to exit vehicle"""
        print("\n" + "="*70)
        print("🚪 SCENARIO 11: Passenger Exit Event")
        print("="*70)
        print("📍 Location: Current ego position")
        print("⚡ Expected: Trigger autonomous mode, alternative transport")
        print("="*70 + "\n")

        exit_event = PassengerLeftEvent(
            actor_tag="Passenger",
            timestamp=datetime.utcnow(),
            location=tuple(self.ego_location)
        )
        publish_passenger_left_vehicle_event(exit_event)

    def scenario_multiple_hazards(self):
        """Scenario 12: Complex scene with multiple hazards"""
        print("\n" + "="*70)
        print("⚠️  SCENARIO 12: Multiple Hazards (Complex)")
        print("="*70)
        print("📍 Location: Various positions - testing decision priority")
        print("⚡ Expected: Prioritize most critical hazard")
        print("="*70 + "\n")

        # Police 300m ahead
        event1 = self.create_event("Police", True, self.get_location_ahead(300.0))
        publish_actor_seen_event(event1)
        time.sleep(0.3)

        # Pedestrian 100m ahead (more immediate)
        event2 = self.create_event("Pedestrian", True, self.get_location_ahead(100.0))
        publish_actor_seen_event(event2)
        time.sleep(0.3)

        # Traffic sign 200m ahead
        event3 = self.create_event("TrafficSigns", True, self.get_location_ahead(200.0))
        publish_actor_seen_event(event3)

    # ==================== SCENARIO RUNNER ====================

    def run_all_scenarios(self, interval_seconds: float = 10.0):
        """Run all scenarios with specified interval"""
        scenarios = [
            self.scenario_police_ahead,
            self.scenario_accident_close,
            self.scenario_pedestrian_crossing,
            self.scenario_construction_zone,
            self.scenario_emergency_vehicle,
            self.scenario_traffic_jam,
            self.scenario_truck_breakdown,
            self.scenario_cyclist_on_road,
            self.scenario_bus_stop,
            self.scenario_motorcycle_weaving,
            self.scenario_multiple_hazards,
            # Passenger exit comes last to test alternative transport
            self.scenario_passenger_exit,
        ]

        print("\n" + "🎬 "*20)
        print("🎬  MOCK SCENARIO RUNNER - FASLit Navigation System Testing")
        print("🎬 "*20)
        print(f"\nTotal Scenarios: {len(scenarios)}")
        print(f"Interval: {interval_seconds} seconds")
        print(f"Estimated Duration: {len(scenarios) * interval_seconds / 60:.1f} minutes")
        print("\n" + "🎬 "*20 + "\n")

        try:
            for i, scenario in enumerate(scenarios, 1):
                self.scenario_count = i
                print(f"\n⏰ Running Scenario {i}/{len(scenarios)}...")

                # Run the scenario
                scenario()

                # Simulate vehicle movement
                self.update_ego_position(random.uniform(50.0, 150.0))

                # Wait before next scenario
                if i < len(scenarios):
                    print(f"\n⏳ Waiting {interval_seconds} seconds before next scenario...")
                    print(f"   (Ego position: {self.ego_location[0]:.1f}m)\n")
                    time.sleep(interval_seconds)

            print("\n" + "✅ "*20)
            print("✅  ALL SCENARIOS COMPLETED")
            print("✅ "*20 + "\n")

        except KeyboardInterrupt:
            print("\n\n⚠️  Scenario runner interrupted by user")
            print(f"Completed {self.scenario_count}/{len(scenarios)} scenarios\n")


def main():
    """Main entry point"""
    simulator = ScenarioSimulator()

    # Run all scenarios with 10-second interval
    simulator.run_all_scenarios(interval_seconds=10.0)


if __name__ == "__main__":
    main()
