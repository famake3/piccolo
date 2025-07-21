from src.network import ArtNetClient


def test_build_packet():
    client = ArtNetClient("127.0.0.1")
    data = b"\x01\x02\x03"
    packet = client._build_packet(1, data)
    assert packet.startswith(b"Art-Net\x00")
    # OpCode should be ArtDMX (0x5000) little endian
    assert packet[8:10] == b"\x00\x50"
    # Protocol version 14
    assert packet[10:12] == b"\x00\x0e"
    # Sequence and physical
    assert packet[12:14] == b"\x00\x00"
    # Universe little endian
    assert packet[14:16] == b"\x01\x00"
    # Payload length big endian
    assert packet[16:18] == b"\x00\x03"
    assert packet[18:] == data
