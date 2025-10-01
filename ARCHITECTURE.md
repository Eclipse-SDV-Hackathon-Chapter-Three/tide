# FASLit System Architecture

## Component Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MQTT Broker (Mosquitto)                         │
│                    Running on Team Laptop (192.168.41.250)              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                     ┌──────────────┼──────────────┐
                     │              │              │
                     ▼              ▼              ▼
         ┌─────────────────┐  ┌─────────┐  ┌─────────────┐
         │  CARLA Sim      │  │ Nav-App │  │  Frontend   │
         │  (Publisher)    │  │ Backend │  │  (Display)  │
         └─────────────────┘  └─────────┘  └─────────────┘
```

## Detailed Data Flow

### 1. Event Detection Flow

```
CARLA Simulator                 Nav-App Backend              Frontend Display
(or test_simulator.py)          (subscriber.py)           (test_frontend.py or Android)
─────────────────              ─────────────────           ──────────────────────

    📸 Detect actor
    (police, accident, etc.)
         │
         │ MQTT publish to
         │ "adas_actor_event"
         ├─────────────────────►  Receive event
         │                              │
         │                              │ Classify hazard
         │                              │ Assess severity
         │                              │ Make decision
         │                              │
         │                              │ DECISION:
         │                              ├─► Approaching → REROUTE
         │                              │       │
         │                              │       │ Publish to
         │                              │       │ "infotainment/reroute"
         │                              │       └────────────────────►  🔄 Display
         │                              │                               reroute
         │                              │                               notification
         │                              │
         │                              ├─► Affected → ALTERNATIVES
         │                              │       │
         │                              │       │ Publish to
         │                              │       │ "infotainment/alternatives"
         │                              │       └────────────────────►  🚶 Display
         │                              │                               transport
         │                              │                               options
         │                              │
         │                              └─► Always publish hazard
         │                                      │ notification
         │                                      │ "infotainment/hazard"
         │                                      └────────────────────►  ⚠️ Display
         │                                                              hazard alert
         │
    🚗 Publish vehicle data
    (speed, location)
         │ MQTT publish to
         │ "vehicle/data"
         └─────────────────────►  Update vehicle state
                                  Track if stuck
                                  Update central server
                                       │
                                       │ Publish to
                                       │ "infotainment/status"
                                       └────────────────────►  📊 Update
                                                               status bar
```

### 2. User Interaction Flow

```
Frontend Display              Nav-App Backend              Autonomous System
─────────────────            ─────────────────            ─────────────────

User selects
alternative transport
    │
    │ MQTT publish to
    │ "user/action"
    │ {
    │   "action": "select_alternative",
    │   "data": {
    │     "transport_mode": "public_transit",
    │     "autonomous_mode": "return_home"
    │   }
    │ }
    ├────────────────────►  Receive action
    │                            │
    │                            │ Process choice
    │                            │ Validate exit
    │                            │ Initiate autonomous
    │                            │      │
    │                            │      │ Publish to
    │                            │      │ "infotainment/autonomous"
    │◄───────────────────────────┘
    │
    │ Display confirmation
    │ Show tracking QR
    │ Vehicle now autonomous  ────────────────────►  Vehicle drives
    │                                                 itself home
```

## Message Schemas

### ADAS Actor Event (Input to Nav-App)
```json
{
  "actor_tag": "vehicle.police.car",
  "location": [1800.0, 500.0, 0.0],
  "is_visible": true,
  "timestamp": "2025-10-01T14:35:22.123456"
}
```

### Hazard Notification (Nav-App → Frontend)
```json
{
  "message_type": "hazard_notification",
  "title": "⚠️ HAZARD AHEAD",
  "description": "Police detected 800m ahead",
  "hazard_type": "police",
  "severity": "high",
  "distance_meters": 800.0,
  "alert_level": "warning",
  "icon": "ic_police",
  "timestamp": "2025-10-01T14:35:22.123456",
  "show_duration_seconds": 10
}
```

### Reroute Notification (Nav-App → Frontend)
```json
{
  "message_type": "reroute_notification",
  "title": "🔄 Route Updated",
  "description": "New route calculated to avoid police",
  "old_eta_minutes": 25,
  "new_eta_minutes": 27,
  "time_saved_minutes": -2,
  "reason": "police",
  "timestamp": "2025-10-01T14:35:23.456789",
  "show_duration_seconds": 8,
  "auto_accept": true
}
```

### Alternative Suggestion (Nav-App → Frontend)
```json
{
  "message_type": "alternative_suggestion",
  "title": "🚶 Alternative Options Available",
  "description": "You may be stuck for ~20 minutes. Consider these faster alternatives:",
  "current_eta_minutes": 25,
  "delay_estimate_minutes": 20,
  "alternatives": [
    {
      "mode": "public_transit",
      "icon": "ic_bus",
      "estimated_time_minutes": 15,
      "estimated_cost": 2.50,
      "distance_km": 3.2,
      "description": "Bus to destination - fastest option",
      "instructions": [
        "Walk 200m to bus stop",
        "Take Bus #42 towards Downtown",
        "Get off at Main St (5 stops)"
      ]
    }
  ],
  "requires_user_action": true,
  "timeout_seconds": 60
}
```

### User Action (Frontend → Nav-App)
```json
{
  "action": "select_alternative",
  "data": {
    "transport_mode": "public_transit",
    "autonomous_mode": "return_home"
  }
}
```

## FASLit Decision Strategy

```
┌───────────────────────────────────────────────────────────┐
│              HAZARD DETECTED                              │
└───────────────────┬───────────────────────────────────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  Classify & Assess   │
         │  - Type (police, etc)│
         │  - Severity          │
         │  - Distance          │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │   Decision Engine    │
         └──────────┬───────────┘
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
   ┌────────────┐      ┌──────────────┐
   │ APPROACHING│      │   AFFECTED   │
   │  (Far)     │      │   (Close/    │
   │            │      │    Stuck)    │
   └─────┬──────┘      └───────┬──────┘
         │                     │
         ▼                     ▼
   ┌────────────┐      ┌──────────────┐
   │   FIRST    │      │   SECOND     │
   │   AVOID    │      │  LEAVE IT    │
   │            │      │              │
   │  REROUTE   │      │ SUGGEST      │
   │            │      │ ALTERNATIVES │
   └────────────┘      └──────────────┘
