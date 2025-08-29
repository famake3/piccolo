// Particle Photon Art-Net to NeoPixel controller
//
// This sketch listens for Art-Net packets on UDP port 6454 and maps the DMX
// payload directly to a strip of NeoPixels.  Each pixel consumes three DMX
// channels in RGB order.
//
// Required libraries (install via the Particle IDE):
//   * neopixel
//
// Configure the pixel pin and number of LEDs to match your hardware.

#include "Particle.h"
#include "neopixel.h"

// ----- Configuration -----
#define PIXEL_PIN   D2          // Data pin for the NeoPixel strip
#define PIXEL_COUNT 60          // Number of pixels on the strip
#define PIXEL_TYPE  WS2812B     // Pixel type (see neopixel library docs)

// Art-Net constants
const uint16_t ARTNET_PORT = 6454;
const uint16_t OP_DMX = 0x5000;              // Opcode for ArtDMX packet
const size_t  ARTNET_HEADER = 18;            // Size of Art-Net header
const size_t  MAX_DMX = 512;                 // Maximum DMX payload

Adafruit_NeoPixel strip(PIXEL_COUNT, PIXEL_PIN, PIXEL_TYPE);
UDP Udp;
uint8_t packet[ARTNET_HEADER + MAX_DMX];
char ipAddress[24];

void setup()
{
    strip.begin();
    strip.show(); // Initialize all pixels to 'off'
    Udp.begin(ARTNET_PORT);

    IPAddress ip = WiFi.localIP();
    snprintf(ipAddress, sizeof(ipAddress), "%u.%u.%u.%u", ip[0], ip[1], ip[2], ip[3]);
    Particle.variable("ip", ipAddress);
}

void loop()
{
    int packetSize = Udp.parsePacket();
    if (packetSize <= 0) {
        return;
    }

    int len = Udp.read(packet, sizeof(packet));
    if (len < ARTNET_HEADER) {
        return; // not a valid Art-Net packet
    }

    // Validate header "Art-Net" and opcode
    if (memcmp(packet, "Art-Net\0", 8) != 0) {
        return;
    }
    uint16_t opcode = packet[8] | (packet[9] << 8);
    if (opcode != OP_DMX) {
        return;
    }

    uint16_t dmxLength = (packet[16] << 8) | packet[17];
    if (dmxLength > MAX_DMX) {
        dmxLength = MAX_DMX;
    }
    const uint8_t* dmxData = packet + ARTNET_HEADER;

    for (int i = 0; i < PIXEL_COUNT; i++)
    {
        int index = i * 3;
        uint8_t r = index < dmxLength     ? dmxData[index]     : 0;
        uint8_t g = index + 1 < dmxLength ? dmxData[index + 1] : 0;
        uint8_t b = index + 2 < dmxLength ? dmxData[index + 2] : 0;
        strip.setPixelColor(i, r, g, b);
    }
    strip.show();
}

