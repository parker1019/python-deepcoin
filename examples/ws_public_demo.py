import time
import logging

from deepcoin.ws import DeepcoinWebsocketManager
from deepcoin.ws.enums import WSAction, PUBLIC_FUTURES_WS_ENDPOINT, PUBLIC_SPOT_WS_ENDPOINT
from deepcoin.utils.logger import init_logger

init_logger(level=logging.DEBUG)

def on_topic_action(msg: dict):
    logging.info("[Topic Action] %s", msg)

def on_market_data(msg: dict):
    logging.info("[Market Data] %s", msg)

def on_kline(msg: dict):
    logging.info("[K line] %s", msg)

def on_last_tx(msg: dict):
    logging.info("[Last Transactions] %s", msg)

def on_orderbook(msg: dict):
    logging.info("[Order Book] %s", msg)

if __name__ == "__main__":
    # SPOT WebSocket
    ws = DeepcoinWebsocketManager(PUBLIC_SPOT_WS_ENDPOINT)
    # FUTURES WebSocket
    ws = DeepcoinWebsocketManager(PUBLIC_FUTURES_WS_ENDPOINT)

    # Register Topic action Callbacks
    ws.register_callback(WSAction.RECV_TOPIC_ACTION, on_topic_action)
    # The Latest Market Data
    ws.register_callback(WSAction.PUSH_MARKET_DATA, on_market_data)
    # Last Transactions
    ws.register_callback(WSAction.PUSH_LAST_TX, on_last_tx)
    # K-Lines
    ws.register_callback(WSAction.PUSH_KLINE, on_kline)
    # 25-Level Incremental Market Data
    ws.register_callback(WSAction.PUSH_ORDERBOOK, on_orderbook)

    ws.start()

    for _ in range(30):
        if ws.is_alive():
            break
        time.sleep(0.1)
    else:
        raise RuntimeError("WebSocket connection failed.")

    # The Latest Market Data
    ws.subscribe_market_data("BTCUSDT")
    # Last Transactions
    ws.subscribe_trade("BTCUSDT")
    # K-Lines (1 minute)
    ws.subscribe_kline("BTCUSDT", "1m")
    # 25-level-incremental-market-data
    ws.subscribe_orderbook("BTCUSDT")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Unsubscribing and stopping WebSocket manager.")
        ws.unsubscribe_all()
        ws.stop()
