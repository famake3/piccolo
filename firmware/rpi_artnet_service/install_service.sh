#!/usr/bin/env bash
set -e

# Script to install the rpi_artnet_service as a systemd service.
# Prompts the user for configuration, sets up a virtual environment,
# and installs a systemd unit to run on boot.

read -rp "Installation directory [/opt/rpi_artnet_service]: " INSTALL_DIR
INSTALL_DIR=${INSTALL_DIR:-/opt/rpi_artnet_service}
read -rp "Service user [pi]: " SERVICE_USER
SERVICE_USER=${SERVICE_USER:-pi}
read -rp "Service name [rpi_artnet]: " SERVICE_NAME
SERVICE_NAME=${SERVICE_NAME:-rpi_artnet}

LED_TYPE=""
while [[ "$LED_TYPE" != "neopixel" && "$LED_TYPE" != "dotstar" ]]; do
  read -rp "LED type (neopixel/dotstar): " LED_TYPE
 done
read -rp "Number of pixels: " NUM_PIXELS
read -rp "Brightness [1.0]: " BRIGHTNESS
BRIGHTNESS=${BRIGHTNESS:-1.0}

if [[ "$LED_TYPE" == "neopixel" ]]; then
  read -rp "Data pin [D18]: " PIN
  PIN=${PIN:-D18}
  LED_ARGS="--led-type neopixel --num-pixels ${NUM_PIXELS} --pin ${PIN} --brightness ${BRIGHTNESS}"
  PYTHON_REQ=(adafruit-blinka adafruit-circuitpython-neopixel rpi_ws281x RPi.GPIO)
  if [[ "$SERVICE_USER" != "root" ]]; then
    echo "NeoPixel requires root privileges. Forcing service user to root."
    SERVICE_USER=root
  fi
else
  read -rp "Data pin [MOSI]: " DATA_PIN
  DATA_PIN=${DATA_PIN:-MOSI}
  read -rp "Clock pin [SCLK]: " CLOCK_PIN
  CLOCK_PIN=${CLOCK_PIN:-SCLK}
  LED_ARGS="--led-type dotstar --num-pixels ${NUM_PIXELS} --data-pin ${DATA_PIN} --clock-pin ${CLOCK_PIN} --brightness ${BRIGHTNESS}"
  PYTHON_REQ=(adafruit-blinka adafruit-circuitpython-dotstar RPi.GPIO)
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

sudo apt-get update
sudo apt-get install -y python3-lgpio

sudo mkdir -p "${INSTALL_DIR}"
sudo cp "${SCRIPT_DIR}/artnet_service.py" "${INSTALL_DIR}/"
python3 -m venv --system-site-packages "${INSTALL_DIR}/venv"
"${INSTALL_DIR}/venv/bin/pip" install --upgrade pip
"${INSTALL_DIR}/venv/bin/pip" install "${PYTHON_REQ[@]}"
sudo chown -R "${SERVICE_USER}:${SERVICE_USER}" "${INSTALL_DIR}"

SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
sudo tee "${SERVICE_FILE}" > /dev/null <<SERVICE
[Unit]
Description=Raspberry Pi Art-Net LED Service
After=network.target

[Service]
Type=simple
User=${SERVICE_USER}
WorkingDirectory=${INSTALL_DIR}
Environment=LGDIR=/tmp
ExecStart=${INSTALL_DIR}/venv/bin/python ${INSTALL_DIR}/artnet_service.py ${LED_ARGS}
Restart=on-failure

[Install]
WantedBy=multi-user.target
SERVICE

sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}.service"
sudo systemctl start "${SERVICE_NAME}.service"

echo "Service ${SERVICE_NAME}.service installed and started."
