import builtins
from pathlib import Path

from src.config import load_config
from src.devices import LEDDevice


def test_load_config(tmp_path):
    # copy example config to temp directory to avoid modifying repo file
    example = Path("config.example.yaml")
    tmp_config = tmp_path / "config.yaml"
    tmp_config.write_text(example.read_text())

    config = load_config(tmp_config)
    assert len(config.devices) == 2
    first = config.devices[0]
    assert isinstance(first, LEDDevice)
    assert first.name == "strip1"
    assert first.ip == "192.168.1.50"
    assert first.pixel_count == 150
    assert first.universe == 0
