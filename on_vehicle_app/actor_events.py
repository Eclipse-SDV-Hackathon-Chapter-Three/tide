from datetime import datetime
from typing import Tuple
import numpy as np
from contract.adas_actor_event import AdasActorEvent

# Detect pixels by semantic ID in the Red channel
def detect_actor(
    raw_data: bytes,
    width: int,
    height: int,
    class_id: int,
) -> bool:
    """
    Returns True if any pixel is tagged with the given class_id in a semantic-segmentation frame.
    - raw_data: flattened 32-bit BGRA bytes (len == width*height*4)
    - class_id: semantic tag ID to check (12 for pedestrian)
    """
    expected = width * height * 4
    if len(raw_data) != expected:
        raise ValueError(f"raw_data length {len(raw_data)} != {expected} (width*height*4)")

    img = np.frombuffer(raw_data, dtype=np.uint8).reshape((height, width, 4))
    red_channel = img[..., 2]  # In BGRA, index 2 is Red (semantic class ID)

    return np.any(red_channel == class_id)

# Build AdasActorEvent
def make_brand_new_actor_event(
    raw_data: bytes,
    width: int,
    height: int,
    location: Tuple[float, float, float],
    class_id: int,
    actor_tag: str,
) -> AdasActorEvent:
    visible = detect_actor(raw_data, width, height, class_id)
    return AdasActorEvent(
        UUID=None,
        actor_tag=actor_tag,
        is_visible=visible,
        timestamp=datetime.utcnow(),
        location=location,
    )
