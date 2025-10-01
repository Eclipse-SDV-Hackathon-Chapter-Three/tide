# FASLit Test App - Android Frontend

A simple Android test application for monitoring FASLit navigation system messages in real-time.

## Features

- 📱 Real-time MQTT message monitoring
- 🗺️ **Live map visualization** showing vehicle position and home location
- 🚗 Vehicle state display (location, mode, ETA, passenger status)
- 🚨 Visual alerts for hazards, reroutes, and alternatives
- 🎨 Modern Material 3 UI with dark theme
- 🔄 Auto-scrolling message feed
- ⚡ Color-coded message types

## Requirements

- Android Studio Ladybug (2024.2.1) or newer
- Android SDK 35
- Minimum Android version: 7.0 (API 24)
- JDK 17

## Setup Instructions

### 1. Open Project in Android Studio

1. Launch Android Studio
2. Select **File → Open**
3. Navigate to `/workspace/hello/faslit-test-app`
4. Click **Open**
5. Wait for Gradle sync to complete

### 2. Configure MQTT Broker Address

**IMPORTANT:** Update the broker URL before running the app.

Open `app/src/main/java/com/faslit/testapp/MainActivity.kt` and find this line:

```kotlin
private val BROKER_URL = "tcp://localhost:1883" // Change to your broker IP
```

Change it to:
- **For local testing on emulator:** `tcp://10.0.2.2:1883` (connects to host machine)
- **For physical device:** `tcp://<YOUR_COMPUTER_IP>:1883` (e.g., `tcp://192.168.1.100:1883`)
- **For hackathon shared laptop:** `tcp://192.168.41.250:1883`

### 3. Run the App

#### Option A: Android Emulator (Recommended for Testing)

1. Create a new emulator if needed:
   - Click **Device Manager** in Android Studio
   - Click **Create Virtual Device**
   - Select a device (e.g., Pixel 6)
   - Select Android 14 (API 34) system image
   - Click **Finish**

2. Run the app:
   - Click the green **Run** button (▶) in Android Studio
   - Select your emulator
   - Wait for app to launch

#### Option B: Physical Android Device

1. Enable Developer Mode on your device:
   - Go to **Settings → About Phone**
   - Tap **Build Number** 7 times
   - Go back to **Settings → Developer Options**
   - Enable **USB Debugging**

2. Connect device via USB

3. Run the app:
   - Click the green **Run** button (▶) in Android Studio
   - Select your device
   - Allow USB debugging on device if prompted

### 4. Test with Simulator

Make sure you have the MQTT broker and nav_app running:

**Terminal 1 - Start Mosquitto:**
```bash
cd /workspace/hello
mosquitto -v
```

**Terminal 2 - Start Nav App:**
```bash
cd /workspace/hello
PYTHONPATH=/workspace/hello pipenv run python3 nav_app/subscriber.py
```

**Terminal 3 - Start Test Simulator:**
```bash
cd /workspace/hello
PYTHONPATH=/workspace/hello pipenv run python3 nav_app/test_simulator.py
```

The Android app should now display messages from the simulator in real-time!

## App Features Explained

### Connection Status Card
- **Green:** Connected to MQTT broker
- **Orange:** Connecting...
- **Red:** Disconnected

### Map View
Interactive 2D map showing:
- **Grid:** 500m grid lines for spatial reference
- **Blue vehicle icon:** Current vehicle position (triangle pointing up)
- **Green home icon:** Home location at (1000, 1000)
- **Cyan line:** Path from vehicle to home
- **Map bounds:** -500 to 2500 on X and Y axes
- Updates in real-time as vehicle moves

### Vehicle State Card
Shows real-time vehicle information:
- **Location:** Current X, Y coordinates
- **Mode:** Autonomous driving mode (normal, return_home, continue_to_destination, etc.)
- **Passenger:** Whether passenger is in vehicle
- **ETA:** Estimated time to arrival in minutes

