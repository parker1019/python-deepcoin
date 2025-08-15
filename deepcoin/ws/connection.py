import threading
import time
import json
import websocket
import logging
from typing import Callable, Optional

from .exceptions import (
    DeepcoinWebSocketConnectionError,
    DeepcoinWebSocketProtocolError,
)

logger = logging.getLogger(__name__)


class WebSocketConnection:
    """
    Handles a single WebSocket connection for Deepcoin.
    Includes:
        - automatic reconnection
        - optional heartbeat ping
        - on_message callback dispatch
    """

    def __init__(
        self,
        url: str,
        on_message: Callable[[dict], None],
        on_open: Optional[Callable[[], None]] = None,
        on_close: Optional[Callable[[], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        ping_interval: float = 15.0,
        reconnect: bool = True,
        reconnect_delay: float = 5.0,
    ):
        self.url = url
        self.ws: Optional[websocket.WebSocketApp] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        self.on_message = on_message
        self.on_open = on_open
        self.on_close = on_close
        self.on_error = on_error

        self.ping_interval = ping_interval
        self.reconnect = reconnect
        self.reconnect_delay = reconnect_delay

        self._last_pong_time = time.time()

    def _on_message(self, ws, message: str):
        try:
            data = json.loads(message)
            self.on_message(data)
        except Exception as e:
            logger.exception("Error while parsing WebSocket message.")
            raise DeepcoinWebSocketProtocolError(str(e))

    def _on_open(self, ws):
        logger.info("WebSocket opened.")
        self._last_pong_time = time.time()
        if self.on_open:
            self.on_open()

    def _on_close(self, ws, close_status_code, close_msg):
        logger.warning(f"WebSocket closed: {close_status_code} - {close_msg}")
        if self.on_close:
            self.on_close()

    def _on_error(self, ws, error: Exception):
        logger.error(f"WebSocket error: {error}")
        if self.on_error:
            self.on_error(error)

    def _on_pong(self, ws, message):
        logger.debug("PONG received.")
        self._last_pong_time = time.time()

    def _run_forever(self):
        while not self._stop_event.is_set():
            self.ws = websocket.WebSocketApp(
                self.url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_close=self._on_close,
                on_error=self._on_error,
                on_pong=self._on_pong,
            )

            try:
                self.ws.run_forever(
                    ping_interval=self.ping_interval,
                    ping_timeout=None,
                    ping_payload="ping",
                )
            except Exception as e:
                logger.exception("Unexpected WebSocket failure.")
                if self.on_error:
                    self.on_error(e)

            if not self.reconnect:
                logger.info("Reconnect disabled. Exiting WS loop.")
                break

            logger.info(f"Reconnecting in {self.reconnect_delay} seconds...")
            time.sleep(self.reconnect_delay)

    def start(self):
        """Start the WebSocket connection in a separate thread."""
        if self._thread and self._thread.is_alive():
            logger.warning("WebSocket thread already running.")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_forever, daemon=True)
        self._thread.start()
        logger.info("WebSocket thread started.")

    def stop(self):
        """Stop the WebSocket connection gracefully."""
        self._stop_event.set()
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("WebSocket connection stopped.")

    def send(self, message: dict):
        """Send a message (JSON-serializable dict) over the socket."""
        if self.ws and self.ws.sock and self.ws.sock.connected:
            try:
                payload = json.dumps(message)
                self.ws.send(payload)
                logger.debug(f"Sent: {payload}")
            except Exception as e:
                logger.exception("Failed to send WS message.")
                raise DeepcoinWebSocketConnectionError(str(e))
        else:
            raise DeepcoinWebSocketConnectionError("WebSocket is not connected.")

    def is_alive(self) -> bool:
        sock = getattr(self.ws, 'sock', None) if self.ws else None
        return sock is not None and getattr(sock, 'connected', False)
