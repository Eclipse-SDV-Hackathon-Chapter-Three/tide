# FASLit Implementation Summary

## ✅ Complete System Delivered

### System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         CARLA Simulator                          │
│                  (ADAS Events via Cameras)                       │
└────────────────────────┬─────────────────────────────────────────┘
                         │ MQTT: adas_actor_event
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                   nav_app (Backend - Python)                     │
├──────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ HAZARD CLASSIFIER                                          │  │
│  │ • Classifies: police, accident, construction, etc.         │  │
│  │ • Assesses severity: LOW, MEDIUM, HIGH, CRITICAL           │  │
│  └────────────────────────────────────────────────────────────┘  │
│                          ▼                                        │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ DECISION ENGINE (FASLit Strategy)                          │  │
│  │                                                            │  │
│  │ APPROACHING (>500m):  AFFECTED (<100m, slow):             │  │
│  │ ┌──────────────────┐  ┌──────────────────────┐            │  │
│  │ │ FIRST AVOID      │  │ SECOND LEAVE IT      │            │  │
│  │ │ • Reroute        │  │ • Suggest alternatives│            │  │
│  │ │ • Avoid hazard   │  │ • Exit vehicle        │            │  │
│  │ └──────────────────┘  └──────────────────────┘            │  │
│  └────────────────────────────────────────────────────────────┘  │
│                          ▼                                        │
│  ┌──────────────┬──────────────┬────────────────┐               │
│  │ Route Manager│ Alt. Transport│ Autonomous Mgr │               │
│  └──────────────┴──────────────┴────────────────┘               │
│                          │                                        │
│                          ├─────────────────┬────────────────┐    │
│                          ▼                 ▼                ▼    │
│              MQTT: infotainment/*   MQTT: v2v/*   Central DB    │
└──────────────────┬───────────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────────┐
│            Android Infotainment (Frontend - Kotlin)              │
├──────────────────────────────────────────────────────────────────┤
│  • Hazard Alerts          • Alternative Suggestions              │
│  • Reroute Display        • User Selection Interface             │
│  • Autonomous Confirmation • Vehicle Tracking QR Code            │
└──────────────────────────────────────────────────────────────────┘
```

## Implementation Components

### 1. Backend Modules (nav_app/)

#### [`hazard_classifier.py`](nav_app/hazard_classifier.py)
- **Purpose**: Classify ADAS detections and assess severity
- **Input**: Actor tag, visibility, distance, vehicle speed
- **Output**: HazardType, HazardSeverity
- **Logic**:
  - Maps actor tags (police_car, accident, construction) to hazard types
  - Calculates severity based on distance and speed
  - Determines if alternatives should be suggested

#### [`decision_engine.py`](nav_app/decision_engine.py)
- **Purpose**: Core FASLit strategy implementation
- **States**:
  - `UNAFFECTED`: No action needed
  - `APPROACHING`: >500m away → REROUTE (First Avoid)
  - `AFFECTED`: <100m, slow speed → SUGGEST ALTERNATIVES (Second Leave It)
- **Output**: Decision with action, reasoning, confidence

#### [`route_manager.py`](nav_app/route_manager.py)
- **Purpose**: Dynamic route calculation and hazard avoidance
- **Features**:
  - Maintains current route with waypoints
  - Tracks known hazards with expiration
  - Recalculates routes avoiding hazards
  - Estimates delays based on severity

#### [`alternative_transport.py`](nav_app/alternative_transport.py)
- **Purpose**: Generate multi-modal transport suggestions
- **Modes**: Walk, Public Transit, Taxi, Rideshare, Bike
- **Calculates**:
  - Estimated time (based on average speeds)
  - Cost (base + per-km rates)
  - Step-by-step instructions
- **Output**: Sorted list of TransportOptions

#### [`autonomous_manager.py`](nav_app/autonomous_manager.py)
- **Purpose**: Manage vehicle after passenger exits
- **Modes**:
  - `CONTINUE_TO_DESTINATION`: Vehicle continues to original destination
  - `RETURN_HOME`: Vehicle returns to preset home location
  - `PARK_NEARBY`: Find nearby parking
  - `AWAIT_INSTRUCTIONS`: Stay in place
- **Features**:
  - Validates exit requests
  - Generates tracking URLs/QR codes
  - Monitors autonomous session

#### [`central_server.py`](nav_app/central_server.py)
- **Purpose**: V2V communication via central hub
- **Features**:
  - Share hazard detections across vehicle network
  - Report passenger exits (city usage statistics)
  - Receive and process shared hazards from other vehicles
  - Vehicle status broadcasting

#### [`infotainment_publisher.py`](nav_app/infotainment_publisher.py)
- **Purpose**: Backend → Frontend communication
- **Publishes**:
  - Hazard notifications
  - Reroute commands
  - Alternative transport suggestions
  - Autonomous confirmations
  - Screen mode commands
- **Topics**: `infotainment/*`

#### [`subscriber.py`](nav_app/subscriber.py)
- **Purpose**: Main application orchestrator
- **Flow**:
  1. Receives ADAS events from CARLA
  2. Classifies hazards
  3. Makes decision (approaching vs affected)
  4. Executes action (reroute or suggest alternatives)
  5. Publishes to infotainment display
  6. Shares hazards via V2V
  7. Manages passenger exits

### 2. Data Contracts (contract/)

#### [`adas_actor_event.py`](contract/adas_actor_event.py)
- Actor detection from CARLA ADAS
- Fields: actor_tag, is_visible, timestamp, location

#### [`passenger_leaving_event.py`](contract/passenger_leaving_event.py)
- Passenger exit detection
- Fields: timestamp, location

#### [`infotainment_message.py`](contract/infotainment_message.py)
- All frontend communication messages:
  - HazardNotification
  - RerouteNotification
  - AlternativeSuggestion
  - AutonomousConfirmation
  - VehicleStatusUpdate
  - CentralScreenCommand
  - TransportAlternative

### 3. Frontend Integration

See [`INFOTAINMENT_INTEGRATION.md`](INFOTAINMENT_INTEGRATION.md) for complete Android integration guide.

**MQTT Topics for Android:**
- Subscribe to: `infotainment/*` (all 6 topics)
- Publish to: `user/action` (user selections)

## User Scenarios

### Scenario 1: Approaching Driver (FIRST AVOID)

**Situation**: Driver is 600m away from accident

1. **CARLA** detects accident via cameras → publishes `adas_actor_event`
2. **nav_app** receives event
3. **Hazard Classifier**: Type=ACCIDENT, Severity=HIGH
4. **Decision Engine**: State=APPROACHING → Action=REROUTE
5. **Route Manager**: Calculates new route avoiding hazard
6. **Infotainment Publisher**:
   - Publishes hazard notification
   - Publishes reroute with ETA comparison
7. **Android Display**:
   - Shows hazard alert banner
   - Switches to MAP view
   - Displays old ETA (35 min) vs new ETA (32 min)
   - Shows "3 minutes saved"
   - Auto-accepts after 8 seconds
8. **Result**: Driver avoids hazard, arrives faster

### Scenario 2: Affected Driver (SECOND LEAVE IT)

**Situation**: Driver is stuck in traffic jam (5+ minutes at <10 km/h)

1. **CARLA** detects traffic jam
2. **nav_app** receives event + vehicle status (speed < 10 km/h)
3. **Hazard Classifier**: Type=TRAFFIC_JAM, Severity=HIGH
4. **Decision Engine**: State=AFFECTED → Action=SUGGEST_ALTERNATIVES
5. **Alternative Transport Suggester**: Generates 4 options:
   - Public Transit: 27 min, $3.50
   - Taxi: 30 min, $15.50
   - Rideshare: 32 min, $12.00
   - Walk: 50 min, $0
6. **Comparison**: Staying = 55 min (35 min ETA + 20 min delay)
7. **Infotainment Publisher**: Publishes alternatives
8. **Android Display**:
   - Switches to ALTERNATIVES screen
   - Shows 3 best options with icons, times, costs
   - "Choose" button for each
   - 60-second countdown
9. **User Action**: Taps "Choose" on Public Transit
10. **Android**: Publishes user selection to `user/action`
11. **nav_app**:
    - Receives selection
    - Creates PassengerExitRequest
    - Initiates autonomous session (mode: RETURN_HOME)
12. **Infotainment Publisher**: Publishes autonomous confirmation
13. **Android Display**:
    - Shows confirmation message
    - Displays QR code for vehicle tracking
    - Shows vehicle will return home at 19:15
14. **Result**:
    - Passenger takes public transit (27 min)
    - Vehicle drives home autonomously
    - Passenger saves 28 minutes vs staying

## V2V Network Sharing

When `vehicle_abc123` detects hazard:

1. Publishes to `v2v/hazards/broadcast`:
```json
{
  "event_id": "uuid",
  "vehicle_id": "vehicle_abc123",
  "hazard_type": "accident",
  "severity": "high",
  "location": [600, 300, 0],
  "timestamp": "2025-09-30T18:30:00"
}
```

2. Other vehicles (`vehicle_xyz789`) subscribe and receive
3. `vehicle_xyz789` checks if hazard affects their route
4. If yes: Reroutes automatically (FIRST AVOID)
5. Result: Prevents multiple vehicles from being affected

## City Analytics

When passengers exit vehicles:

- Publishes to `v2v/passenger_exit`:
```json
{
  "vehicle_id": "vehicle_abc123",
  "exit_location": [500, 250, 0],
  "chosen_transport_mode": "public_transit",
  "autonomous_mode": "return_home",
  "reason": "hazard_avoidance"
}
```

**Use Case**: City coordinators can track:
- How often robo-taxi passengers switch to public transit
- Which hazards cause most exits
- If the robo-taxi service is effective
- Public transit usage patterns during road events

## Running the System

### 1. Start MQTT Broker
```bash
# On shared laptop
mosquitto -v
```

### 2. Update Configuration
```bash
# Edit mqtt_config.json with shared laptop IP
vim mqtt_config.json
```

### 3. Start nav_app (Backend)
```bash
cd /workspace/hello
python -m nav_app.subscriber
```

### 4. Start Android Infotainment (Frontend)
- Open in Android Studio
- Update broker IP in MqttModule.kt
- Run on device

### 5. Start CARLA (on shared laptop)
- CARLA simulation generates ADAS events
- Events published to `adas_actor_event`

## File Structure

```
/workspace/hello/
├── contract/
│   ├── adas_actor_event.py
│   ├── passenger_leaving_event.py
│   ├── adas_actor_monitor_event.py
│   └── infotainment_message.py          # NEW
├── nav_app/
│   ├── __init__.py                      # NEW
│   ├── subscriber.py                    # UPDATED
│   ├── hazard_classifier.py             # NEW
│   ├── decision_engine.py               # NEW
│   ├── route_manager.py                 # NEW
│   ├── alternative_transport.py         # NEW
│   ├── autonomous_manager.py            # NEW
│   ├── central_server.py                # NEW
│   └── infotainment_publisher.py        # NEW
├── mqtt_config.json
├── CLAUDE.md
├── INFOTAINMENT_INTEGRATION.md          # NEW
└── IMPLEMENTATION_SUMMARY.md            # NEW (this file)
```

## Key Design Decisions

### 1. Backend-Frontend Separation
- **Why**: Android team can work independently
- **Benefit**: Clear contracts via MQTT topics
- **Trade-off**: Requires both running for full demo

### 2. Severity-Based Decision Making
- **Why**: Not all hazards require same response
- **Logic**:
  - LOW: Just notify
  - MEDIUM: Monitor, maybe reroute
  - HIGH: Strong reroute or alternatives
  - CRITICAL: Force alternatives/stop
- **Benefit**: Intelligent, context-aware responses

### 3. Distance Thresholds
- **APPROACHING**: >500m (time to reroute)
- **AFFECTED**: <100m (too late to avoid)
- **Why**: Matches real driving scenarios
- **Tunable**: Can adjust based on testing

### 4. Multi-Modal Transport Integration
- **Why**: Matches user story - faster alternatives exist
- **Modes**: Public transit, taxi, rideshare, walk, bike
- **Benefit**: Real-world feasibility
- **Note**: Production would call actual APIs

### 5. V2V via Central Hub
- **Why**: Simpler than true mesh V2V
- **Benefit**: Centralized analytics
- **Trade-off**: Single point of failure
- **Production**: Would use both (mesh + hub)

## Demo Recommendations

### Setup
1. Two laptops side-by-side
2. Left: CARLA + nav_app output (terminal)
3. Right: Android infotainment (large display)
4. Both connected to same WiFi

### Flow
1. **Show normal driving**: Android shows speed, map
2. **Inject hazard**: CARLA detects accident ahead
3. **Show backend**: Terminal shows classification, decision
4. **Show frontend**: Android shows alert banner
5. **Scenario 1**: If approaching → show reroute with map
6. **Scenario 2**: If affected → show alternatives screen
7. **User selects**: Tap public transit on Android
8. **Show confirmation**: QR code, autonomous mode
9. **Show V2V**: Another vehicle receives shared hazard
10. **Show analytics**: Terminal shows passenger exit event

### Talking Points
- "This is First Avoid - we reroute before you get stuck"
- "This is Second Leave It - we find you faster alternatives when stuck"
- "Vehicle becomes autonomous - takes itself home"
- "Other vehicles learn from your hazard detection"
- "City gets data on robo-taxi effectiveness"

## Future Enhancements

1. **Machine Learning**: Train model on hazard patterns
2. **Real APIs**: Integrate Google Maps, Uber API, transit APIs
3. **Weather Integration**: Factor weather into severity
4. **Historical Data**: Learn which hazards cause most delays
5. **Cost Optimization**: Consider fuel cost vs alternative cost
6. **Route Preferences**: Learn user's preferred alternatives
7. **Multi-Vehicle Coordination**: Group passengers for rideshares

## Success Metrics

### For Hackathon Demo
- ✅ Both scenarios working end-to-end
- ✅ Android display updates in real-time
- ✅ Clear visual distinction between scenarios
- ✅ V2V sharing demonstrated
- ✅ Autonomous handoff shown

### For Production
- Time saved per driver
- Reduction in traffic congestion
- Adoption rate of alternatives
- Cost savings vs staying in vehicle
- User satisfaction scores

## Team Tide 🌊

**Innovation**: Transform unavoidable delays into solvable problems
**Impact**: Individual time savings + societal congestion reduction
**Feasibility**: Built on existing technologies (CARLA, MQTT, Android, Ankaios)

---

*"First Avoid, Second Leave it there" - Don't just navigate around problems, give drivers the power to leave them behind.* 🚗→🚶→🚇
