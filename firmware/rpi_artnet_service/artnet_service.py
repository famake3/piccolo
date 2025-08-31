"""Art-Net to NeoPixel / DotStar service for Raspberry Pi.

This script listens for Art-Net packets and updates an attached LED strip.
It supports both NeoPixel and DotStar devices and handles multiple
universes so that more than 170 pixels can be controlled.

The service is intended to run on a Raspberry Pi and requires either the
``neopixel`` or ``adafruit_dotstar`` libraries depending on the selected LED
type.  The board specific modules are imported lazily so that the file can be
imported without the hardware specific dependencies which keeps ``pytest``
happy on systems without those packages available.
"""

from __future__ import annotations

import argparse
import logging
import socket
import struct
from typing import Iterable, Optional, Tuple

# Art-Net constants
ARTNET_PORT = 6454
ARTNET_HEADER = b"Art-Net\0"
OPCODE_ARTDMX = 0x5000


_LOGGER = logging.getLogger(__name__)


class LEDStrip:
    """A tiny abstraction over the LED strip implementations."""

    def __init__(self, pixels):
        self._pixels = pixels

    def __setitem__(self, index: int, value: Tuple[int, int, int]) -> None:
        self._pixels[index] = value

    def show(self) -> None:
        self._pixels.show()


def _parse_artdmx(packet: bytes) -> Optional[Tuple[int, bytes]]:
    """Validate and extract fields from an ArtDMX packet.

    Returns a tuple of ``(universe, data)`` if the packet is valid or
    ``None`` if the packet is not a valid ArtDMX message.
    """

    if len(packet) < 18:
        return None
    if not packet.startswith(ARTNET_HEADER):
        return None
    opcode = struct.unpack("<H", packet[8:10])[0]
    if opcode != OPCODE_ARTDMX:
        return None
    length = struct.unpack(">H", packet[16:18])[0]
    data = packet[18 : 18 + length]
    universe = struct.unpack("<H", packet[14:16])[0]
    return universe, data


def _init_strip(args: argparse.Namespace) -> LEDStrip:
    """Initialise the LED strip based on command line arguments."""

    if args.led_type == "neopixel":
        import board
        import neopixel

        pin = getattr(board, args.pin)
        pixels = neopixel.NeoPixel(
            pin,
            args.num_pixels,
            brightness=args.brightness,
            auto_write=False,
        )
    elif args.led_type == "dotstar":
        import board
        import adafruit_dotstar as dotstar

        data_pin = getattr(board, args.data_pin)
        clock_pin = getattr(board, args.clock_pin)
        pixels = dotstar.DotStar(
            clock_pin,
            data_pin,
            args.num_pixels,
            brightness=args.brightness,
            auto_write=False,
        )
    else:
        raise ValueError(f"Unsupported LED type {args.led_type}")

    return LEDStrip(pixels)


def run_service(args: argparse.Namespace) -> None:
    """Run the Art-Net service."""

    strip = _init_strip(args)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", ARTNET_PORT))
    _LOGGER.info("Listening for Art-Net on UDP %d", ARTNET_PORT)

    bytes_per_pixel = 3  # RGB only for now
    pixels_per_universe = 512 // bytes_per_pixel
    total_universes = (args.num_pixels + pixels_per_universe - 1) // pixels_per_universe
    last_universe = total_universes - 1
    buffer = [(0, 0, 0)] * args.num_pixels

    while True:
        data, _addr = sock.recvfrom(1024)
        parsed = _parse_artdmx(data)
        if not parsed:
            continue
        universe, dmx = parsed
        start = universe * pixels_per_universe
        for i in range(min(pixels_per_universe, args.num_pixels - start)):
            base = i * bytes_per_pixel
            if base + 2 >= len(dmx):
                break
            r, g, b = dmx[base : base + 3]
            idx = start + i
            buffer[idx] = (r, g, b)
            strip[idx] = (r, g, b)
        # Only refresh once the final universe has been processed
        if universe == last_universe:
            strip.show()


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--led-type", choices=["neopixel", "dotstar"], required=True)
    parser.add_argument("--num-pixels", type=int, required=True)
    parser.add_argument("--brightness", type=float, default=1.0)
    parser.add_argument("--pin", default="D18", help="NeoPixel data pin (when using neopixel)")
    parser.add_argument("--data-pin", default="MOSI", help="DotStar data pin (when using dotstar)")
    parser.add_argument("--clock-pin", default="SCLK", help="DotStar clock pin (when using dotstar)")
    return parser


def main(argv: Optional[Iterable[str]] = None) -> None:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO)
    run_service(args)


if __name__ == "__main__":  # pragma: no cover - manual execution only
    main()
