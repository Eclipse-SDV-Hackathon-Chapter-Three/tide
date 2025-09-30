from pydantic import BaseModel


class AdasActorMonitorEvent(BaseModel):
    actor_tag: str
    should_monitor: bool
