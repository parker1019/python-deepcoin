import time
import hmac
import base64
from hashlib import sha256
from urllib.parse import urlparse
import requests

def _iso_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())

class DeepcoinAuth(requests.auth.AuthBase):
    def __init__(self, api_key: str, api_secret: str, passphrase: str):
        self.api_key = api_key
        self.api_secret = api_secret.encode()
        self.passphrase = passphrase

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        ts = _iso_timestamp()

        parsed = urlparse(r.url)
        request_path = parsed.path
        if parsed.query:
            request_path += "?" + parsed.query

        body = r.body or ""
        if isinstance(body, bytes):
            body = body.decode("utf-8")

        prehash = f"{ts}{r.method.upper()}{request_path}{body}"
        signature = base64.b64encode(hmac.new(self.api_secret, prehash.encode(), sha256).digest()).decode()

        r.headers.setdefault("Content-Type", "application/json")
        r.headers["DC-ACCESS-KEY"] = self.api_key
        r.headers["DC-ACCESS-SIGN"] = signature
        r.headers["DC-ACCESS-TIMESTAMP"] = ts
        r.headers["DC-ACCESS-PASSPHRASE"] = self.passphrase
        return r
