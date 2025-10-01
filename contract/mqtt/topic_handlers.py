from contract.mqtt.topics import Topics
from contract.notification_manager import update_notification_message

TOPIC_HANDLERS: dict = {
    Topics.FRONTEND_NOTIFICATION_UPDATE: lambda payload: update_notification_message(payload)
}