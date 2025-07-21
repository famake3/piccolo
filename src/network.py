"""Network communication utilities for Art-Net devices."""
from __future__ import annotations

import socket
from dataclasses import dataclass


@dataclass
class ArtNetClient:
    """Simple Art-Net client using UDP."""

    target_ip: str
    port: int = 6454  # standard Art-Net port

    def send_dmx(self, universe: int, data: bytes) -> None:
        """Send a DMX payload to the configured Art-Net device."""

        payload = self._build_packet(universe, data)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(payload, (self.target_ip, self.port))

    def _build_packet(self, universe: int, data: bytes) -> bytes:
        """Return a full Art-Net DMX packet for the given universe."""

        if len(data) > 512:
            raise ValueError("DMX payloads may not exceed 512 bytes")

        # ID and OpCode for ArtDMX
        packet = bytearray(b"Art-Net\x00")
        packet.extend((0x00, 0x50))  # OpCode = ArtDMX (little endian)

        # Protocol version 14 (0x000e) big endian
        packet.extend((0x00, 0x0E))

        # Sequence and physical
        packet.extend((0x00, 0x00))

        # Universe (little endian)
        packet.extend(universe.to_bytes(2, "little"))

        # Length of DMX data (big endian)
        packet.extend(len(data).to_bytes(2, "big"))

        packet.extend(data)
        return bytes(packet)
