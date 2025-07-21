"""Definitions for LED devices."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class LEDDevice:
    """Representation of an Art-Net controlled LED device."""

    name: str
    ip: str
    pixel_count: int
    group: str | None = None
    universe: int = 0


@dataclass
class DeviceGroup:
    """Logical group of multiple devices."""

    name: str
    devices: List[LEDDevice]


@dataclass
class LEDSegment:
    """A segment of LEDs on a device."""

    device: str
    start: int
    length: int


@dataclass
class LightGroup:
    """Group of LED segments possibly across multiple devices."""

    name: str
    segments: List[LEDSegment]
