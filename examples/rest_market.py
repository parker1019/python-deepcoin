from deepcoin.client import Client
from deepcoin.exceptions import DeepcoinAPIException, DeepcoinRequestException

client = Client()

try:
    print("=== Order Book ===")
    order_book = client.get_order_book(inst_id="BTC-USDT-SWAP", sz=5)
    print(order_book)
except DeepcoinAPIException as e:
    print(f"[API ERROR] {e}")
except DeepcoinRequestException as e:
    print(f"[REQUEST ERROR] {e}")

try:
    print("=== K-line Data ===")
    candles = client.get_candles(inst_id="BTC-USDT-SWAP", bar="1m", limit=5)
    print(candles)
except DeepcoinAPIException as e:
    print(f"[API ERROR] {e}")
except DeepcoinRequestException as e:
    print(f"[REQUEST ERROR] {e}")

try:
    print("=== Instruments ===")
    instruments = client.get_instruments(inst_type="SWAP")
    print(instruments)
except DeepcoinAPIException as e:
    print(f"[API ERROR] {e}")
except DeepcoinRequestException as e:
    print(f"[REQUEST ERROR] {e}")

try:
    print("=== Market Tickers ===")
    tickers = client.get_tickers(inst_type="SWAP")
    print(tickers)
except DeepcoinAPIException as e:
    print(f"[API ERROR] {e}")
except DeepcoinRequestException as e:
    print(f"[REQUEST ERROR] {e}")
