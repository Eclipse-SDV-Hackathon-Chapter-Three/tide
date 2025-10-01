# Quick Start - Testing FASLit Navigation System

---

## 🚀 For Team Testing with Shared MQTT Broker

**→ See [TEAM_WORKFLOW.md](TEAM_WORKFLOW.md) for complete guide!**

The shared MQTT broker is at `192.168.41.250:1883` (team WiFi required).

---

## Problems Solved

**Issue 1**: Nav_app continuously prints "ADAS event detected" without running mock scenarios
- **Cause**: Shared broker (192.168.41.250) has other publishers or retained messages
- **Solution**: See [TEAM_WORKFLOW.md](TEAM_WORKFLOW.md) - includes graceful handling when offline

**Issue 2**: Vehicle status updates not being published
- **Cause**: Vehicle simulator wasn't running
- **Solution**: Run `run_vehicle_simulator.py` (NEW - created for you!)

## Quick Test (3 Terminals)

```bash
# Terminal 1: Vehicle telemetry
python run_vehicle_simulator.py

# Terminal 2: Navigation system
python -m nav_app.subscriber

# Terminal 3: Hazard scenarios
python test_quick_scenarios.py
```

## What Was Added

### 1. `run_vehicle_simulator.py` ⭐ NEW
Simulates vehicle computer publishing speed, location, passenger status every 1 second.
- **Why needed**: nav_app needs this for vehicle status updates to infotainment
- **Publishes**: `vehicle/data` topic

### 2. `run_mock_scenarios.py` ⭐ NEW
12 diverse scenarios (police, accidents, traffic jams, etc.) with 10-second intervals.
- **Duration**: ~2 minutes total
- **Use**: Comprehensive testing

### 3. `test_quick_scenarios.py` ⭐ NEW
5 selected scenarios with 3-second intervals for rapid testing.
- **Duration**: ~15 seconds
- **Use**: Quick development testing

### 4. `TESTING.md` ⭐ NEW
Complete troubleshooting guide for MQTT issues, local broker setup, monitoring traffic.

### 5. `SCENARIOS.md` (Updated)
Added vehicle simulator info and 3-terminal setup instructions.

### 6. `mqtt_config_local.json` ⭐ NEW
Config for local broker testing (avoids shared broker interference).

## Files Summary

| File | Purpose | Interval |
|------|---------|----------|
| `run_vehicle_simulator.py` | Vehicle telemetry | 1 second |
| `run_mock_scenarios.py` | 12 diverse scenarios | 10 seconds |
| `test_quick_scenarios.py` | 5 quick scenarios | 3 seconds |
| `run_fake_carla.py` | Original simple test | 0.1 seconds |

## Fixing Your Issues

### Stop Continuous ADAS Events

**Option A: Use Local Broker**
```bash
# 1. Install mosquitto
sudo apt-get install mosquitto

# 2. Start it
mosquitto -v

# 3. Use local config
cp mqtt_config_local.json mqtt_config.json

# 4. Run tests - no interference!
```

**Option B: Clear Retained Messages**
```bash
mosquitto_pub -h 192.168.41.250 -t "vehicle/adas-actor/seen" -n -r
```

**Option C: Monitor What's Being Published**
```bash
mosquitto_sub -h 192.168.41.250 -t "#" -v
```

### Enable Vehicle Status Updates

Just run the vehicle simulator in a separate terminal:
```bash
python run_vehicle_simulator.py
```

Now nav_app will receive vehicle data and publish status updates to `infotainment/status`.

## MQTT Topics Overview

### Published by Simulators
- `vehicle/data` - Vehicle telemetry (speed, location, passenger)
- `vehicle/adas-actor/seen` - ADAS hazard events
- `vehicle/passenger/left` - Passenger exit events

### Published by nav_app
- `infotainment/hazard` - Hazard notifications
- `infotainment/reroute` - Reroute suggestions
- `infotainment/alternatives` - Alternative transport options
- `infotainment/status` - Vehicle status updates ⭐ (needs vehicle simulator!)
- `infotainment/autonomous` - Autonomous mode confirmation
- `v2v/hazards/report` - Share hazards with other vehicles

## Complete Architecture

```
┌─────────────────────┐
│ Vehicle Simulator   │ ──┐
│ (1 sec interval)    │   │
└─────────────────────┘   │
                           ▼
┌─────────────────────┐  MQTT Broker
│ Scenario Generator  │   (Mosquitto)
│ (10 sec interval)   │ ──┤
└─────────────────────┘   │
                           ▼
                    ┌──────────────┐
                    │  nav_app     │
                    │  (FASLit)    │
                    └──────────────┘
                           │
                           ▼
                    Infotainment Display
                    (Android AAOS)
```

## Documentation

- **[TESTING.md](TESTING.md)** - Complete testing guide, troubleshooting, MQTT setup
- **[SCENARIOS.md](SCENARIOS.md)** - All 12 scenarios explained, customization
- **[CLAUDE.md](CLAUDE.md)** - Project overview, architecture, team context

## Next Steps

1. **Start local MQTT broker** (if needed): `mosquitto -v`
2. **Run vehicle simulator**: `python run_vehicle_simulator.py`
3. **Run nav_app**: `python -m nav_app.subscriber`
4. **Run scenarios**: `python test_quick_scenarios.py`
5. **Monitor MQTT** (optional): `mosquitto_sub -h localhost -t "#" -v`

## Key Points

✅ **All original SDV code is intact** - New files don't modify existing code
✅ **Uses same contracts** - Compatible with nav_app subscriber
✅ **10-second intervals** - As requested, not too fast
✅ **Diverse scenarios** - 12 different hazard types
✅ **Vehicle status updates** - Now working with vehicle simulator
✅ **No more continuous events** - Use local broker to avoid interference

Questions? Check [TESTING.md](TESTING.md) for detailed troubleshooting!
