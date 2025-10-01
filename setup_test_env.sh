#!/bin/bash
# Setup script for FASLit testing environment

echo "========================================="
echo "FASLit Testing Environment Setup"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install paho-mqtt pydantic

# Make scripts executable
echo ""
echo "Making scripts executable..."
chmod +x run_test_frontend.sh
chmod +x test_all.sh
chmod +x nav_app/test_frontend.py
chmod +x nav_app/test_simulator.py

# Check MQTT config
echo ""
echo "Checking MQTT configuration..."
if grep -q '"broker": "localhost"' mqtt_config.json; then
    echo "⚠️  MQTT broker is set to 'localhost'"
    echo ""
    echo "For team laptop testing, update mqtt_config.json:"
    echo '  {"broker": "192.168.41.250", "port": 1883}'
    echo ""
else
    echo "✓ MQTT broker configuration looks good"
fi

# Summary
echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Files created:"
echo "  ✓ nav_app/test_frontend.py"
echo "  ✓ nav_app/test_simulator.py"
echo "  ✓ Documentation files"
echo ""
echo "Next steps:"
echo "  1. Update mqtt_config.json with team laptop IP (if needed)"
echo "  2. Run: ./test_all.sh"
echo "  Or manually:"
echo "     Terminal 1: python3 nav_app/subscriber.py"
echo "     Terminal 2: python3 nav_app/test_frontend.py"
echo "     Terminal 3: python3 nav_app/test_simulator.py"
echo ""
echo "Documentation:"
echo "  - START_HERE.md (begin here)"
echo "  - QUICK_TEST.md (quick reference)"
echo "  - TESTING_GUIDE.md (detailed guide)"
echo ""
