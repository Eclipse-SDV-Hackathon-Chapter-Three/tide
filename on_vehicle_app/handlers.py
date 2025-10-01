
from contract.adas_actor_monitor_event import AdasActorMonitorEvent
from on_vehicle_app.constants import ACTORS_BEING_MONITORED

def handle_vehicle_adas_actor_should_monitor(payload: AdasActorMonitorEvent):
    if payload.should_monitor not in ACTORS_BEING_MONITORED:
        ACTORS_BEING_MONITORED.append(payload.actor_tag)
        print(f"Now monitoring actor: {payload.actor_tag}")
    else:
        ACTORS_BEING_MONITORED.remove(payload.actor_tag)
        print(f"Stopped monitoring actor: {payload.actor_tag}")
