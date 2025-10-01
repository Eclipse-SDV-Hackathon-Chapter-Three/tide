# Mock Scenario Testing Guide

This guide explains how to use the mock scenario scripts for testing the FASLit navigation system.

## Available Scripts

### 1. `run_vehicle_simulator.py` (New - Required)
- **Purpose**: Simulates vehicle telemetry (speed, location, passenger status)
- **Interval**: 1 second updates
- **Publishes**: Vehicle data for nav_app to consume
- **Use Case**: Required for realistic testing, enables vehicle status updates

```bash
python run_vehicle_simulator.py
```

**⚠️ Important**: Run this alongside scenario generators for complete testing!

### 2. `run_fake_carla.py` (Original)
- **Purpose**: Original simple CARLA sensor loop
- **Interval**: 0.1 seconds (continuous)
- **Actor**: Always generates "Pedestrian" events
- **Use Case**: Continuous testing, basic functionality verification

```bash
python run_fake_carla.py
```

### 3. `run_mock_scenarios.py` (New - Comprehensive)
- **Purpose**: Comprehensive scenario testing with diverse hazards
- **Interval**: 10 seconds between scenarios
- **Scenarios**: 12 different scenarios
- **Duration**: ~2 minutes total
- **Use Case**: Full system testing, demo presentations

```bash
python run_mock_scenarios.py
```

### 4. `test_quick_scenarios.py` (New - Quick Test)
- **Purpose**: Quick testing with subset of scenarios
- **Interval**: 3 seconds between scenarios
- **Scenarios**: 5 selected scenarios
- **Duration**: ~15 seconds total
- **Use Case**: Rapid development testing, debugging

```bash
python test_quick_scenarios.py
```

## Scenario Descriptions

### Scenario 1: Police Car Ahead 🚨
- **Location**: 200m ahead
- **Expected**: High severity, reroute suggestion for approaching vehicles
- **Tests**: Hazard classification, distance calculation, reroute decision

### Scenario 2: Traffic Accident Close By 🚧
- **Location**: 50m ahead (critical distance)
- **Expected**: Critical severity, immediate action required
- **Tests**: Multi-actor detection, critical severity handling

### Scenario 3: Pedestrians Crossing Road 🚶
- **Location**: 80m ahead
- **Actors**: Multiple pedestrians
- **Expected**: Medium severity, slow down warning
- **Tests**: Multiple actor tracking, pedestrian detection

### Scenario 4: Construction Zone 🏗️
- **Location**: 300m ahead with warning signs at 250m
- **Expected**: Medium severity, suggest reroute
- **Tests**: Multi-stage hazard detection, traffic sign recognition

### Scenario 5: Emergency Vehicle 🚑
- **Location**: Behind ego vehicle (-50m)
- **Expected**: High priority, pull over suggestion
- **Tests**: Rear hazard detection, emergency priority

### Scenario 6: Heavy Traffic Jam 🚗🚙🚕
- **Location**: 150m ahead
- **Actors**: 5 stopped vehicles
- **Expected**: High severity, suggest alternatives if stuck
- **Tests**: Multi-vehicle detection, alternative transport suggestions

### Scenario 7: Broken Down Truck 🚛
- **Location**: 120m ahead, blocking lane
- **Expected**: High severity, lane change or reroute
- **Tests**: Large vehicle detection, obstacle avoidance

### Scenario 8: Cyclist on Road 🚴
- **Location**: 60m ahead
- **Expected**: Low-medium severity, maintain safe distance
- **Tests**: Vulnerable road user detection, distance management

### Scenario 9: Bus at Bus Stop 🚌
- **Location**: 100m ahead, right side
- **Expected**: Low severity, watch for pedestrians
- **Tests**: Stationary vehicle detection, side-position handling

### Scenario 10: Motorcycle in Traffic 🏍️
- **Location**: Multiple positions (90-100m)
- **Expected**: Medium severity, unpredictable movement
- **Tests**: Fast-moving object tracking, position updates

