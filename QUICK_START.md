# Quick Start Card 🚀

## For Testing with Team MQTT Broker (192.168.41.250)

---

### Prerequisites
- [ ] Connected to **team WiFi**
- [ ] Shared broker running at **192.168.41.250:1883**
- [ ] Installed: `paho-mqtt`, `pydantic`, `numpy`

---

### 3-Terminal Setup

```bash
┌─────────────────────────────────────────────────────────────┐
│ Terminal 1: VEHICLE SIMULATOR                               │
│ python run_vehicle_simulator.py                             │
│                                                             │
│ Publishes: vehicle/data (1 sec interval)                   │
│ Success: ✅ Connected to broker at 192.168.41.250:1883     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Terminal 2: NAVIGATION APP                                  │
│ python -m nav_app.subscriber                                │
│                                                             │
│ Subscribes: vehicle/data, vehicle/adas-actor/seen          │
│ Success: [FASLit] System ready. Monitoring for events...   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Terminal 3: SCENARIO GENERATOR (Choose one)                 │
│                                                             │
│ python run_mock_scenarios.py      ← Full (12 scenarios)    │
│ python test_quick_scenarios.py    ← Quick (5 scenarios)    │
│ python run_fake_carla.py          ← Continuous             │
│                                                             │
│ Publishes: vehicle/adas-actor/seen                         │
└─────────────────────────────────────────────────────────────┘
```

---

### What You'll See

#### ✅ **When Connected to Team WiFi**
```
✅ Connected to broker at 192.168.41.250:1883
📡 Publishing to: vehicle/adas-actor/seen

🚨 SCENARIO 1: Police Car Ahead
Publishing actor seen event for actor: Police
{"UUID":null,"actor_tag":"Police","is_visible":true,...}

📸 ADAS Event Detected  ← nav_app receives it!
Actor: Police
Severity: high
Distance: 150m
```

#### ⚠️ **When NOT Connected (Offline Mode)**
```
⚠️  Note: MQTT not connected - Connection refused
   (Make sure you're on team WiFi and broker at 192.168.41.250 is running)
   Messages are printed above for visibility.

Publishing actor seen event for actor: Police
{"UUID":null,"actor_tag":"Police","is_visible":true,...}
```
**→ Scripts still work! Events printed locally.**

---

### Test Scenarios (10s intervals)

| # | Scenario | Distance | Severity |
|---|----------|----------|----------|
| 1 | 🚨 Police car | 200m | High |
| 2 | 🚧 Accident | 50m | Critical |
| 3 | 🚶 Pedestrians | 80m | Medium |
| 4 | 🏗️ Construction | 300m | Medium |
| 5 | 🚑 Emergency vehicle | -50m (behind) | High |
| 6 | 🚗🚙🚕 Traffic jam | 150m | High |
| 7 | 🚛 Broken truck | 120m | High |
| 8 | 🚴 Cyclist | 60m | Medium |
| 9 | 🚌 Bus at stop | 100m | Low |
| 10 | 🏍️ Motorcycle | 90-100m | Medium |
| 11 | ⚠️ Multiple hazards | Various | Complex |
| 12 | 🚪 Passenger exit | 0m | Event |

---

### Troubleshooting

| Problem | Solution |
|---------|----------|
| ⚠️ Connection refused | Check team WiFi, broker running |
| 📡 Continuous events | Other team members testing |
| ❌ Events not received | Check topics match, both connected |
| 🔄 Want unique topics | See [TEAM_WORKFLOW.md](TEAM_WORKFLOW.md) |

---

### Monitor MQTT Traffic

```bash
# See everything
mosquitto_sub -h 192.168.41.250 -t "#" -v

# See ADAS events only
mosquitto_sub -h 192.168.41.250 -t "vehicle/adas-actor/seen" -v

# See infotainment messages
mosquitto_sub -h 192.168.41.250 -t "infotainment/#" -v
```

---

### Key Files

| File | Purpose |
|------|---------|
| **run_vehicle_simulator.py** | Vehicle telemetry (REQUIRED) |
| **run_mock_scenarios.py** | Full test - 12 scenarios |
| **test_quick_scenarios.py** | Quick test - 5 scenarios |
| **nav_app/subscriber.py** | Navigation system (FASLit) |

---

### Documentation

| Guide | When to Read |
|-------|--------------|
| **[TEAM_WORKFLOW.md](TEAM_WORKFLOW.md)** | Using shared broker (YOU!) |
| [TESTING.md](TESTING.md) | Local testing setup |
| [SCENARIOS.md](SCENARIOS.md) | Scenario details |
| [SUMMARY.md](SUMMARY.md) | What was changed |

---

### MQTT Topics

**Published by Simulators:**
- `vehicle/data` ← Vehicle telemetry (1s)
- `vehicle/adas-actor/seen` ← ADAS events (10s)
- `vehicle/passenger/left` ← Passenger exit

**Published by nav_app:**
- `infotainment/hazard` ← Hazard alerts
- `infotainment/reroute` ← Reroute suggestions
- `infotainment/alternatives` ← Alternative transport
- `infotainment/status` ← Vehicle status
- `v2v/hazards/report` ← V2V network

---

### Duration Estimates

| Script | Duration | Scenarios |
|--------|----------|-----------|
| `test_quick_scenarios.py` | ~15 seconds | 5 |
| `run_mock_scenarios.py` | ~2 minutes | 12 |
| `run_fake_carla.py` | Continuous | 1 |

---

### Remember

✅ Scripts work **offline** (print locally)
✅ Need team **WiFi** for full integration
✅ **10-second** intervals between scenarios
✅ Original SDV code **intact**
✅ **Graceful** error handling

---

**Need Help?** → Read [TEAM_WORKFLOW.md](TEAM_WORKFLOW.md)

**Ready?** → Run the 3-terminal setup above! 🚀
