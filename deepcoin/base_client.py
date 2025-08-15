import requests
from typing import Dict, Optional, Any
from .auth import DeepcoinAuth

class BaseClient:
    BASE_ENDPOINT_DEFAULT = "https://api.deepcoin.com"

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        passphrase: Optional[str] = None,
        requests_params: Optional[Dict[str, Any]] = None,
        base_endpoint: str = BASE_ENDPOINT_DEFAULT,
        time_unit: Optional[str] = None,
    ):
        self.API_KEY = api_key
        self.API_SECRET = api_secret
        self.PASSPHRASE = passphrase
        self._requests_params = requests_params or {}
        self.BASE_ENDPOINT = base_endpoint
        self.TIME_UNIT = time_unit

        self.session = self._init_session()
        if self.API_KEY and self.API_SECRET and self.PASSPHRASE:
            self.session.auth = DeepcoinAuth(self.API_KEY, self.API_SECRET, self.PASSPHRASE)

    def _init_session(self) -> requests.Session:
        s = requests.session()
        s.headers.update({"Accept": "application/json"})
        return s

    def _get_headers(self) -> Dict[str, str]:
        return {"Accept": "application/json"}

    def _create_api_uri(self, path: str, version: str = "v1") -> str:
        return f"{self.BASE_ENDPOINT}{path}"

    def _get_request_kwargs(self, method: str, signed: bool, force_params: bool = False, **kwargs):
        if self._requests_params:
            kwargs.update(self._requests_params)
        return kwargs
