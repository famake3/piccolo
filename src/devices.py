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
    universe: int = 0
    group: str | None = None


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
