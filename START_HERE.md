# 🚗 FASLit Testing Suite - START HERE

## What This Is

A complete testing environment for your FASLit (First Avoid, Second Leave It) navigation app. Test your backend logic with a visual terminal frontend before integrating with Android.

## 🎯 Goal

Verify that your nav-app correctly:
1. Detects hazards from ADAS
2. Makes smart decisions (reroute vs alternatives)
3. Publishes formatted messages to frontend
4. Handles user interactions

## ⚡ Quick Start (60 seconds)

### Step 1: Update MQTT Config (if using team laptop)
```bash
# Edit mqtt_config.json
{
"broker": "192.168.41.250",  # ← Team laptop IP
"port": 1883
}
```

### Step 2: Run Tests

**Option A - Automatic (macOS):**
```bash
./test_all.sh
```

**Option B - Manual (3 terminals):**
```bash
# Terminal 1
PYTHONPATH=/workspace/hello pipenv run python3 nav_app/subscriber.py

# Terminal 2
PYTHONPATH=/workspace/hello pipenv run python3 nav_app/test_frontend.py

# Terminal 3
PYTHONPATH=/workspace/hello pipenv run python3 nav_app/test_simulator.py --auto
```

### Step 3: Watch It Work! 🎉

Terminal 2 will show:
- 🚨 Red/yellow/blue hazard alerts
- 🔄 Reroute notifications
- 🚶 Alternative transport options
- 🤖 Autonomous confirmations

## 📚 Documentation

| File | What It's For | When to Use |
|------|--------------|-------------|
| **SUMMARY.md** | Overview of everything | Start here for big picture |
| **QUICK_TEST.md** | 30-second reference | Quick testing during hackathon |
| **TESTING_GUIDE.md** | Complete testing procedures | Detailed testing steps |
| **ARCHITECTURE.md** | System architecture | Understanding data flow |
| **FRONTEND_TESTING_README.md** | This package overview | Understanding what you got |

## 🔧 What Was Created

### Test Tools
- ✅ `nav_app/test_frontend.py` - Visual display of messages
- ✅ `nav_app/test_simulator.py` - Event generator
- ✅ `run_test_frontend.sh` - Quick launcher
- ✅ `test_all.sh` - Complete test setup

### Documentation
- ✅ `SUMMARY.md` - Complete package overview
- ✅ `TESTING_GUIDE.md` - Testing procedures
- ✅ `QUICK_TEST.md` - Quick reference
- ✅ `ARCHITECTURE.md` - Architecture diagrams
- ✅ `FRONTEND_TESTING_README.md` - Package details
- ✅ `START_HERE.md` - This file

## 🎬 Test Scenarios

### Scenario 1: Approaching Hazard
- Vehicle far from hazard
- **Expected:** Reroute (First Avoid)
- **See:** Blue reroute notification

### Scenario 2: Stuck in Traffic
- Vehicle close and slow
- **Expected:** Alternative suggestions (Second Leave It)
- **See:** Yellow alternatives panel

### Scenario 3: Critical Emergency
- Emergency vehicle nearby
- **Expected:** Critical alert
- **See:** Red emergency warning

## 📱 For Android Integration

Your `MqttClusterBinder.kt` already has:
- ✅ MQTT subscription setup (lines 54-61)
- ✅ Message handling (line 139)
- ✅ User action publishing (line 593)

Use `test_frontend.py` as your reference for:
- Parsing JSON messages
- Displaying different message types
- Handling user actions

## 🐛 Troubleshooting

**Nothing showing in frontend?**
```bash
# Check MQTT broker connectivity
mosquitto_sub -h 192.168.41.250 -t '#' -v
```

**Nav-app not starting?**
```bash
# Install dependencies
pip install paho-mqtt pydantic
```

**Want custom tests?**
```bash
# Interactive mode
python3 nav_app/test_simulator.py
# Then select option 5 for custom events
```

## 🎓 Learning Path

1. **Read this file** (you are here) ✓
2. **Run quick test** (./test_all.sh or manual)
3. **Check QUICK_TEST.md** for reference
4. **Read ARCHITECTURE.md** to understand flow
5. **Use TESTING_GUIDE.md** for detailed testing
6. **Study test_frontend.py** for Android integration

## 🏆 Hackathon Demo Script

7. Open `test_frontend.py` → "This displays our nav-app messages"
8. Run `test_simulator.py --auto` → "Watch the FASLit strategy in action"
9. Point out decisions:
- First Avoid → Automatic reroute
- Second Leave It → Alternative suggestions
1. Show Android app → "Same integration in AAOS"
2. Explain benefits → "Reduces congestion, helps passengers"

## ✅ Success Checklist

Your setup is working when:
- [ ] 3 terminals running without errors
- [ ] Frontend shows colored messages
- [ ] Backend logs decisions
- [ ] All 3 scenarios work
- [ ] Messages appear instantly

## 🚀 What's Next?

1. ✅ Test with simulator (you can do this now!)
2. ⏭️ Test with team laptop MQTT broker
3. ⏭️ Test with CARLA simulation
4. ⏭️ Integrate with Android UI
5. ⏭️ Practice demo presentation

## 💡 Why This Helps

**Before:** Hard to tell if backend works, unclear how to integrate with Android

**After:** Visual testing, clear reference code, quick iterations, impressive demo

## 📞 Quick Reference

```bash
# Start backend
python3 nav_app/subscriber.py

# Start frontend display
python3 nav_app/test_frontend.py

# Run automated tests
python3 nav_app/test_simulator.py --auto

# Interactive testing
python3 nav_app/test_simulator.py

# Check MQTT messages
mosquitto_sub -h 192.168.41.250 -t '#' -v
```

## 🎯 File Purpose Quick Guide

| Need to... | Open this file |
|------------|----------------|
| Start testing now | `QUICK_TEST.md` |
| Understand the system | `ARCHITECTURE.md` |
| Test step-by-step | `TESTING_GUIDE.md` |
| See what you got | `SUMMARY.md` |
| Get Android integration help | `test_frontend.py` (code) |
| Run quick tests | `./test_all.sh` |

---

**Ready to test?** → Open **QUICK_TEST.md**

**Need to understand architecture?** → Open **ARCHITECTURE.md**

**Want detailed testing guide?** → Open **TESTING_GUIDE.md**

**Just want the summary?** → Open **SUMMARY.md**

Good luck with the hackathon! 🎉🚀
