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
        """Send a DMX payload to the configured Art-Net device.

        This is a minimal implementation and does not build a full Art-Net
        packet. Only a basic UDP payload is sent as a placeholder.
        """
        payload = self._build_packet(universe, data)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(payload, (self.target_ip, self.port))

    def _build_packet(self, universe: int, data: bytes) -> bytes:
        """Return a minimal Art-Net packet for the given universe."""
        # Proper Art-Net packet structure should be implemented here.
        # For now this is just a stub sending raw data.
        header = b"Art-Net\x00" + universe.to_bytes(2, "big")
        return header + data
