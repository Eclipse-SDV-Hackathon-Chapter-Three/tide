# Nav-App to Infotainment Integration Complete

## Overview

This document describes the **complete bidirectional communication** between the nav-app backend (Python) and the infotainment display (Android AAOS).

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        MQTT Broker                              │
│              (Mosquitto on shared laptop)                       │
└─────────┬────────────────────────────────────────┬──────────────┘
          │                                        │
          ▼                                        ▼
┌─────────────────────┐                  ┌──────────────────────┐
│   nav_app           │                  │  Android             │
│   (Python Backend)  │ ◄──Messages───►  │  Infotainment        │
│                     │                  │  (Kotlin Frontend)   │
├─────────────────────┤                  ├──────────────────────┤
│ • subscriber.py     │                  │ • MqttClusterBinder  │
│ • infotainment_     │                  │ • UI Components      │
│   publisher.py      │                  │ • User Actions       │
└─────────────────────┘                  └──────────────────────┘
```

## MQTT Topics

### Backend → Frontend (nav_app publishes)

| Topic | Purpose | Handler |
|-------|---------|---------|
| `infotainment/hazard` | Hazard detection alerts | `handleNavAppMessage()` |
| `infotainment/reroute` | Reroute notifications | `handleNavAppMessage()` |
| `infotainment/alternatives` | Transport suggestions | `handleNavAppMessage()` |
| `infotainment/autonomous` | Autonomous confirmation | `handleNavAppMessage()` |
| `infotainment/status` | Vehicle status updates | `handleNavAppMessage()` |
| `infotainment/screen_command` | Change display mode | `handleNavAppMessage()` |

### Frontend → Backend (Android publishes)

| Topic | Purpose | Handler |
|-------|---------|---------|
| `user/action` | User selections | `_handle_user_action()` |

## Implementation Details

### 1. Nav-App Backend ([subscriber.py](nav_app/subscriber.py))

**Subscriptions:**
```python
# Subscribe to user actions from infotainment
self.user_action_topic = "user/action"
self.mqtt_client.subscribe(self.user_action_topic)
```

**User Action Handler:**
```python
def _handle_user_action(self, data: dict):
    """Handle user action from infotainment display"""
    action_type = data.get("action", "unknown")
    action_data = data.get("data", {})

    if action_type == "select_alternative":
        transport_mode = action_data.get("transport_mode", "walk")
        autonomous_mode = action_data.get("autonomous_mode", "return_home")
        self.handle_passenger_choice(transport_mode, autonomous_mode)

    elif action_type == "accept_reroute":
        # User accepted the reroute
        pass

    elif action_type == "dismiss_alert":
        # User dismissed an alert
        pass
```

**Publishing to Infotainment:**
```python
# Initialize infotainment publisher
self.infotainment = InfotainmentPublisher(self.mqtt_client, self.vehicle_id)

# Publish hazard notification
self.infotainment.publish_hazard_detected(
    hazard_type, severity, distance_meters, description
)

# Publish reroute notification
self.infotainment.publish_reroute(
    reason="accident",
    old_eta_minutes=35,
    new_eta_minutes=32,
    auto_accept=True
)

# Publish alternative transport options
self.infotainment.publish_alternatives(
    current_eta_minutes=35,
    delay_estimate_minutes=20,
    alternatives=suggestions
)

