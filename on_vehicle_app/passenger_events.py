
from contract.adas_actor_event import AdasActorEvent


def should_passenger_leave_vehicle(adas_actor_event: AdasActorEvent) -> bool:
    """
    determine if the passenger should leave the vehicle based on the AdasActorEvent
    """
    return False
