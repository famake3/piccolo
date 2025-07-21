"""MQTT client wrapper used for external triggers."""

from __future__ import annotations

from typing import Callable
import paho.mqtt.client as mqtt


class MQTTClient:
    """Small helper around paho-mqtt for subscribing to events."""

    def __init__(self) -> None:
        self.client = mqtt.Client()

    def connect(self, broker: str) -> None:
        """Connect to the given MQTT broker."""
        self.client.connect(broker)

    def subscribe(self, topic: str, callback: Callable[[str], None]) -> None:
        """Subscribe to a topic and register a callback for messages."""

        def _on_message(
            _client: mqtt.Client, _userdata: object, msg: mqtt.MQTTMessage
        ) -> None:
            callback(msg.payload.decode())

        self.client.subscribe(topic)
        self.client.message_callback_add(topic, _on_message)

    def start(self) -> None:
        """Start background network loop."""
        self.client.loop_start()

    def stop(self) -> None:
        """Stop background network loop."""
        self.client.loop_stop()

    def publish(self, topic: str, payload: str) -> None:
        self.client.publish(topic, payload)