# Publish autonomous confirmation
self.infotainment.publish_autonomous_confirmation(
    chosen_transport_mode="public_transit",
    vehicle_destination=(1000.0, 1000.0, 0.0),
    autonomous_mode="return_home",
    estimated_arrival=datetime.now(),
    tracking_url="https://tracking.app/..."
)
```

### 2. Infotainment Publisher ([infotainment_publisher.py](nav_app/infotainment_publisher.py))

All messages include:
- `message_type` - Message identifier
- `vehicle_id` - Unique vehicle ID
- `timestamp` - ISO format timestamp
- Type-specific fields (see [INFOTAINMENT_INTEGRATION.md](INFOTAINMENT_INTEGRATION.md))

### 3. Android Integration ([MqttClusterBinder.kt](sdv_lab/android_python/android/digital-cluster-app/app/src/main/java/com/example/digitalclusterapp/core/data/remote/remote/mqtt/MqttClusterBinder.kt))

**Subscriptions:**
```kotlin
private val INFOTAINMENT_TOPICS = listOf(
    "infotainment/hazard",
    "infotainment/reroute",
    "infotainment/alternatives",
    "infotainment/autonomous",
    "infotainment/status",
    "infotainment/screen_command"
)

// Subscribe on connection
INFOTAINMENT_TOPICS.forEach { topic ->
    client.subscribeWith()
        .topicFilter(topic)
        .qos(MqttQos.AT_LEAST_ONCE)
        .send()
}
```

**Message Handler:**
```kotlin
private fun handleNavAppMessage(topic: String, message: String) {
    val json = JSONObject(message)
    val messageType = json.optString("message_type", "unknown")

    when (messageType) {
        "hazard_notification" -> {
            // Show hazard alert on display
        }
        "reroute_notification" -> {
            // Show reroute with ETA comparison
        }
        "alternative_suggestion" -> {
            // Show transport alternatives
            _navAppMessage.value = message  // Emit to UI
        }
        "autonomous_confirmation" -> {
            // Show autonomous confirmation
        }
        "screen_command" -> {
            // Switch display mode
        }
    }
}
```

**Publishing User Actions:**
```kotlin
// User selects alternative transport
fun selectAlternativeTransport(
    transportMode: String,
    autonomousMode: String = "return_home"
): Boolean {
    return publishUserAction("select_alternative", mapOf(
        "transport_mode" to transportMode,
        "autonomous_mode" to autonomousMode
    ))
}

// User accepts reroute
fun acceptReroute(): Boolean {
    return publishUserAction("accept_reroute", emptyMap())
}

// User dismisses alert
fun dismissAlert(): Boolean {
    return publishUserAction("dismiss_alert", emptyMap())
}

// Internal publish method
fun publishUserAction(action: String, data: Map<String, Any>): Boolean {
    val json = JSONObject().apply {
        put("action", action)
        put("data", JSONObject(data))
    }
    return publishMessage(USER_ACTION_TOPIC, json.toString())
}
```

## Message Flow Examples

### Scenario 1: FIRST AVOID (Approaching Driver)

1. **ADAS detects hazard** → `adas_actor_event`
2. **nav_app processes** → Classifies hazard, calculates distance
3. **nav_app publishes** → `infotainment/hazard` (hazard alert)
4. **Android displays** → Hazard alert banner with distance
5. **nav_app recalculates** → Finds better route
6. **nav_app publishes** → `infotainment/reroute` (new route)
7. **Android displays** → Map view with new route, ETA comparison
8. **Auto-accepts** → After 8 seconds (or user taps accept)
9. **(Optional) Android publishes** → `user/action` with `accept_reroute`

### Scenario 2: SECOND LEAVE IT (Affected Driver)

1. **ADAS detects hazard** → `adas_actor_event`
2. **nav_app processes** → Detects vehicle is stuck (speed < 10 km/h, 5+ min)
3. **nav_app publishes** → `infotainment/hazard` (hazard alert)
4. **Android displays** → Hazard alert banner
5. **nav_app generates** → Alternative transport suggestions
6. **nav_app publishes** → `infotainment/alternatives` (transport options)
7. **Android displays** → Alternatives screen with 3 options (bus, taxi, walk)
8. **User selects** → Taps "Public Transit"
9. **Android publishes** → `user/action` with `select_alternative`
   ```json
   {
     "action": "select_alternative",
     "data": {
       "transport_mode": "public_transit",
       "autonomous_mode": "return_home"
     }
   }
   ```
10. **nav_app receives** → `_handle_user_action()` called
11. **nav_app initiates** → Autonomous mode session
12. **nav_app publishes** → `infotainment/autonomous` (confirmation + QR code)
13. **Android displays** → Autonomous confirmation screen with tracking URL

## Testing

### Option 1: Full Integration (Android + nav_app)

**Terminal 1: Start MQTT Broker**
```bash
mosquitto -v
```

**Terminal 2: Start nav_app**
```bash
cd /workspace/hello
python -m nav_app.subscriber
```

**Terminal 3: Start Android App**
```bash
cd sdv_lab/android_python/android/digital-cluster-app
./gradlew installDebug
adb shell am start -n com.example.digitalclusterapp/.MainActivity
```

**Terminal 4: Simulate ADAS Event**
```bash
mosquitto_pub -t "adas_actor_event" -m '{
  "actor_tag": "police_car",
  "is_visible": true,
  "timestamp": "2025-10-01T12:00:00",
  "location": [600.0, 300.0, 0.0]
}'
```

### Option 2: Simulator Testing (No Android Device)

**Terminal 1: Start MQTT Broker**
```bash
mosquitto -v
```

**Terminal 2: Start nav_app**
```bash
python -m nav_app.subscriber
```

**Terminal 3: Start Infotainment Simulator**
```bash
python -m nav_app.infotainment_simulator
```

**Terminal 4: Simulate ADAS Event (for SECOND LEAVE IT scenario)**
```bash
# First, update nav_app to be stuck
mosquitto_pub -t "vehicle/data" -m '{
  "location": [500.0, 500.0, 0.0],
  "speed": 5.0
}'

