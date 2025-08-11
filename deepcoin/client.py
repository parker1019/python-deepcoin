from typing import Dict, Optional, Any
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
        testnet: bool = False,
    ):
        super().__init__(
            api_key=api_key,
            api_secret=api_secret,
            passphrase=passphrase,
            requests_params=requests_params,
            base_endpoint=base_endpoint,
            testnet=testnet,
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

        if "data" in kwargs:
            for key in list(kwargs["data"].keys()):
                if key == "headers":
                    headers.update(kwargs["data"][key])
                    del kwargs["data"][key]

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
