from datetime import datetime
from typing import Tuple
from pydantic import BaseModel


class PassengerLeftEvent(BaseModel):
    timestamp: datetime
    location: Tuple[float, float, float]
