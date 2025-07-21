from src.network import ArtNetClient


def test_build_packet():
    client = ArtNetClient("127.0.0.1")
    data = b"\x01\x02\x03"
    packet = client._build_packet(1, data)
    assert packet.startswith(b"Art-Net\x00")
    # Universe is big endian two bytes
    assert packet[8:10] == b"\x00\x01"
    assert packet[10:] == data
