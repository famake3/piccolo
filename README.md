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

## Quick Start

After installing the dependencies, launch the built-in REST API server and
web panel:

```bash
python -m src.rest_api
```

The server listens on <http://localhost:8000>. Open `/panel` in your browser
to register devices and begin controlling your LEDs.

## Configuration

Devices are described in a YAML configuration file. See
`config.example.yaml` for a starting point:

```yaml
devices:
  - name: "strip1"
    ip: "192.168.1.50"
    pixel_count: 150
```

Each device entry must define the Art-Net device IP address and the
number of pixels it controls. Groups are created separately using
segments from one or more devices.

Load the configuration with:

```python
from src.config import load_config
config = load_config("config.yaml")
```

## Extending

Several modules are provided which you can extend:

* `src/rest_api.py` – FastAPI-based REST API server and web panel.
* `src/mqtt.py` – add MQTT handling if required.
* `src/effects.py` – light effect engine with basic animations.
* `src/favorites.py` – store favourite colors for reuse.

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
python -m piccolo --config config.yaml
```

By default it will listen on <http://localhost:8000>. A simple HTML panel
is available at `/panel` and the following API endpoints are exposed:

* `GET /devices` – list registered devices.
* `POST /devices` – register a new device.
* `GET /groups` – list groups and their members.
* `POST /groups` – create a new group from device segments.
* `POST /devices/{name}/command` – send a hex encoded DMX payload to a device.
* `POST /groups/{name}/command` – send a command to all devices in a group.
* `POST /devices/{name}/effect` – run a built-in light effect on a device.
* `POST /groups/{name}/effect` – run an effect on all devices in a group.
* `POST /devices/{name}/color` – set a device to a solid color.
* `POST /groups/{name}/color` – set a group of devices to a color.
* `GET /favorites` – list stored colours.
* `POST /favorites` – add a favourite colour.
* `DELETE /favorites/{name}` – remove a favourite colour.
* `POST /triggers/{event}` – trigger a named event hook.

Color and effect endpoints accept an optional `universe` query parameter
which is added to each device's base universe when sending data.

Use any HTTP client or the web panel to manage your lighting setup.

The `/panel` route now serves a basic HTML interface which can register
devices, create groups and send colour or effect commands. Open
`http://localhost:8000/panel` in a browser to try it out.

## Particle Photon Firmware

A sample Particle Photon sketch for receiving Art-Net data and updating a strip of NeoPixels is available at `firmware/photon_artnet/photon_artnet.ino`. Import it into the Particle IDE and add the `neopixel` library to build firmware for your hardware. The sketch also registers a Particle variable `ip` with the device's current IP address, which you can view in the Particle Console, Web IDE, or CLI.

## Raspberry Pi Art-Net Service

An example Python service for Raspberry Pi devices is provided at
`firmware/rpi_artnet_service/artnet_service.py`. The script listens for
Art-Net packets and drives a connected NeoPixel or DotStar strip. It
handles multiple universes automatically so installations with more than
170 pixels can be controlled from a single Pi.

### Setup

1. Enable the required hardware interfaces via `raspi-config` (enable SPI for
   DotStar strips).
2. Install the CircuitPython compatibility layer and LED drivers. On Raspberry
   Pi OS you can use `apt`:

   ```sh
   sudo apt update
   sudo apt install python3-adafruit-blinka \
       python3-adafruit-circuitpython-neopixel \
       python3-adafruit-circuitpython-dotstar
   ```

   Or create a virtual environment and use `pip`:

   ```sh
   python3 -m venv venv
   source venv/bin/activate
   pip install adafruit-blinka adafruit-circuitpython-neopixel \
       adafruit-circuitpython-dotstar
   ```

3. Run the service with your strip type and pixel count:

   ```sh
   python3 artnet_service.py --led-type neopixel --num-pixels 300 --pin D18
   python3 artnet_service.py --led-type dotstar --num-pixels 300 \
       --data-pin MOSI --clock-pin SCLK
   ```

You may need `sudo` when accessing hardware pins. See
`firmware/rpi_artnet_service/README.md` for more details.
