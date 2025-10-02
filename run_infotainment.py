import contract.mqtt.client
import infotainment_app.subscribers

contract.mqtt.client.initialize_mqtt_client()
infotainment_app.subscribers.start_listening_to_topics()

# this blocks forever
contract.mqtt.client.listen()
