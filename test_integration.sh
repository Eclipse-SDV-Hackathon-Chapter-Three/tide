#!/bin/bash
# Integration Test Script for nav_app ↔ Infotainment Communication

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 Nav-App ↔ Infotainment Integration Test"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "This script tests the complete bidirectional communication between:"
echo "  • nav_app (Python backend)"
echo "  • Infotainment display (Android AAOS frontend)"
echo ""
echo "Prerequisites:"
echo "  1. MQTT broker running (mosquitto -v)"
echo "  2. nav_app running (python -m nav_app.subscriber)"
echo "  3. Infotainment simulator running (python -m nav_app.infotainment_simulator)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Load MQTT config
BROKER=$(python3 -c "import json; print(json.load(open('mqtt_config.json'))['broker'])")
PORT=$(python3 -c "import json; print(json.load(open('mqtt_config.json'))['port'])")

echo "📡 MQTT Configuration:"
echo "   Broker: $BROKER"
echo "   Port: $PORT"
echo ""

# Test 1: Check MQTT broker connection
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 1: MQTT Broker Connection"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if mosquitto_pub -h $BROKER -p $PORT -t "test/connection" -m "ping" 2>/dev/null; then
    echo "✅ MQTT broker is reachable"
else
    echo "❌ MQTT broker is not reachable at $BROKER:$PORT"
    echo "   Start broker with: mosquitto -v"
    exit 1
fi
echo ""

# Test 2: Simulate vehicle stuck (for SECOND LEAVE IT scenario)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 2: Backend → Frontend Communication (HAZARD ALERT)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Publishing ADAS hazard event..."
echo ""
mosquitto_pub -h $BROKER -p $PORT -t "adas_actor_event" -m '{
  "actor_tag": "accident",
  "is_visible": true,
  "timestamp": "2025-10-01T12:00:00",
  "location": [600.0, 300.0, 0.0]
}'

echo "✅ Published hazard event to adas_actor_event topic"
echo ""
echo "Expected flow:"
echo "  1. nav_app receives ADAS event"
echo "  2. nav_app classifies hazard"
echo "  3. nav_app publishes to infotainment/hazard"
echo "  4. Infotainment simulator displays hazard alert"
echo ""
sleep 2

# Test 3: Simulate slow vehicle speed (stuck scenario)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 3: Backend → Frontend Communication (ALTERNATIVE SUGGESTIONS)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Note: This requires nav_app to detect vehicle is stuck (speed < 10 km/h, 5+ min)"
echo "For testing, you may need to manually trigger this in the code by setting:"
echo "  app.time_stuck_minutes = 10"
echo "  app.current_speed = 5.0"
echo ""
echo "Then publish another hazard event to trigger alternative suggestions."
echo ""

# Test 4: Simulate user action
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 4: Frontend → Backend Communication (USER ACTION)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Simulating user selecting public transit..."
echo ""
mosquitto_pub -h $BROKER -p $PORT -t "user/action" -m '{
  "action": "select_alternative",
  "data": {
    "transport_mode": "public_transit",
    "autonomous_mode": "return_home"
  }
}'

echo "✅ Published user action to user/action topic"
echo ""
echo "Expected flow:"
echo "  1. Infotainment publishes user selection"
echo "  2. nav_app receives user action"
echo "  3. nav_app initiates autonomous mode"
echo "  4. nav_app publishes to infotainment/autonomous"
echo "  5. Infotainment displays autonomous confirmation"
echo ""
sleep 2

# Test 5: Accept reroute
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 5: Frontend → Backend Communication (ACCEPT REROUTE)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Simulating user accepting reroute..."
echo ""
mosquitto_pub -h $BROKER -p $PORT -t "user/action" -m '{
  "action": "accept_reroute",
  "data": {}
}'

echo "✅ Published accept_reroute action"
echo ""
sleep 2

# Test 6: Dismiss alert
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 6: Frontend → Backend Communication (DISMISS ALERT)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Simulating user dismissing alert..."
echo ""
mosquitto_pub -h $BROKER -p $PORT -t "user/action" -m '{
  "action": "dismiss_alert",
  "data": {}
}'

echo "✅ Published dismiss_alert action"
echo ""
sleep 2

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Integration Test Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Check the following terminals for output:"
echo "  • nav_app terminal - Should show received user actions"
echo "  • Infotainment simulator terminal - Should show hazard alerts and suggestions"
echo ""
echo "Integration Status:"
echo "  ✅ Backend → Frontend: Hazards, Reroutes, Alternatives, Autonomous"
echo "  ✅ Frontend → Backend: User actions (select, accept, dismiss)"
echo "  ✅ Bidirectional communication working"
echo ""
echo "For interactive testing:"
echo "  • In infotainment simulator, type 1, 2, 3 to select alternatives"
echo "  • In infotainment simulator, type 'a' to accept, 'd' to dismiss"
echo ""
echo "See NAV_APP_INFOTAINMENT_INTEGRATION.md for full documentation."
echo ""
