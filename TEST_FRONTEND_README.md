# FASLit Test Frontend - Complete Package

## 🎉 What You Just Got

A complete **terminal-based frontend** for testing your FASLit navigation app! This lets you see all your backend messages in real-time with beautiful formatting, colors, and icons - all in your terminal.

## 🚀 Quick Start (3 steps)

### 1. Setup
```bash
./setup_test_env.sh
```

### 2. Update MQTT Config (if using team laptop)
```bash
# Edit mqtt_config.json
{
  "broker": "192.168.41.250",
  "port": 1883
}
```

### 3. Run Tests
```bash
./test_all.sh
```

That's it! You should see 3 terminal windows open with your nav-app running.

## 📦 What's Included

### Core Testing Tools
1. **`nav_app/test_frontend.py`**
   - Terminal display showing all nav-app messages
   - Color-coded alerts (red/yellow/blue)
   - Formatted reroute notifications
   - Alternative transport options
   - **USE THIS as reference for Android integration**

2. **`nav_app/test_simulator.py`**
   - Simulates ADAS events (police, accidents, emergencies)
   - Simulates vehicle data (speed, location)
   - 3 pre-built test scenarios
   - Interactive mode for custom testing

3. **Helper Scripts**
   - `setup_test_env.sh` - Install dependencies
   - `run_test_frontend.sh` - Launch frontend
   - `test_all.sh` - Launch complete test suite

### Documentation
1. **START_HERE.md** - Begin here for quick orientation
2. **QUICK_TEST.md** - 30-second quick reference
3. **TESTING_GUIDE.md** - Complete testing procedures
4. **ARCHITECTURE.md** - System architecture and data flow
5. **SUMMARY.md** - Package overview
6. **FRONTEND_TESTING_README.md** - Detailed package info

## 🎯 Why This Matters

### For Testing
✅ **Visual confirmation** - See your messages in real-time
✅ **No CARLA needed** - Test with simulator
✅ **Quick iterations** - Change code, see results instantly
✅ **Catch bugs early** - Verify backend before Android work

### For Android Integration
✅ **Reference code** - `test_frontend.py` shows exactly how to parse messages
✅ **Message examples** - See real JSON payloads
✅ **User actions** - Learn how to send actions back to nav-app
✅ **Clear contracts** - All schemas documented

### For Hackathon Demo
✅ **Impressive visualization** - Show live message flow
✅ **Working prototype** - Demonstrate FASLit strategy
✅ **Professional setup** - Multiple components working together
✅ **Easy to explain** - Clear separation of concerns

## 📱 Example Output

When you run the test frontend, you'll see:

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

Available Alternatives:

1. 🚶 WALK
   ├─ Time: 35 minutes
   ├─ Cost: $0.00
   └─ Distance: 2.8 km

2. 🚌 PUBLIC TRANSIT
   ├─ Time: 15 minutes
   ├─ Cost: $2.50
   └─ Distance: 3.2 km

3. 🚕 TAXI
   ├─ Time: 12 minutes
   ├─ Cost: $15.00
   └─ Distance: 3.5 km

► USER ACTION REQUIRED
────────────────────────────────────────────────────────────────────────────────
```

## 🔧 Manual Testing (if automatic doesn't work)

Open 3 terminal windows:

### Terminal 1: Backend
```bash
cd /Users/donghyun/All/hello
python3 nav_app/subscriber.py
```

### Terminal 2: Frontend Display
```bash
cd /Users/donghyun/All/hello
python3 nav_app/test_frontend.py
```

### Terminal 3: Event Simulator
```bash
cd /Users/donghyun/All/hello
python3 nav_app/test_simulator.py --auto
```

## 🎬 Test Scenarios

### Scenario 1: Approaching Hazard (First Avoid)
- **Setup:** Vehicle 800m from police car, traveling 60 km/h
- **Expected:** Reroute notification (blue)
- **Strategy:** First Avoid - take alternative route before reaching hazard

### Scenario 2: Stuck in Traffic (Second Leave It)
- **Setup:** Vehicle 50m from accident, traveling 5 km/h (stuck)
- **Expected:** Alternative suggestions (yellow)
- **Strategy:** Second Leave It - passenger exits, uses alternative transport

### Scenario 3: Critical Emergency
- **Setup:** Emergency vehicle detected nearby
- **Expected:** Critical hazard alert (red)
- **Strategy:** High priority warning to driver

## 🔗 Message Flow

```
CARLA/Simulator                Nav-App Backend           Frontend Display
───────────────                ───────────────           ────────────────

📸 Detect hazard               ┌─────────────┐           ┌─────────────┐
(police, accident)             │   Receive   │           │             │
      │                        │   & Classify│           │             │
      │ adas_actor_event       │             │           │             │
      ├───────────────────────►│   Decide:   │           │             │
      │                        │  - Reroute? │           │             │
      │                        │  - Alts?    │           │             │
      │                        │             │           │             │
      │                        │   Publish   │           │             │
      │                        │   Messages  │  infotainment/hazard    │
      │                        ├────────────────────────►│  Display    │
      │                        │             │  infotainment/reroute   │
      │                        ├────────────────────────►│  Messages   │
      │                        │             │  infotainment/alternatives
      │                        ├────────────────────────►│             │
      │                        │             │           │             │
      │                        │◄────────────────────────┤  User       │
      │                        │  user/action            │  Actions    │
      │                        └─────────────┘           └─────────────┘
