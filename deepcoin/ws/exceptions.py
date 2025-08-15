from __future__ import annotations


class DeepcoinWebSocketError(Exception):
    """Base class for all Deepcoin WebSocket errors."""


class DeepcoinWebSocketConnectionError(DeepcoinWebSocketError):
    """Raised when a WS connection cannot be established or maintained."""


class DeepcoinWebSocketProtocolError(DeepcoinWebSocketError):
    """Raised when server/client messages violate expected protocol/spec."""


class DeepcoinSubscriptionError(DeepcoinWebSocketError):
    """Raised when a subscription/unsubscription request fails or is invalid."""


class DeepcoinCallbackError(DeepcoinWebSocketError):
    """Raised when a user-provided callback raises or is not callable."""
