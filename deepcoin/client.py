from typing import Dict, Optional, Any, List
import requests

from .base_client import BaseClient
from .exceptions import (
    DeepcoinAPIException,
    DeepcoinRequestException,
)


class Client(BaseClient):
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        passphrase: Optional[str] = None,
        requests_params: Optional[Dict[str, Any]] = None,
        base_endpoint: str = BaseClient.BASE_ENDPOINT_DEFAULT,
    ):
        super().__init__(
            api_key=api_key,
            api_secret=api_secret,
            passphrase=passphrase,
            requests_params=requests_params,
            base_endpoint=base_endpoint,
        )

    def _init_session(self) -> requests.Session:
        headers = self._get_headers()
        session = requests.session()
        session.headers.update(headers)
        return session

    def _request(
        self, method: str, uri: str, signed: bool = False, force_params: bool = False, **kwargs
    ):
        headers = {}
        if method.upper() in ["POST", "PUT", "DELETE"]:
            headers.update({"Content-Type": "application/json"})

        if "data" in kwargs and isinstance(kwargs["data"], dict):
            if "headers" in kwargs["data"]:
                headers.update(kwargs["data"]["headers"])
                del kwargs["data"]["headers"]
        kwargs = self._get_request_kwargs(method, signed, force_params, **kwargs)

        data = kwargs.pop("data", None)
        if method.upper() == "GET":
            kwargs["params"] = data
        else:
            kwargs["json"] = data

        self.response = getattr(self.session, method)(uri, headers=headers, **kwargs)
        return self._handle_response(self.response)

    @staticmethod
    def _handle_response(response: requests.Response):
        """Handle API responses from the Deepcoin server."""
        if not (200 <= response.status_code < 300):
            raise DeepcoinAPIException(response, response.status_code, response.text)

        if response.text == "":
            return {}

        try:
            data = response.json()
        except ValueError:
            raise DeepcoinRequestException(f"Invalid Response: {response.text}")
        
        raw_code = data.get("code") or data.get("error_code")
        if raw_code is None:
            return data

        if str(raw_code) in ("0", "00000"):
            return data

        raise DeepcoinAPIException(response, response.status_code, response.text)

    def _get(self, path, signed=False, version="v1", **kwargs):
        return self._request_api("get", path, signed, version, **kwargs)

    def _post(self, path, signed=False, version="v1", **kwargs):
        return self._request_api("post", path, signed, version, **kwargs)

    def _put(self, path, signed=False, version="v1", **kwargs):
        return self._request_api("put", path, signed, version, **kwargs)

    def _delete(self, path, signed=False, version="v1", **kwargs):
        return self._request_api("delete", path, signed, version, **kwargs)

    def _request_api(self, method, path: str, signed: bool = False, version="v1", **kwargs):
        uri = self._create_api_uri(path, version)
        return self._request(method, uri, signed, **kwargs)
    
    # === Account APIs ===

    def get_balances(self, inst_type: str, ccy: Optional[str] = None):
        """
        GET /deepcoin/account/balances
        Get account asset list and balance info.
        inst_type: "SPOT" or "SWAP"
        ccy: optional currency (e.g., "USDT")
        """
        params = {"instType": inst_type}
        if ccy:
            params["ccy"] = ccy
        return self._get("/deepcoin/account/balances", signed=True, data=params)

    def get_bills(
        self,
        inst_type: str,
        ccy: Optional[str] = None,
        type: Optional[str] = None,
        after: Optional[int] = None,
        before: Optional[int] = None,
        limit: Optional[int] = None,
    ):
        """
        GET /deepcoin/account/bills
        Get account transaction history.
        type: 2=income, 3=outcome, 4=transfer-in, 5=fee, etc.
        """
        params = {"instType": inst_type}
        if ccy:
            params["ccy"] = ccy
        if type:
            params["type"] = type
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        if limit:
            params["limit"] = limit

        return self._get("/deepcoin/account/bills", signed=True, data=params)

    def get_positions(self, inst_type: str, inst_id: Optional[str] = None):
        """
        GET /deepcoin/account/positions
        Get positions list.
        inst_type: "SPOT" or "SWAP"
        """
        params = {"instType": inst_type}
        if inst_id:
            params["instId"] = inst_id
        return self._get("/deepcoin/account/positions", signed=True, data=params)

    def set_leverage(self, inst_id: Optional[str], lever: str, mgn_mode: str, mrg_position: str):
        """
        POST /deepcoin/account/set-leverage
        Set leverage for a given instrument.
        mgn_mode: "cross" or "isolated"
        mrg_position: "merge" or "split"
        """
        payload = {
            "lever": lever,
            "mgnMode": mgn_mode,
            "mrgPosition": mrg_position
        }
        if inst_id:
            payload["instId"] = inst_id
        return self._post("/deepcoin/account/set-leverage", signed=True, data=payload)

    # === Market APIs ===

    def get_order_book(self, inst_id: str, sz: int):
        """
        GET /deepcoin/market/books
        Get order book depth.
        - inst_id: e.g. "BTC-USDT-SWAP"
        - sz: number of depth levels (1..400)
        """
        if not inst_id:
            raise ValueError("inst_id is required")
        if not isinstance(sz, int) or not (1 <= sz <= 400):
            raise ValueError("sz must be an integer between 1 and 400")

        params = {"instId": inst_id, "sz": sz}
        return self._get("/deepcoin/market/books", signed=False, data=params)

    def get_candles(
        self,
        inst_id: str,
        bar: str = "1m",
        after: Optional[int] = None,
        limit: Optional[int] = None,
    ):
        """
        GET /deepcoin/market/candles
        K-line data.
        - bar: one of {"1m","5m","15m","30m","1H","4H","12H","1D","1W","1M","1Y"}
        - after: request content before this timestamp (ms); use previous response's ts for paging
        - limit: max 300 (default 100)
        """
        if not inst_id:
            raise ValueError("inst_id is required")

        allowed_bars = {"1m","5m","15m","30m","1H","4H","12H","1D","1W","1M","1Y"}
        if bar not in allowed_bars:
            raise ValueError(f"bar must be one of {sorted(allowed_bars)}")

        params: Dict[str, Any] = {"instId": inst_id, "bar": bar}
        if after is not None:
            params["after"] = int(after)
        if limit is not None:
            params["limit"] = int(limit)

        return self._get("/deepcoin/market/candles", signed=False, data=params)

    def get_instruments(
        self,
        inst_type: str,
        uly: Optional[str] = None,
        inst_id: Optional[str] = None,
    ):
        """
        GET /deepcoin/market/instruments
        List tradable products.
        - inst_type: "SPOT" or "SWAP"
        - uly: index symbol (perpetual only)
        - inst_id: product id
        """
        if inst_type not in {"SPOT", "SWAP"}:
            raise ValueError('inst_type must be "SPOT" or "SWAP"')

        params: Dict[str, Any] = {"instType": inst_type}
        if uly:
            params["uly"] = uly
        if inst_id:
            params["instId"] = inst_id

        return self._get("/deepcoin/market/instruments", signed=False, data=params)

    def get_tickers(self, inst_type: str, uly: Optional[str] = None):
        """
        GET /deepcoin/market/tickers
        Market tickers.
        - inst_type: "SPOT" or "SWAP"
        - uly: index symbol (perpetual only)
        """
        if inst_type not in {"SPOT", "SWAP"}:
            raise ValueError('inst_type must be "SPOT" or "SWAP"')

        params: Dict[str, Any] = {"instType": inst_type}
        if uly:
            params["uly"] = uly

        return self._get("/deepcoin/market/tickers", signed=False, data=params)

    # === Trade APIs ===

    def place_order(
        self,
        inst_id: str,
        td_mode: str,
        side: str,
        ord_type: str,
        sz: str,
        ccy: Optional[str] = None,
        cl_ord_id: Optional[str] = None,
        tag: Optional[str] = None,
        pos_side: Optional[str] = None,
        mrg_position: Optional[str] = None,
        close_pos_id: Optional[str] = None,
        px: Optional[str] = None,
        reduce_only: Optional[bool] = None,
        tgt_ccy: Optional[str] = None,
        tp_trigger_px: Optional[str] = None,
        sl_trigger_px: Optional[str] = None,
    ):
        """
        POST /deepcoin/trade/order

        Place a new order.

        Required:
          - inst_id: product ID, e.g. "BTC-USDT-SWAP" or "BTC-USDT"
          - td_mode: "isolated" | "cross" | "cash" (spot)
          - side: "buy" | "sell"
          - ord_type: "market" | "limit" | "post_only" | "ioc"
          - sz: order size (string)

        Notes:
          - For SWAP instruments, `pos_side` (long|short) and `mrg_position` (merge|split) are required.
          - `px` is required for `limit` and `post_only`.
          - `tgt_ccy` only applies to spot market orders ("base_ccy" | "quote_ccy").
        """
        if not inst_id:
            raise ValueError("inst_id is required")
        if td_mode not in {"isolated", "cross", "cash"}:
            raise ValueError('td_mode must be one of {"isolated","cross","cash"}')
        if side not in {"buy", "sell"}:
            raise ValueError('side must be "buy" or "sell"')
        if ord_type not in {"market", "limit", "post_only", "ioc"}:
            raise ValueError('ord_type must be one of {"market","limit","post_only","ioc"}')
        if not sz:
            raise ValueError("sz is required")
        if ord_type in {"limit", "post_only"} and not px:
            raise ValueError("px is required for limit/post_only orders")

        is_swap = "-SWAP" in inst_id.upper()
        if is_swap:
            if not pos_side:
                raise ValueError("pos_side is required for SWAP instruments (long|short)")
            if mrg_position not in {"merge", "split"}:
                raise ValueError('mrg_position is required for SWAP instruments and must be {"merge","split"}')

        if tgt_ccy and tgt_ccy not in {"base_ccy", "quote_ccy"}:
            raise ValueError('tgt_ccy must be "base_ccy" or "quote_ccy"')

        payload: Dict[str, Any] = {
            "instId": inst_id,
            "tdMode": td_mode,
            "side": side,
            "ordType": ord_type,
            "sz": sz,
        }

        if ccy is not None:
            payload["ccy"] = ccy
        if cl_ord_id is not None:
            payload["clOrdId"] = cl_ord_id
        if tag is not None:
            payload["tag"] = tag
        if pos_side is not None:
            payload["posSide"] = pos_side
        if mrg_position is not None:
            payload["mrgPosition"] = mrg_position
        if close_pos_id is not None:
            payload["closePosId"] = close_pos_id
        if px is not None:
            payload["px"] = px
        if reduce_only is not None:
            payload["reduceOnly"] = reduce_only
        if tgt_ccy is not None:
            payload["tgtCcy"] = tgt_ccy
        if tp_trigger_px is not None:
            payload["tpTriggerPx"] = tp_trigger_px
        if sl_trigger_px is not None:
            payload["slTriggerPx"] = sl_trigger_px

        return self._post("/deepcoin/trade/order", signed=True, data=payload)

    def replace_order(
        self,
        order_sys_id: str,
        price: Optional[float] = None,
        volume: Optional[int] = None,
    ):
        """
        POST /deepcoin/trade/replace-order
        Modify price and/or size of an existing order.

        Required:
          - order_sys_id: order system ID

        Optionals:
          - price: new price (float)
          - volume: new size (integer, contracts)
        """
        if not order_sys_id:
            raise ValueError("order_sys_id is required")
        if price is None and volume is None:
            raise ValueError("At least one of price or volume must be provided")

        payload: Dict[str, Any] = {"OrderSysID": str(order_sys_id)}
        if price is not None:
            payload["price"] = float(price)
        if volume is not None:
            payload["volume"] = int(volume)

        return self._post("/deepcoin/trade/replace-order", signed=True, data=payload)

    def cancel_order(self, inst_id: str, ord_id: str):
        """
        POST /deepcoin/trade/cancel-order
        Cancel a single open order.

        Required:
          - inst_id: product ID
          - ord_id: order ID
        """
        if not inst_id:
            raise ValueError("inst_id is required")
        if not ord_id:
            raise ValueError("ord_id is required")

        payload = {"instId": inst_id, "ordId": ord_id}
        return self._post("/deepcoin/trade/cancel-order", signed=True, data=payload)

    def batch_cancel_order(self, order_sys_ids: List[str]):
        """
        POST /deepcoin/trade/batch-cancel-order
        Batch-cancel up to 50 limit orders.

        Required:
          - order_sys_ids: list of order system IDs (max 50)
        """
        if not order_sys_ids:
            raise ValueError("order_sys_ids is required")
        if len(order_sys_ids) > 50:
            raise ValueError("order_sys_ids cannot exceed 50 items")

        payload = {"orderSysIDs": order_sys_ids}
        return self._post("/deepcoin/trade/batch-cancel-order", signed=True, data=payload)

    def cancel_all_swap_orders(
        self,
        instrument_id: str,
        product_group: str,
        is_cross_margin: int,
        is_merge_mode: int,
    ):
        """
        POST /deepcoin/trade/swap/cancel-all
        One-click cancel (contracts only). Cancels limit orders for a given instrument.

        Required:
          - instrument_id: e.g. "BTCUSDT"
          - product_group: "Swap" (coin) or "SwapU" (USDT)
          - is_cross_margin: 1 (cross) or 0 (isolated)
          - is_merge_mode: 1 (merge) or 0 (split)
        """
        if not instrument_id:
            raise ValueError("instrument_id is required")
        if product_group not in {"Swap", "SwapU"}:
            raise ValueError('product_group must be "Swap" or "SwapU"')
        if is_cross_margin not in (0, 1):
            raise ValueError("is_cross_margin must be 0 or 1")
        if is_merge_mode not in (0, 1):
            raise ValueError("is_merge_mode must be 0 or 1")

        payload = {
            "InstrumentID": instrument_id,
            "ProductGroup": product_group,
            "IsCrossMargin": int(is_cross_margin),
            "IsMergeMode": int(is_merge_mode),
        }
        return self._post("/deepcoin/trade/swap/cancel-all", signed=True, data=payload)

    def get_fills(
        self,
        inst_type: str,
        inst_id: Optional[str] = None,
        ord_id: Optional[str] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        begin: Optional[int] = None,
        end: Optional[int] = None,
        limit: Optional[int] = None,
    ):
        """
        GET /deepcoin/trade/fills
        Get fills (trade details).

        Required:
        - inst_type: "SPOT" or "SWAP"

        Optionals:
        - inst_id: instrument ID
        - ord_id: order ID
        - after: older page cursor (billId)
        - before: newer page cursor (billId)
        - begin: start timestamp in ms
        - end: end timestamp in ms
        - limit: number of records (1–100, default 100)
        """
        if inst_type not in {"SPOT", "SWAP"}:
            raise ValueError('inst_type must be "SPOT" or "SWAP"')
        if limit is not None and (limit < 1 or limit > 100):
            raise ValueError("limit must be within 1..100")

        params: Dict[str, Any] = {"instType": inst_type}
        if inst_id is not None:
            params["instId"] = str(inst_id)
        if ord_id is not None:
            params["ordId"] = str(ord_id)
        if after is not None:
            params["after"] = str(after)
        if before is not None:
            params["before"] = str(before)
        if begin is not None:
            params["begin"] = int(begin)
        if end is not None:
            params["end"] = int(end)
        if limit is not None:
            params["limit"] = int(limit)

        return self._get("/deepcoin/trade/fills", signed=True, data=params)

    def get_order_by_id(
        self,
        inst_id: str,
        ord_id: str,
    ):
        """
        GET /deepcoin/trade/orderByID
        Get a live order by ID.

        Required:
        - inst_id: instrument ID
        - ord_id: order ID
        """
        if not inst_id:
            raise ValueError("inst_id is required")
        if not ord_id:
            raise ValueError("ord_id is required")

        params: Dict[str, Any] = {
            "instId": str(inst_id),
            "ordId": str(ord_id),
        }
        return self._get("/deepcoin/trade/orderByID", signed=True, data=params)

    def get_finished_order_by_id(
        self,
        inst_id: str,
        ord_id: str,
    ):
        """
        GET /deepcoin/trade/finishOrderByID
        Get a historical (finished) order by ID.

        Required:
        - inst_id: instrument ID
        - ord_id: order ID
        """
        if not inst_id:
            raise ValueError("inst_id is required")
        if not ord_id:
            raise ValueError("ord_id is required")

        params: Dict[str, Any] = {
            "instId": str(inst_id),
            "ordId": str(ord_id),
        }
        return self._get("/deepcoin/trade/finishOrderByID", signed=True, data=params)

    def get_orders_history(
        self,
        inst_type: str,
        inst_id: Optional[str] = None,
        ord_type: Optional[str] = None,
        state: Optional[str] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        limit: Optional[int] = None,
        ord_id: Optional[str] = None,
    ):
        """
        GET /deepcoin/trade/orders-history
        Get historical orders list.

        Required:
        - inst_type: "SPOT" or "SWAP"

        Optionals:
        - inst_id: instrument ID
        - ord_type: "market" | "limit" | "post_only"
        - state: "canceled" | "filled"
        - after: older page cursor (ordId)
        - before: newer page cursor (ordId)
        - limit: 1–100 (default 100)
        - ord_id: order ID
        """
        if inst_type not in {"SPOT", "SWAP"}:
            raise ValueError('inst_type must be "SPOT" or "SWAP"')
        if ord_type and ord_type not in {"market", "limit", "post_only"}:
            raise ValueError('ord_type must be one of {"market","limit","post_only"}')
        if state and state not in {"canceled", "filled"}:
            raise ValueError('state must be "canceled" or "filled"')
        if limit is not None and (limit < 1 or limit > 100):
            raise ValueError("limit must be within 1..100")

        params: Dict[str, Any] = {"instType": inst_type}
        if inst_id is not None:
            params["instId"] = str(inst_id)
        if ord_type is not None:
            params["ordType"] = str(ord_type)
        if state is not None:
            params["state"] = str(state)
        if after is not None:
            params["after"] = str(after)
        if before is not None:
            params["before"] = str(before)
        if limit is not None:
            params["limit"] = int(limit)
        if ord_id is not None:
            params["ordId"] = str(ord_id)

        return self._get("/deepcoin/trade/orders-history", signed=True, data=params)

    def get_orders_pending(
        self,
        inst_id: str,
        index: int,
        limit: Optional[int] = None,
        ord_id: Optional[str] = None,
    ):
        """
        GET /deepcoin/trade/v2/orders-pending
        Get all open (unfilled) orders for the current account.

        Required:
        - inst_id: instrument ID
        - index: page number (>=1)

        Optionals:
        - limit: 1–100 (default 30)
        - ord_id: filter by order ID
        """
        if not inst_id:
            raise ValueError("inst_id is required")
        if not isinstance(index, int) or index < 1:
            raise ValueError("index must be a positive integer (page number)")
        if limit is not None and (limit < 1 or limit > 100):
            raise ValueError("limit must be within 1..100")

        params: Dict[str, Any] = {
            "instId": str(inst_id),
            "index": int(index),
        }
        if limit is not None:
            params["limit"] = int(limit)
        if ord_id is not None:
            params["ordId"] = str(ord_id)

        return self._get("/deepcoin/trade/v2/orders-pending", signed=True, data=params)

    def get_funding_rate_cycle(
        self,
        inst_type: str,
        inst_id: Optional[str] = None,
    ):
        """
        GET /deepcoin/trade/funding-rate
        Get funding-fee settlement interval for contracts (perpetuals).

        Required:
        - inst_type: "SwapU" | "Swap"

        Optionals:
        - inst_id: instrument ID
        """
        if inst_type not in {"SwapU", "Swap"}:
            raise ValueError('inst_type must be "SwapU" (USDT) or "Swap" (coin)')

        params: Dict[str, Any] = {"instType": str(inst_type)}
        if inst_id is not None:
            params["instId"] = str(inst_id)

        return self._get("/deepcoin/trade/funding-rate", signed=True, data=params)

    def get_current_funding_rate(
        self,
        inst_type: str,
        inst_id: Optional[str] = None,
    ):
        """
        GET /deepcoin/trade/fund-rate/current-funding-rate
        Get current funding rate(s) for contracts.

        Required:
        - inst_type: "SwapU" (USDT) | "Swap" (coin)

        Optionals:
        - inst_id: instrument ID
        """
        if inst_type not in {"SwapU", "Swap"}:
            raise ValueError('inst_type must be "SwapU" (USDT) or "Swap" (coin)')

        params: Dict[str, Any] = {"instType": str(inst_type)}
        if inst_id is not None:
            params["instId"] = str(inst_id)

        return self._get(
            "/deepcoin/trade/fund-rate/current-funding-rate",
            signed=True,
            data=params,
        )


    def get_funding_rate_history(
        self,
        inst_id: str,
        page: Optional[int] = None,
        size: Optional[int] = None,
    ):
        """
        GET /deepcoin/trade/fund-rate/history
        Get historical funding rates for a specific instrument.

        Required:
        - inst_id: instrument ID

        Optionals:
        - page: >= 1 (default 1)
        - size: 1–100 (default 20)
        """
        if not inst_id:
            raise ValueError("inst_id is required")
        if page is not None and int(page) < 1:
            raise ValueError("page must be >= 1")
        if size is not None and (int(size) < 1 or int(size) > 100):
            raise ValueError("size must be within 1..100")

        params: Dict[str, Any] = {"instId": str(inst_id)}
        if page is not None:
            params["page"] = int(page)
        if size is not None:
            params["size"] = int(size)

        return self._get(
            "/deepcoin/trade/fund-rate/history",
            signed=True,
            data=params,
        )

    def replace_order_sltp(
        self,
        order_sys_id: str,
        tp_trigger_px: Optional[float] = None,
        sl_trigger_px: Optional[float] = None,
    ):
        """
        POST /deepcoin/trade/replace-order-sltp
        Modify TP/SL on an existing OPEN LIMIT order (opening order).

        Required:
        - order_sys_id: order system ID

        Optionals:
        - tp_trigger_px: float (None or 0 => remove TP)
        - sl_trigger_px: float (None or 0 => remove SL)
        """
        if not order_sys_id:
            raise ValueError("order_sys_id is required")

        payload: Dict[str, Any] = {"orderSysID": str(order_sys_id)}
        if tp_trigger_px is not None:
            payload["tpTriggerPx"] = float(tp_trigger_px)
        if sl_trigger_px is not None:
            payload["slTriggerPx"] = float(sl_trigger_px)

        return self._post("/deepcoin/trade/replace-order-sltp", signed=True, data=payload)

    # === Listen Key APIs (Only for private WS) ===

    def get_listenkey(self) -> str:
        """
        GET /deepcoin/listenkey/acquire
        Get a new listenKey for private WebSocket connection.

        Returns:
        - listenKey (str): WebSocket authentication key
        """
        resp = self._get("/deepcoin/listenkey/acquire", signed=True)
        return resp["data"]["listenkey"]
    
    def extend_listenkey(self, listenkey: str) -> str:
        """
        GET /deepcoin/listenkey/extend
        Extend listenKey expiration time (sliding window).

        Required:
        - listenkey (str): The key to extend

        Returns:
        - listenKey (str): Renewed key (same as input)
        """
        if not listenkey:
            raise ValueError("listenkey is required")

        resp = self._get(
            "/deepcoin/listenkey/extend",
            signed=True,
            params={"listenkey": listenkey}
        )
        return resp["data"]["listenkey"]
