import os
from dotenv import load_dotenv
from deepcoin.client import Client
from deepcoin.exceptions import DeepcoinAPIException, DeepcoinRequestException

load_dotenv(override=True)

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
passphrase = os.getenv("API_PASSPHRASE")

if not all([api_key, api_secret, passphrase]):
    raise ValueError("Please set API_KEY, API_SECRET, and API_PASSPHRASE in .env")

client = Client(api_key=api_key, api_secret=api_secret, passphrase=passphrase)

try:
    # === Place Order ===
    print("=== Place Order ===")
    order = client.place_order(
        inst_id="BTC-USDT-SWAP",
        td_mode="cross",
        side="buy",
        ord_type="limit",
        sz="1",
        px="115000",
        pos_side="long",
        mrg_position="merge",
    )
    print(order)
except DeepcoinAPIException as e:
    print(f"[API ERROR] {e}")
except DeepcoinRequestException as e:
    print(f"[REQUEST ERROR] {e}")

try:
    # === Replace Order ===
    print("=== Replace Order ===")
    order_id = "1001105614869143"
    replaced = client.replace_order(order_sys_id=order_id, price=116000)
    print(replaced)
except DeepcoinAPIException as e:
    print(f"[API ERROR] {e}")
except DeepcoinRequestException as e:
    print(f"[REQUEST ERROR] {e}")

try:
    # === Replace SL/TP ===
    print("=== Replace SL/TP ===")
    order_id = "1001105614869143"
    sltp = client.replace_order_sltp(order_sys_id=order_id, tp_trigger_px=120000)
    print(sltp)
except DeepcoinAPIException as e:
    print(f"[API ERROR] {e}")
except DeepcoinRequestException as e:
    print(f"[REQUEST ERROR] {e}")

try:
    # === Cancel Order ===
    print("=== Cancel Order ===")
    order_id = "1001105614869143"
    cancel = client.cancel_order(inst_id="BTC-USDT-SWAP", ord_id=order_id)
    print(cancel)
except DeepcoinAPIException as e:
    print(f"[API ERROR] {e}")
except DeepcoinRequestException as e:
    print(f"[REQUEST ERROR] {e}")

try:
    # === Batch Cancel Orders ===
    print("=== Batch Cancel Orders ===")
    order_id = ["1001105615124082"]
    batch_cancel = client.batch_cancel_order(order_sys_ids=order_id)
    print(batch_cancel)
except DeepcoinAPIException as e:
    print(f"[API ERROR] {e}")
except DeepcoinRequestException as e:
    print(f"[REQUEST ERROR] {e}")

try:
    # === Cancel All Swap Orders ===
    print("=== Cancel All Swap Orders ===")
    cancel_all = client.cancel_all_swap_orders(
        instrument_id="BTCUSDT",
        product_group="SwapU",
        is_cross_margin=1,
        is_merge_mode=1
    )
    print(cancel_all)
except DeepcoinAPIException as e:
    print(f"[API ERROR] {e}")
except DeepcoinRequestException as e:
    print(f"[REQUEST ERROR] {e}")

try:
    # === Get Fills ===
    print("=== Get Fills ===")
    fills = client.get_fills(inst_type="SWAP", limit=5)
    print(fills)
except DeepcoinAPIException as e:
    print(f"[API ERROR] {e}")
except DeepcoinRequestException as e:
    print(f"[REQUEST ERROR] {e}")

try:
    # === Get Order By ID ===
    print("=== Get Order By ID ===")
    order_id = "1001105615282020"
    live_order = client.get_order_by_id(inst_id="BTC-USDT-SWAP", ord_id=order_id)
    print(live_order)
except DeepcoinAPIException as e:
    print(f"[API ERROR] {e}")
except DeepcoinRequestException as e:
    print(f"[REQUEST ERROR] {e}")

try:
    # === Get Finished Order By ID ===
    print("=== Get Finished Order By ID ===")
    order_id = "1001105615282020"
    finished_order = client.get_finished_order_by_id(inst_id="BTC-USDT-SWAP", ord_id=order_id)
    print(finished_order)
except DeepcoinAPIException as e:
    print(f"[API ERROR] {e}")
except DeepcoinRequestException as e:
    print(f"[REQUEST ERROR] {e}")

try:
    # === Get Orders History ===
    print("=== Get Orders History ===")
    orders_history = client.get_orders_history(inst_type="SWAP", limit=5)
    print(orders_history)
except DeepcoinAPIException as e:
    print(f"[API ERROR] {e}")
except DeepcoinRequestException as e:
    print(f"[REQUEST ERROR] {e}")

try:
    # === Get Orders Pending ===
    print("=== Get Orders Pending ===")
    pending_orders = client.get_orders_pending(inst_id="BTC-USDT-SWAP", index=1, limit=5)
    print(pending_orders)
except DeepcoinAPIException as e:
    print(f"[API ERROR] {e}")
except DeepcoinRequestException as e:
    print(f"[REQUEST ERROR] {e}")

try:
    # === Get Funding Rate Cycle ===
    print("=== Get Funding Rate Cycle ===")
    funding_cycle = client.get_funding_rate_cycle(inst_type="SwapU", inst_id="BTCUSDT")
    print(funding_cycle)
except DeepcoinAPIException as e:
    print(f"[API ERROR] {e}")
except DeepcoinRequestException as e:
    print(f"[REQUEST ERROR] {e}")

try:
    # === Get Current Funding Rate ===
    print("=== Get Current Funding Rate ===")
    current_funding = client.get_current_funding_rate(inst_type="SwapU", inst_id="BTCUSDT")
    print(current_funding)
except DeepcoinAPIException as e:
    print(f"[API ERROR] {e}")
except DeepcoinRequestException as e:
    print(f"[REQUEST ERROR] {e}")

try:
    # === Get Funding Rate History ===
    print("=== Get Funding Rate History ===")
    funding_history = client.get_funding_rate_history(inst_id="BTCUSDT", size=5)
    print(funding_history)
except DeepcoinAPIException as e:
    print(f"[API ERROR] {e}")
except DeepcoinRequestException as e:
    print(f"[REQUEST ERROR] {e}")