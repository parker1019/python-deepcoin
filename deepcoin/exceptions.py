from typing import Dict

_DEEPCOIN_ERROR_MAP: Dict[int, str] = {
    50100: "API has been frozen, please contact customer service",
    50101: "APIKey does not match the current environment",
    50102: "Request timestamp has expired",
    50103: 'Request header "DC-ACCESS-KEY" cannot be empty',
    50104: 'Request header "DC-ACCESS-PASSPHRASE" cannot be empty',
    50105: 'Request header "DC-ACCESS-PASSPHRASE" is incorrect',
    50106: 'Request header "DC-ACCESS-SIGN" cannot be empty',
    50107: 'Request header "DC-ACCESS-TIMESTAMP" cannot be empty',
    50108: "Broker ID does not exist",
    50109: "Broker domain does not exist",
    50110: "Invalid IP",
    50111: "Invalid signature",
    50112: "Invalid DC-ACCESS-TIMESTAMP",
    50113: "Invalid DC-ACCESS-KEY",
    50114: "Invalid authorization",
    50115: "Invalid request type",
}

class DeepcoinAPIException(Exception):
    """Exception for API response errors (include HTTP non 2xx or JSON code != '0')"""

    def __init__(self, response, status_code=None, text=None):
        self.status_code = status_code or response.status_code
        self.response = response
        self.code = None
        self.message = None

        try:
            json_res = response.json()
            self.code = json_res.get("code") or json_res.get("error_code")
            self.message = json_res.get("msg") or json_res.get("message") or str(json_res)
        except ValueError:
            self.message = text or response.text

        super().__init__(self.__str__())

    def __str__(self):
        return f"HTTP {self.status_code} | code = {self.code} | msg = {self.message}"

class DeepcoinRequestException(Exception):
    """Exception for request errors (network issues, invalid responses, etc.)"""

    def __init__(self, message):
        super().__init__(message)


class NotImplementedException(Exception):
    """Raised when a feature or method is not implemented"""
    pass
