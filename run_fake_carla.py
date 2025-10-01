
import contract.mqtt.client
from on_vehicle_app.sensor_loop import run_fake_carla_sensor_loop
import multiprocessing
import on_vehicle_app.subscribers

contract.mqtt.client.initialize_mqtt_client()
on_vehicle_app.subscribers.start_listening_to_topics()

sensor_process = multiprocessing.Process(target=run_fake_carla_sensor_loop)
sensor_process.start()

# this blocks forever
contract.mqtt.client.start_mqtt_client()
