from __future__ import annotations

import logging
from typing import Callable, Optional

from .connection import WebSocketConnection
from .dispatcher import MessageDispatcher
from .enums import PUBLIC_FUTURES_WS_ENDPOINT

logger = logging.getLogger(__name__)


class DeepcoinWebSocketStream:
    """
    Represents a single WebSocket stream (connection + dispatcher).
    Can be managed individually, or wrapped in a higher-level manager.
    """

    def __init__(
        self,
        endpoint: str = PUBLIC_FUTURES_WS_ENDPOINT,
        ping_interval: float = 15.0,
        reconnect: bool = True,
    ):
        self._endpoint = endpoint
        self._dispatcher = MessageDispatcher()
        self._connection = WebSocketConnection(
            url=self._endpoint,
            on_message=self._on_message,
            on_open=self._on_open,
            on_close=self._on_close,
            on_error=self._on_error,
            ping_interval=ping_interval,
            reconnect=reconnect,
        )
        self._local_no_counter = 1000

    def start(self):
        """Starts this stream's connection."""
        logger.info(f"Starting WS stream to {self._endpoint}")
        self._connection.start()

    def stop(self):
        """Stops the WebSocket stream."""
        self._connection.stop()

    def send(self, message: dict):
        """Send raw payload over this WebSocket."""
        self._connection.send(message)

    def is_alive(self) -> bool:
        return self._connection.is_alive()

    def register(self, topic_id: str, callback: Callable[[dict], None]):
        """Register a callback for a given TopicID."""
        self._dispatcher.register(topic_id, callback)

    def unregister(self, topic_id: str):
        self._dispatcher.unregister(topic_id)

    def _on_message(self, msg: dict):
        self._dispatcher.dispatch(msg)

    def _on_open(self):
        logger.info("Stream connected.")

    def _on_close(self):
        logger.info("Stream disconnected.")

    def _on_error(self, error: Exception):
        logger.error(f"Stream error: {error}")

    def next_local_no(self) -> int:
        self._local_no_counter += 1
        return self._local_no_counter
