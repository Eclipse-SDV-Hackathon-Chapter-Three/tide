# Team Testing Workflow - Shared MQTT Broker

This guide is specifically for testing with the **shared team MQTT broker** on the intranet.

## Network Setup

### MQTT Broker Location
- **Host**: `192.168.41.250` (shared laptop)
- **Port**: `1883`
- **Location**: Team intranet (requires WiFi connection)

### Before Testing

1. **Switch to team WiFi network**
2. **Verify broker is accessible** (it should be running on the shared laptop)
3. Run your test scripts

⚠️ **Note**: When not connected to team WiFi, scripts will still run and print events locally, but won't publish to MQTT.

## Quick Start (3 Terminals)

### Setup
```bash
# Make sure you're on the team WiFi network!
# Broker: 192.168.41.250:1883
```

### Terminal 1: Vehicle Simulator
```bash
python run_vehicle_simulator.py
```

**What it does**:
- Publishes vehicle telemetry every 1 second
- Topic: `vehicle/data`
- Data: location, speed, passenger status

**Expected output**:
```
✅ Connected to broker at 192.168.41.250:1883
📡 Publishing to: vehicle/data
[VehicleSim] Position:  100.5m | Speed:  62.3 km/h | Passenger: True
```

### Terminal 2: Navigation App
```bash
python -m nav_app.subscriber
```

**What it does**:
- Subscribes to ADAS events and vehicle data
- Makes routing decisions (FASLit strategy)
- Publishes to infotainment topics

**Expected output**:
```
[FASLit] Connected to MQTT broker at 192.168.41.250:1883
[FASLit] Subscribed to ADAS events
[FASLit] System ready. Monitoring for events...
```

### Terminal 3: Scenario Generator
```bash
# Choose one:

# Full comprehensive test (12 scenarios, ~2 minutes)
python run_mock_scenarios.py

# Quick test (5 scenarios, ~15 seconds)
python test_quick_scenarios.py

# Original continuous test
python run_fake_carla.py
```

**What it does**:
- Publishes ADAS events (hazards detected by sensors)
- Topic: `vehicle/adas-actor/seen`
- 12 diverse scenarios with 10-second intervals

## Understanding the Output

### ✅ Successfully Connected
```
✅ Connected to MQTT broker
📡 Publishing to: vehicle/adas-actor/seen
Publishing actor seen event for actor: Police
{"UUID":null,"actor_tag":"Police",...}
```
Events are being published to the shared broker!

### ⚠️ Not Connected (Offline Mode)
```
⚠️  Note: MQTT not connected - [Errno 111] Connection refused
   (Make sure you're on team WiFi and broker at 192.168.41.250 is running)
   Messages are printed above for visibility.
```
Scripts still work locally - events are printed but not published to broker.

**This is OK if**:
- You're just testing the script logic
- You're not on team WiFi yet
- You want to see what events would be generated

## MQTT Topics Used

### Published by Simulators
```
vehicle/data                      - Vehicle telemetry (1 sec)
vehicle/adas-actor/seen           - ADAS hazard events
vehicle/passenger/left            - Passenger exit events
```

### Published by nav_app
```
infotainment/hazard               - Hazard notifications
infotainment/reroute              - Reroute suggestions
infotainment/alternatives         - Alternative transport options
infotainment/status               - Vehicle status updates
infotainment/autonomous           - Autonomous mode confirmation
infotainment/screen_command       - Display commands

v2v/hazards/report                - Share hazards with other vehicles
v2v/hazards/broadcast             - Receive hazards from others
v2v/passenger_exit                - Passenger exit events (V2V)
v2v/vehicle/{id}/status           - Vehicle status (V2V)
```

## Monitoring MQTT Traffic

If you have `mosquitto-clients` installed:

```bash
# Monitor all traffic
mosquitto_sub -h 192.168.41.250 -t "#" -v

# Monitor ADAS events only
mosquitto_sub -h 192.168.41.250 -t "vehicle/adas-actor/seen" -v

# Monitor infotainment messages
mosquitto_sub -h 192.168.41.250 -t "infotainment/#" -v

# Monitor V2V network
mosquitto_sub -h 192.168.41.250 -t "v2v/#" -v
```

## Continuous ADAS Events Issue

### Problem
Nav_app continuously prints "ADAS event detected" even without running scenarios.

### Causes
1. **Other team members** running publishers on the same broker
2. **Previous test** still running in background
3. **Retained MQTT messages** being replayed

### Solutions

#### Option 1: Use Unique Topics for Your Tests
Add a prefix to your topics:

```python
# In your test terminal, before running:
export MQTT_TOPIC_PREFIX="yourname"

# Or modify Topics in contract/mqtt/topics.py:
VEHICLE_ADAS_ACTOR_SEEN = "yourname/vehicle/adas-actor/seen"
```

Then only subscribe to your topics in nav_app.

#### Option 2: Clear Retained Messages
```bash
mosquitto_pub -h 192.168.41.250 -t "vehicle/adas-actor/seen" -n -r
```

#### Option 3: Check Who's Publishing
Monitor the topic to see what's being published:
```bash
mosquitto_sub -h 192.168.41.250 -t "vehicle/#" -v
```

#### Option 4: Coordinate with Team
Use the team chat to check who's currently testing.

