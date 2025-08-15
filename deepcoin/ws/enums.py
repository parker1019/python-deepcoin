from __future__ import annotations

from enum import Enum
from typing import Final, Set


class Action(str, Enum):
    """Subscription operations.

    0: Unsubscribe ALL
    1: Subscribe
    2: Unsubscribe
    """
    UNSUB_ALL = "0"
    SUBSCRIBE = "1"
    UNSUBSCRIBE = "2"

class WSAction(str, Enum):
    """Official Deepcoin WS action names used in messages."""
    PING = "ping"
    PONG = "pong"
    # Public
    PUSH_MARKET_DATA = "PushMarketDataOverView"
    PUSH_LAST_TX = "PushMarketTrade"
    PUSH_KLINE = "PushKLine"
    PUSH_ORDERBOOK = "PushMarketOrder"
    RECV_TOPIC_ACTION = "RecvTopicAction"
    # Private
    PUSH_ORDER = "PushOrder"
    PUSH_ACCOUNT = "PushAccount"
    PUSH_POSITION = "PushPosition"
    PUSH_TRADE = "PushTrade"
    PUSH_ACCOUNT_DETAIL = "PushAccountDetail"
    PUSH_TRIGGER_ORDER = "PushTriggerOrder"

class TopicID(str, Enum):
    """Public WS Topic IDs (contracts)."""
    LAST_TRANSACTIONS = "2"
    LATEST_MARKET_DATA = "7"
    KLINE = "11"
    ORDERBOOK_25_INCREMENTAL = "25"

PUBLIC_FUTURES_WS_ENDPOINT: Final[str] = "wss://stream.deepcoin.com/public/ws"
PUBLIC_SPOT_WS_ENDPOINT: Final[str] = "wss://stream.deepcoin.com/public/spotws"

PRIVATE_WS_ENDPOINT: Final[str] = "wss://stream.deepcoin.com/v1/private"

ALLOWED_PERIODS: Final[Set[str]] = {
    "1m", "5m", "15m", "30m", "1h", "4h", "12h", "1d", "1w", "1o", "1y"
}

DEFAULT_EXCHANGE_ID: Final[str] = "DeepCoin"
