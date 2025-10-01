# FASLit Frontend Testing - Complete Package

## What You Got

I've created a **complete terminal-based frontend** for testing your FASLit nav-app integration. This will let you verify that all your backend logic works correctly before integrating with the Android app.

### New Files Created

1. **`nav_app/test_frontend.py`** - Terminal-based display that shows:
   - 🚨 Hazard alerts (color-coded by severity)
   - 🔄 Reroute notifications (with ETA comparison)
   - 🚶 Alternative transport options (with icons, time, cost)
   - 🤖 Autonomous mode confirmations
   - 📊 Vehicle status updates

2. **`nav_app/test_simulator.py`** - Event generator that simulates:
   - ADAS actor detections (police, accidents, emergencies)
   - Vehicle data (speed, location)
   - Passenger exit events
   - Includes 3 pre-built test scenarios

3. **`run_test_frontend.sh`** - Quick launcher script

4. **Documentation:**
   - `TESTING_GUIDE.md` - Comprehensive testing guide
   - `QUICK_TEST.md` - 30-second quick start
   - `ARCHITECTURE.md` - System architecture and data flow

## Why This Matters

Your nav_app publishes messages to MQTT topics, and your Android frontend needs to:
1. Subscribe to those topics
2. Parse the JSON messages
3. Display them in the UI
4. Send user actions back

The **test_frontend.py** shows you **EXACTLY** how to do all of this in Python. You can use it as a reference for your Android Kotlin code.

## Quick Start (3 Terminals)

```bash
# Terminal 1 - Backend
python3 nav_app/subscriber.py

# Terminal 2 - Frontend (THIS IS THE NEW TOOL)
python3 nav_app/test_frontend.py

# Terminal 3 - Test Events
python3 nav_app/test_simulator.py --auto
```

## What You'll See

### Terminal 2 (Frontend) will show beautiful formatted output like:

```
════════════════════════════════════════════════════════════════════════════════
 HAZARD ALERT
⚠️ HAZARD AHEAD
├─ Type: police
├─ Severity: HIGH
├─ Distance: 800m
└─ Police detected 800m ahead
Time: 14:35:22
────────────────────────────────────────────────────────────────────────────────

 REROUTE NOTIFICATION
🔄 Route Updated
├─ Reason: police
├─ Old ETA: 25 minutes
├─ New ETA: 27 minutes
└─ ⚠ Additional Time: 2 minutes
✓ REROUTE AUTO-ACCEPTED
────────────────────────────────────────────────────────────────────────────────

 ALTERNATIVE OPTIONS
🚶 Alternative Options Available
You may be stuck for ~20 minutes. Consider these faster alternatives:
├─ Current ETA in vehicle: 25 minutes
└─ Estimated delay: 20 minutes

Available Alternatives:

1. 🚶 WALK
   ├─ Time: 35 minutes
   ├─ Cost: $0.00
   ├─ Distance: 2.8 km
   └─ Walk to destination - healthy option
   Steps:
      • Head north on Main St for 500m
      • Turn right on Oak Ave

2. 🚌 PUBLIC TRANSIT
   ├─ Time: 15 minutes
   ├─ Cost: $2.50
   ├─ Distance: 3.2 km
   └─ Bus to destination - fastest option
   Steps:
      • Walk 200m to bus stop
      • Take Bus #42 towards Downtown

3. 🚕 TAXI
   ├─ Time: 12 minutes
   ├─ Cost: $15.00
   ├─ Distance: 3.5 km
   └─ Taxi service - door to door

► USER ACTION REQUIRED
Select an option (1-3) or press Enter to stay in vehicle
────────────────────────────────────────────────────────────────────────────────
```

## How to Use for Android Integration

### Step 1: Run the test frontend
```bash
python3 nav_app/test_frontend.py
```

### Step 2: Look at the code
The test frontend shows exactly how to:

**Subscribe to topics:**
```python
self.INFOTAINMENT_TOPICS = [
    "infotainment/hazard",
    "infotainment/reroute",
    "infotainment/alternatives",
    "infotainment/autonomous",
    "infotainment/status",
    "infotainment/screen_command"
]
```

