"""Definitions for LED devices."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class LEDDevice:
    """Representation of an Art-Net controlled LED device."""

    name: str
    ip: str
    pixel_count: int
    group: str | None = None


@dataclass
class DeviceGroup:
    """Logical group of multiple devices."""

    name: str
    devices: List[LEDDevice]
