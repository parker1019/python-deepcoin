from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .enums import (
    Action,
    TopicID,
    ALLOWED_PERIODS,
    DEFAULT_EXCHANGE_ID,
)


@dataclass(frozen=True)
class SendTopicAction:
    """A convenience builder for the WS 'SendTopicAction' payload.

    Official format (top-level):
    {
      "SendTopicAction": {
        "Action": "1",
        "FilterValue": "DeepCoin_BTCUSDT[_<period>]",
        "LocalNo": 9,
        "ResumeNo": -2,
        "TopicID": "2"
      }
    }
    """
    action: Action
    topic_id: str
    filter_value: str
    local_no: int
    resume_no: int = -2  # -1/-2 per endpoint; overridden by specific builders
    business_no: Optional[int] = None

    def to_payload(self) -> Dict[str, Any]:
        payload = {
            "SendTopicAction": {
                "Action": self.action.value,
                "FilterValue": self.filter_value,
                "LocalNo": self.local_no,
                "ResumeNo": self.resume_no,
                "TopicID": self.topic_id,
            }
        }
        if self.business_no is not None:
            payload["SendTopicAction"]["BusinessNo"] = self.business_no
        return payload


# ---------------------------
# FilterValue helpers
# ---------------------------

def build_filter_value(
    symbol: str,
    *,
    exchange_id: str = DEFAULT_EXCHANGE_ID,
    period: Optional[str] = None,
) -> str:
    """Construct FilterValue as '<ExchangeID>_<InstrumentID>[_<Period>]'.

    Raises:
        ValueError: if period is provided but not allowed by spec.
    """
    if period is None:
        return f"{exchange_id}_{symbol}"
    if period not in ALLOWED_PERIODS:
        raise ValueError(f"Unsupported period '{period}'. Allowed: {sorted(ALLOWED_PERIODS)}")
    return f"{exchange_id}_{symbol}_{period}"


# ---------------------------
# Builders for common topics
# ---------------------------

def sub_last_transactions(
    symbol: str,
    *,
    local_no: int,
    exchange_id: str = DEFAULT_EXCHANGE_ID,
    resume_no: int = -2,
    business_no: Optional[int] = None,
) -> Dict[str, Any]:
    """TopicID=2 last transactions"""
    sta = SendTopicAction(
        action=Action.SUBSCRIBE,
        topic_id=TopicID.LAST_TRANSACTIONS.value,
        filter_value=build_filter_value(symbol, exchange_id=exchange_id),
        local_no=local_no,
        resume_no=resume_no,
        business_no=business_no,
    )
    return sta.to_payload()


def sub_latest_market_data(
    symbol: str,
    *,
    local_no: int,
    exchange_id: str = DEFAULT_EXCHANGE_ID,
    resume_no: int = -2,
    business_no: Optional[int] = None,
) -> Dict[str, Any]:
    """TopicID=7 latest market data"""
    sta = SendTopicAction(
        action=Action.SUBSCRIBE,
        topic_id=TopicID.LATEST_MARKET_DATA.value,
        filter_value=build_filter_value(symbol, exchange_id=exchange_id),
        local_no=local_no,
        resume_no=resume_no,
        business_no=business_no,
    )
    return sta.to_payload()


def sub_kline(
    symbol: str,
    period: str,
    *,
    local_no: int,
    exchange_id: str = DEFAULT_EXCHANGE_ID,
    resume_no: int = -1,
    business_no: Optional[int] = None,
) -> Dict[str, Any]:
    """TopicID=11 K line"""
    sta = SendTopicAction(
        action=Action.SUBSCRIBE,
        topic_id=TopicID.KLINE.value,
        filter_value=build_filter_value(symbol, exchange_id=exchange_id, period=period),
        local_no=local_no,
        resume_no=resume_no,
        business_no=business_no,
    )
    return sta.to_payload()


def sub_orderbook_25_incremental(
    symbol: str,
    *,
    local_no: int,
    exchange_id: str = DEFAULT_EXCHANGE_ID,
    resume_no: int = -1,
    business_no: Optional[int] = None,
) -> Dict[str, Any]:
    """TopicID=25 25 order book incremental updates"""
    sta = SendTopicAction(
        action=Action.SUBSCRIBE,
        topic_id=TopicID.ORDERBOOK_25_INCREMENTAL.value,
        filter_value=build_filter_value(symbol, exchange_id=exchange_id),
        local_no=local_no,
        resume_no=resume_no,
        business_no=business_no,
    )
    return sta.to_payload()


# ---------------------------
# Unsubscribe helpers
# ---------------------------

def unsub(
    topic_id: TopicID | str,
    symbol: str,
    *,
    local_no: int,
    exchange_id: str = DEFAULT_EXCHANGE_ID,
    period: Optional[str] = None,
    resume_no: int = 0,
    business_no: Optional[int] = None,
) -> Dict[str, Any]:
    """Unsubscribe from a specific topic/symbol combination."""
    sta = SendTopicAction(
        action=Action.UNSUBSCRIBE,
        topic_id=topic_id if isinstance(topic_id, str) else topic_id.value,
        filter_value=build_filter_value(symbol, exchange_id=exchange_id, period=period),
        local_no=local_no,
        resume_no=resume_no,
        business_no=business_no,
    )
    return sta.to_payload()


def unsub_all(
    *,
    local_no: int,
    resume_no: int = 0,
) -> Dict[str, Any]:
    """Unsubscribe ALL topics in the current session."""
    sta = SendTopicAction(
        action=Action.UNSUB_ALL,
        topic_id="",
        filter_value="",
        local_no=local_no,
        resume_no=resume_no,
    )
    return sta.to_payload()