**Parse messages:**
```python
data = json.loads(message.payload.decode())
message_type = data.get("message_type", "unknown")

if message_type == "hazard_notification":
    severity = data.get("severity", "medium")
    title = data.get("title", "Hazard Detected")
    distance = data.get("distance_meters", 0)
    # Display in UI...
```

**Send user actions:**
```python
def send_user_action(self, action: str, data: dict):
    payload = {
        "action": action,
        "data": data
    }
    self.mqtt_client.publish("user/action", json.dumps(payload))
```

### Step 3: Translate to Kotlin

Your **MqttClusterBinder.kt** already has the MQTT setup! You just need to:

1. **Parse the messages** (similar to test_frontend.py lines 140-187)
2. **Update UI** based on message_type
3. **Publish user actions** (already implemented in lines 593-640)

## Test Scenarios

### Scenario 1: Approaching Hazard (First Avoid)
- Triggers reroute
- Shows new ETA
- Auto-accepts route change

### Scenario 2: Stuck in Traffic (Second Leave It)
- Shows alternatives (walk, bus, taxi)
- Displays time/cost for each
- Waits for user selection

### Scenario 3: Critical Emergency
- Red alert
- Shows emergency vehicle
- Critical severity

## Integration Checklist

- [x] Nav-app backend complete
- [x] MQTT message contracts defined
- [x] Infotainment publisher working
- [x] Test frontend created ← **YOU ARE HERE**
- [ ] Test all scenarios with test_frontend.py
- [ ] Verify message formats
- [ ] Integrate with Android MqttClusterBinder
- [ ] Create Android UI components for each message type
- [ ] Test with real CARLA simulation

## File Locations

```
/Users/donghyun/All/hello/
├── nav_app/
│   ├── subscriber.py              # Your nav-app backend
│   ├── test_frontend.py           # NEW: Test display
│   ├── test_simulator.py          # NEW: Event simulator
│   └── infotainment_publisher.py  # Publishes to frontend
├── contract/
│   └── infotainment_message.py    # Message schemas
├── run_test_frontend.sh           # NEW: Quick launcher
├── TESTING_GUIDE.md               # NEW: Complete guide
├── QUICK_TEST.md                  # NEW: Quick reference
├── ARCHITECTURE.md                # NEW: Architecture docs
└── mqtt_config.json               # MQTT broker config
```

## Next Steps for Hackathon

1. **Update mqtt_config.json** with team laptop IP:
   ```json
   {"broker": "192.168.41.250", "port": 1883}
   ```

2. **Run the 3-terminal test**:
   - Verify all messages appear correctly
   - Check colors, formatting, data

3. **Use test_frontend.py as reference** for Android integration:
   - Same MQTT topics
   - Same JSON parsing
   - Same message handling

4. **During demo**:
   - Show test_frontend.py in real-time
   - Run automated test sequence
   - Then show Android app with same functionality

## Message Flow Summary

```
CARLA/Simulator  →  [adas_actor_event]  →  Nav-App
                                              ↓ Process & Decide
Nav-App  →  [infotainment/hazard]      →  Frontend (displays alert)
         →  [infotainment/reroute]     →  Frontend (shows reroute)
         →  [infotainment/alternatives] → Frontend (shows options)

Frontend  →  [user/action]  →  Nav-App (processes user choice)

Nav-App  →  [infotainment/autonomous]  →  Frontend (confirms autonomous)
```

## Support

**If test_frontend.py doesn't show messages:**
1. Check MQTT broker running: `mosquitto -v`
2. Verify broker IP in mqtt_config.json
3. Ensure nav_app is connected (check Terminal 1)

**If messages are malformed:**
1. Check contract/infotainment_message.py schemas
2. Verify JSON serialization in infotainment_publisher.py
3. Look for errors in nav_app console

**For Android integration questions:**
1. Reference test_frontend.py code (it's heavily commented)
2. Check MqttClusterBinder.kt (already has most of the setup)
3. Use ARCHITECTURE.md for data flow understanding

## Why This Helps

Before this, you couldn't easily see if your nav_app was working correctly. Now you have:

✓ **Visual confirmation** that messages are being published
✓ **Reference implementation** for Android integration
✓ **Test scenarios** to verify all features work
✓ **Documentation** for your team and judges
✓ **Quick demo tool** for the hackathon presentation

Good luck with the hackathon! 🚀
