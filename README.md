# Welcome to python-deepcoin v0.2.0

This is an unofficial Python wrapper for the [DeepCoin API](https://www.deepcoin.com/docs/authentication)
This package provides an easy-to-use, Pythonic interface for interacting with DeepCoin's REST and WebSocket APIs, supporting both spot and derivatives trading.

## Features
- **Account Endpoints**
  - `get_balances()` – Get Account Balance
  - `get_bills()` – Get Bills
  - `get_positions()` – Get Positions
  - `set_leverage()` – Set Leverage

- **Market Endpoints**
  - `get_order_book()` – Get Order Book
  - `get_candles()` – Get K-line Data
  - `get_instruments()` – Get Product Info
  - `get_tickers()` – Get Market Tickers

- **Trade Endpoints**
  - `place_order()` – Place Order
  - `replace_order()` – Amend Order
  - `cancel_order()` - Cancel Order
  - `batch_cancel_order()` – Batch Cancel Orders
  - `cancel_all_swap_orders()` – Cancel All Orders
  - `get_fills()` – Get Trade Details
  - `get_order_by_id()` - Get Order by ID
  - `get_finished_order_by_id()` – Get Historical Order by ID
  - `get_orders_history()` – Order History
  - `get_orders_pending()` – Get All Pending Orders
  - `get_funding_rate_cycle()` – Get Funding Rate
  - `get_current_funding_rate()` - Get Current Funding Rate 
  - `get_funding_rate_history()` - Get Funding Rate History
  - `replace_order_sltp()` - Modify Take Profit and Stop Loss for Open Limit Orders

- **WebSocket**
  - Public
  - Private

## Quick Start

### Installation

Install via pip:

```bash
pip install python-deepcoin
```

### Authentication

Most endpoints require authentication. To begin, initialize the client with your API key and secret:

```python
from deepcoin import DeepcoinClient

client = DeepcoinClient(
    api_key='your_api_key',
    api_secret='your_api_secret',
    passphrase='your_api_passphrase'
)
```

### Example Usage

Get Account Balance

```python
balance = client.get_balances()
print(balance)
```

More Examples

You can find more usage examples in the `examples/` folder.