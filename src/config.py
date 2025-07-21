"""Configuration loading utilities."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import yaml

from .devices import LEDDevice


@dataclass
class Config:
    """Application configuration."""

    devices: List[LEDDevice]


def load_config(path: str | Path) -> Config:
    """Load configuration from a YAML file."""
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}

    devices = [
        LEDDevice(
            name=item.get("name", f"device_{i}"),
            ip=item["ip"],
            pixel_count=item["pixel_count"],
            group=item.get("group"),
            universe=item.get("universe", 0),
        )
        for i, item in enumerate(data.get("devices", []))
    ]

    return Config(devices=devices)
