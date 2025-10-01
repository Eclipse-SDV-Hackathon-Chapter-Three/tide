from contract.mqtt.topic_handlers import TOPIC_HANDLERS
from contract.mqtt.topics import Topics
from nav_app.handlers import handle_vehicle_adas_actor_seen

TOPIC_HANDLERS[Topics.VEHICLE_ADAS_ACTOR_SEEN] = handle_vehicle_adas_actor_seen
