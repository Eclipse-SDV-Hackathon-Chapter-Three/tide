# How To Run

## Dev Container Setup

enter the repositories devcontainer to ensure development environment is set up correctly

Docker must be installed on the shared laptop

1. on the shared laptop, open a new terminal, navigate to the repository
2. start a sudo VS Code session by running `sudo code --no-sandbox --user-data-dir=/home/sdv-hacker/`
3. This should open VS Code in a new window at our repository
4. Install the VS Code Dev Containers extension if you haven't already
5. Press F1, and search for the command "Reopen in Dev Container"
6. VS Code should reload and start building the dev container
7. After the build is done, you should be in the dev container. To double check this, VS Codes remote connection (usually in the bottom left corner) should say "Dev Container: tide"

## MQTT Broker

Dev container is not necessasry for this. Just a properly setup SDV Hackathon shared laptop :)

1. change the wifi to the teams local wifi
1. on the shared laptop, open a new terminal, and navigate to the repository
2. run `ank -k apply sdv_lab/shared-laptop-manifest.yaml`
3. wait for ankaios to say the `mqtt_broker` workflow has a `Running(Ok)` status

Sometimes the MQTT broker fails to run, but still says its running. To fix this, kill the process and restart it by running

```
sudo netstat -tulnp | grep 1883
# read the PID from the output and use it in the command below
sudo kill <PID_HERE>
ank -k delete workload mqtt_broker
ank -k apply sdv_lab/shared-laptop-manifest.yaml
```

## Carla Simulator (In-Vehicle Data Collection App)

In the VS Code devcontainer

1. change the wifi to the teams local wifi
2. open a new terminal
3. run `pipenv install`
4. run `pipenv run python run_fake_carla.py`
5. data should start publishing to the `vehicle/adas-actor/seen` every 1 second

## Navigation Application (Back-End)

In the VS Code devcontainer

1. change the wifi to the teams local wifi
2. open a new terminal
3. run `pipenv install`
4. run `pipenv run python run_nav_app.py`
5. if the Carla simulator is running, you should start seeing data being received from the Carla simulator
6. if it determines a new incident is detected, it will publish it to the `vehicle/adas-actor/event-created` topic

## Infotainment (In-Vehicle)

1. 1. change the wifi to the teams local wifi
2. open a new terminal
3. run `pipenv install`
4. run `pipenv run python run_nav_app.py`

## Mobile App

1. 
