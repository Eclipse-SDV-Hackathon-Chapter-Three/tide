"""
Quick Test Script - Run a few scenarios with shorter interval
Useful for quick testing without waiting 2 minutes
"""
from run_mock_scenarios import ScenarioSimulator


def main():
    """Run a subset of scenarios with 3-second interval"""
    simulator = ScenarioSimulator()

    print("\n" + "🧪 "*20)
    print("🧪  QUICK TEST - Running 5 scenarios with 3-second interval")
    print("🧪 "*20 + "\n")

    scenarios = [
        ("Police Ahead", simulator.scenario_police_ahead),
        ("Pedestrian Crossing", simulator.scenario_pedestrian_crossing),
        ("Traffic Jam", simulator.scenario_traffic_jam),
        ("Multiple Hazards", simulator.scenario_multiple_hazards),
        ("Passenger Exit", simulator.scenario_passenger_exit),
    ]

    for i, (name, scenario_func) in enumerate(scenarios, 1):
        print(f"\n⏰ Test {i}/{len(scenarios)}: {name}")
        scenario_func()
        simulator.update_ego_position(100.0)

        if i < len(scenarios):
            import time
            print(f"\n⏳ Waiting 3 seconds...\n")
            time.sleep(3)

    print("\n" + "✅ "*20)
    print("✅  QUICK TEST COMPLETED")
    print("✅ "*20 + "\n")


if __name__ == "__main__":
    main()
