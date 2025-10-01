
import numpy as np
from contract.adas_actor_event import AdasActorEvent
from on_vehicle_app.actor_events import make_brand_new_actor_event
from on_vehicle_app.constants import CARLA_CLASS_LABELS

def get_ego_location() -> tuple[float, float, float]:
    # Placeholder for actual ego vehicle location retrieval logic
    return (0.0, 0.0, 0.0)


def create_fake_semantic_segmentation_sensor_data() -> AdasActorEvent:
    # Example of datas from Carla
    # BGRA tuples: (B, G, R, A). Only Red holds the class ID.
    fake_raw_data = [
        (0, 0, 12, 255),  # pedestrian
        (0, 0, 7, 255),   # road (example)
        (0, 0, 10, 255),  # vehicle (example)
        (0, 0, 0, 255),   # background
    ]
    width = 2
    height = 2
    # sensor_location = camera.get_transform().location
    # location = (sensor_location.x, sensor_location.y, sensor_location.z)

    raw = bytes(np.array(fake_raw_data, dtype=np.uint8).ravel())

    class_id = 12  # Pedestrian
    actor_tag = CARLA_CLASS_LABELS[class_id]

    evt: AdasActorEvent = make_brand_new_actor_event(
        raw_data=raw,
        width=width,
        height=height,
        location=(0.0, 0.0, 0.0),
        class_id=class_id,
        actor_tag=actor_tag
    )
    return evt
