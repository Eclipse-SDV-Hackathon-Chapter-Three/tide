# Quick Start Guide - FASLit Android Test App

## 🚀 Setup (15 minutes with Google Maps)

### Step 1: Open in Android Studio
```bash
# In Android Studio:
File → Open → Select: /workspace/hello/faslit-test-app
```

### Step 2: Get Google Maps API Key ⚠️ REQUIRED

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project → Enable "Maps SDK for Android"
3. Create API key (Credentials → Create Credentials → API key)
4. Copy the API key

**Add to app:**
- Open `app/src/main/AndroidManifest.xml`
- Replace `YOUR_API_KEY_HERE` with your API key

📖 **Detailed guide:** See [GOOGLE_MAPS_SETUP.md](GOOGLE_MAPS_SETUP.md)

### Step 3: Configure Broker (IMPORTANT!)

Edit `app/src/main/java/com/faslit/testapp/MainActivity.kt` line 226:

```kotlin
// For Android Emulator (testing on local machine):
private val BROKER_URL = "tcp://10.0.2.2:1883"

// OR for physical device (replace with your computer IP):
private val BROKER_URL = "tcp://192.168.1.XXX:1883"
```

**Find your computer IP:**
```bash
# Mac/Linux:
ifconfig | grep "inet "

# Windows:
ipconfig
```

### Step 3: Start MQTT Broker

```bash
cd /workspace/hello
mosquitto -v
```

Should see: `Opening ipv4 listen socket on port 1883`

### Step 4: Run Android App

1. Click green ▶ button in Android Studio
2. Select emulator or connected device
3. Wait for app to launch
4. Status should turn **GREEN** (connected)

### Step 5: Test with Simulator

Open new terminal:
```bash
cd /workspace/hello
PYTHONPATH=/workspace/hello pipenv run python3 nav_app/test_simulator.py
```

Watch messages appear in the Android app! 🎉

## 📱 Emulator vs Physical Device

### Using Emulator (Easiest)
- **Pros:** No physical device needed, `10.0.2.2` always works
- **Cons:** Slower performance
- **Broker URL:** `tcp://10.0.2.2:1883`

### Using Physical Device
- **Pros:** Better performance, real-world testing
- **Cons:** Need USB cable, must find computer IP
- **Broker URL:** `tcp://<YOUR_COMPUTER_IP>:1883`

## 🐛 Quick Troubleshooting

### Red Status (Not Connected)
1. Check broker URL is correct
2. Verify mosquitto is running: `ps aux | grep mosquitto`
3. Check firewall allows port 1883
4. For device: ping your computer from device

### No Messages Appearing
1. Check test_simulator.py is running
2. Verify nav_app/subscriber.py is running
3. Check logcat in Android Studio for errors

### Gradle Sync Failed
1. Check internet connection
2. File → Invalidate Caches → Restart
3. Verify JDK 17 is selected in preferences

## 🎯 Expected Behavior

When everything works:
1. ✅ Status card shows **GREEN**
2. ✅ Vehicle state updates with location
3. ✅ Messages scroll automatically
4. ✅ Different colors for different message types

## 🔧 Testing Commands

**Test broker from CLI:**
```bash
# Subscribe to all infotainment messages:
mosquitto_sub -h localhost -t "infotainment/#" -v

# Publish test message:
mosquitto_pub -h localhost -t "infotainment/hazard" -m '{"message_type":"hazard_notification","title":"Test Alert","description":"This is a test","severity":"low"}'
```

If you see the test message in Android app, everything works! ✨

## 📖 Full Documentation

See [README.md](README.md) for detailed information.
