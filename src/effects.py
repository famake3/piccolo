"""Light effect generation utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple
import math
import random


@dataclass
class Color:
    """Simple RGB color container."""

    r: int
    g: int
    b: int

    def clamp(self) -> None:
        self.r = max(0, min(255, int(self.r)))
        self.g = max(0, min(255, int(self.g)))
        self.b = max(0, min(255, int(self.b)))

    def as_bytes(self) -> bytes:
        self.clamp()
        return bytes((self.r, self.g, self.b))


class EffectEngine:
    """Generate pixel frames for various lighting effects."""

    def __init__(self, pixel_count: int) -> None:
        self.pixel_count = pixel_count

    def _repeat(self, color: Color) -> List[Color]:
        return [Color(color.r, color.g, color.b) for _ in range(self.pixel_count)]

    def color_cycle(self, colors: List[Color], step: int) -> List[Color]:
        """Return a frame cycling through the given colors."""
        if not colors:
            return self._repeat(Color(0, 0, 0))
        index = step % len(colors)
        return self._repeat(colors[index])

    def flicker(
        self, color: Color, intensity: Tuple[float, float], step: int
    ) -> List[Color]:
        """Return a flickering frame using random brightness variation."""
        low, high = intensity
        scale = random.uniform(low, high)
        flick = Color(int(color.r * scale), int(color.g * scale), int(color.b * scale))
        flick.clamp()
        return self._repeat(flick)

    def wave(self, color: Color, wavelength: int, step: int) -> List[Color]:
        """Return a wave pattern moving across the pixels."""
        frame: List[Color] = []
        for i in range(self.pixel_count):
            phase = (i + step) / max(1, wavelength)
            factor = (math.sin(phase * math.tau) + 1) / 2
            wave_color = Color(
                int(color.r * factor), int(color.g * factor), int(color.b * factor)
            )
            wave_color.clamp()
            frame.append(wave_color)
        return frame

    @staticmethod
    def to_bytes(frame: List[Color]) -> bytes:
        """Convert a frame to DMX byte payload."""
        payload = bytearray()
        for c in frame:
            payload.extend(c.as_bytes())
        return bytes(payload)
