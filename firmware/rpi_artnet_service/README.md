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

Install the appropriate CircuitPython library for your LED type before running
(e.g. `pip install adafruit-circuitpython-neopixel`).
