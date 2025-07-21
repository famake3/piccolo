import pytest
from fastapi.testclient import TestClient

from src.rest_api import RestAPI


@pytest.fixture
def client():
    api = RestAPI()
    return TestClient(api.app)


def test_register_device(client):
    resp = client.post(
        "/devices",
        json={"name": "dev1", "ip": "1.2.3.4", "pixel_count": 10},
    )
    assert resp.status_code == 200
    assert resp.json() == {"status": "registered"}


def test_create_group(client):
    client.post("/devices", json={"name": "dev1", "ip": "1.2.3.4", "pixel_count": 10})
    resp = client.post(
        "/groups",
        json={
            "name": "g1",
            "segments": [{"device": "dev1", "start": 0, "length": 5}],
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {"status": "group created"}


def test_run_effect(monkeypatch, client):
    calls = []

    def dummy_send(self, universe, data):
        calls.append((self.target_ip, universe, data))

    monkeypatch.setattr("src.network.ArtNetClient.send_dmx", dummy_send)

    client.post("/devices", json={"name": "dev1", "ip": "1.2.3.4", "pixel_count": 5})
    resp = client.post("/devices/dev1/effect", params={"effect": "wave", "step": 1})
    assert resp.status_code == 200
    assert resp.json() == {"status": "sent"}
    assert calls


def test_group_color(monkeypatch, client):
    calls = []

    def dummy_send(self, universe, data):
        calls.append((self.target_ip, universe, data))

    monkeypatch.setattr("src.network.ArtNetClient.send_dmx", dummy_send)

    client.post("/devices", json={"name": "dev1", "ip": "1.2.3.4", "pixel_count": 5})
    client.post("/devices", json={"name": "dev2", "ip": "1.2.3.5", "pixel_count": 5})
    client.post(
        "/groups",
        json={
            "name": "g1",
            "segments": [
                {"device": "dev1", "start": 0, "length": 5},
                {"device": "dev2", "start": 0, "length": 5},
            ],
        },
    )
    resp = client.post("/groups/g1/color", json={"r": 10, "g": 20, "b": 30})
    assert resp.status_code == 200
    assert resp.json() == {"status": "sent"}
    assert len(calls) == 2


def test_group_effect(monkeypatch, client):
    calls = []

    def dummy_send(self, universe, data):
        calls.append((self.target_ip, universe, data))

    monkeypatch.setattr("src.network.ArtNetClient.send_dmx", dummy_send)

    client.post("/devices", json={"name": "dev1", "ip": "1.2.3.4", "pixel_count": 5})
    client.post("/devices", json={"name": "dev2", "ip": "1.2.3.5", "pixel_count": 5})
    client.post(
        "/groups",
        json={
            "name": "g1",
            "segments": [
                {"device": "dev1", "start": 0, "length": 5},
                {"device": "dev2", "start": 0, "length": 5},
            ],
        },
    )
    resp = client.post("/groups/g1/effect", params={"effect": "wave", "step": 0})
    assert resp.status_code == 200
    assert resp.json() == {"status": "sent"}
    assert len(calls) == 2
