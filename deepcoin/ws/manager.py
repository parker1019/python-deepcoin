from __future__ import annotations

import logging
from typing import Callable, Optional

from .connection import WebSocketConnection
from .dispatcher import MessageDispatcher
from . import topics
from .enums import TopicID, PUBLIC_FUTURES_WS_ENDPOINT, PRIVATE_WS_ENDPOINT

logger = logging.getLogger(__name__)


class DeepcoinWebsocketManager:
    """
    WebSocket manager for Deepcoin public topics.
    Handles connection, subscription, and callback dispatch.
    """

    def __init__(self, endpoint: str = PUBLIC_FUTURES_WS_ENDPOINT):
        self._endpoint = endpoint
        self._dispatcher = MessageDispatcher()
        self._connection = WebSocketConnection(
            url=self._endpoint,
            on_message=self._on_message,
            on_open=self._on_open,
            on_close=self._on_close,
            on_error=self._on_error,
        )
        self._local_no_counter = 1000  # for generating unique local_no

    # -------------------------
    # WebSocket lifecycle
    # -------------------------

    def start(self):
        """Start WebSocket background thread."""
        logger.info("Starting Deepcoin WS manager.")
        self._connection.start()

    def stop(self):
        """Stop WebSocket connection and thread."""
        logger.info("Stopping Deepcoin WS manager.")
        self._connection.stop()

    def is_alive(self) -> bool:
        return self._connection.is_alive()

    # -------------------------
    # Callback registration
    # -------------------------

    def register_callback(self, topic: TopicID | str, callback: Callable[[dict], None]):
        """Register a user callback for a specific TopicID."""
        self._dispatcher.register(topic, callback)

    def unregister_callback(self, topic: TopicID | str):
        self._dispatcher.unregister(topic)

    # -------------------------
    # Subscription helpers
    # -------------------------

    def subscribe_market_data(self, symbol: str):
        """Subscribe to market ticker/overview (TopicID=7)."""
        payload = topics.sub_latest_market_data(symbol, local_no=self._next_local_no())
        self._connection.send(payload)

    def subscribe_trade(self, symbol: str):
        """Subscribe to last trade updates (TopicID=2)."""
        payload = topics.sub_last_transactions(symbol, local_no=self._next_local_no())
        self._connection.send(payload)

    def subscribe_kline(self, symbol: str, period: str):
        """Subscribe to Kline updates (TopicID=11)."""
        payload = topics.sub_kline(symbol, period, local_no=self._next_local_no())
        self._connection.send(payload)

    def subscribe_orderbook(self, symbol: str):
        """Subscribe to 25-depth incremental orderbook (TopicID=25)."""
        payload = topics.sub_orderbook_25_incremental(symbol, local_no=self._next_local_no())
        self._connection.send(payload)

    def unsubscribe(self, topic_id: TopicID | str, symbol: str, period: Optional[str] = None):
        """Unsubscribe from a topic."""
        payload = topics.unsub(
            topic_id=topic_id,
            symbol=symbol,
            local_no=self._next_local_no(),
            period=period,
        )
        self._connection.send(payload)

    def unsubscribe_all(self):
        """Unsubscribe from all topics."""
        payload = topics.unsub_all(local_no=self._next_local_no())
        self._connection.send(payload)

    # -------------------------
    # Internal handlers
    # -------------------------

    def _on_message(self, msg: dict):
        self._dispatcher.dispatch(msg)

    def _on_open(self):
        logger.info("WebSocket connected.")

    def _on_close(self):
        logger.info("WebSocket disconnected.")

    def _on_error(self, error: Exception):
        logger.error(f"WebSocket error: {error}")

    def _next_local_no(self) -> int:
        """Generate unique LocalNo for each subscription."""
        self._local_no_counter += 1
        return self._local_no_counter
