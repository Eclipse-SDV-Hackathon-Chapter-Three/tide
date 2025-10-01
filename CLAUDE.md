# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Team Tide's Eclipse SDV Hackathon project: A traffic hazard reporting system using ADAS sensors to detect and report objects of interest (police, road hazards) and passenger behavior. Built on the SDV Lab framework using Eclipse open-source tools.

## Core Architecture

### Three-Component System
1. **Carla Simulation Team** - Generates vehicle sensor data and ADAS events from CARLA simulator
2. **Navigation Application (nav_app)** - Python MQTT subscriber that receives and processes events
3. **Infotainment Display** - Android Automotive (AAOS) application for driver notifications

### Data Contracts
The `/contract` directory defines shared event models using Pydantic:
- `AdasActorEvent` - Detected actors with tag, visibility, timestamp, location
- `PassengerLeftEvent` - Passenger exit events with timestamp and location
- `AdasActorMonitorEvent` - Actor monitoring metadata

These contracts ensure consistency between the simulation publisher and application subscribers.

### Communication Layer
- **Primary Protocol**: MQTT (Mosquitto broker running on shared laptop)
- **Secondary Options**: uProtocol, Zenoh (available in sdv_lab examples)
- **Configuration**: `mqtt_config.json` at project root defines broker connection details
- **Topics**: Event types map to MQTT topics (e.g., "adas_actor_event")

### Deployment
- **Orchestration**: Eclipse Ankaios manages containerized workloads
- **Container Engine**: Podman
- **Manifests**: `.yaml` files define workload configuration, including agent assignment, network settings, and config injection

## Development Setup

### Environment
```bash
# The project uses Docker devcontainers (.devcontainer/)
# Container includes: Python 3.13, pipenv, MQTT client libraries

# Install Python dependencies
pipenv install

# Or using pip
pip install paho-mqtt==1.6.1 pydantic
```

### Running Components
```bash
# Start Ankaios on your machine
sudo systemctl start ank-server ank-agent

# Apply a workload manifest (update IP addresses first!)
cd sdv_lab/uprotocol/cruise-control-app
ank apply cruise-control-app.yaml

# Remove workloads
ank apply -d cruise-control-app.yaml

# Check workload status
ank get workloads
ank logs <workload_name>
```

### Ankaios Manifest Structure
```yaml
apiVersion: v0.1
workloads:
  my_workload:
    runtime: podman
    agent: agent_A  # Which Ankaios node to run on
    configs:        # Define config data
      my_config: my_config
    files:          # Mount configs into container
      - mountPoint: /app/config.json
        data: "{{my_config}}"
    restartPolicy: NEVER
    runtimeConfig: |
      image: ghcr.io/my-org/my-image:latest
      commandOptions: ["--net=host", "-e", "ENV_VAR=value"]
```

**Important**: Replace `localhost` with the shared laptop's IP address in manifests when deploying to the hackathon infrastructure.

## Project Structure

```
/contract/           - Pydantic event models (data contracts)
/nav_app/            - Navigation application subscriber
  subscriber.py      - MQTT client listening for ADAS events
/sdv_lab/            - Eclipse SDV Lab examples and blueprints
  android_python/    - MQTT with Android AAOS example
  ego-vehicle/       - CARLA control examples (uProtocol, Zenoh, container)
  pid_controller/    - PID cruise control (Python-Zenoh, Rust-uProtocol)
  uprotocol/         - uProtocol examples
  ankaios/           - Ankaios SDK examples (Python, Rust)
/.devcontainer/      - VS Code dev environment configuration
```

## Code Standards

### Python
- **Formatter**: Black (VS Code extension configured)
- **Linting**: Pylance
- **Type Hints**: Required for all function signatures
- **Dependencies**: Managed via Pipfile (pipenv)

### Git Workflow
- Main branch is protected - no direct pushes
- Work on feature branches, submit PRs for review
- Cross-team review required (one reviewer from different sub-team)

### Branch Organization
- `main` - Protected production branch
- `transaction` - Current development branch
- `nav-app` - Navigation app feature work
- `add_document` - Documentation updates

## SDV Lab Examples

The `sdv_lab/` directory contains working examples to reference:

### MQTT Examples
- `android_python/` - Python MQTT pub/sub with Android AAOS display
  - Publisher cycles speed 0-100 km/h
  - Subscriber displays on Android gauge

### uProtocol Examples
- `uprotocol/cruise-control-app/` - Rust app publishing operational status
- `ego-vehicle/uprotocol-control/` - CARLA vehicle control via uProtocol
- `pid_controller/rust-uprotocol/` - PID controller using uProtocol over Zenoh

### Zenoh Examples
- `pid_controller/python-zenoh/` - Real-time PID controller
- `ego-vehicle/zenoh-control/` - CARLA control via Zenoh

### Ankaios SDK
- `ankaios/example_workloads/python_workload/` - Python SDK for dynamic workload management
- `ankaios/example_workloads/rust_workload/` - Rust SDK equivalent

## Common Issues

### MQTT Connection
- Ensure `mqtt_config.json` has correct broker IP (shared laptop address, not localhost)
- Check network connectivity to shared laptop
- Verify MQTT broker is running on shared laptop: `mosquitto -v`

### Ankaios Deployment
- Workloads must specify `agent` matching your Ankaios node name
- Use `--net=host` for containers that need host network access
- Check agent status: `ank get state`
- View logs: `ank logs <workload_name>`

### CARLA Simulator
- CARLA 0.9.15 runs on shared laptop with GPU
- Access CARLA API via Python: `import carla`
- Sensor data published to MQTT/uProtocol/Zenoh based on configuration

## Key Dependencies

### Python
- `paho-mqtt==1.6.1` - MQTT client
- `pydantic` - Data validation and contracts

### Rust (in sdv_lab examples)
- `up-rust` - uProtocol implementation
- `zenoh` - Pub/sub messaging
- `tokio` - Async runtime

### Infrastructure
- Eclipse Ankaios v0.6.0 - Workload orchestration
- Podman - Container runtime
- CARLA 0.9.15 - Vehicle simulation
- Mosquitto - MQTT broker

## Testing Strategy

- Unit tests for core logic (CARLA app, nav app)
- Integration tests via automated scripts once prototype is ready
- Manual testing in CARLA simulator with Android display

## Team Context

- **Team Name**: Tide
- **Challenge**: SDV Lab - ADAS hazard detection and reporting
- **Standup Schedule**: 5-minute standups every hour
- **Review Policy**: Cross-team code review required
