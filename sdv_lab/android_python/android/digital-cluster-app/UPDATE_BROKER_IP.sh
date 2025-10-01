#!/bin/bash
# Script to update MQTT broker IP in Android app

echo "======================================================================"
echo "FASLit Android Infotainment - Update MQTT Broker IP"
echo "======================================================================"
echo ""

# Get the broker IP from user
read -p "Enter team laptop IP address (e.g., 192.168.1.100): " BROKER_IP

if [ -z "$BROKER_IP" ]; then
    echo "❌ Error: No IP address provided"
    exit 1
fi

# Validate IP format (basic check)
if ! [[ $BROKER_IP =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ Error: Invalid IP address format"
    exit 1
fi

echo ""
echo "Updating broker IP to: $BROKER_IP"

# Path to MqttClusterBinder.kt
FILE="app/src/main/java/com/example/digitalclusterapp/core/data/remote/remote/mqtt/MqttClusterBinder.kt"

if [ ! -f "$FILE" ]; then
    echo "❌ Error: $FILE not found"
    echo "   Make sure you run this script from the digital-cluster-app directory"
    exit 1
fi

# Create backup
cp "$FILE" "$FILE.backup"
echo "✓ Created backup: $FILE.backup"

# Update the IP address
sed -i "s/private const val BROKER_HOST = \".*\"/private const val BROKER_HOST = \"$BROKER_IP\"/" "$FILE"

# Verify the change
if grep -q "BROKER_HOST = \"$BROKER_IP\"" "$FILE"; then
    echo "✓ Successfully updated broker IP to: $BROKER_IP"
    echo ""
    echo "======================================================================"
    echo "Next Steps:"
    echo "======================================================================"
    echo "1. Open Android Studio"
    echo "2. Build > Clean Project"
    echo "3. Build > Rebuild Project"
    echo "4. Run > Run 'app'"
    echo ""
    echo "Check Logcat for:"
    echo "  ✓ Subscribed to nav_app: infotainment/hazard"
    echo "  ✓ Subscribed to nav_app: infotainment/reroute"
    echo "  ..."
    echo "======================================================================"
else
    echo "❌ Error: Failed to update broker IP"
    echo "   Restoring backup..."
    mv "$FILE.backup" "$FILE"
    exit 1
fi
