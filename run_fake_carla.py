
import contract.mqtt.client
import on_vehicle_app.subscribers
import on_vehicle_app.publishers

contract.mqtt.client.initialize_mqtt_client()
on_vehicle_app.subscribers.start_listening_to_topics()
on_vehicle_app.publishers.publish_should_monitor_event()

# this blocks forever
contract.mqtt.client.start_mqtt_client()