### Scenario 11: Passenger Exit Event 🚪
- **Location**: Current ego position
- **Expected**: Trigger autonomous mode, alternative transport
- **Tests**: Passenger exit handling, autonomous vehicle handoff

### Scenario 12: Multiple Hazards ⚠️
- **Location**: Various (100-300m)
- **Actors**: Police, pedestrian, traffic signs
- **Expected**: Prioritize most critical hazard
- **Tests**: Decision priority logic, complex scene handling

## Running with nav_app

### Complete Test Setup (3 Terminals)

#### Terminal 1: Vehicle Simulator (REQUIRED)
```bash
python run_vehicle_simulator.py
```
Publishes vehicle data every 1 second - needed for realistic testing and status updates.

#### Terminal 2: Navigation App
```bash
python -m nav_app.subscriber
```
Subscribes to vehicle data and ADAS events, publishes decisions to infotainment.

#### Terminal 3: Scenario Generator
```bash
# Full test (2 minutes)
python run_mock_scenarios.py

# Quick test (15 seconds)
python test_quick_scenarios.py

# Original continuous test
python run_fake_carla.py
```

**Note**: Vehicle simulator is needed for:
- Realistic vehicle position tracking
- Speed calculations for hazard severity
- Vehicle status updates to infotainment
- Detecting if vehicle is stuck (for alternative suggestions)

## Customizing Scenarios

### Change Interval
Edit the script and modify the interval parameter:

```python
# In run_mock_scenarios.py
simulator.run_all_scenarios(interval_seconds=5.0)  # 5 seconds instead of 10

# In test_quick_scenarios.py
time.sleep(5)  # 5 seconds instead of 3
```

### Run Specific Scenarios
```python
from run_mock_scenarios import ScenarioSimulator

sim = ScenarioSimulator()
sim.scenario_police_ahead()
sim.scenario_traffic_jam()
# etc.
```

### Create Custom Scenarios
Add new scenarios to `ScenarioSimulator` class:

```python
def scenario_custom(self):
    """Your custom scenario"""
    print("Custom scenario...")
    location = self.get_location_ahead(150.0)
    event = self.create_event("Car", True, location)
    publish_actor_seen_event(event)
```

## Expected Outputs

### From Publisher (Scenario Script)
- Scenario description and metadata
- Published ADAS events (JSON format)
- Timing information

### From Subscriber (nav_app)
- Hazard classification
- Severity assessment
- Decision output (reroute/alternatives)
- Infotainment display messages
- V2V network sharing

## Testing Strategy

1. **Development**: Use `test_quick_scenarios.py` for rapid iteration
2. **Integration**: Use `run_mock_scenarios.py` for comprehensive testing
3. **Stress Test**: Use `run_fake_carla.py` for continuous load testing
4. **Demo**: Use `run_mock_scenarios.py` for presentations

## Troubleshooting

### No Events Received
- Check MQTT broker is running
- Verify topic names match in publisher and subscriber
- Check `mqtt_config.json` has correct broker IP

### Events Not Processing
- Check Pydantic models match between contracts
- Verify JSON serialization/deserialization
- Check subscriber's `_handle_adas_event()` method

### Performance Issues
- Reduce interval in scenarios
- Decrease number of actors per scenario
- Check MQTT broker performance

## Architecture

```
run_mock_scenarios.py
  ├─ ScenarioSimulator
  │   ├─ Creates AdasActorEvent with varied data
  │   └─ Publishes to MQTT topic "vehicle/adas-actor/seen"
  │
  └─ Publishes to MQTT Broker (Mosquitto)
       │
       └─> nav_app/subscriber.py
            ├─ Receives events
            ├─ Classifies hazards
            ├─ Makes decisions
            ├─ Publishes to infotainment
            └─ Shares via V2V
```

## Notes

- All scripts keep the original SDV code intact (in `on_vehicle_app/`)
- New scripts use the same contracts and publishers
- Scenarios simulate realistic driving conditions
- Timing intervals can be adjusted for different testing needs