# Wait 5+ minutes or modify time_stuck_minutes in code for testing

# Then send hazard that triggers alternatives
mosquitto_pub -t "adas_actor_event" -m '{
  "actor_tag": "accident",
  "is_visible": true,
  "timestamp": "2025-10-01T12:00:00",
  "location": [600.0, 500.0, 0.0]
}'
```

**In Simulator Terminal:**
- Type `1`, `2`, or `3` to select alternative transport
- Type `a` to accept reroute
- Type `d` to dismiss alert
- Type `h` for help

### Expected Output

**Infotainment Simulator shows:**
```
================================================================================
🚨 HAZARD ALERT 🚨
================================================================================
  Title: ⚠️ Hazard Detected
  Accident detected 100m ahead
  Type: accident | Severity: HIGH
  Distance: 100m ahead
================================================================================

================================================================================
🚶 ALTERNATIVE OPTIONS (SECOND LEAVE IT)
================================================================================
  🚶 Alternative Options Available
  You may be stuck for ~20 minutes. Consider these faster alternatives:

  ⏱  TIME COMPARISON:
     Staying in vehicle: ~55 minutes
     Best alternative: ~27 minutes

  📋 ALTERNATIVE OPTIONS:

  1. 🚌 PUBLIC TRANSIT TO DESTINATION
     Time: 27 min | Cost: $3.50
     Distance: 4.2 km
     [ CHOOSE OPTION 1 ] - Type '1' to select

  2. 🚕 TAXI TO DESTINATION
     Time: 30 min | Cost: $15.50
     Distance: 4.2 km
     [ CHOOSE OPTION 2 ] - Type '2' to select

  3. 🚶 WALK TO DESTINATION
     Time: 52 min | Cost: $0.00
     Distance: 4.2 km
     [ CHOOSE OPTION 3 ] - Type '3' to select

  💡 Type 1, 2, or 3 to choose an option
================================================================================
```

**User types `1` (select public transit):**

**Simulator shows:**
```
✅ Selected option 1: Public transit to destination
📤 Sent user action to nav_app: select_alternative
```

**nav_app shows:**
```
──────────────────────────────────────────────────────────────────────
👤 User Action from Infotainment Display
──────────────────────────────────────────────────────────────────────
Action: select_alternative
Data: {'transport_mode': 'public_transit', 'autonomous_mode': 'return_home'}

