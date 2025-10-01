# Quick Test Reference

## 30-Second Test Setup

### 1. Update Broker IP
```bash
# Edit mqtt_config.json
{
  "broker": "192.168.41.250",  # ← Team laptop IP
  "port": 1883
}
```

### 2. Open 3 Terminals

**Terminal 1 - Backend:**
```bash
cd /Users/donghyun/All/hello
python3 nav_app/subscriber.py
```

**Terminal 2 - Frontend Display:**
```bash
cd /Users/donghyun/All/hello
python3 nav_app/test_frontend.py
```

**Terminal 3 - Test Events:**
```bash
cd /Users/donghyun/All/hello
python3 nav_app/test_simulator.py --auto
```

### 3. Watch the Magic ✨

You should see:
1. **Terminal 1**: Nav-app processing events, making decisions
2. **Terminal 2**: Beautiful colored display of hazards, reroutes, alternatives
3. **Terminal 3**: Simulator sending test events

## Expected Output

### Frontend Display:
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
```

## Quick Debug

**No messages showing?**
```bash
# Test MQTT connectivity
mosquitto_sub -h 192.168.41.250 -t '#' -v

# Should see messages flowing
```

**Frontend not connecting?**
- Check broker IP in mqtt_config.json
- Ensure MQTT broker running on team laptop
- Verify network connectivity

**Backend not processing?**
- Check paho-mqtt installed: `pip install paho-mqtt`
- Check all nav_app modules present
- Look for Python errors in Terminal 1

## Message Topics Reference

| Topic | Purpose | Publisher | Subscriber |
|-------|---------|-----------|------------|
| `adas_actor_event` | Hazard detection | CARLA/Simulator | Nav-app |
| `vehicle/data` | Vehicle status | CARLA/Simulator | Nav-app |
| `infotainment/hazard` | Hazard alerts | Nav-app | Frontend |
| `infotainment/reroute` | Reroute notices | Nav-app | Frontend |
| `infotainment/alternatives` | Transport options | Nav-app | Frontend |
| `user/action` | User selections | Frontend | Nav-app |

## Test Scenarios in 1 Minute

**Scenario 1 - Approaching (Reroute):**
```python
# In simulator:
Select option: 1
# Expected: Blue reroute notification on frontend
```

**Scenario 2 - Stuck (Alternatives):**
```python
# In simulator:
Select option: 2
# Expected: Yellow alternatives panel with options
```

**Scenario 3 - Critical:**
```python
# In simulator:
Select option: 3
# Expected: Red critical alert
```

## Integration Checklist

For Android frontend:

- [ ] Subscribe to `infotainment/*` topics in MqttClusterBinder.kt
- [ ] Parse JSON messages (see test_frontend.py for examples)
- [ ] Display hazard notifications with severity colors
- [ ] Show reroute with old/new ETA comparison
- [ ] Display alternative options with selection UI
- [ ] Publish user actions to `user/action` topic
- [ ] Handle screen state changes

## Files You Need

```
nav_app/
  ├── subscriber.py          # Main nav-app (backend)
  ├── test_frontend.py       # Test display (THIS IS YOUR REFERENCE)
  ├── test_simulator.py      # Event generator
  └── infotainment_publisher.py  # Message publisher

contract/
  ├── infotainment_message.py    # Message schemas
  └── adas_actor_event.py        # Event schemas
```

## Success Criteria

✓ All 3 terminals running without errors
✓ Frontend displays colored, formatted messages
✓ Backend logs show decision-making process
✓ Messages appear within 1 second of event
✓ User actions can be simulated

---

**For Hackathon Demo:**
1. Run automated test: `python3 nav_app/test_simulator.py --auto`
2. Show frontend terminal with live updates
3. Explain FASLit strategy (First Avoid → Reroute, Second Leave It → Alternatives)
4. Show Android app with same integration
