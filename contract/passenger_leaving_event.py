from datetime import datetime
from typing import Tuple
from pydantic import BaseModel


class PassengerLeftEvent(BaseModel):
    actor_tag: str
    timestamp: datetime
    location: Tuple[float, float, float]
