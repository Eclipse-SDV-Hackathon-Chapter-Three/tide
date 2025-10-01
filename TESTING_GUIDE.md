# FASLit Nav-App Testing Guide

Complete guide for testing the FASLit navigation application with the new test frontend.

## Overview

This testing setup includes:
1. **Test Frontend** (`nav_app/test_frontend.py`) - Terminal-based display for viewing nav_app messages
2. **Test Simulator** (`nav_app/test_simulator.py`) - Simulates ADAS events for testing
3. **Your Nav-App** (`nav_app/subscriber.py`) - The actual navigation application

## Quick Start

### Prerequisites

1. **MQTT Broker** must be running on shared laptop (192.168.41.250)
2. **Update mqtt_config.json** with correct broker IP:
   ```json
   {
     "broker": "192.168.41.250",
     "port": 1883,
     "keepalive": 60
   }
   ```
3. **Python dependencies** installed:
   ```bash
   pip install paho-mqtt pydantic
   ```

### Running the Test

You'll need **3 terminal windows**:

#### Terminal 1: Nav-App (Backend)
```bash
cd /Users/donghyun/All/hello
python3 nav_app/subscriber.py
```

#### Terminal 2: Test Frontend (Display)
```bash
cd /Users/donghyun/All/hello
python3 nav_app/test_frontend.py

# Or use the launcher:
./run_test_frontend.sh
```

#### Terminal 3: Test Simulator (Event Generator)
```bash
cd /Users/donghyun/All/hello
python3 nav_app/test_simulator.py

# Or run automated test sequence:
python3 nav_app/test_simulator.py --auto
```

## Test Scenarios

### Scenario 1: Approaching Hazard (First Avoid)
**Expected Flow:**
1. Simulator sends ADAS event (police car 800m ahead)
2. Nav-app classifies hazard and makes decision
3. Nav-app triggers REROUTE (First Avoid strategy)
4. Frontend displays reroute notification with new ETA

**What to verify:**
- ✓ Hazard detected and classified correctly
- ✓ Reroute notification appears on frontend
- ✓ New ETA is calculated and displayed
- ✓ Screen switches to MAP view

### Scenario 2: Stuck in Traffic (Second Leave It)
**Expected Flow:**
1. Simulator sends low speed vehicle data (5 km/h)
2. Simulator sends ADAS event (accident nearby)
3. Nav-app detects vehicle is stuck
4. Nav-app triggers SUGGEST ALTERNATIVES (Second Leave It strategy)
5. Frontend displays alternative transport options

**What to verify:**
- ✓ Alternative options displayed (walk, public transit, taxi)
- ✓ Time and cost estimates shown
- ✓ User can select an option
- ✓ Autonomous mode confirmation appears

### Scenario 3: Critical Hazard
**Expected Flow:**
1. Simulator sends emergency vehicle detection
2. Nav-app classifies as CRITICAL severity
3. Frontend displays critical hazard alert (RED)

**What to verify:**
- ✓ Critical alert appears in red
- ✓ Emergency vehicle icon shown
- ✓ Distance and severity displayed correctly

## Test Frontend Features

The test frontend displays:

### 1. Hazard Notifications
- Color-coded by severity (Red/Yellow/Blue)
- Shows hazard type, distance, description
- Automatic screen switching

### 2. Reroute Notifications
- Old vs new ETA comparison
- Time saved calculation
- Auto-accept indicator

### 3. Alternative Suggestions
- List of transport options with icons
- Time, cost, distance for each option
- Step-by-step instructions
- User action required prompt

### 4. Autonomous Confirmation
- Chosen transport mode
- Vehicle autonomous mode (return_home, continue_to_destination)
- Tracking URL
- Estimated arrival time

### 5. Vehicle Status (Compact)
- Current speed and location
- Manual vs autonomous mode
- Passenger status

## Test Simulator Commands

### Interactive Mode
```bash
python3 nav_app/test_simulator.py
```

Options:
1. Approaching hazard (triggers reroute)
2. Stuck in traffic (suggests alternatives)
3. Critical emergency vehicle
4. Run full sequence
5. Custom ADAS event
6. Update vehicle data
0. Exit

### Automated Mode
```bash
python3 nav_app/test_simulator.py --auto
```
Runs all 3 test scenarios sequentially.

### Custom ADAS Event
Create your own test events with custom:
- Actor tags (e.g., vehicle.police.car, static.prop.trafficcone01)
- Locations (x, y, z coordinates)
- Vehicle speed and position

## Common Actor Tags

For testing different hazard types:

```
Police:           vehicle.police.car
Accident:         static.prop.trafficcone01
Emergency:        vehicle.carlamotors.firetruck
                  vehicle.carlamotors.ambulance
Construction:     static.prop.constructioncone
Traffic:          vehicle.* (any vehicle)
Hazard:           static.prop.streetbarrier
```

## Expected Message Flow

```
┌─────────────┐         ┌──────────┐         ┌──────────────┐
│  Simulator  │────1────│ Nav-App  │────2────│   Frontend   │
│  (or CARLA) │         │ (Backend)│         │  (Display)   │
└─────────────┘         └──────────┘         └──────────────┘
                              │
                              │ 3. User Action
                              │◄──────────────
                              │
                              ▼
                        Process & Decide
```

1. Simulator/CARLA sends ADAS events → nav_app
2. Nav-app processes and publishes to infotainment topics → frontend
3. Frontend displays messages and can send user actions back → nav_app

## Troubleshooting

### Frontend not receiving messages
- Check MQTT broker is running: `mosquitto -v`
- Verify broker IP in mqtt_config.json
- Check nav_app is connected and running

### Nav-app not detecting events
- Check simulator is connected to same broker
- Verify topics match (adas_actor_event, vehicle/data)
- Check console output for errors

### Messages not formatted correctly
- Check that Pydantic models match between nav_app and contracts
- Verify JSON serialization of datetime objects
- Check infotainment_publisher.py is being used

## Integration with Android Frontend

When your Android frontend is ready:

1. **Subscribe to same topics** in `MqttClusterBinder.kt`:
   - infotainment/hazard
   - infotainment/reroute
   - infotainment/alternatives
   - infotainment/autonomous
   - infotainment/status
   - infotainment/screen_command

2. **Parse messages** using the same JSON format from `contract/infotainment_message.py`

3. **Send user actions** to `user/action` topic:
   ```json
   {
     "action": "select_alternative",
     "data": {
       "transport_mode": "public_transit",
       "autonomous_mode": "return_home"
     }
   }
   ```

4. **The test frontend code** shows exactly how to parse and display each message type

## Next Steps

1. Run the test scenarios and verify all messages appear correctly
2. Test user action responses (alternative selection, reroute acceptance)
3. Integrate the message handling into your Android Automotive app
4. Replace test_frontend with real Android UI components

## Files Created

- `nav_app/test_frontend.py` - Terminal-based frontend for testing
- `nav_app/test_simulator.py` - Event simulator for testing
- `run_test_frontend.sh` - Quick launcher script
- `TESTING_GUIDE.md` - This guide

## Support

For issues or questions during the hackathon:
- Check nav_app console logs for backend errors
- Check frontend console for message parsing errors
- Verify MQTT broker connectivity with `mosquitto_sub -h 192.168.41.250 -t '#'`
