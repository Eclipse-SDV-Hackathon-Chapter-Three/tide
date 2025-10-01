//
// Copyright (c) 2025 The X-Verse <https://github.com/The-Xverse>
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
use std::thread;
use backon::{ExponentialBuilder, Retryable};
use log::{error, info};
use std::error::Error;
use std::str::FromStr;
use std::time::{SystemTime};
use up_rust::{UMessageBuilder, UPayloadFormat,
    UTransport, UUri,
};
use up_transport_mqtt5::{Mqtt5Transport, Mqtt5TransportOptions, MqttClientOptions};
// uProtocol resource IDs for sensors
// const RESOURCE_SEMANTIC_SEG_IMAGE_SENSOR: u16 = 0x8001;


pub(crate) fn get_mqtt_config() -> Mqtt5TransportOptions {
    let mut mqtt_client_options = MqttClientOptions::default();
    let uri = "192.168.41.250:1883".to_string();
    mqtt_client_options.broker_uri = uri.clone();
    let options = Mqtt5TransportOptions {
        mqtt_client_options,
        ..Default::default()
    };
    info!("MQTT Configured URI: {:?}", uri);
    options
}


async fn start_mqtt_client(mqtt_client: &Mqtt5Transport) -> Result<(), Box<dyn Error>> {
    info!("Starting MQTT client...");
    Ok((|| {
        info!("Connecting to broker...");
        mqtt_client.connect()
    })
    .retry(ExponentialBuilder::default())
    .when(|err| {
        info!("Connection attempt failed: {err}");
        true
    })
    .await?)
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    env_logger::init();
    info!("Starting carla data scraper");
    thread::park();
    Ok(())
    // // Set up MQTT session for traditional Zenoh subscribers
    // let mqtt_config = get_mqtt_config();
    // let authority = "EGOVehicle";
    // let mqtt_client = Mqtt5Transport::new(mqtt_config, authority).await?;
    // start_mqtt_client(&mqtt_client).await?;

    // // Define MQTT topics to subscribe to
    // let topic_event_created = "vehicle/adas-actor/event_created".to_string();

    // loop {
    //     let current_time = SystemTime::now()
    //         .duration_since(SystemTime::UNIX_EPOCH)
    //         .unwrap()
    //         .as_secs();
    //     let uuri  = UUri::from_str(topic_event_created.as_str())?;
    //     let message = UMessageBuilder::publish(uuri)
    //         .with_ttl(1000)
    //         .build_with_payload(
    //             current_time.to_string(),
    //             UPayloadFormat::UPAYLOAD_FORMAT_TEXT,
    //         )
    //         .expect("Failed to build message");

    //     if let Err(e) = mqtt_client.send(message).await {
    //         error!(
    //             "Failed to publish message [topic: {}]: {}",
    //             topic_event_created,
    //             e
    //         );
    //     } else {
    //         info!(
    //             "Successfully published message [topic: {}]",
    //             topic_event_created,
    //         );
    //     }
    //     info!("Sleeping for 1 second...");
    //     tokio::time::sleep(std::time::Duration::from_secs(1)).await;
    // }
}
