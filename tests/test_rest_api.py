from pathlib import Path

from src.rest_api import RestAPI


def test_api_loads_config(tmp_path):
    example = Path("config.example.yaml")
    config = tmp_path / "config.yaml"
    config.write_text(example.read_text())

    api = RestAPI(config=config)
    assert "strip1" in api.devices
    assert api.devices["strip1"].ip == "192.168.1.50"
    assert "stage_left" in api.groups
    assert "strip1" in api.groups["stage_left"]
