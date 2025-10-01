# Google Maps API Setup Guide

## Overview

The FASLit Test App now uses **Google Maps** to display vehicle location in real-world coordinates. CARLA simulation coordinates are converted to GPS coordinates centered on **Berlin, Germany**.

## Coordinate Mapping

- **CARLA (0, 0)** → **Berlin Center** (52.5200° N, 13.4050° E)
- **CARLA (1000, 1000)** → **Home Location** (~11m north and ~11m east of Berlin center)
- **Scale:** 1 CARLA unit ≈ 0.00001° ≈ 1.1 meters

Example:
- CARLA (500, 500) → GPS (52.5250° N, 13.4100° E)
- Vehicle moves on real Berlin streets!

## Getting a Google Maps API Key

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click **Select a project** → **New Project**
4. Enter project name: "FASLit Test App"
5. Click **Create**

### Step 2: Enable Maps SDK

1. In the search bar, type "Maps SDK for Android"
2. Click **Maps SDK for Android**
3. Click **Enable**
4. Wait for activation (~30 seconds)

### Step 3: Create API Key

1. Go to **Credentials** (left sidebar)
2. Click **Create Credentials** → **API key**
3. Copy the API key (looks like: `AIzaSyB...`)
4. Click **Restrict Key** (recommended for security)

### Step 4: Restrict API Key (Optional but Recommended)

1. **Application restrictions:**
   - Select "Android apps"
   - Click "Add an item"
   - Package name: `com.faslit.testapp`
   - SHA-1 fingerprint: Get from Android Studio (see below)

2. **API restrictions:**
   - Select "Restrict key"
   - Check ✅ **Maps SDK for Android**
   - Click **Save**

### Getting SHA-1 Fingerprint (For Restrictions)

Open terminal in Android Studio and run:

```bash
# Debug certificate (for development)
keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android -keypass android

# Look for "SHA1:" in the output, copy the value
```

## Configure the App

### Method 1: Direct in AndroidManifest.xml (Quick)

1. Open `app/src/main/AndroidManifest.xml`
2. Find this line:
   ```xml
   android:value="YOUR_API_KEY_HERE" />
   ```
3. Replace `YOUR_API_KEY_HERE` with your actual API key:
   ```xml
   android:value="AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" />
   ```
4. **⚠️ Warning:** Don't commit your API key to public repositories!

### Method 2: Using local.properties (Secure)

More secure for version control:

1. Open/create `local.properties` in project root
2. Add your API key:
   ```properties
   MAPS_API_KEY=AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

3. Update `app/build.gradle.kts`:
   ```kotlin
   android {
       defaultConfig {
           // Load API key from local.properties
           val properties = Properties()
           properties.load(project.rootProject.file("local.properties").inputStream())
           manifestPlaceholders["MAPS_API_KEY"] = properties.getProperty("MAPS_API_KEY", "")
       }
   }
   ```

4. Update `AndroidManifest.xml`:
   ```xml
   <meta-data
       android:name="com.google.android.geo.API_KEY"
       android:value="${MAPS_API_KEY}" />
   ```

5. Add to `.gitignore`:
   ```
   local.properties
   ```

## Build and Run

1. **Sync Gradle:**
   - File → Sync Project with Gradle Files

2. **Clean and Rebuild:**
   - Build → Clean Project
   - Build → Rebuild Project

3. **Run on Emulator/Device:**
   - Click ▶ Run button
   - Select device
   - Grant location permissions if prompted

## Expected Result

When the app launches, you should see:
- ✅ **Google Maps** displaying Berlin, Germany
- 🔵 **Blue marker:** Vehicle position (updates in real-time)
- 🟢 **Green marker:** Home location (fixed at CARLA 1000,1000)
- 📍 **Cyan line:** Path from vehicle to home
- 🎮 **Zoom controls:** Zoom in/out buttons
- 🧭 **Compass:** Shows north direction

## Troubleshooting

### "Google Maps Android API" error on screen

**Problem:** API key not configured or invalid

**Solution:**
1. Verify API key is correct in AndroidManifest.xml
2. Check that Maps SDK for Android is enabled in Google Cloud Console
3. Wait a few minutes after enabling (can take time to activate)
4. Make sure no extra spaces in the API key

### Map shows gray screen

**Problem:** API key restrictions or billing not enabled

**Solution:**
1. Check API restrictions allow "Maps SDK for Android"
2. Enable billing in Google Cloud (free tier: $200 credit/month)
3. Remove all restrictions temporarily to test

### "Authorization failure" error

**Problem:** Package name or SHA-1 fingerprint mismatch

**Solution:**
1. Verify package name is exactly: `com.faslit.testapp`
2. Get SHA-1 from debug keystore (command above)
3. Add SHA-1 to API key restrictions
4. Uninstall app and reinstall

### Vehicle marker not appearing

**Problem:** Vehicle state not updating or coordinates invalid

**Solution:**
1. Check MQTT connection (status should be green)
2. Verify test_simulator.py is running and publishing location
3. Check logcat for coordinate conversion messages
4. Default location is (0, 0) = Berlin center

## Free Tier Limits

Google Maps offers generous free tier:
- **$200 credit per month**
- **28,500 map loads/month free**
- **40,000 API calls/month free**

For testing, you'll stay well within limits! 🎉

## Alternative: Using Debug API Key

For quick testing without restrictions:

1. Get API key from Google Cloud Console
2. **Don't restrict it** (skip Step 4 above)
3. Use directly in AndroidManifest.xml
4. ⚠️ **Never deploy to production without restrictions!**

## Map Features

### Camera Controls
- **Zoom:** Pinch to zoom or use +/- buttons
- **Pan:** Drag to move around
- **Rotate:** Two-finger rotate gesture
- **Tilt:** Two-finger drag up/down

### Markers
- **Tap marker:** Shows info window with details
- **Vehicle marker:** Shows CARLA coordinates and mode
- **Home marker:** Shows "Destination"

### Auto-Follow
- Camera automatically follows vehicle as it moves
- Zoom level: 14 (neighborhood view)
- Smooth transitions with LaunchedEffect

## Coordinate Conversion Details

```kotlin
fun carlaToGPS(carlaX: Float, carlaY: Float): LatLng {
    val berlinLat = 52.5200  // Berlin latitude
    val berlinLng = 13.4050  // Berlin longitude
    val scale = 0.00001      // ~1.1 meters per unit

    val lat = berlinLat + (carlaY * scale)
    val lng = berlinLng + (carlaX * scale)

    return LatLng(lat, lng)
}
```

**Examples:**
- (0, 0) → (52.5200, 13.4050)
- (1000, 1000) → (52.5300, 13.4150)
- (2000, -500) → (52.5150, 13.4250)

## Resources

- [Google Maps Platform Documentation](https://developers.google.com/maps/documentation)
- [Maps Compose Library](https://github.com/googlemaps/android-maps-compose)
- [Google Cloud Console](https://console.cloud.google.com/)
- [API Key Best Practices](https://developers.google.com/maps/api-security-best-practices)

## Next Steps

1. ✅ Get API key from Google Cloud Console
2. ✅ Enable Maps SDK for Android
3. ✅ Add API key to AndroidManifest.xml
4. ✅ Rebuild and run the app
5. ✅ Start MQTT broker and simulator
6. ✅ Watch vehicle move on real Berlin streets! 🗺️🚗

Happy mapping! 🎉
