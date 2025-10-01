import contract.mqtt.client
import nav_app.subscribers
import nav_app.publishers

contract.mqtt.client.initialize_mqtt_client()
nav_app.subscribers.start_listening_to_topics()
nav_app.publishers.publish_should_monitor_event()

# this blocks forever
contract.mqtt.client.start_mqtt_client()
