# Infotainment Integration Guide

## Architecture Overview

The FASLit system follows a **Backend-Frontend** architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                        MQTT Broker                              │
│              (localhost / Shared Laptop IP)                     │
└─────────┬────────────────────────────────────────┬──────────────┘
          │                                        │
          ▼                                        ▼
┌─────────────────────┐                  ┌──────────────────────┐
│   nav_app           │                  │  Android             │
│   (Python Backend)  │                  │  Infotainment        │
│                     │                  │  (Kotlin Frontend)   │
├─────────────────────┤                  ├──────────────────────┤
│ • Hazard Detection  │                  │ • ClusterState       │
│ • Decision Engine   │                  │ • UI Display         │
│ • Route Manager     │                  │ • User Interaction   │
│ • Alt. Transport    │ ──Messages──>    │ • Touch Controls     │
│ • Autonomous Mgr    │                  │ • Gauges & Alerts    │
└─────────────────────┘                  └──────────────────────┘
```

## Communication Flow

### 1. MQTT Topics

**Backend → Frontend (nav_app publishes, Android subscribes):**

| Topic | Purpose | Message Type |
|-------|---------|-------------|
| `infotainment/hazard` | Hazard detection alerts | HazardNotification |
| `infotainment/reroute` | Reroute notifications (FIRST AVOID) | RerouteNotification |
| `infotainment/alternatives` | Transport suggestions (SECOND LEAVE IT) | AlternativeSuggestion |
| `infotainment/autonomous` | Autonomous mode confirmation | AutonomousConfirmation |
| `infotainment/status` | Vehicle status updates | VehicleStatusUpdate |
| `infotainment/screen_command` | Change display mode | CentralScreenCommand |

**Frontend → Backend (Android publishes, nav_app subscribes):**

| Topic | Purpose | Data Format |
|-------|---------|------------|
| `user/action` | User selections from infotainment | JSON with action type |
| `vehicle/data` | Vehicle state (speed, location) | JSON with vehicle data |

### 2. Message Contracts

All message contracts are defined in [`contract/infotainment_message.py`](contract/infotainment_message.py)

#### HazardNotification
```json
{
  "message_type": "hazard_notification",
  "title": "⚠️ Hazard Detected",
  "description": "Accident detected 350m ahead",
  "hazard_type": "accident",
  "severity": "high",
  "distance_meters": 350.0,
  "alert_level": "warning",
  "icon": "ic_accident",
  "timestamp": "2025-09-30T18:30:00",
  "show_duration_seconds": 10,
  "vehicle_id": "vehicle_abc123"
}
```

**Android Display:** Show alert banner at top of cluster display with hazard icon and distance.

---

#### RerouteNotification (FIRST AVOID Scenario)
```json
{
  "message_type": "reroute_notification",
  "title": "🔄 Route Updated",
  "description": "New route calculated to avoid accident",
  "old_eta_minutes": 35,
  "new_eta_minutes": 32,
  "time_saved_minutes": 3,
  "reason": "accident",
  "timestamp": "2025-09-30T18:30:05",
  "show_duration_seconds": 8,
  "auto_accept": true,
  "vehicle_id": "vehicle_abc123"
}
```

**Android Display:**
- Switch `CentralScreenState` to `MAP`
- Show new route highlighted
- Display ETA comparison
- Auto-accept after 8 seconds if no user interaction

---

#### AlternativeSuggestion (SECOND LEAVE IT Scenario)
```json
{
  "message_type": "alternative_suggestion",
  "title": "🚶 Alternative Options Available",
  "description": "You may be stuck for ~20 minutes. Consider these faster alternatives:",
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
        "Take Line 2 towards Central Station",
        "Transfer at Central Station to Line 5",
        "Estimated total time: 27 minutes"
      ]
    },
    {
      "mode": "taxi",
      "icon": "ic_taxi",
      "estimated_time_minutes": 30,
      "estimated_cost": 15.5,
      "distance_km": 4.2,
      "description": "Taxi to destination",
      "instructions": [
        "Exit vehicle and enable autonomous parking mode",
        "Taxi will arrive in 5 minutes",
        "Direct route to destination",
        "Estimated cost: $15.50"
      ]
    }
  ],
  "timestamp": "2025-09-30T18:35:00",
  "requires_user_action": true,
  "timeout_seconds": 60,
  "vehicle_id": "vehicle_abc123"
}
```

**Android Display:**
- Create new screen state: `ALTERNATIVES`
- Show list of transport options with:
  - Mode icon
  - Estimated time
  - Cost
  - "Choose" button for each option
- Highlight best option (first in list)
- Show countdown timer (60 seconds)
- Send user selection back to backend via `user/action` topic

---

#### AutonomousConfirmation
```json
{
  "message_type": "autonomous_confirmation",
  "title": "🤖 Autonomous Mode Active",
  "description": "You chose public_transit. Your vehicle will return home and park autonomously.",
  "chosen_transport_mode": "public_transit",
  "vehicle_destination": [1000.0, 1000.0, 0.0],
  "autonomous_mode": "return_home",
  "estimated_arrival_time": "2025-09-30T19:15:00",
  "tracking_url": "https://vehicle-tracking.app/track/vehicle_abc123/session_xyz",
  "timestamp": "2025-09-30T18:36:00",
  "vehicle_id": "vehicle_abc123"
}
```

**Android Display:**
- Show confirmation message
- Display QR code for `tracking_url`
- Show vehicle destination on map
- Display estimated arrival time
- Change to autonomous driving mode UI

---

#### CentralScreenCommand
```json
{
  "message_type": "screen_command",
  "screen_state": "HAZARD_ALERT",
  "data": {
    "hazard_type": "accident",
    "severity": "high",
    "distance": 350.0
  },
  "vehicle_id": "vehicle_abc123"
}
```

**Screen States:**
- `MODES` - Driving mode selection (default)
- `MAP` - Navigation map view
- `SENSORS_FORWARD` - Forward sensors display
- `SENSORS_BLIND` - Blind spot sensors
- `HAZARD_ALERT` - Hazard warning screen (custom)
- `ALTERNATIVES` - Alternative transport options (custom)
- `AUTONOMOUS_ACTIVE` - Autonomous mode status (custom)

---

## Android Integration Steps

### 1. Add New Screen States

In [`CentralScreenState.kt`](sdv_lab/android_python/android/digital-cluster-app/app/src/main/java/com/example/digitalclusterapp/core/domain/model/CentralScreenState.kt):

```kotlin
enum class CentralScreenState {
    MODES,
    MAP,
    SENSORS_FORWARD,
    SENSORS_BLIND,
    HAZARD_ALERT,        // NEW
    ALTERNATIVES,        // NEW
    AUTONOMOUS_ACTIVE    // NEW
}
```

### 2. Create Data Models

```kotlin
// InfotainmentMessage.kt
data class HazardNotification(
    val messageType: String,
    val title: String,
    val description: String,
    val hazardType: String,
    val severity: String,
    val distanceMeters: Float,
    val alertLevel: String,
    val icon: String,
    val timestamp: String,
    val showDurationSeconds: Int,
    val vehicleId: String
)