### Message Feed
Real-time stream of infotainment messages with color coding:
- **Red:** Hazard notifications (🚨 accidents, obstacles, police)
- **Orange:** Reroute notifications (🔄 route updates)
- **Blue:** Alternative transport suggestions (🚶 public transit, taxi, walk)
- **Green:** Autonomous mode confirmations (🤖 self-driving actions)
- **Purple:** Screen commands (📺 UI state changes)
- **Gray:** Vehicle status updates (low frequency)

## Troubleshooting

### App won't connect to MQTT

1. **Check broker address:**
   - Emulator: Use `10.0.2.2` to reach host machine
   - Physical device: Use your computer's local IP address
   - Find your IP: `ifconfig` (Mac/Linux) or `ipconfig` (Windows)

2. **Check firewall:**
   - Ensure port 1883 is not blocked
   - On Mac: System Preferences → Security & Privacy → Firewall
   - On Linux: `sudo ufw allow 1883`

3. **Verify broker is running:**
   ```bash
   mosquitto -v
   ```
   Should show "Opening ipv4 listen socket on port 1883"

4. **Test broker from command line:**
   ```bash
   mosquitto_sub -h localhost -t "infotainment/#" -v
   ```

### Gradle sync fails

1. **Check internet connection** (Gradle needs to download dependencies)
2. **Invalidate caches:** File → Invalidate Caches → Invalidate and Restart
3. **Check Java version:** Android Studio → Settings → Build, Execution, Deployment → Build Tools → Gradle → Gradle JDK (should be 17)

### App crashes on startup

1. **Check logcat** in Android Studio for error messages
2. **Verify minimum SDK:** App requires Android 7.0 (API 24) or higher
3. **Clean and rebuild:** Build → Clean Project, then Build → Rebuild Project

## MQTT Topics

The app subscribes to these topics from nav_app:
- `infotainment/hazard` - Hazard notifications
- `infotainment/reroute` - Route change notifications
- `infotainment/alternatives` - Alternative transport suggestions
- `infotainment/autonomous` - Autonomous mode confirmations
- `infotainment/status` - Vehicle status updates
- `infotainment/screen_command` - Screen state commands

## Message Format

All messages follow this JSON format:
```json
{
  "message_type": "hazard_notification",
  "title": "Hazard Ahead",
  "description": "Accident detected 500m ahead",
  "severity": "high",
  "timestamp": "2025-10-01T13:30:00Z"
}
```

## Development Tips

- **Live reload:** Changes to Kotlin code require rebuild (Ctrl+F9)
- **Compose preview:** Use `@Preview` annotations to preview UI in IDE
- **Debugging:** Set breakpoints in `handleMessage()` to inspect incoming messages
- **Logs:** Use Android Studio Logcat to view app logs (filter by "FASLitTestApp")

## Tech Stack

- **Language:** Kotlin
- **UI Framework:** Jetpack Compose with Material 3
- **MQTT Client:** Eclipse Paho Android Service
- **Architecture:** MVVM with StateFlow
- **Coroutines:** kotlinx-coroutines-android

## File Structure

```
faslit-test-app/
├── app/
│   ├── src/main/
│   │   ├── java/com/faslit/testapp/
│   │   │   └── MainActivity.kt          # Main app code
│   │   ├── res/
│   │   │   └── values/
│   │   │       └── strings.xml
│   │   └── AndroidManifest.xml
│   └── build.gradle.kts                  # App dependencies
├── build.gradle.kts                      # Project config
├── settings.gradle.kts                   # Module settings
└── README.md                             # This file
```

## Next Steps

1. ✅ Open in Android Studio
2. ✅ Configure broker URL
3. ✅ Run on emulator or device
4. ✅ Start MQTT broker and nav_app
5. ✅ Watch messages appear in real-time!

## Support

For issues or questions:
- Check the troubleshooting section above
- Review Android Studio Logcat for error messages
- Verify MQTT broker is accessible from your device
- Test MQTT connection with `mosquitto_sub` command

Enjoy testing FASLit! 🚗💨