```

### Decision Criteria

**FIRST AVOID (Reroute):**
- Distance to hazard > 500m
- OR approaching at moderate/high speed
- Vehicle can still take alternative route

**SECOND LEAVE IT (Alternatives):**
- Distance to hazard < 200m
- AND speed < 10 km/h (stuck)
- AND stuck for > 5 minutes
- Passenger can exit and use alternative transport

## Module Breakdown

### Nav-App Backend (`nav_app/`)

```
subscriber.py               # Main application entry point
├── FASlitNavigationApp    # Core application class
│   ├── _on_adas_message()     # Handle ADAS events
│   ├── _make_decision()        # Decision engine
│   ├── _execute_reroute()      # First Avoid
│   └── _suggest_alternatives() # Second Leave It

hazard_classifier.py       # Classify actor tags → hazard types
route_manager.py          # Route planning with hazard avoidance
decision_engine.py        # Core FASLit decision logic
alternative_transport.py  # Generate transport alternatives
autonomous_manager.py     # Handle autonomous vehicle handoff
central_server.py         # V2V communication
infotainment_publisher.py # Publish to frontend (KEY MODULE)
```

### Contracts (`contract/`)

```
adas_actor_event.py       # ADAS event schema
passenger_leaving_event.py # Passenger exit schema
infotainment_message.py   # Frontend message schemas (IMPORTANT)
```

### Test Tools (`nav_app/`)

```
test_frontend.py          # Terminal frontend (YOUR REFERENCE)
test_simulator.py         # Event simulator for testing
```

## Integration Points

### For Android Frontend:

1. **MqttClusterBinder.kt** already has:
   - ✓ Subscription to infotainment topics (lines 54-61)
   - ✓ Message handling (handleNavAppMessage, line 139)
   - ✓ User action publishing (publishUserAction, line 593)

2. **What you need to add:**
   - Parse JSON messages using schemas from `infotainment_message.py`
   - Display UI components for each message type
   - Handle user interactions (button clicks → publishUserAction)

3. **Reference implementation:**
   - `test_frontend.py` shows exactly how to:
     - Parse each message type
     - Format data for display
     - Handle user actions
     - Manage screen states

## MQTT Topics Summary

| Topic | Direction | QoS | Purpose |
|-------|-----------|-----|---------|
| `adas_actor_event` | CARLA → Nav-App | 1 | Hazard detection events |
| `vehicle/data` | CARLA → Nav-App | 1 | Vehicle speed/location |
| `passenger_exit` | CARLA → Nav-App | 1 | Passenger exit detection |
| `infotainment/hazard` | Nav-App → Frontend | 1 | Hazard alerts |
| `infotainment/reroute` | Nav-App → Frontend | 1 | Reroute notifications |
| `infotainment/alternatives` | Nav-App → Frontend | 1 | Transport suggestions |
| `infotainment/autonomous` | Nav-App → Frontend | 1 | Autonomous confirmations |
| `infotainment/status` | Nav-App → Frontend | 0 | Vehicle status updates |
| `infotainment/screen_command` | Nav-App → Frontend | 1 | Screen control |
| `user/action` | Frontend → Nav-App | 1 | User interactions |

## Testing Strategy

1. **Unit Testing**: Each module has specific logic
2. **Integration Testing**: Use test_simulator.py
3. **End-to-End Testing**: CARLA → Nav-App → Android
4. **Demo Scenario**: Automated test sequence

See `TESTING_GUIDE.md` for detailed testing procedures.