data class AlternativeSuggestion(
    val messageType: String,
    val title: String,
    val description: String,
    val currentEtaMinutes: Int,
    val delayEstimateMinutes: Int,
    val alternatives: List<TransportAlternative>,
    val timestamp: String,
    val requiresUserAction: Boolean,
    val timeoutSeconds: Int,
    val vehicleId: String
)

data class TransportAlternative(
    val mode: String,
    val icon: String,
    val estimatedTimeMinutes: Int,
    val estimatedCost: Float,
    val distanceKm: Float,
    val description: String,
    val instructions: List<String>
)
```

### 3. Subscribe to Infotainment Topics

In [`MqttClusterBinder.kt`](sdv_lab/android_python/android/digital-cluster-app/app/src/main/java/com/example/digitalclusterapp/core/data/remote/remote/mqtt/MqttClusterBinder.kt):

```kotlin
private val INFOTAINMENT_TOPICS = listOf(
    "infotainment/hazard",
    "infotainment/reroute",
    "infotainment/alternatives",
    "infotainment/autonomous",
    "infotainment/status",
    "infotainment/screen_command"
)

fun subscribeToInfotainment() {
    INFOTAINMENT_TOPICS.forEach { topic ->
        mqttClient.subscribe(topic, 1) { topic, message ->
            handleInfotainmentMessage(topic, message)
        }
    }
}

private fun handleInfotainmentMessage(topic: String, message: String) {
    val json = JSONObject(message)
    val messageType = json.getString("message_type")

    when (messageType) {
        "hazard_notification" -> handleHazardNotification(json)
        "reroute_notification" -> handleRerouteNotification(json)
        "alternative_suggestion" -> handleAlternativeSuggestion(json)
        "autonomous_confirmation" -> handleAutonomousConfirmation(json)
        "screen_command" -> handleScreenCommand(json)
        "vehicle_status" -> handleVehicleStatus(json)
    }
}
```

### 4. Update ViewModel

```kotlin
// ClusterViewModel.kt
private val _infotainmentState = MutableStateFlow<InfotainmentState>(InfotainmentState.Idle)
val infotainmentState: StateFlow<InfotainmentState> = _infotainmentState.asStateFlow()

fun handleHazardAlert(notification: HazardNotification) {
    _infotainmentState.value = InfotainmentState.HazardAlert(notification)
    _currentCentralScreen.value = CentralScreenState.HAZARD_ALERT
}

fun handleAlternatives(suggestion: AlternativeSuggestion) {
    _infotainmentState.value = InfotainmentState.Alternatives(suggestion)
    _currentCentralScreen.value = CentralScreenState.ALTERNATIVES
}

