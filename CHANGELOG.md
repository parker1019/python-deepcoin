# Changelog

## [0.2.0] - 2025-08-15

### Added
- **WebSocket Client**
  - Introduced unified WebSocket manager: `DeepcoinWebsocketManager`.
  - Supports both **public** and **private** WebSocket endpoints.
  - Auto-renewal of `listenKey` every 30 minutes via background thread.
  - Dispatcher-based callback system (register/unregister per topic).
  - Demo examples for public and private WebSocket usage (`examples/ws_*.py`).

### Infra
- WebSocket enums and topic definitions (`WSAction`, `TopicID`, etc).
- `WebSocketConnection` base handler using `websocket-client`.
- `MessageDispatcher` for internal routing of action-based messages.
- Logging structure updated for `deepcoin.ws` namespace.

## [0.1.0] - 2025-08-15

### Added
- Initial implementation of Deepcoin REST API client.
- **Account API**
  - `get_balances()` - Retrieve account balances.
  - `get_bills()` - Query billing/transaction records.
  - `get_positions()` - Fetch current position information.
  - `set_leverage()` - Set leverage per instrument.

- **Market API**
  - `get_order_book()` - Retrieve order book (depth).
  - `get_candles()` - Get K-line (OHLCV) data.
  - `get_instruments()` - Query available trading pairs.
  - `get_tickers()` - Get 24-hour ticker statistics.

- **Trade API**
  - `place_order()` - Create a new order.
  - `replace_order()` - Modify price/quantity of an existing order.
  - `replace_order_sltp()` - Modify SL/TP of an open limit order.
  - `cancel_order()` - Cancel specific order.
  - `batch_cancel_order()` - Cancel multiple orders by ID.
  - `cancel_all_swap_orders()` - Cancel all swap orders for an instrument.
  - `get_fills()` - Get historical fill details.
  - `get_order_by_id()` - Get live order info.
  - `get_finished_order_by_id()` - Get historical order by ID.
  - `get_orders_pending()` - Retrieve all open orders.
  - `get_orders_history()` - Query order history (paginated).
  - `get_funding_rate_cycle()` - Get funding settlement interval and next cycle.
  - `get_current_funding_rate()` - Get current funding rate per instrument.
  - `get_funding_rate_history()` - Get funding rate history.

### Infra
- Base client and authentication (`HMAC-SHA256`) with signature headers (`DC-ACCESS-KEY`, etc).
- Exception handling (`DeepcoinRequestException`, `DeepcoinAPIException`).
- Modularized package layout with `account`, `market`, and `trade` clients.

