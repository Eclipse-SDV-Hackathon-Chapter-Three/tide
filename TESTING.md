# Testing Guide - FASLit Navigation System

Complete guide for testing the nav_app with mock data and avoiding unwanted MQTT messages.

## Problem: Continuous ADAS Events

If nav_app is continuously printing "ADAS event detected" without running mock scenarios, it means:
1. The shared broker (`192.168.41.250`) has other publishers sending events
2. MQTT retained messages are being replayed
3. Another test script is running

## Solution: Local Testing Setup

### Option 1: Use Local MQTT Broker (Recommended)

#### Step 1: Install and Start Mosquitto

```bash
# Install mosquitto (if not installed)
sudo apt-get update
sudo apt-get install mosquitto mosquitto-clients

# Start mosquitto broker
mosquitto -v
# Or run as service
sudo systemctl start mosquitto
```

#### Step 2: Update Config for Local Testing

```bash
# Use local config instead of shared broker
cp mqtt_config_local.json mqtt_config.json
```

This changes the broker from `192.168.41.250` to `localhost`.

#### Step 3: Run Tests with Clean Broker

Now run your tests - no interference from other vehicles!

### Option 2: Use Different MQTT Topics

Keep using shared broker but use unique topic names for testing:

```python
# In nav_app/subscriber.py, change:
self.adas_actor_event_topic = "test/vehicle/adas-actor/seen"
self.passenger_exit_topic = "test/vehicle/passenger/left"

# In on_vehicle_app/publishers.py, change:
Topics.VEHICLE_ADAS_ACTOR_SEEN = "test/vehicle/adas-actor/seen"
Topics.VEHICLE_PASSENGER_LEFT = "test/vehicle/passenger/left"
```

### Option 3: Clear Retained Messages

If the broker has retained messages, clear them:

```bash
# Install mosquitto clients if needed
sudo apt-get install mosquitto-clients

# Clear specific topic
mosquitto_pub -h 192.168.41.250 -t "vehicle/adas-actor/seen" -n -r

# Monitor what's being published
mosquitto_sub -h 192.168.41.250 -t "#" -v
```

## Complete Test Workflow

### Terminal 1: MQTT Broker (if using local)
```bash
mosquitto -v
```

### Terminal 2: Vehicle Data Simulator
```bash
# Publishes vehicle location, speed, passenger status every 1 second
python run_vehicle_simulator.py
```

### Terminal 3: Navigation App
```bash
# Subscribes to ADAS events and vehicle data
python -m nav_app.subscriber
```

### Terminal 4: Scenario Generator
```bash
# Run one of these:

# Full comprehensive test (10s intervals)
python run_mock_scenarios.py

# Quick test (3s intervals)
python test_quick_scenarios.py

# Continuous simple test
python run_fake_carla.py
```

## What Each Component Does

### 1. `run_vehicle_simulator.py` (NEW)
**Purpose**: Simulates vehicle computer publishing telemetry
**Publishes to**: `vehicle/data`
**Interval**: 1 second
**Data**:
```json
{
  "location": [100.5, 0.2, 0.0],
  "speed": 62.3,
  "has_passenger": true,
  "timestamp": "2025-10-01T12:00:00"
}
```

**Why needed**: nav_app needs this to:
- Update current position
- Calculate distances to hazards
- Track if vehicle is stuck (for alternative transport suggestions)
- Publish vehicle status updates to infotainment

### 2. `run_mock_scenarios.py`
**Purpose**: Simulates ADAS sensor detecting hazards
**Publishes to**: `vehicle/adas-actor/seen`
**Interval**: 10 seconds between scenarios
**Data**: `AdasActorEvent` (police, pedestrians, accidents, etc.)

### 3. `nav_app/subscriber.py`
**Purpose**: Main navigation logic (FASLit strategy)
**Subscribes to**:
- `vehicle/adas-actor/seen` - ADAS events
- `vehicle/passenger/left` - Passenger exit
- `vehicle/data` - Vehicle telemetry
- `user/action` - User input from infotainment

**Publishes to**:
- `infotainment/hazard` - Hazard notifications
- `infotainment/reroute` - Reroute suggestions
- `infotainment/alternatives` - Alternative transport
- `infotainment/status` - Vehicle status updates
- `v2v/hazards/report` - Share hazards with other vehicles

## Expected Output

### From Vehicle Simulator
```
[VehicleSim] Position:  100.5m | Speed:  62.3 km/h | Passenger: True
[VehicleSim] Position:  117.8m | Speed:  63.1 km/h | Passenger: True
[VehicleSim] Position:  135.2m | Speed:  61.8 km/h | Passenger: True
```

### From Scenario Generator
```
🚨 SCENARIO 1: Police Car Ahead
📍 Location: 200m ahead on same lane
⚡ Expected: High severity, trigger reroute
Publishing actor seen event for actor: Police
```

