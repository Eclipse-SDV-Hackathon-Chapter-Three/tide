import contract.mqtt.client
import infotainment_app.subsribers

contract.mqtt.client.initialize_mqtt_client()
infotainment_app.subsribers.start_listening_to_topics()

# this blocks forever
contract.mqtt.client.listen()
