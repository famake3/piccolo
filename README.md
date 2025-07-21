# piccolo

Network light control for RGB LEDs

This project provides the foundation for controlling network-based LED
installations. The codebase is minimal and intended to be extended with
additional features such as REST APIs or MQTT communication.

## Requirements

* Python 3.11+
* pip

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Devices are described in a YAML configuration file. See
`config.example.yaml` for a starting point:

```yaml
devices:
  - name: "strip1"
    ip: "192.168.1.50"
    pixel_count: 150
    group: "stage_left"
```

Each device entry must define the Art-Net device IP address and the
number of pixels it controls. Devices can optionally be assigned to a
group.

Load the configuration with:

```python
from src.config import load_config
config = load_config("config.yaml")
```

## Extending

Several modules are provided which you can extend:

* `src/rest_api.py` – FastAPI-based REST API server and web panel.
* `src/mqtt.py` – add MQTT handling if required.
* `src/effects.py` – build a light effect engine.

Networking helpers for Art-Net are in `src/network.py` and LED device
definitions in `src/devices.py`.

## Running

After installing dependencies and creating a configuration file, you can
use the modules in your own scripts. A very simple example to send blank
frames to all configured devices:

```python
from src.config import load_config
from src.network import ArtNetClient

cfg = load_config("config.yaml")
for device in cfg.devices:
    client = ArtNetClient(device.ip)
    client.send_dmx(0, b"\x00" * device.pixel_count * 3)
```

This will send a zeroed DMX packet to each device. Build on top of this
to create your own lighting controller.

## REST API and Web Panel

The project includes a small FastAPI application exposing REST endpoints
for device and group management. Launch the server with:

```bash
python -m src.rest_api
```

By default it will listen on <http://localhost:8000>. A simple HTML panel
is available at `/panel` and the following API endpoints are exposed:

* `GET /devices` – list registered devices.
* `POST /devices` – register a new device.
* `GET /groups` – list groups and their members.
* `POST /groups` – create a new group.
* `POST /devices/{name}/command` – send a hex encoded DMX payload to a device.
* `POST /groups/{name}/command` – send a command to all devices in a group.

Use any HTTP client or the web panel to manage your lighting setup.
