from __future__ import annotations

from typing import Callable, Dict, Any
import logging

from .enums import TopicID
from .exceptions import DeepcoinCallbackError

logger = logging.getLogger(__name__)


class MessageDispatcher:
    """Dispatches Deepcoin WebSocket messages to the appropriate user callback."""

    def __init__(self):
        # action -> callback
        self._callbacks: Dict[str, Callable[[dict], None]] = {}

    def register(self, action: str, callback: Callable[[dict], None]):
        """Register a callback function for a specific topic_id (str or TopicID enum)."""
        if not callable(callback):
            raise DeepcoinCallbackError(f"Callback for action {action} is not callable")
        self._callbacks[action] = callback
        logger.debug(f"Registered callback for action: {action}")

    def unregister(self, action: str):
        """Remove the callback associated with a topic_id."""
        self._callbacks.pop(action, None)
        logger.debug(f"Unregistered callback for action: {action}")

    def dispatch(self, message: dict):
        """
        Dispatch an incoming message to the registered callback.
        Expected format:
        {
            "TopicID": "11",
            "Data": { ... }
        }
        """
        action = message.get("action")
        if not action:
            logger.debug(f"[DISPATCH] Ignored message without 'action': {message}")
            return

        callback = self._callbacks.get(action)
        if not callback:
            logger.warning(f"No callback registered for action: {action}")
            return

        try:
            callback(message)
        except Exception as e:
            logger.exception(f"Error in callback for action {action}: {e}")
            raise DeepcoinCallbackError(str(e)) from e

    def list_registered(self) -> list[str]:
        """Returns the list of registered topic IDs."""
        return list(self._callbacks.keys())