🚶 User selected: public_transit
🤖 Vehicle will: return_home

══════════════════════════════════════════════════════════════════════
👤 PASSENGER CHOOSING ALTERNATIVE TRANSPORT
══════════════════════════════════════════════════════════════════════
...
Autonomous session initiated
══════════════════════════════════════════════════════════════════════
```

**Simulator shows:**
```
================================================================================
🤖 AUTONOMOUS MODE ACTIVATED
================================================================================
  🤖 Autonomous Mode Active
  You chose public_transit. Your vehicle will return home.

  Transport Mode: public_transit
  Vehicle Mode: Return Home

  Estimated Arrival: 13:15

  📱 Tracking URL: https://vehicle-tracking.app/track/vehicle_abc123
  (Scan QR code to track vehicle)
================================================================================
```

## Android UI Integration

To complete the UI integration in Android, you need to:

1. **Create data models** (see [INFOTAINMENT_INTEGRATION.md](INFOTAINMENT_INTEGRATION.md) lines 227-266)
2. **Update ViewModel** to handle infotainment state
3. **Create UI screens** for:
   - Hazard alerts
   - Alternative transport selection
   - Autonomous confirmation
4. **Wire up user actions** to call MqttClusterBinder methods

Example UI button:
```kotlin
// In AlternativeCard composable
Button(onClick = {
    // Call MqttClusterBinder to publish user action
    mqttBinder.selectAlternativeTransport(
        transportMode = alternative.mode,
        autonomousMode = "return_home"
    )
}) {
    Text("Choose")
}
```

## Key Files

### Python Backend
- [`nav_app/subscriber.py`](nav_app/subscriber.py) - Main nav_app with user action handling
- [`nav_app/infotainment_publisher.py`](nav_app/infotainment_publisher.py) - Publishes to Android
- [`nav_app/infotainment_simulator.py`](nav_app/infotainment_simulator.py) - Testing simulator
- [`contract/infotainment_message.py`](contract/infotainment_message.py) - Message contracts

### Android Frontend
- [`MqttClusterBinder.kt`](sdv_lab/android_python/android/digital-cluster-app/app/src/main/java/com/example/digitalclusterapp/core/data/remote/remote/mqtt/MqttClusterBinder.kt) - MQTT integration with user action publishing

### Documentation
- [`INFOTAINMENT_INTEGRATION.md`](INFOTAINMENT_INTEGRATION.md) - Detailed integration guide
- [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md) - Overall system summary

## Status

✅ **Backend → Frontend communication**: Complete
- nav_app publishes hazards, reroutes, alternatives, autonomous confirmations
- Android subscribes and logs all messages

✅ **Frontend → Backend communication**: Complete
- Android publishes user actions (select_alternative, accept_reroute, etc.)
- nav_app subscribes and handles user selections
- Full bidirectional loop working

✅ **Testing infrastructure**: Complete
- Infotainment simulator with interactive user input
- Full end-to-end testing capability without Android device

⚠️ **Android UI screens**: Partial
- Message handling is complete (logs all messages)
- UI screens for alternatives/autonomous need to be created
- User action methods are implemented, ready to wire to UI

## Next Steps for Full Android Integration

1. Create `InfotainmentState` sealed class in ViewModel
2. Expose `navAppMessage` flow to UI
3. Create composable screens:
   - `ClusterHazardAlert` - Display hazard warnings
   - `ClusterAlternatives` - Show transport options with "Choose" buttons
   - `ClusterAutonomousConfirmation` - Show QR code and tracking info
4. Wire button clicks to `MqttClusterBinder` user action methods
5. Add screen state management to switch between displays

See [INFOTAINMENT_INTEGRATION.md](INFOTAINMENT_INTEGRATION.md) for detailed Android UI code examples.
