"""
Infotainment Display Simulator
Simulates the Android infotainment display for testing without actual Android device.
Shows what messages nav_app is sending to the infotainment display.
Allows sending user actions back to nav_app.
"""
import json
import threading
from datetime import datetime
import paho.mqtt.client as mqtt


class InfotainmentSimulator:
    """Simulates Android infotainment display via terminal output"""

    def __init__(self, broker: str, port: int):
        self.broker = broker
        self.port = port
        self.client = mqtt.Client(client_id="infotainment_simulator")
        self.client.on_message = self._on_message
        self.client.on_connect = self._on_connect

        self.TOPICS = [
            "infotainment/hazard",
            "infotainment/reroute",
            "infotainment/alternatives",
            "infotainment/autonomous",
            "infotainment/status",
            "infotainment/screen_command"
        ]

        self.USER_ACTION_TOPIC = "user/action"
        self.current_alternatives = []  # Store current alternatives for selection

    def start(self):
        """Start the simulator"""
        print("\n" + "="*80)
        print("🖥️  INFOTAINMENT DISPLAY SIMULATOR")
        print("="*80)
        print(f"Connecting to MQTT broker: {self.broker}:{self.port}")
        print("Simulating what will appear on Android infotainment screen...")
        print("="*80 + "\n")

        try:
            self.client.connect(self.broker, self.port, keepalive=60)

            # Start user input thread
            input_thread = threading.Thread(target=self._user_input_loop, daemon=True)
            input_thread.start()

            self.client.loop_forever()
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("\nMake sure MQTT broker is running:")
            print(f"  mosquitto -v")

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"✅ Connected to MQTT broker")
            for topic in self.TOPICS:
                self.client.subscribe(topic)
                print(f"✅ Subscribed to: {topic}")
            print("\n" + "="*80)
            print("📺 WAITING FOR NAV_APP MESSAGES...")
            print("="*80 + "\n")
        else:
            print(f"❌ Connection failed with code {rc}")

    def _on_message(self, client, userdata, message):
        try:
            data = json.loads(message.payload.decode())
            message_type = data.get("message_type", "unknown")

            if message_type == "hazard_notification":
                self._display_hazard(data)
            elif message_type == "reroute_notification":
                self._display_reroute(data)
            elif message_type == "alternative_suggestion":
                self._display_alternatives(data)
            elif message_type == "autonomous_confirmation":
                self._display_autonomous(data)
            elif message_type == "screen_command":
                self._display_screen_command(data)
            elif message_type == "vehicle_status":
                pass  # Silent - too frequent

        except Exception as e:
            print(f"Error: {e}")

    def _display_hazard(self, data: dict):
        severity = data.get("severity", "unknown")
        border = "🔴" if severity == "critical" else "🟡" if severity == "high" else "🟢"

        print("\n" + "▓"*80)
        print(f"{border} HAZARD ALERT {border}")
        print("▓"*80)
        print(f"  Title: {data.get('title', '')}")
        print(f"  {data.get('description', '')}")
        print(f"  Type: {data.get('hazard_type', '')} | Severity: {severity.upper()}")
        print(f"  Distance: {data.get('distance_meters', 0):.0f}m ahead")
        print("▓"*80 + "\n")

    def _display_reroute(self, data: dict):
        print("\n" + "="*80)
        print("🔄 ROUTE UPDATED (FIRST AVOID)")
        print("="*80)
        print(f"  {data.get('title', '')}")
        print(f"  {data.get('description', '')}")
        print()
        print(f"  📊 ETA COMPARISON:")
        print(f"     Old Route: {data.get('old_eta_minutes', 0)} minutes")
        print(f"     New Route: {data.get('new_eta_minutes', 0)} minutes")
        print(f"     ✅ TIME SAVED: {data.get('time_saved_minutes', 0)} minutes")
        print()
        print(f"  Reason: {data.get('reason', '')}")
        if data.get('auto_accept'):
            print(f"  ⏱  Auto-accepting in 8 seconds...")
        print("="*80 + "\n")

    def _display_alternatives(self, data: dict):
        # Store alternatives for user selection
        self.current_alternatives = data.get('alternatives', [])

        print("\n" + "="*80)
        print("🚶 ALTERNATIVE OPTIONS (SECOND LEAVE IT)")
        print("="*80)
        print(f"  {data.get('title', '')}")
        print(f"  {data.get('description', '')}")
        print()
        print(f"  ⏱  TIME COMPARISON:")
        print(f"     Staying in vehicle: ~{data.get('current_eta_minutes', 0) + data.get('delay_estimate_minutes', 0)} minutes")

        alternatives = data.get('alternatives', [])
        if alternatives:
            print(f"     Best alternative: ~{alternatives[0].get('estimated_time_minutes', 0)} minutes")

        print()
        print(f"  📋 ALTERNATIVE OPTIONS:")

        for i, alt in enumerate(alternatives[:3], 1):
            mode_icons = {
                "walk": "🚶",
                "public_transit": "🚌",
                "taxi": "🚕",
                "rideshare": "🚗",
                "bike": "🚲"
            }
            icon = mode_icons.get(alt.get('mode', ''), '•')

            print(f"\n  {i}. {icon} {alt.get('description', '').upper()}")
            print(f"     Time: {alt.get('estimated_time_minutes', 0)} min | Cost: ${alt.get('estimated_cost', 0):.2f}")
            print(f"     Distance: {alt.get('distance_km', 0):.1f} km")
            print(f"     [ CHOOSE OPTION {i} ] - Type '{i}' to select")

        print()
        print(f"  ⏱  Timeout: {data.get('timeout_seconds', 60)} seconds")
        print("  💡 Type 1, 2, or 3 to choose an option")
        print("="*80 + "\n")

    def _display_autonomous(self, data: dict):
        print("\n" + "="*80)
        print("🤖 AUTONOMOUS MODE ACTIVATED")
        print("="*80)
        print(f"  {data.get('title', '')}")
        print(f"  {data.get('description', '')}")
        print()
        print(f"  Transport Mode: {data.get('chosen_transport_mode', '')}")
        print(f"  Vehicle Mode: {data.get('autonomous_mode', '').replace('_', ' ').title()}")
        print()
        arrival = data.get('estimated_arrival_time', '')
        if arrival:
            try:
                dt = datetime.fromisoformat(arrival.replace('Z', '+00:00'))
                print(f"  Estimated Arrival: {dt.strftime('%H:%M')}")
            except:
                print(f"  Estimated Arrival: {arrival}")
        print()
        print(f"  📱 Tracking URL: {data.get('tracking_url', '')}")
        print(f"  (Scan QR code to track vehicle)")
        print("="*80 + "\n")

    def _display_screen_command(self, data: dict):
        screen = data.get('screen_state', '')
        print(f"📺 Screen changed to: {screen}")

    def _user_input_loop(self):
        """Listen for user input to simulate button presses"""
        print("\n💡 INTERACTIVE COMMANDS (type anytime):")
        print("  1, 2, 3  - Choose alternative transport option 1, 2, or 3")
        print("  a        - Accept reroute")
        print("  d        - Dismiss alert")
        print("  c        - Cancel autonomous mode")
        print("  h        - Show this help\n")

        while True:
            try:
                cmd = input().strip().lower()

                if cmd == 'h':
                    print("\n💡 COMMANDS:")
                    print("  1, 2, 3  - Choose alternative transport option")
                    print("  a        - Accept reroute")
                    print("  d        - Dismiss alert")
                    print("  c        - Cancel autonomous mode\n")

                elif cmd in ['1', '2', '3']:
                    idx = int(cmd) - 1
                    if idx < len(self.current_alternatives):
                        alt = self.current_alternatives[idx]
                        self._publish_user_action("select_alternative", {
                            "transport_mode": alt.get('mode', 'walk'),
                            "autonomous_mode": "return_home"
                        })
                        print(f"✅ Selected option {cmd}: {alt.get('description', '')}")
                    else:
                        print(f"❌ Option {cmd} not available")

                elif cmd == 'a':
                    self._publish_user_action("accept_reroute", {})
                    print("✅ Accepted reroute")

                elif cmd == 'd':
                    self._publish_user_action("dismiss_alert", {})
                    print("✅ Dismissed alert")

                elif cmd == 'c':
                    self._publish_user_action("cancel_autonomous", {})
                    print("✅ Cancelled autonomous mode")

            except Exception as e:
                pass  # Ignore errors from input

    def _publish_user_action(self, action: str, data: dict):
        """Publish user action back to nav_app"""
        try:
            payload = {
                "action": action,
                "data": data
            }
            json_payload = json.dumps(payload)
            self.client.publish(self.USER_ACTION_TOPIC, json_payload)
            print(f"📤 Sent user action to nav_app: {action}")
        except Exception as e:
            print(f"❌ Failed to send user action: {e}")


def main():
    # Load config
    try:
        with open("mqtt_config.json") as f:
            config = json.load(f)
        broker = config["broker"]
        port = config["port"]
    except:
        broker = "localhost"
        port = 1883

    print("\n" + "🖥️ " * 40)
    print("INFOTAINMENT DISPLAY SIMULATOR")
    print("Simulates the Android infotainment screen in your terminal")
    print("Shows what nav_app is sending to the Android display")
    print("🖥️ " * 40 + "\n")

    simulator = InfotainmentSimulator(broker, port)

    try:
        simulator.start()
    except KeyboardInterrupt:
        print("\n\n✅ Simulator stopped")
        print("Goodbye! 👋\n")


if __name__ == "__main__":
    main()