```

## 📋 Integration Checklist

### For Android:
- [ ] Run test_frontend.py to see message formats
- [ ] Study how messages are parsed (lines 140-187)
- [ ] Check MqttClusterBinder.kt subscriptions (already done!)
- [ ] Implement UI components for each message type
- [ ] Wire user action buttons to publishUserAction()
- [ ] Test with nav_app backend
- [ ] Test with CARLA simulation

## 🐛 Troubleshooting

### Dependencies Not Installed
```bash
pip3 install paho-mqtt pydantic
```

### Frontend Not Receiving Messages
```bash
# Test MQTT connectivity
mosquitto_sub -h 192.168.41.250 -t '#' -v

# Check mqtt_config.json
cat mqtt_config.json

# Verify broker IP is correct
```

### Nav-App Not Processing Events
```bash
# Check nav_app is running
# Look for connection messages in Terminal 1
# Verify topics match (adas_actor_event, vehicle/data)
```

### Want to Debug MQTT Messages
```bash
# Subscribe to all topics
mosquitto_sub -h 192.168.41.250 -t '#' -v

# Subscribe to specific topic
mosquitto_sub -h 192.168.41.250 -t 'infotainment/hazard' -v
```

## 📚 Documentation Guide

| When you need... | Read this file |
|------------------|----------------|
| Quick orientation | `START_HERE.md` |
| Quick testing | `QUICK_TEST.md` |
| Understand system | `ARCHITECTURE.md` |
| Complete testing guide | `TESTING_GUIDE.md` |
| Package overview | `SUMMARY.md` |
| Android integration help | `test_frontend.py` (code) + `ARCHITECTURE.md` |

## 🎓 Learning the Code

### Study These Files in Order:

1. **`mqtt_config.json`** - MQTT broker configuration
2. **`contract/infotainment_message.py`** - Message schemas
3. **`nav_app/infotainment_publisher.py`** - How messages are published
4. **`nav_app/test_frontend.py`** - How messages are received & displayed
5. **`sdv_lab/.../MqttClusterBinder.kt`** - Android MQTT integration

## 🏆 Success Criteria

Your setup is working when:
- ✅ All 3 terminals run without errors
- ✅ Frontend displays colored messages
- ✅ Backend logs show decision-making
- ✅ Hazard alerts appear with correct severity colors
- ✅ Reroute shows ETA comparison
- ✅ Alternatives show transport options
- ✅ Messages appear within 1 second

## 🎯 Next Steps

1. **Run setup:** `./setup_test_env.sh`
2. **Run tests:** `./test_all.sh` or manual 3-terminal setup
3. **Verify output:** Check Terminal 2 for formatted messages
4. **Study code:** Open `test_frontend.py` to understand parsing
5. **Integrate Android:** Use test_frontend.py as reference
6. **Test with CARLA:** Replace simulator with real events
7. **Demo practice:** Run automated test sequence

## 💡 Key Files

```
/Users/donghyun/All/hello/
├── 📋 START_HERE.md                    # Start here!
├── 📋 QUICK_TEST.md                    # Quick reference
├── 📋 TESTING_GUIDE.md                 # Complete guide
├── 📋 ARCHITECTURE.md                  # Architecture
├── 📋 SUMMARY.md                       # Overview
├── 📋 TEST_FRONTEND_README.md          # This file
│
├── 🚀 setup_test_env.sh                # Setup script
├── 🚀 test_all.sh                      # Run all tests
├── 🚀 run_test_frontend.sh             # Run frontend
│
├── nav_app/
│   ├── 💻 test_frontend.py             # Frontend display
│   ├── 💻 test_simulator.py            # Event simulator
│   ├── 💻 subscriber.py                # Nav-app backend
│   └── 💻 infotainment_publisher.py    # Message publisher
│
├── contract/
│   ├── 📄 infotainment_message.py      # Message schemas
│   └── 📄 adas_actor_event.py          # Event schemas
│
└── ⚙️  mqtt_config.json                # MQTT configuration
```

## 🎬 Demo Script

1. **Open START_HERE.md** - Show organization
2. **Run `./test_all.sh`** - Launch everything
3. **Point to Terminal 2** - "This is our test frontend"
4. **Run test scenario** - In Terminal 3, select option 4
5. **Explain FASLit:**
   - First Avoid → Reroute when approaching
   - Second Leave It → Alternatives when stuck
6. **Show Android app** - Same integration
7. **Highlight benefits** - Reduce congestion, help passengers

## 🙏 Support

**During the Hackathon:**
- Check `QUICK_TEST.md` for rapid debugging
- Use `ARCHITECTURE.md` to understand message flow
- Reference `test_frontend.py` for Android integration
- Run `./test_all.sh` to verify everything works

**Files to Share with Team:**
- `START_HERE.md` - Team orientation
- `QUICK_TEST.md` - Quick reference during coding
- `test_frontend.py` - Reference implementation

## ✨ What Makes This Special

This isn't just a test tool - it's:
- 📚 **Living documentation** - Shows exactly how messages flow
- 🎓 **Learning tool** - Reference for Android integration
- 🐛 **Debug tool** - Catch backend issues early
- 🎬 **Demo tool** - Impressive visualization for judges
- 🚀 **Development accelerator** - Test without rebuilding Android

---

## Ready to Test?

1. **Setup:** `./setup_test_env.sh`
2. **Test:** `./test_all.sh`
3. **Learn:** Open `START_HERE.md`

Good luck with your hackathon! 🎉🚗🚀
