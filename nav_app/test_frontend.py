#!/usr/bin/env python3
"""
Simple Terminal-based Frontend for Testing FASLit Nav-App
Displays messages from nav_app and allows user interaction testing.
"""
import json
import sys
from datetime import datetime
from typing import Optional
import paho.mqtt.client as mqtt
from dataclasses import dataclass


@dataclass
class DisplayConfig:
    """Configuration for terminal display colors and formatting"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Colors
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    # Backgrounds
    BG_RED = "\033[101m"
    BG_YELLOW = "\033[103m"
    BG_BLUE = "\033[104m"


class TestFrontend:
    """Simple terminal-based frontend for testing nav_app integration"""

    def __init__(self, config_path: str = "mqtt_config.json"):
        """Initialize test frontend"""

        # Load configuration
        with open(config_path) as f:
            config = json.load(f)

        self.broker = config["broker"]
        self.port = config["port"]
        self.keepalive = config.get("keepalive", 60)

        # MQTT client
        self.mqtt_client = mqtt.Client(client_id="test_frontend")
        self.mqtt_client.on_message = self._on_message
        self.mqtt_client.on_connect = self._on_connect

        # Infotainment topics (from nav_app)
        self.INFOTAINMENT_TOPICS = [
            "infotainment/hazard",
            "infotainment/reroute",
            "infotainment/alternatives",
            "infotainment/autonomous",
            "infotainment/status",
            "infotainment/screen_command"
        ]

        # Topic for sending user actions back
        self.USER_ACTION_TOPIC = "user/action"

        # Current displayed alternatives (for user selection)
        self.current_alternatives = []

        # Display config
        self.display = DisplayConfig()

    def start(self):
        """Start the test frontend"""
        self._print_header()

        # Connect to MQTT broker
        print(f"\n{self.display.CYAN}Connecting to MQTT broker at {self.broker}:{self.port}...{self.display.RESET}")
        self.mqtt_client.connect(self.broker, self.port, self.keepalive)

        # Subscribe to all infotainment topics
        for topic in self.INFOTAINMENT_TOPICS:
            self.mqtt_client.subscribe(topic)

        print(f"{self.display.GREEN}✓ Subscribed to all infotainment topics{self.display.RESET}\n")

        # Start listening
        self._print_ready()
        self.mqtt_client.loop_forever()

    def _print_header(self):
        """Print application header"""
        print("\n" + "="*80)
        print(f"{self.display.BOLD}{self.display.CYAN}FASLit Nav-App Test Frontend{self.display.RESET}")
        print(f"{self.display.DIM}Terminal-based display for testing navigation application messages{self.display.RESET}")
        print("="*80)

    def _print_ready(self):
        """Print ready message"""
        print(f"\n{self.display.GREEN}{self.display.BOLD}🚗 FRONTEND READY{self.display.RESET}")
        print(f"{self.display.DIM}Waiting for messages from nav_app...{self.display.RESET}\n")
        print("-"*80 + "\n")

    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            print(f"{self.display.GREEN}✓ Connected to MQTT broker{self.display.RESET}")
        else:
            print(f"{self.display.RED}✗ Connection failed with code {rc}{self.display.RESET}")

    def _on_message(self, client, userdata, message):
        """Handle incoming messages"""
        try:
            data = json.loads(message.payload.decode())
            message_type = data.get("message_type", "unknown")

            # Route to appropriate display handler
            if message_type == "hazard_notification":
                self._display_hazard(data)
            elif message_type == "reroute_notification":
                self._display_reroute(data)
            elif message_type == "alternative_suggestion":
                self._display_alternatives(data)
            elif message_type == "autonomous_confirmation":
                self._display_autonomous(data)
            elif message_type == "vehicle_status":
                self._display_status(data)
            elif message_type == "screen_command":
                self._display_screen_command(data)
            else:
                print(f"{self.display.YELLOW}Unknown message type: {message_type}{self.display.RESET}")

        except Exception as e:
            print(f"{self.display.RED}Error processing message: {e}{self.display.RESET}")

    def _display_hazard(self, data: dict):
        """Display hazard notification"""
        severity = data.get("severity", "medium")

        # Choose color based on severity
        if severity == "critical":
            color = self.display.RED
            bg = self.display.BG_RED
        elif severity == "high":
            color = self.display.YELLOW
            bg = self.display.BG_YELLOW
        else:
            color = self.display.BLUE
            bg = self.display.BG_BLUE

        print(f"\n{bg}{self.display.BOLD} HAZARD ALERT {self.display.RESET}")
        print(f"{color}{self.display.BOLD}{data.get('title', 'Hazard Detected')}{self.display.RESET}")
        print(f"{color}├─ Type: {data.get('hazard_type', 'unknown')}{self.display.RESET}")
        print(f"{color}├─ Severity: {severity.upper()}{self.display.RESET}")
        print(f"{color}├─ Distance: {data.get('distance_meters', 0):.0f}m{self.display.RESET}")
        print(f"{color}└─ {data.get('description', 'No description')}{self.display.RESET}")
        print(f"{self.display.DIM}Time: {self._format_time(data.get('timestamp'))}{self.display.RESET}\n")
        print("-"*80 + "\n")

    def _display_reroute(self, data: dict):
        """Display reroute notification"""
        print(f"\n{self.display.BG_BLUE}{self.display.BOLD} REROUTE NOTIFICATION {self.display.RESET}")
        print(f"{self.display.CYAN}{self.display.BOLD}{data.get('title', 'Route Updated')}{self.display.RESET}")
        print(f"{self.display.CYAN}├─ Reason: {data.get('reason', 'hazard')}{self.display.RESET}")
        print(f"{self.display.CYAN}├─ Old ETA: {data.get('old_eta_minutes', 0)} minutes{self.display.RESET}")
        print(f"{self.display.CYAN}├─ New ETA: {data.get('new_eta_minutes', 0)} minutes{self.display.RESET}")

        time_saved = data.get('time_saved_minutes', 0)
        if time_saved > 0:
            print(f"{self.display.GREEN}└─ ✓ Time Saved: {time_saved} minutes{self.display.RESET}")
        elif time_saved < 0:
            print(f"{self.display.YELLOW}└─ ⚠ Additional Time: {abs(time_saved)} minutes{self.display.RESET}")
        else:
            print(f"{self.display.CYAN}└─ Same ETA{self.display.RESET}")

        if data.get('auto_accept', True):
            print(f"{self.display.GREEN}{self.display.BOLD}✓ REROUTE AUTO-ACCEPTED{self.display.RESET}")

        print(f"{self.display.DIM}Time: {self._format_time(data.get('timestamp'))}{self.display.RESET}\n")
        print("-"*80 + "\n")

    def _display_alternatives(self, data: dict):
        """Display alternative transportation suggestions"""
        print(f"\n{self.display.BG_YELLOW}{self.display.BOLD} ALTERNATIVE OPTIONS {self.display.RESET}")
        print(f"{self.display.YELLOW}{self.display.BOLD}{data.get('title', 'Alternatives Available')}{self.display.RESET}")
        print(f"{self.display.YELLOW}{data.get('description', '')}{self.display.RESET}")
        print(f"{self.display.YELLOW}├─ Current ETA in vehicle: {data.get('current_eta_minutes', 0)} minutes{self.display.RESET}")
        print(f"{self.display.YELLOW}└─ Estimated delay: {data.get('delay_estimate_minutes', 0)} minutes{self.display.RESET}\n")

        alternatives = data.get("alternatives", [])
        self.current_alternatives = alternatives  # Store for user selection

        print(f"{self.display.BOLD}Available Alternatives:{self.display.RESET}\n")

        for i, alt in enumerate(alternatives, 1):
            mode = alt.get('mode', 'unknown')
            time = alt.get('estimated_time_minutes', 0)
            cost = alt.get('estimated_cost', 0)
            distance = alt.get('distance_km', 0)

            # Color based on mode
            if mode == "walk":
                mode_color = self.display.GREEN
                icon = "🚶"
            elif mode == "public_transit":
                mode_color = self.display.BLUE
                icon = "🚌"
            elif mode in ["taxi", "rideshare"]:
                mode_color = self.display.YELLOW
                icon = "🚕"
            else:
                mode_color = self.display.WHITE
                icon = "🚗"

            print(f"{mode_color}{self.display.BOLD}{i}. {icon} {mode.upper().replace('_', ' ')}{self.display.RESET}")
            print(f"   ├─ Time: {time} minutes")
            print(f"   ├─ Cost: ${cost:.2f}")
            print(f"   ├─ Distance: {distance:.1f} km")
            print(f"   └─ {alt.get('description', '')}")

            # Show instructions if available
            instructions = alt.get('instructions', [])
            if instructions:
                print(f"   {self.display.DIM}Steps:{self.display.RESET}")
                for step in instructions[:2]:  # Show first 2 steps
                    print(f"   {self.display.DIM}   • {step}{self.display.RESET}")
            print()

        print(f"{self.display.MAGENTA}{self.display.BOLD}► USER ACTION REQUIRED{self.display.RESET}")
        print(f"{self.display.MAGENTA}Select an option (1-{len(alternatives)}) or press Enter to stay in vehicle{self.display.RESET}")

        # Simulate user selection (in real app, this would be from touch input)
        print(f"{self.display.DIM}[Simulated: Auto-selecting option 1 after 3 seconds...]{self.display.RESET}\n")

        print(f"{self.display.DIM}Time: {self._format_time(data.get('timestamp'))}{self.display.RESET}\n")
        print("-"*80 + "\n")

    def _display_autonomous(self, data: dict):
        """Display autonomous mode confirmation"""
        print(f"\n{self.display.BG_BLUE}{self.display.BOLD} AUTONOMOUS MODE ACTIVE {self.display.RESET}")
        print(f"{self.display.CYAN}{self.display.BOLD}{data.get('title', 'Autonomous Mode')}{self.display.RESET}")
        print(f"{self.display.CYAN}{data.get('description', '')}{self.display.RESET}\n")

        print(f"{self.display.GREEN}✓ Transport chosen: {data.get('chosen_transport_mode', 'unknown')}{self.display.RESET}")
        print(f"{self.display.GREEN}✓ Vehicle mode: {data.get('autonomous_mode', 'unknown').replace('_', ' ')}{self.display.RESET}")

        dest = data.get('vehicle_destination', [0, 0, 0])
        print(f"{self.display.GREEN}✓ Vehicle destination: ({dest[0]:.1f}, {dest[1]:.1f}){self.display.RESET}")

        arrival = data.get('estimated_arrival_time', 'unknown')
        print(f"{self.display.GREEN}✓ Estimated arrival: {arrival}{self.display.RESET}")

        tracking_url = data.get('tracking_url', '')
        if tracking_url:
            print(f"\n{self.display.CYAN}📱 Track your vehicle: {tracking_url}{self.display.RESET}")

        print(f"\n{self.display.BOLD}🤖 Your vehicle will now drive itself{self.display.RESET}")
        print(f"{self.display.DIM}Time: {self._format_time(data.get('timestamp'))}{self.display.RESET}\n")
        print("-"*80 + "\n")

    def _display_status(self, data: dict):
        """Display vehicle status update (compact format)"""
        speed = data.get('current_speed', 0)
        location = data.get('current_location', [0, 0, 0])
        has_passenger = data.get('has_passenger', True)
        autonomous = data.get('autonomous_active', False)

        # Only show significant status changes
        status_icon = "🤖" if autonomous else "👤"
        mode = "AUTONOMOUS" if autonomous else "MANUAL"

        print(f"{self.display.DIM}[STATUS] {status_icon} {mode} | "
              f"Speed: {speed:.0f} km/h | "
              f"Location: ({location[0]:.0f}, {location[1]:.0f}) | "
              f"Passenger: {'Yes' if has_passenger else 'No'}{self.display.RESET}")

    def _display_screen_command(self, data: dict):
        """Display screen command"""
        screen_state = data.get('screen_state', 'UNKNOWN')
        screen_data = data.get('data', {})

        print(f"{self.display.MAGENTA}[SCREEN] Switching to: {screen_state}{self.display.RESET}")
        if screen_data:
            print(f"{self.display.DIM}  Data: {screen_data}{self.display.RESET}")

    def _format_time(self, timestamp_str: Optional[str]) -> str:
        """Format timestamp for display"""
        if not timestamp_str:
            return "unknown"

        try:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return dt.strftime("%H:%M:%S")
        except:
            return timestamp_str

    def send_user_action(self, action: str, data: dict):
        """Send user action back to nav_app"""
        payload = {
            "action": action,
            "data": data
        }

        self.mqtt_client.publish(self.USER_ACTION_TOPIC, json.dumps(payload))
        print(f"{self.display.GREEN}✓ Sent user action: {action}{self.display.RESET}")

    def select_alternative(self, transport_mode: str, autonomous_mode: str = "return_home"):
        """Simulate user selecting an alternative transport option"""
        self.send_user_action("select_alternative", {
            "transport_mode": transport_mode,
            "autonomous_mode": autonomous_mode
        })

    def accept_reroute(self):
        """Simulate user accepting reroute"""
        self.send_user_action("accept_reroute", {})

    def dismiss_alert(self):
        """Simulate user dismissing alert"""
        self.send_user_action("dismiss_alert", {})


def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("FASLit Nav-App Test Frontend")
    print("="*80)
    print("This tool will display messages from your nav_app in real-time.")
    print("Make sure your nav_app is running and connected to the same MQTT broker.")
    print("="*80)

    try:
        frontend = TestFrontend()
        frontend.start()
    except KeyboardInterrupt:
        print("\n\n[Frontend] Shutting down...")
        print("[Frontend] Goodbye!")
    except Exception as e:
        print(f"\n[Frontend] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
