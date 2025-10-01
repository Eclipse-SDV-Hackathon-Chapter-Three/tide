#!/bin/bash
# Complete FASLit Testing Script
# Opens 3 terminals and runs the full test suite

echo "========================================="
echo "FASLit Complete Test Setup"
echo "========================================="
echo ""
echo "This script will:"
echo "1. Check MQTT broker configuration"
echo "2. Open 3 terminal windows"
echo "3. Run nav-app, frontend, and simulator"
echo ""

# Check mqtt_config.json
if grep -q '"broker": "localhost"' mqtt_config.json; then
    echo "⚠️  WARNING: mqtt_config.json is set to 'localhost'"
    echo ""
    echo "For team laptop testing, you need:"
    echo '  {"broker": "192.168.41.250", "port": 1883}'
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting. Please update mqtt_config.json first."
        exit 1
    fi
fi

# Check if running on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - use osascript to open new Terminal windows

    # Terminal 1 - Nav-App Backend
    osascript -e 'tell app "Terminal"
        do script "cd /Users/donghyun/All/hello && echo \"Starting Nav-App Backend...\" && python3 nav_app/subscriber.py"
    end tell'

    sleep 2

    # Terminal 2 - Test Frontend
    osascript -e 'tell app "Terminal"
        do script "cd /Users/donghyun/All/hello && echo \"Starting Test Frontend Display...\" && sleep 3 && python3 nav_app/test_frontend.py"
    end tell'

    sleep 2

    # Terminal 3 - Test Simulator
    osascript -e 'tell app "Terminal"
        do script "cd /Users/donghyun/All/hello && echo \"Starting Test Event Simulator...\" && sleep 5 && python3 nav_app/test_simulator.py"
    end tell'

    echo ""
    echo "✓ Opened 3 terminal windows:"
    echo "  1. Nav-App Backend"
    echo "  2. Test Frontend Display"
    echo "  3. Test Event Simulator"
    echo ""
    echo "In Terminal 3, select a test scenario to run."
    echo ""

else
    # Linux or other - provide manual instructions
    echo "Not running on macOS. Please open 3 terminals manually:"
    echo ""
    echo "Terminal 1:"
    echo "  cd /Users/donghyun/All/hello"
    echo "  python3 nav_app/subscriber.py"
    echo ""
    echo "Terminal 2:"
    echo "  cd /Users/donghyun/All/hello"
    echo "  python3 nav_app/test_frontend.py"
    echo ""
    echo "Terminal 3:"
    echo "  cd /Users/donghyun/All/hello"
    echo "  python3 nav_app/test_simulator.py"
    echo ""
fi
