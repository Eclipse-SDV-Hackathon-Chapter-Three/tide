import json
from contract.mqtt.client import CLIENT
from contract.mqtt.topics import Topics

def update_notification_message(message: str):
    """
    Sends a message to the frontend to update the notification UI.

    :param message: The notification message to display.
    """
    print(f"Publishing topic {Topics.FRONTEND_NOTIFICATION_UPDATE} with {message}")
    payload_str = json.dumps({
        "notificationMessage": message
    })
    CLIENT.publish(Topics.FRONTEND_NOTIFICATION_UPDATE, payload_str)