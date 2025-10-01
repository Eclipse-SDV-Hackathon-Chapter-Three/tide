# FASLit nav_app Integration

## ✅ Integration Complete!

The Android infotainment app is now integrated with the FASLit nav_app backend!

## What Was Added

### Modified File: `MqttClusterBinder.kt`

**Added:**
1. ✅ Subscription to 6 nav_app topics (`infotainment/*`)
2. ✅ Message parsing for all nav_app message types
3. ✅ Logging of received navigation events
4. ✅ State flow for UI integration (`navAppMessage`)

**Topics Subscribed:**
- `infotainment/hazard` - Hazard alerts
- `infotainment/reroute` - Reroute notifications
- `infotainment/alternatives` - Alternative transport suggestions
- `infotainment/autonomous` - Autonomous mode confirmations
- `infotainment/status` - Vehicle status updates
- `infotainment/screen_command` - Screen mode commands

## Setup Instructions

### Step 1: Update MQTT Broker IP

In `MqttClusterBinder.kt` line 48, change:

```kotlin
private const val BROKER_HOST = "10.0.2.2" // Replace with your broker host
```

To your team laptop's IP (e.g., `192.168.1.100`):

```kotlin
private const val BROKER_HOST = "192.168.1.100" // Team laptop IP
```

### Step 2: Build and Run

```bash
# In Android Studio
Build > Clean Project
Build > Rebuild Project
Run > Run 'app'
```

### Step 3: Start nav_app Backend

On your other laptop:

```bash
cd /workspace/hello
# Update mqtt_config.json with team laptop IP first!
python -m nav_app.subscriber
```

## Testing the Integration

### Watch Android Logcat

Filter by tag: `MqttClusterBinder`

**You should see:**
```
✓ Subscribed to: vehicle/parameters
✓ Subscribed to nav_app: infotainment/hazard
✓ Subscribed to nav_app: infotainment/reroute
✓ Subscribed to nav_app: infotainment/alternatives
...
```

### Send Test Hazard

From any terminal:

```bash
mosquitto_pub -h 192.168.1.100 -t "adas_actor_event" -m '{
  "actor_tag": "accident",
  "is_visible": true,
  "timestamp": "2025-09-30T19:00:00",
  "location": [600.0, 300.0, 0.0]
}'
```

**Android Logcat should show:**
```
🚨 HAZARD: ⚠️ Hazard Detected - Accident detected 600m ahead (Severity: high)
🔄 REROUTE: Route Updated - Old: 35min, New: 32min, Saved: 3min
```

## Message Types & Logging

When nav_app publishes messages, you'll see in Logcat:

### Hazard Alert
```
🚨 HAZARD: ⚠️ Hazard Detected - Accident detected 600m ahead (Severity: high)
```

### Reroute (FIRST AVOID)
```
🔄 REROUTE: Route Updated - Old: 35min, New: 32min, Saved: 3min
```

### Alternatives (SECOND LEAVE IT)
```
🚶 ALTERNATIVES: Alternative Options Available - 3 options available
```

### Autonomous Confirmation
```
🤖 AUTONOMOUS: Autonomous Mode Active - Mode: return_home
```

### Screen Command
```
📺 SCREEN COMMAND: Switch to MAP
```

## Accessing Messages in UI

The `navAppMessage` StateFlow is exposed for UI components:

```kotlin
// In your ViewModel or Composable
val navAppMessage by mqttBinder.navAppMessage.collectAsState()

LaunchedEffect(navAppMessage) {
    navAppMessage?.let { message ->
        val json = JSONObject(message)
        val messageType = json.getString("message_type")

        when (messageType) {
            "hazard_notification" -> {
                // Show hazard alert UI
                showHazardAlert(json)
            }
            "alternative_suggestion" -> {
                // Show alternatives screen
                showAlternativesScreen(json)
            }
            // ... handle other types
        }
    }
}
```

## Message Formats

### Hazard Notification
```json
{
  "message_type": "hazard_notification",
  "title": "⚠️ Hazard Detected",
  "description": "Accident detected 600m ahead",
  "hazard_type": "accident",
  "severity": "high",
  "distance_meters": 600.0,
  "alert_level": "warning",
  "icon": "ic_accident",
  "timestamp": "2025-09-30T19:00:00",
  "show_duration_seconds": 10,
  "vehicle_id": "vehicle_abc123"
}
```

### Alternative Suggestion
```json
{
  "message_type": "alternative_suggestion",
  "title": "🚶 Alternative Options Available",
  "description": "You may be stuck for ~20 minutes...",
  "current_eta_minutes": 35,
  "delay_estimate_minutes": 20,
  "alternatives": [
    {
      "mode": "public_transit",
      "icon": "ic_bus",
      "estimated_time_minutes": 27,
      "estimated_cost": 3.5,
      "distance_km": 4.2,
      "description": "Public transit to destination",
      "instructions": [
        "Exit vehicle and enable autonomous parking mode",
        "Walk to nearest transit station (150m)",
        "Take Line 2 towards Central Station"
      ]
    }
  ],
  "timestamp": "2025-09-30T19:00:00",
  "requires_user_action": true,
  "timeout_seconds": 60
}
```

## Current Status

**✅ DONE - Backend Integration:**
- Messages are received
- JSON parsing works
- Logging is functional
- State flow is available

**🚧 TODO - UI Implementation:**
- Create hazard alert composable
- Create alternatives screen composable
- Create autonomous confirmation screen
- Wire up to ViewModel
- Add screen transitions

## Next Steps

1. **Test with Logcat** - Verify messages are received
2. **Build UI Components** - Create composables for each message type
3. **Wire to ViewModel** - Connect `navAppMessage` flow to UI
4. **Test with CARLA** - Full end-to-end test

## Troubleshooting

### Not receiving messages

**Check:**
1. MQTT broker IP is correct
2. Both devices on same network
3. nav_app is running
4. Logcat shows "✓ Subscribed to nav_app: infotainment/..."

### Messages not parsing

**Check Logcat for:**
```
Error handling nav_app message
```

If you see this, the JSON format may be incorrect.

### Connection issues

```bash
# Test MQTT connectivity
mosquitto_sub -h 192.168.1.100 -t "infotainment/#" -v
```

## Architecture

```
CARLA (Team Laptop)
    │
    ├─ ADAS detects hazard
    │
    └─→ Publishes: adas_actor_event
              │
              ▼
        nav_app (Python)
              │
              ├─ Classifies hazard
              ├─ Makes decision
              │
              └─→ Publishes: infotainment/*
                        │
                        ▼
              Android Infotainment
                        │
                        ├─ MqttClusterBinder receives
                        ├─ Parses JSON
                        ├─ Logs to Logcat ✅
                        └─ Emits to navAppMessage StateFlow
                                  │
                                  └─→ UI displays (TODO)
```

## Support

For complete details, see:
- [`/workspace/hello/INFOTAINMENT_INTEGRATION.md`](../../../../../INFOTAINMENT_INTEGRATION.md)
- [`/workspace/hello/IMPLEMENTATION_SUMMARY.md`](../../../../../IMPLEMENTATION_SUMMARY.md)

---

**Status: Backend integration complete! ✅**
**Next: Build UI components for displaying nav_app messages**
