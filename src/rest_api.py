"""REST API using FastAPI for device control."""

from __future__ import annotations

from dataclasses import asdict
from typing import Callable, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel

from .devices import LEDDevice
from .effects import Color, EffectEngine
from .favorites import FavoritesManager
from .network import ArtNetClient


class DeviceModel(BaseModel):
    """Pydantic model for device registration."""

    name: str
    ip: str
    pixel_count: int
    group: Optional[str] = None
    universe: int = 0


class GroupModel(BaseModel):
    """Model for group creation."""

    name: str
    devices: List[str] = []


class LightCommand(BaseModel):
    """Model describing a light command payload."""

    universe: int = 0
    data: str  # hex encoded bytes


class FavoriteModel(BaseModel):
    """Model describing a color favorite."""

    name: str
    r: int
    g: int
    b: int


class RestAPI:
    """Simple REST API server providing device management."""

    def __init__(self) -> None:
        self.app = FastAPI(title="Piccolo Control Panel")
        self.devices: Dict[str, LEDDevice] = {}
        self.groups: Dict[str, List[str]] = {}
        self.favorites = FavoritesManager()
        self.event_hooks: Dict[str, Callable[[dict | None], None]] = {}
        self.effect_engines: Dict[str, EffectEngine] = {}
        self._setup_routes()

    def add_event_hook(self, name: str, handler: Callable[[dict | None], None]) -> None:
        """Register a handler to be invoked when an event is triggered."""
        self.event_hooks[name] = handler

    def _get_engine(self, name: str) -> EffectEngine:
        if name not in self.effect_engines:
            pixel_count = self.devices[name].pixel_count
            self.effect_engines[name] = EffectEngine(pixel_count)
        return self.effect_engines[name]

    def attach_mqtt(self, topic: str, mqtt_client: "MQTTClient", event: str) -> None:
        """Bind an MQTT topic to a named event."""

        def _callback(message: str) -> None:
            handler = self.event_hooks.get(event)
            if handler:
                handler({"message": message})

        mqtt_client.subscribe(topic, _callback)

    def _setup_routes(self) -> None:
        @self.app.get("/", response_class=PlainTextResponse)
        def root() -> str:
            return "Piccolo control panel running."

        @self.app.get("/panel", response_class=HTMLResponse)
        def panel() -> str:
            return (
                "<html><head><title>Piccolo Control Panel</title></head>"
                "<body><h1>Piccolo Control Panel</h1>"
                "<p>Use a REST client to manage devices and groups.</p>"
                "</body></html>"
            )

        @self.app.get("/devices")
        def list_devices() -> List[Dict[str, object]]:
            return [asdict(d) for d in self.devices.values()]

        @self.app.post("/devices")
        def register_device(device: DeviceModel) -> Dict[str, str]:
            if device.name in self.devices:
                raise HTTPException(status_code=400, detail="Device already exists")
            self.devices[device.name] = LEDDevice(**device.dict())
            if device.group:
                self.groups.setdefault(device.group, []).append(device.name)
            return {"status": "registered"}

        @self.app.get("/groups")
        def list_groups() -> Dict[str, List[str]]:
            return self.groups

        @self.app.post("/groups")
        def create_group(group: GroupModel) -> Dict[str, str]:
            if group.name in self.groups:
                raise HTTPException(status_code=400, detail="Group already exists")
            for dev_name in group.devices:
                if dev_name not in self.devices:
                    raise HTTPException(
                        status_code=404, detail=f"Device {dev_name} not found"
                    )
            self.groups[group.name] = list(group.devices)
            for dev_name in group.devices:
                self.devices[dev_name].group = group.name
            return {"status": "group created"}

        @self.app.get("/favorites")
        def list_favorites() -> List[Dict[str, int]]:
            return [asdict(f) for f in self.favorites.list()]

        @self.app.post("/favorites")
        def add_favorite(fav: FavoriteModel) -> Dict[str, str]:
            self.favorites.add(fav.name, fav.r, fav.g, fav.b)
            return {"status": "added"}

        @self.app.delete("/favorites/{name}")
        def delete_favorite(name: str) -> Dict[str, str]:
            self.favorites.remove(name)
            return {"status": "removed"}

        @self.app.post("/devices/{name}/command")
        def send_command(name: str, cmd: LightCommand) -> Dict[str, str]:
            if name not in self.devices:
                raise HTTPException(status_code=404, detail="Device not found")
            payload = bytes.fromhex(cmd.data)
            client = ArtNetClient(self.devices[name].ip)
            base = self.devices[name].universe
            client.send_dmx(base + cmd.universe, payload)
            return {"status": "sent"}

        @self.app.post("/groups/{name}/command")
        def send_group_command(name: str, cmd: LightCommand) -> Dict[str, str]:
            if name not in self.groups:
                raise HTTPException(status_code=404, detail="Group not found")
            for dev_name in self.groups[name]:
                payload = bytes.fromhex(cmd.data)
                client = ArtNetClient(self.devices[dev_name].ip)
                base = self.devices[dev_name].universe
                client.send_dmx(base + cmd.universe, payload)
            return {"status": "sent"}

        @self.app.post("/groups/{name}/effect")
        def run_group_effect(name: str, effect: str, step: int = 0) -> Dict[str, str]:
            if name not in self.groups:
                raise HTTPException(status_code=404, detail="Group not found")
            for dev_name in self.groups[name]:
                engine = self._get_engine(dev_name)
                if effect == "cycle":
                    colors = [Color(255, 0, 0), Color(0, 255, 0), Color(0, 0, 255)]
                    frame = engine.color_cycle(colors, step)
                elif effect == "wave":
                    frame = engine.wave(Color(255, 255, 255), 20, step)
                elif effect == "flicker":
                    frame = engine.flicker(Color(255, 255, 255), (0.2, 1.0), step)
                else:
                    raise HTTPException(status_code=400, detail="Unknown effect")
                payload = EffectEngine.to_bytes(frame)
                base = self.devices[dev_name].universe
                ArtNetClient(self.devices[dev_name].ip).send_dmx(base, payload)
            return {"status": "sent"}

        @self.app.post("/devices/{name}/effect")
        def run_device_effect(name: str, effect: str, step: int = 0) -> Dict[str, str]:
            if name not in self.devices:
                raise HTTPException(status_code=404, detail="Device not found")
            engine = self._get_engine(name)
            if effect == "cycle":
                colors = [
                    Color(r, g, b)
                    for r, g, b in [
                        (255, 0, 0),
                        (0, 255, 0),
                        (0, 0, 255),
                    ]
                ]
                frame = engine.color_cycle(colors, step)
            elif effect == "wave":
                frame = engine.wave(Color(255, 255, 255), 20, step)
            elif effect == "flicker":
                frame = engine.flicker(Color(255, 255, 255), (0.2, 1.0), step)
            else:
                raise HTTPException(status_code=400, detail="Unknown effect")
            payload = EffectEngine.to_bytes(frame)
            base = self.devices[name].universe
            ArtNetClient(self.devices[name].ip).send_dmx(base, payload)
            return {"status": "sent"}

        @self.app.post("/triggers/{event}")
        def trigger_event(event: str, payload: Optional[dict] = None) -> Dict[str, str]:
            handler = self.event_hooks.get(event)
            if not handler:
                raise HTTPException(status_code=404, detail="Event not registered")
            handler(payload)
            return {"status": "triggered"}

    def start(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """Start the REST API server using uvicorn."""
        import uvicorn

        uvicorn.run(self.app, host=host, port=port)


if __name__ == "__main__":
    RestAPI().start()