fun selectAlternative(mode: String, autonomousMode: String) {
    // Publish user choice back to backend
    publishUserAction(
        action = "select_alternative",
        data = mapOf(
            "transport_mode" to mode,
            "autonomous_mode" to autonomousMode
        )
    )
}
```

### 5. Create UI Components

```kotlin
// ClusterHazardAlert.kt
@Composable
fun ClusterHazardAlert(notification: HazardNotification) {
    Box(modifier = Modifier.fillMaxSize()) {
        Column(
            modifier = Modifier.align(Alignment.Center),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                painter = painterResource(getHazardIcon(notification.icon)),
                contentDescription = notification.hazardType,
                tint = getAlertColor(notification.alertLevel),
                modifier = Modifier.size(64.dp)
            )

            Text(
                text = notification.title,
                style = MaterialTheme.typography.h5,
                fontWeight = FontWeight.Bold
            )

            Text(
                text = notification.description,
                style = MaterialTheme.typography.body1
            )

            Text(
                text = "${notification.distanceMeters.toInt()}m ahead",
                style = MaterialTheme.typography.body2,
                color = Color.Gray
            )
        }
    }
}

// ClusterAlternatives.kt
@Composable
fun ClusterAlternatives(
    suggestion: AlternativeSuggestion,
    onSelectAlternative: (String, String) -> Unit
) {
    LazyColumn(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        item {
            Text(
                text = suggestion.title,
                style = MaterialTheme.typography.h6,
                fontWeight = FontWeight.Bold
            )
            Text(
                text = suggestion.description,
                style = MaterialTheme.typography.body2
            )
            Spacer(modifier = Modifier.height(16.dp))
        }

        items(suggestion.alternatives) { alternative ->
            AlternativeCard(
                alternative = alternative,
                onSelect = {
                    onSelectAlternative(alternative.mode, "continue_to_destination")
                }
            )
            Spacer(modifier = Modifier.height(8.dp))
        }
    }
}

@Composable
fun AlternativeCard(
    alternative: TransportAlternative,
    onSelect: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = 4.dp
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                painter = painterResource(getTransportIcon(alternative.icon)),
                contentDescription = alternative.mode,
                modifier = Modifier.size(48.dp)
            )

            Column(modifier = Modifier.weight(1f).padding(start = 16.dp)) {
                Text(
                    text = alternative.description,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "${alternative.estimatedTimeMinutes} min • $${alternative.estimatedCost}",
                    style = MaterialTheme.typography.body2
                )
            }

            Button(onClick = onSelect) {
                Text("Choose")
            }
        }
    }
}
```

### 6. Update Main Screen

```kotlin
// ClusterScreen.kt
when (infotainmentState) {
    is InfotainmentState.HazardAlert -> {
        ClusterHazardAlert(notification = infotainmentState.notification)
    }
    is InfotainmentState.Alternatives -> {
        ClusterAlternatives(
            suggestion = infotainmentState.suggestion,
            onSelectAlternative = viewModel::selectAlternative
        )
    }
    is InfotainmentState.AutonomousActive -> {
        ClusterAutonomousConfirmation(confirmation = infotainmentState.confirmation)
    }
    else -> {
        // Existing cluster display
        Cluster(state = clusterState)
    }
}
```

## Testing the Integration

### 1. Start MQTT Broker
```bash
# On shared laptop
mosquitto -v
```

### 2. Start Android Infotainment
- Open Android Studio
- Load project: `sdv_lab/android_python/android/digital-cluster-app`
- Update MQTT broker IP in `MqttModule.kt`
- Run on device/emulator

### 3. Start nav_app Backend
```bash
cd /workspace/hello
python -m nav_app.subscriber
```

### 4. Simulate ADAS Events
Publish test hazard event to `adas_actor_event` topic:
```bash
mosquitto_pub -t "adas_actor_event" -m '{
  "actor_tag": "police_car",
  "is_visible": true,
  "timestamp": "2025-09-30T18:30:00",
  "location": [600.0, 300.0, 0.0]
}'
```

### 5. Expected Flow
1. nav_app receives ADAS event
2. nav_app classifies hazard and makes decision
3. nav_app publishes to infotainment topics
4. Android displays alert/alternatives
5. User selects option on Android
6. Android publishes choice back to nav_app
7. nav_app initiates autonomous mode

## Demo Scenarios

### Scenario 1: Approaching Driver (FIRST AVOID)
1. Hazard detected 600m ahead
2. Display shows hazard alert
3. Backend calculates reroute
4. Display switches to MAP, shows new route
5. ETA comparison displayed
6. Route auto-accepted

### Scenario 2: Affected Driver (SECOND LEAVE IT)
1. Hazard detected, vehicle stuck (<10 km/h for 5+ min)
2. Display shows hazard alert
3. Display switches to ALTERNATIVES screen
4. Shows 3 transport options with times/costs
5. User selects "Public Transit"
6. Display shows autonomous confirmation + QR code
7. Vehicle enters autonomous mode

## MQTT Configuration

Update [`mqtt_config.json`](mqtt_config.json):
```json
{
  "broker": "192.168.1.100",
  "port": 1883,
  "keepalive": 60
}
```

Replace `192.168.1.100` with shared laptop's IP address during hackathon.
