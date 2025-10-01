def update_notification_message(payload):
    """
    Updates the notification message based on the payload received.

    Args:
        payload (dict): The payload containing the notification message.
    """
    try:
        notification_message = payload.get("message", "")
        if notification_message:
            print(f"Notification updated: {notification_message}")
        else:
            print("Payload does not contain a valid message.")
    except Exception as e:
        print(f"Error updating notification message: {e}")