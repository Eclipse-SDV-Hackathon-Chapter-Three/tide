from datetime import datetime
from typing import Tuple
from uuid import uuid4
from pydantic import BaseModel


class AdasActorEvent(BaseModel):
    uuid: uuid4 | None
    actor_tag: str
    is_visible: bool
    timestamp: datetime
    location: Tuple[float, float, float]
