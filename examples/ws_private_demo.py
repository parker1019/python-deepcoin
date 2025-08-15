import time
import logging
import os
from dotenv import load_dotenv

from deepcoin.ws import DeepcoinWebsocketManager
from deepcoin.ws.enums import WSAction, PRIVATE_WS_ENDPOINT
from deepcoin.utils.logger import init_logger
from deepcoin.client import Client

init_logger(level=logging.DEBUG)

load_dotenv(override=True)

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
passphrase = os.getenv("API_PASSPHRASE")

if not all([api_key, api_secret, passphrase]):
    raise ValueError("Please set API_KEY, API_SECRET, and API_PASSPHRASE in .env")

def on_order(msg: dict):
    logging.info("[Order] %s", msg)

def on_account(msg: dict):
    logging.info("[Account] %s", msg)

def on_position(msg: dict):
    logging.info("[Position] %s", msg)

def on_trade(msg: dict):
    logging.info("[Trade] %s", msg)

def on_orderbook(msg: dict):
    logging.info("[Order Book] %s", msg)

def on_account_detail(msg: dict):
    logging.info("[Account Detail] %s", msg)

def on_trigger_order(msg: dict):
    logging.info("[Trigger Order] %s", msg)

if __name__ == "__main__":
    # REST client to get listenKey
    client = Client(api_key=api_key, api_secret=api_secret, passphrase=passphrase)

    # PRIVATE WebSocket
    ws = DeepcoinWebsocketManager(PRIVATE_WS_ENDPOINT, client=client)

    # Order
    ws.register_callback(WSAction.PUSH_ORDER, on_order)
    # Asset Notification
    ws.register_callback(WSAction.PUSH_ACCOUNT, on_account)
    # Position Notification
    ws.register_callback(WSAction.PUSH_POSITION, on_position)
    # Trade Notification
    ws.register_callback(WSAction.PUSH_TRADE, on_trade)
    # Account Details
    ws.register_callback(WSAction.PUSH_ACCOUNT_DETAIL, on_account_detail)
    # Trigger Order Notification
    ws.register_callback(WSAction.PUSH_TRIGGER_ORDER, on_trigger_order)

    ws.start()

    for _ in range(30):
        if ws.is_alive():
            break
        time.sleep(0.1)
    else:
        raise RuntimeError("WebSocket connection failed.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Unsubscribing and stopping WebSocket manager.")
        ws.unsubscribe_all()
        ws.stop()
