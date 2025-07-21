from src.effects import EffectEngine, Color


def test_color_cycle():
    eng = EffectEngine(3)
    colors = [Color(1, 2, 3), Color(4, 5, 6)]
    frame = eng.color_cycle(colors, step=1)
    assert len(frame) == 3
    assert frame[0].r == 4
    assert frame[1].g == 5


def test_to_bytes():
    frame = [Color(1, 2, 3), Color(4, 5, 6)]
    data = EffectEngine.to_bytes(frame)
    assert data == b"\x01\x02\x03\x04\x05\x06"
