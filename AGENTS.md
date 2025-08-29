# AGENTS

This repository hosts multiple Art-Net based lighting programs.

## Components

- **Art-Net sender (Python)**: `src/` and the `piccolo` package implement a sender with REST API, MQTT hooks, and effect utilities.
- **Photon firmware**: `firmware/photon_artnet/photon_artnet.ino` targets the Particle Photon to receive Art-Net data and drive NeoPixels.
- **Planned Raspberry Pi examples**: upcoming Art-Net programs for Raspberry Pi will target NeoPixel and DotStar devices and live alongside the Photon firmware.

## Development Guidelines

- Python code should follow PEP 8 conventions and run on Python 3.11+.
- Run `pytest` before committing changes to verify functionality.
- Place board-specific firmware inside `firmware/` and document new programs.
- Add additional AGENTS files within subdirectories when needed for component-specific instructions.
