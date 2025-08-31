# Raspberry Pi Art-Net LED Service

This example service listens for Art-Net `ArtDMX` packets on UDP port 6454 and
updates an attached LED strip. It supports both NeoPixel and DotStar devices
and will automatically span multiple universes so that more than 170 pixels can
be controlled.

## Usage

```sh
python3 artnet_service.py --led-type neopixel --num-pixels 300 --pin D18
python3 artnet_service.py --led-type dotstar --num-pixels 300 --data-pin MOSI --clock-pin SCLK
```

NeoPixel strips should be connected to GPIO18 (`D18`, physical pin 12). DotStar
strips use the SPI0 interface: wire data to MOSI (GPIO10, physical pin 19) and
clock to SCLK (GPIO11, physical pin 23).

Install the appropriate CircuitPython library for your LED type and the `RPi.GPIO`
dependency before running. NeoPixel strips also require the `rpi_ws281x` library
and must run with root privileges to access `/dev/mem`. For example, `pip install
adafruit-circuitpython-neopixel RPi.GPIO rpi_ws281x`. The `install_service.sh`
script installs these dependencies automatically and forces the systemd service
to run as root when NeoPixel is selected.

## Systemd Installation

Use the provided script to install the service so it starts on boot:

```sh
./install_service.sh
```

The script prompts for the target directory, Linux user, LED type and pin configuration,
then creates a virtual environment and systemd unit. The service is enabled and started immediately.
