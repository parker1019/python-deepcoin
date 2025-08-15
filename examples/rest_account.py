import os
from dotenv import load_dotenv
from deepcoin.client import Client
from deepcoin.exceptions import DeepcoinAPIException, DeepcoinRequestException

load_dotenv(override=True)

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
passphrase = os.getenv("API_PASSPHRASE")

if not all([api_key, api_secret, passphrase]):
    raise ValueError("Please set API_KEY, API_SECRET, API_PASSPHRASE in .env")

client = Client(api_key=api_key, api_secret=api_secret, passphrase=passphrase)

try:
    print("=== Balances ===")
    balances = client.get_balances(inst_type="SPOT")
    print(balances)
except DeepcoinAPIException as e:
    print(f"[API ERROR] {e}")
except DeepcoinRequestException as e:
    print(f"[REQUEST ERROR] {e}")

try:
    print("=== Bills ===")
    bills = client.get_bills(inst_type="SPOT", limit=5)
    print(bills)
except DeepcoinAPIException as e:
    print(f"[API ERROR] {e}")
except DeepcoinRequestException as e:
    print(f"[REQUEST ERROR] {e}")

try:
    print("=== Positions ===")
    positions = client.get_positions(inst_type="SWAP")
    print(positions)
except DeepcoinAPIException as e:
    print(f"[API ERROR] {e}")
except DeepcoinRequestException as e:
    print(f"[REQUEST ERROR] {e}")

try:
    print("=== Set Leverage ===")
    set_leverage = client.set_leverage(
        inst_id="BTC-USDT-SWAP", lever="10", mgn_mode="cross", mrg_position="merge"
    )
    print(set_leverage)
except DeepcoinAPIException as e:
    print(f"[API ERROR] {e}")
except DeepcoinRequestException as e:
    print(f"[REQUEST ERROR] {e}")
