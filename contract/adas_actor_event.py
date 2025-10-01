from datetime import datetime
from typing import Tuple
from pydantic import BaseModel


class AdasActorEvent(BaseModel):
    actor_tag: str
    is_visible: bool
    timestamp: datetime
    location: Tuple[float, float, float]
    seen_amb: bool
