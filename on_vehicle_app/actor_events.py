from datetime import datetime
from typing import Tuple
from pydantic import BaseModel
import numpy as np

CARLA_CLASS_LABELS = {
    0: "Unlabeled",
    1: "Roads",
    2: "SideWalks",
    3: "Building",
    4: "Wall",
    5: "Fence",
    6: "Pole",
    7: "TrafficLight",
    8: "TrafficSigns",
    9: "Vegetation",
    10: "Terrain",
    11: "Sky",
    12: "Pedestrian",
    13: "Rider",
    14: "Car",
    15: "Truck",
    16: "Bus",
    17: "Train",
    18: "Motorcycle",
    19: "Bicycle",
    20: "Static",
    21: "Dynamic",
    22: "Other",
}

# Predefined class
class AdasActorEvent(BaseModel):
    actor_tag: str
    is_visible: bool
    timestamp: datetime
    location: Tuple[float, float, float]

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
def make_actor_event(
    raw_data: bytes,
    width: int,
    height: int,
    location: Tuple[float, float, float],
    class_id: int,
    actor_tag: str,
) -> AdasActorEvent:
    visible = detect_actor(raw_data, width, height, class_id)
    return AdasActorEvent(
        actor_tag=actor_tag,
        is_visible=visible,
        timestamp=datetime.utcnow(),
        location=location,
    )

# Self Test
if __name__ == "__main__":
    # Example of datas from Carla
    # BGRA tuples: (B, G, R, A). Only Red holds the class ID.
    raw_data = [
        (0, 0, 12, 255),  # pedestrian
        (0, 0, 7, 255),   # road (example)
        (0, 0, 10, 255),  # vehicle (example)
        (0, 0, 0, 255),   # background
    ]
    width = 2
    height = 2
    # sensor_location = camera.get_transform().location
    # location = (sensor_location.x, sensor_location.y, sensor_location.z)

    raw = bytes(np.array(raw_data, dtype=np.uint8).ravel())

    class_id = 12  # Pedestrian
    actor_tag = CARLA_CLASS_LABELS[class_id]

    evt = make_actor_event(
        raw_data=raw,
        width=width,
        height=height,
        location=(0.0, 0.0, 0.0),
        class_id=class_id,
        actor_tag=actor_tag
    )
    print(evt.model_dump())
