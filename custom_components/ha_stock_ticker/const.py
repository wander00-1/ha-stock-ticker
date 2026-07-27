"""Constants for the Stock Ticker integration."""

DOMAIN = "ha_stock_ticker"
CONF_SYMBOL = "symbol"

DEFAULT_SCAN_INTERVAL = 300  # seconds; matches the 5-minute candle resolution
CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=5m&range=1d"
