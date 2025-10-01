# Android Infotainment Setup Guide

## 🎯 Quick Setup

Your team laptop IP: **192.168.41.250** ✅

### Step 1: Update Android App

**Option A: Use Script (Easiest)**
```bash
cd sdv_lab/android_python/android/digital-cluster-app
./UPDATE_BROKER_IP.sh
# Enter: 192.168.41.250 when prompted
```

**Option B: Manual Edit**

Edit `app/src/main/java/com/example/digitalclusterapp/core/data/remote/remote/mqtt/MqttClusterBinder.kt`

Line 48, change:
```kotlin
private const val BROKER_HOST = "10.0.2.2"
```

To:
```kotlin
private const val BROKER_HOST = "192.168.41.250"
```

### Step 2: Build Android App

In Android Studio:
```
Build > Clean Project
Build > Rebuild Project
Run > Run 'app'
```

### Step 3: Start nav_app Backend

On your laptop (already updated with correct IP):

```bash
cd /workspace/hello
python -m nav_app.subscriber
```

You should see:
```
🚗 FASLit Navigation System Initialized
Vehicle ID: vehicle_abc12345
[FASLit] Connected to MQTT broker at 192.168.41.250:1883
[FASLit] Infotainment display integration ready
```

### Step 4: Verify Connection

**Check Android Logcat:**

Filter: `MqttClusterBinder`

You should see:
```
Connected successfully to MQTT broker
✓ Subscribed to: vehicle/parameters
✓ Subscribed to nav_app: infotainment/hazard
✓ Subscribed to nav_app: infotainment/reroute
✓ Subscribed to nav_app: infotainment/alternatives
✓ Subscribed to nav_app: infotainment/autonomous
✓ Subscribed to nav_app: infotainment/status
✓ Subscribed to nav_app: infotainment/screen_command
```

## 🧪 Testing

### Send Test Hazard

```bash
mosquitto_pub -h 192.168.41.250 -t "adas_actor_event" -m '{
  "actor_tag": "accident",
  "is_visible": true,
  "timestamp": "2025-09-30T19:00:00",
  "location": [600.0, 300.0, 0.0]
}'
```

**Android Logcat should show:**
```
Nav_app message received - Type: hazard_notification
🚨 HAZARD: ⚠️ Hazard Detected - Accident detected 600m ahead (Severity: high)
🔄 REROUTE: Route Updated - Old: 35min, New: 32min, Saved: 3min
```

### Test with CARLA

Once CARLA is running on team laptop:
1. CARLA detects hazard via cameras
2. Publishes to `adas_actor_event`
3. nav_app receives → makes decision
4. nav_app publishes to `infotainment/*`
5. Android receives and logs messages

## 📱 What the Android App Does Now

### ✅ Backend Integration Complete

The Android app now:
1. ✅ Connects to MQTT broker at team laptop IP
2. ✅ Subscribes to 6 nav_app topics
3. ✅ Receives hazard alerts
4. ✅ Receives reroute notifications
5. ✅ Receives alternative transport suggestions
6. ✅ Receives autonomous confirmations
7. ✅ Logs all messages to Logcat
8. ✅ Exposes `navAppMessage` StateFlow for UI

### 🚧 UI Display (Next Step)

Currently, messages are:
- ✅ Received and parsed
- ✅ Logged to Logcat
- ❌ Not yet displayed on screen

**To display on screen**, the Android team needs to:
1. Create composables for each message type
2. Wire `navAppMessage` flow to UI
3. Add screen transitions

See: [`FASLIT_INTEGRATION.md`](sdv_lab/android_python/android/digital-cluster-app/FASLIT_INTEGRATION.md)

## 🔍 Message Types You'll Receive

### 1. Hazard Notification
When nav_app detects hazard, you'll see in Logcat:
```
🚨 HAZARD: ⚠️ Hazard Detected - Accident detected 600m ahead (Severity: high)
```

### 2. Reroute (FIRST AVOID)
When approaching vehicle needs reroute:
```
🔄 REROUTE: Route Updated - Old: 35min, New: 32min, Saved: 3min
```

### 3. Alternatives (SECOND LEAVE IT)
When affected vehicle gets alternatives:
```
🚶 ALTERNATIVES: Alternative Options Available - 3 options available
```

### 4. Autonomous Confirmation
When passenger exits vehicle:
```
🤖 AUTONOMOUS: Autonomous Mode Active - Mode: return_home
```

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Team Laptop                              │
│  IP: 192.168.41.250                                         │
│                                                             │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────────┐ │
│  │   CARLA     │──→│ MQTT Broker  │←──│    Android      │ │
│  │ Simulator   │   │  (mosquitto) │   │  Infotainment   │ │
│  └─────────────┘   └───────┬──────┘   └─────────────────┘ │
│                            │                                │
└────────────────────────────┼────────────────────────────────┘
                             │
                             │ MQTT Topics
                             │
┌────────────────────────────┼────────────────────────────────┐
│                  Your Laptop                                │
│                                                             │
│  ┌──────────────────────────────────────────┐              │
│  │         nav_app (Python Backend)         │              │
│  ├──────────────────────────────────────────┤              │
│  │ • Receives: adas_actor_event             │              │
│  │ • Classifies hazards                     │              │
│  │ • Makes decisions (FIRST AVOID / SECOND LEAVE IT)       │
│  │ • Publishes: infotainment/*              │              │
│  └──────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

## ✅ Checklist

Before demo:

- [x] Team laptop IP known: `192.168.41.250`
- [x] mqtt_config.json updated (nav_app)
- [ ] Android app BROKER_HOST updated
- [ ] Android app built and running
- [ ] nav_app running and connected
- [ ] Android Logcat shows subscriptions
- [ ] Test message sent and received
- [ ] CARLA integration tested

## 🎬 Demo Flow

1. **Show Android app running** - Normal cluster display
2. **CARLA detects hazard** - Camera sees accident
3. **nav_app receives** - Terminal shows classification
4. **nav_app decides** - "FIRST AVOID" or "SECOND LEAVE IT"
5. **Android receives** - Logcat shows messages
6. **Display updates** - (Once UI is implemented)

## 🆘 Troubleshooting

### Android not receiving messages

```bash
# Check MQTT broker is accessible
mosquitto_sub -h 192.168.41.250 -t "infotainment/#" -v

# Check nav_app is publishing
# (Should see messages in terminal above)
```

### nav_app connection refused

Check:
1. Is MQTT broker running on team laptop?
2. Is firewall allowing port 1883?
3. Are both devices on same network?

```bash
# On team laptop, allow MQTT port
sudo ufw allow 1883/tcp

# Test connectivity
ping 192.168.41.250
```

### Android Logcat empty

Check:
1. Logcat filter is `MqttClusterBinder`
2. App has been rebuilt after IP change
3. Connection logs appear at app startup

## 📚 Documentation

- **[FASLIT_INTEGRATION.md](sdv_lab/android_python/android/digital-cluster-app/FASLIT_INTEGRATION.md)** - Android integration details
- **[INFOTAINMENT_INTEGRATION.md](INFOTAINMENT_INTEGRATION.md)** - Complete integration guide
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Full system overview

---

**Status: Android backend integration complete! ✅**

Next: Build UI to display nav_app messages on screen.

You can test the integration right now by:
1. Starting nav_app
2. Running Android app
3. Watching Logcat for nav_app messages

The messages are coming through - they just need to be displayed! 🚀
