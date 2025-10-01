import time

from contract.passenger_leaving_event import PassengerLeftEvent
from on_vehicle_app.fake_data import create_fake_semantic_segmentation_sensor_data, get_ego_location
from on_vehicle_app.passenger_events import should_passenger_leave_vehicle
from on_vehicle_app.publishers import publish_actor_seen_event, publish_passenger_left_vehicle_event


def run_fake_carla_sensor_loop():
    while True:
        event = create_fake_semantic_segmentation_sensor_data()
        publish_actor_seen_event(event)
        time.sleep(0.1)
        
        if should_passenger_leave_vehicle(event):
            passenger_left_vehicle = PassengerLeftEvent(
                actor_tag=event.actor_tag,
                timestamp=event.timestamp,
                location=get_ego_location()
            )
            publish_passenger_left_vehicle_event(passenger_left_vehicle)
        time.sleep(1)

