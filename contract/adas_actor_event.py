from datetime import datetime
from typing import Tuple
from pydantic import BaseModel


class AdasActorEvent(BaseModel):
    UUID: str
    actor_tag: str
    is_visible: bool
    timestamp: datetime
    location: Tuple[float, float, float]