### From Nav App
```
📸 ADAS Event Detected
Actor: Police
Visible: True
Location: (200.0, 0.0, 0.0)

🔍 Hazard Classification:
  Type: police
  Severity: high
  Distance: 150m

🔄 EXECUTING REROUTE (First Avoid Strategy)
✓ New route calculated:
  Distance: 12.5 km
  ETA: 15 minutes
```

## Vehicle Status Updates

The nav_app now publishes vehicle status updates when:
1. **Vehicle data received** (via `_handle_vehicle_data()`)
2. **Infotainment initialized** (after MQTT connection)

To see status updates, you MUST run the vehicle simulator!

### Status Update Format
```json
{
  "message_type": "vehicle_status",
  "current_speed": 62.3,
  "current_location": [100.5, 0.2, 0.0],
  "destination": [5000.0, 3000.0, 0.0],
  "has_passenger": true,
  "autonomous_active": false,
  "timestamp": "2025-10-01T12:00:00"
}
```

## Monitoring MQTT Traffic

### See All Messages
```bash
# Subscribe to all topics
mosquitto_sub -h localhost -t "#" -v

# Or for shared broker
mosquitto_sub -h 192.168.41.250 -t "#" -v
```

### Monitor Specific Topics
```bash
# ADAS events
mosquitto_sub -h localhost -t "vehicle/adas-actor/seen" -v

# Vehicle data
mosquitto_sub -h localhost -t "vehicle/data" -v

# Infotainment messages
mosquitto_sub -h localhost -t "infotainment/#" -v

# V2V network
mosquitto_sub -h localhost -t "v2v/#" -v
```

## Troubleshooting

### Issue: nav_app prints ADAS events continuously

**Cause**: Publisher on broker sending events, or retained messages

**Solutions**:
1. Use local broker (`mqtt_config_local.json`)
2. Clear retained messages (see Option 3 above)
3. Check for other running publishers: `ps aux | grep python`
4. Use unique test topics (see Option 2 above)

### Issue: No vehicle status updates

**Cause**: Vehicle simulator not running

**Solution**: Start `run_vehicle_simulator.py` in separate terminal

### Issue: Connection refused to MQTT broker

**Cause**: Mosquitto not running

**Solutions**:
```bash
# Start mosquitto
mosquitto -v

# Or check if running
ps aux | grep mosquitto

# Check port 1883
netstat -tlnp | grep 1883
```

### Issue: Events not reaching nav_app

**Cause**: Topic mismatch between publisher and subscriber

**Solution**: Verify topics match:
```bash
# In one terminal, publish test
mosquitto_pub -h localhost -t "vehicle/adas-actor/seen" -m '{"test": "data"}'

# In another, check if nav_app receives it
```

## Test Scenarios

### Test 1: Basic Integration (5 minutes)
```bash
# Terminal 1
mosquitto -v

# Terminal 2
python run_vehicle_simulator.py

# Terminal 3
python -m nav_app.subscriber

# Terminal 4
python test_quick_scenarios.py
```

**Expected**: All scenarios process correctly, vehicle moves, status updates published

### Test 2: Long-Running Simulation (2 minutes)
```bash
# Same setup, but:
# Terminal 4
python run_mock_scenarios.py
```

**Expected**: 12 scenarios over 2 minutes, comprehensive testing

### Test 3: Stress Test
```bash
# Same setup, but:
# Terminal 4
python run_fake_carla.py
```

**Expected**: Continuous events every 0.1 seconds, test performance

## Architecture Diagram

```
┌─────────────────────┐
│ run_vehicle_        │  Publishes "vehicle/data"
│ simulator.py        │  (1 second interval)
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│                     │
│  MQTT Broker        │
│  (Mosquitto)        │
│  localhost:1883     │
│                     │
└──────┬──────────────┘
       │
       ├──► "vehicle/data" ───────────────────┐
       │                                       │
       ├──► "vehicle/adas-actor/seen" ────┐   │
       │                                   │   │
       ├──► "vehicle/passenger/left" ──┐  │   │
       │                                │  │   │
       ▼                                │  │   │
┌─────────────────────┐                │  │   │
│ run_mock_           │  Publishes ────┴──┘   │
│ scenarios.py        │  ADAS events          │
└─────────────────────┘                       │
                                               │
                                               ▼
                                    ┌──────────────────────┐
                                    │  nav_app/           │
                                    │  subscriber.py      │
                                    │                     │
                                    │  Subscribes to:     │
                                    │  - vehicle/data     │
                                    │  - ADAS events      │
                                    │  - passenger exit   │
                                    │                     │
                                    │  Publishes to:      │
                                    │  - infotainment/*   │
                                    │  - v2v/*           │
                                    └─────────────────────┘
```

## Summary

1. **Use local MQTT broker** to avoid interference
2. **Run vehicle simulator** for realistic testing and status updates
3. **Run scenario generator** to test hazard detection
4. **Monitor MQTT traffic** to debug issues
5. **Check topics match** between publishers and subscribers
