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

use async_trait::async_trait;
use backon::{ExponentialBuilder, Retryable};
use carla::client::{ActorBase, Client};
use carla::sensor::data::{
    CollisionEvent, Image as ImageEvent, ImuMeasurement as ImuMeasurementEvent, LaneInvasionEvent,
    LidarMeasurement as LidarMeasurementEvent, ObstacleDetectionEvent,
    RadarMeasurement as RadarMeasurementEvent,
};
use carla_data_serde::{
    CollisionEventSerDe, ImageEventSerBorrowed, ImuMeasurementSerDe, LaneInvasionEventSerDe,
    LidarMeasurementSerBorrowed, ObstacleDetectionEventSerDe, RadarMeasurementSerBorrowed,
};
use clap::Parser;
use ego_vehicle::args::Args;
use ego_vehicle::helpers::setup_sensor_with_transport;
use ego_vehicle::sensors::{
    CollisionFactory, ImageFactory, ImuMeasurementFactory, LaneInvasionFactory,
    LidarMeasurementFactory, ObstacleDetectionFactory, RadarMeasurementFactory,
};
use log;
use serde_json;
use std::error::Error;
use std::str::FromStr;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::time::{Duration, SystemTime};
use up_rust::{
    LocalUriProvider, StaticUriProvider, UListener, UMessage, UMessageBuilder, UPayloadFormat,
    UTransport, UUri,
};
use up_transport_mqtt5::{Mqtt5Transport, Mqtt5TransportOptions, MqttClientOptions};
// uProtocol resource IDs for sensors
const RESOURCE_SEMANTIC_SEG_IMAGE_SENSOR: u16 = 0x8001;


pub(crate) fn get_mqtt_config() -> Mqtt5TransportOptions {
    let mut mqtt_client_options = MqttClientOptions::default();
    mqtt_client_options.broker_uri = "10.1.1.1".to_string();
    let options = Mqtt5TransportOptions {
        mqtt_client_options,
        ..Default::default()
    };
    options
}


async fn start_mqtt_client(mqtt_client: &Mqtt5Transport) -> Result<(), Box<dyn Error>> {
    Ok((|| {
        print!("Connecting to broker...");
        mqtt_client.connect()
    })
    .retry(ExponentialBuilder::default())
    .when(|err| {
        print!("Connection attempt failed: {err}");
        true
    })
    .await?)
}

// Listener for engage status - implements the UListener trait for uProtocol
struct EngageListener {
    data: Arc<Mutex<Option<String>>>, // Shared data structure to store the latest engage status
}

#[async_trait]
impl UListener for EngageListener {
    async fn on_receive(&self, msg: UMessage) {
        if let Some(payload) = msg.payload {
            // Convert the binary payload to a string
            let value =
                String::from_utf8(payload.to_vec()).unwrap_or_else(|_| "Invalid UTF-8".to_string());
            log::trace!("[from_uprotocol] engage : {}", value);

            // Update the shared data structure with the new value
            // This is where the lock is acquired and the data is updated
            let mut data = self.data.lock().unwrap();
            *data = Some(value);
            // Lock is released when data goes out of scope
        }
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Set up MQTT session for traditional Zenoh subscribers
    let mqtt_config = get_mqtt_config();
    let authority = "EGOVehicle";
    let mqtt_client = Mqtt5Transport::new(mqtt_config, authority).await?;
    start_mqtt_client(&mqtt_client).await?;

    // Define MQTT topics to subscribe to
    let topic_event_created = "vehicle/adas-actor/event_created".to_string();

    loop {
        let current_time = SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .unwrap()
            .as_secs();
        let uuri  = UUri::from_str(topic_event_created.as_str())?;
        let message = UMessageBuilder::publish(uuri)
            .with_ttl(1000)
            .build_with_payload(
                current_time.to_string(),
                UPayloadFormat::UPAYLOAD_FORMAT_TEXT,
            )
            .expect("Failed to build message");

        if let Err(e) = mqtt_client.send(message).await {
            print!(
                "Failed to publish message [topic: {}]: {}",
                topic_event_created,
                e
            );
        } else {
            print!(
                "Successfully published message [topic: {}]",
                topic_event_created,
            );
        }
        print!("Sleeping for 1 second...");
        tokio::time::sleep(std::time::Duration::from_secs(1)).await;
    }
}
