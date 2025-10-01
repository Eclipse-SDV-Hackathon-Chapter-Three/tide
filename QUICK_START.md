# Quick Start - Nav-App Infotainment Integration

## 🚀 Run the Integration (3 Steps)

### Terminal 1: MQTT Broker
```bash
mosquitto -v
```

### Terminal 2: nav_app Backend
```bash
cd /workspace/hello
python -m nav_app.subscriber
```

### Terminal 3: Infotainment Simulator
```bash
cd /workspace/hello
python -m nav_app.infotainment_simulator
```

## 📤 Test Backend → Frontend

### Terminal 4: Send Test Events
```bash
# Test 1: Hazard Detection
mosquitto_pub -t "adas_actor_event" -m '{
  "actor_tag": "police_car",
  "is_visible": true,
  "timestamp": "2025-10-01T12:00:00",
  "location": [600.0, 300.0, 0.0]
}'

# Test 2: Accident (triggers alternative suggestions when stuck)
mosquitto_pub -t "adas_actor_event" -m '{
  "actor_tag": "accident",
  "is_visible": true,
  "timestamp": "2025-10-01T12:05:00",
  "location": [700.0, 500.0, 0.0]
}'
```

## 📥 Test Frontend → Backend

**In Terminal 3 (Simulator), type:**
- `1` - Select first alternative (public transit)
- `2` - Select second alternative (taxi)
- `3` - Select third alternative (walk)
- `a` - Accept reroute
- `d` - Dismiss alert
- `c` - Cancel autonomous mode
- `h` - Show help

## 🧪 Run Automated Tests

```bash
./test_integration.sh
```

## 📋 What You'll See

### In nav_app Terminal:
```
🚗 FASLit Navigation System Initialized
Strategy: First Avoid, Second Leave it there
══════════════════════════════════════════════
📸 ADAS Event Detected
🔍 Hazard Classification:
  Type: police
  Severity: medium
  Distance: 100m
[Infotainment] Published to infotainment/hazard
──────────────────────────────────────────────
👤 User Action from Infotainment Display
Action: select_alternative
Data: {'transport_mode': 'public_transit', 'autonomous_mode': 'return_home'}
```

### In Simulator Terminal:
```
🚨 HAZARD ALERT 🚨
  Title: ⚠️ Hazard Detected
  Police car detected 100m ahead
  Type: police | Severity: MEDIUM

🚶 ALTERNATIVE OPTIONS
  1. 🚌 PUBLIC TRANSIT TO DESTINATION
     Time: 27 min | Cost: $3.50
     [ CHOOSE OPTION 1 ] - Type '1' to select

  💡 Type 1, 2, or 3 to choose an option
```

## 📚 Documentation

- **[INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md)** - High-level overview ⭐ Start here
- **[NAV_APP_INFOTAINMENT_INTEGRATION.md](NAV_APP_INFOTAINMENT_INTEGRATION.md)** - Complete implementation details
- **[INFOTAINMENT_INTEGRATION.md](INFOTAINMENT_INTEGRATION.md)** - Architecture and Android UI examples
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Overall FASLit system

## 🔑 Key Topics

### Backend → Frontend (nav_app publishes)
- `infotainment/hazard` - Hazard alerts
- `infotainment/reroute` - Route changes
- `infotainment/alternatives` - Transport options
- `infotainment/autonomous` - Autonomous confirmations

### Frontend → Backend (Android publishes)
- `user/action` - User selections

## ✅ Integration Status

| Feature | Status |
|---------|--------|
| Backend → Frontend | ✅ Complete |
| Frontend → Backend | ✅ Complete |
| Android Subscriptions | ✅ Complete |
| Android User Actions | ✅ Complete |
| Testing Simulator | ✅ Complete |
| Bidirectional Loop | ✅ Working |

## 🎯 Next Steps (Optional)

To add visual UI screens in Android:
1. Create composable screens (HazardAlert, Alternatives, Autonomous)
2. Wire button clicks to existing `MqttClusterBinder` methods
3. See [INFOTAINMENT_INTEGRATION.md](INFOTAINMENT_INTEGRATION.md#android-integration-steps)

---

**The integration is complete and ready to demo! 🎉**
