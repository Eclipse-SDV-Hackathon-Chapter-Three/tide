# MQTT Configuration Notes

## Important for Claude Code

⚠️ **When helping with this project, please note:**

1. **Shared MQTT Broker**: The team uses a shared MQTT broker at `192.168.41.250:1883`
   - Running on a shared laptop on the team intranet
   - Requires team WiFi connection
   - Cannot be validated/tested from external networks

2. **Assume Broker is Running**: When providing help:
   - Assume the MQTT broker at `192.168.41.250` is accessible
   - Don't try to ping or validate the connection
   - Focus on script logic and MQTT message structure

3. **Graceful Offline Handling**: Scripts are designed to:
   - Work offline (print events locally)
   - Attempt MQTT connection on first publish
   - Show helpful error messages if connection fails
   - Continue running even without MQTT

## Network Setup

```
Developer Laptop          Team Intranet         Shared Laptop
                          WiFi Network
┌──────────────┐         (192.168.41.x)        ┌──────────────┐
│              │              │                 │              │
│ Test Scripts ├──────────────┼────────────────►│ Mosquitto    │
│              │              │                 │ Broker       │
│ - Simulators │              │                 │ :1883        │
│ - nav_app    │              │                 │              │
│              │              │                 └──────────────┘
└──────────────┘              │                 192.168.41.250
                              │
                              ▼
                    All team members'
                    test instances
```

## Connection States

### When on Team WiFi ✅
```
Connecting to MQTT broker at 192.168.41.250:1883...
✅ Connected to broker at 192.168.41.250:1883
📡 Publishing to: vehicle/adas-actor/seen
```

### When Offline or Wrong Network ⚠️
```
⚠️  Note: MQTT not connected - [Errno 111] Connection refused
   (Make sure you're on team WiFi and broker at 192.168.41.250 is running)
   Messages are printed above for visibility.
```

Scripts continue to run and print events locally!

## Publisher Design

All publishers in `on_vehicle_app/publishers.py` follow this pattern:

```python
def publish(topic: str, payload: str):
    # 1. ALWAYS print for visibility (works offline)
    print(payload)

    # 2. Try to connect to MQTT if not connected
    if not IS_INITIALIZED:
        try:
            initialize_mqtt_client()
        except:
            # Print helpful error, continue running
            return

    # 3. Try to publish
    try:
        CLIENT.publish(topic, payload)
    except:
        # Handle gracefully
        pass
```

This ensures:
- ✅ Scripts work offline for local testing
- ✅ Developers can see event data even without MQTT
- ✅ Helpful error messages when connection fails
- ✅ No crashes due to network issues

## Configuration Files

### `mqtt_config.json` (Default - Team Broker)
```json
{
  "broker": "192.168.41.250",
  "port": 1883
}
```
Used by all scripts by default.

### `mqtt_config_local.json` (Optional - Local Testing)
```json
{
  "broker": "localhost",
  "port": 1883
}
```
For local testing with own mosquitto instance.

To switch: `cp mqtt_config_local.json mqtt_config.json`

## When Helping Developers

### DO:
- ✅ Assume broker at 192.168.41.250 is running
- ✅ Focus on MQTT message structure and topics
- ✅ Help with script logic and data flow
- ✅ Explain print output (works offline)

### DON'T:
- ❌ Try to ping or connect to 192.168.41.250
- ❌ Suggest running local mosquitto (unless asked)
- ❌ Assume scripts won't work without MQTT
- ❌ Write code that crashes without broker connection

## Common Scenarios

### Developer Says: "Scripts print but nav_app doesn't receive events"

**Check**:
1. Are both on same WiFi? (Look for ✅ in output)
2. Topics match? (`vehicle/adas-actor/seen`)
3. Both connected to same broker? (192.168.41.250)
4. Any errors in terminal?

### Developer Says: "Continuous ADAS events without running scenarios"

**Likely**:
1. Other team member testing simultaneously
2. Retained messages on broker
3. Previous test still running in background

**Solutions**: See [TEAM_WORKFLOW.md](TEAM_WORKFLOW.md)

### Developer Says: "Connection refused"

**Check**:
1. On team WiFi network?
2. Broker running on shared laptop?
3. Is this expected (testing offline)?

**If offline testing**: That's OK! Scripts print events locally.

## Testing Workflow Summary

```bash
# Developer on team WiFi:
# Terminal 1
python run_vehicle_simulator.py
# → ✅ Connected to broker at 192.168.41.250:1883

# Terminal 2
python -m nav_app.subscriber
# → ✅ Connected to broker at 192.168.41.250:1883

# Terminal 3
python run_mock_scenarios.py
# → ✅ Connected to broker at 192.168.41.250:1883
# → Events published and received!

# Developer NOT on team WiFi:
python test_quick_scenarios.py
# → ⚠️  MQTT not connected
# → Events printed to console (works locally)
```

## Key Files

- **[TEAM_WORKFLOW.md](TEAM_WORKFLOW.md)** - Complete guide for shared broker testing
- **[TESTING.md](TESTING.md)** - Alternative local testing setup
- **[SCENARIOS.md](SCENARIOS.md)** - Scenario descriptions
- **[README_TESTING.md](README_TESTING.md)** - Quick start guide

## For Claude Code

When a user asks about MQTT or testing:

1. **Assume broker is running** at 192.168.41.250
2. **Focus on** message structure, topics, script logic
3. **Remember** scripts work offline (print-first design)
4. **Refer to** [TEAM_WORKFLOW.md](TEAM_WORKFLOW.md) for team testing
5. **Don't try** to validate network connectivity

The scripts are designed to be helpful whether online or offline!