## Troubleshooting

### Connection Refused
```
⚠️  MQTT not connected - [Errno 111] Connection refused
```

**Solutions**:
1. Check you're on team WiFi
2. Verify broker IP: `ping 192.168.41.250`
3. Check if broker is running on shared laptop
4. Verify port 1883 is accessible

### Connection Timeout
```
⚠️  MQTT not connected - [Errno 110] Connection timed out
```

**Solutions**:
1. Check WiFi connection
2. Verify you're on correct network
3. Check firewall isn't blocking port 1883

### Events Not Received
**Your nav_app doesn't see events from your scenarios**

**Check**:
1. Both scripts connected to same broker (192.168.41.250)
2. Topics match between publisher and subscriber
3. No errors in publisher terminal
4. Monitor with `mosquitto_sub` to verify events are being published

### Too Many Events
**Nav_app receiving events you didn't send**

**Check**:
1. Other team members testing simultaneously
2. Use unique topic prefix (see Option 1 above)
3. Clear retained messages (see Option 2 above)

## Test Scenarios

### Test 1: Offline Local Testing
**Use case**: Test script logic without WiFi
```bash
# Just run the scripts - they'll print events locally
python test_quick_scenarios.py
```
Events printed to console, not published to MQTT.

### Test 2: Full Integration on Team Network
**Use case**: Complete system test with shared broker
```bash
# 1. Connect to team WiFi
# 2. Terminal 1
python run_vehicle_simulator.py

# 3. Terminal 2
python -m nav_app.subscriber

# 4. Terminal 3
python run_mock_scenarios.py
```
All components connected via MQTT broker.

### Test 3: Monitor Only
**Use case**: See what's happening on the network
```bash
mosquitto_sub -h 192.168.41.250 -t "#" -v
```

## Data Flow Architecture

```
┌─────────────────────────┐
│ Your Laptop             │
│                         │
│ ┌─────────────────────┐ │
│ │ Vehicle Simulator   │ │──┐
│ └─────────────────────┘ │  │
│                         │  │
│ ┌─────────────────────┐ │  │
│ │ Scenario Generator  │ │──┤
│ └─────────────────────┘ │  │
│                         │  │
│ ┌─────────────────────┐ │  │
│ │ nav_app             │◄─┤
│ └─────────────────────┘ │  │
└─────────────────────────┘  │
                             │
        Team WiFi            │
    (192.168.41.0/24)        │
                             ▼
                ┌─────────────────────────┐
                │ Shared Laptop           │
                │                         │
                │ ┌─────────────────────┐ │
                │ │ Mosquitto Broker    │ │
                │ │ 192.168.41.250:1883│ │
                │ └─────────────────────┘ │
                └─────────────────────────┘
                             │
                             ▼
                    Other team members'
                    vehicles/apps
```

## Best Practices

### 1. Coordinate Testing Times
Use team chat to avoid conflicts when multiple people test.

### 2. Use Descriptive Client IDs
Scripts already use unique IDs:
- `vehicle_simulator`
- `faslit_{vehicle_id}`
- `vehicle_{vehicle_id}` (for central server)

### 3. Clean Up After Testing
Stop your scripts when done (Ctrl+C) to avoid continuous publishing.

### 4. Monitor Before Publishing
Check what's on the broker before starting your test:
```bash
mosquitto_sub -h 192.168.41.250 -t "#" -v -C 10
```
(Shows last 10 messages then exits)

### 5. Print-First Design
Scripts print events to console even if MQTT fails - you can always see what's happening!

## Scripts Summary

| Script | Publishes To | Interval | MQTT Required? |
|--------|--------------|----------|----------------|
| `run_vehicle_simulator.py` | `vehicle/data` | 1 sec | Yes (for full test) |
| `run_mock_scenarios.py` | `vehicle/adas-actor/seen` | 10 sec | Yes (for full test) |
| `test_quick_scenarios.py` | `vehicle/adas-actor/seen` | 3 sec | Yes (for full test) |
| `run_fake_carla.py` | `vehicle/adas-actor/seen` | 0.1 sec | Yes (for full test) |
| `nav_app/subscriber.py` | `infotainment/*`, `v2v/*` | On event | Yes |

**Note**: All scripts work offline (print events locally) but need MQTT for full integration.

## FAQ

**Q: Can I test without connecting to team WiFi?**
A: Yes! Scripts will run and print events locally. MQTT publishing will fail gracefully.

**Q: How do I know if I'm connected to MQTT?**
A: Look for `✅ Connected to broker at 192.168.41.250:1883` in output.

**Q: What if someone else is testing at the same time?**
A: Use unique topic prefixes or coordinate via team chat.

**Q: Do I need to install mosquitto locally?**
A: No! The broker runs on the shared laptop. You only need `paho-mqtt` Python package.

**Q: Why do scripts still print when MQTT fails?**
A: Print-first design ensures you can always see the data, even offline.

**Q: How do I stop getting continuous events?**
A: See "Continuous ADAS Events Issue" section above.

## Support

- **Team Chat**: Coordinate testing times
- **MQTT Monitoring**: `mosquitto_sub -h 192.168.41.250 -t "#" -v`
- **Debug Mode**: Check script output for `⚠️` or `❌` messages
