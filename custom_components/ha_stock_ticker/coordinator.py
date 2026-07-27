"""Data update coordinator for the Stock Ticker integration."""

from __future__ import annotations

import logging
from datetime import time, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import CHART_URL, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

ASX_TIMEZONE = ZoneInfo("Australia/Sydney")
ASX_MARKET_OPEN = time(10, 0)
ASX_MARKET_CLOSE = time(16, 0)


def is_asx_market_open(now: Any = None) -> bool:
    """Return whether the ASX is within its Mon-Fri 10:00-16:00 session.

    Doesn't account for public holidays.
    """
    local = (now or dt_util.utcnow()).astimezone(ASX_TIMEZONE)
    if local.weekday() >= 5:
        return False
    return ASX_MARKET_OPEN <= local.time() < ASX_MARKET_CLOSE


class StockChartError(Exception):
    """Raised when the Yahoo Finance chart endpoint returns no usable data."""


async def fetch_chart_result(hass: HomeAssistant, symbol: str) -> dict[str, Any]:
    """Fetch and return chart.result[0] for a symbol.

    Raises StockChartError if the symbol is unknown or the response is
    otherwise unusable.
    """
    session = async_get_clientsession(hass)
    url = CHART_URL.format(symbol=symbol)
    async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as resp:
        if resp.status != 200:
            raise StockChartError(f"HTTP {resp.status} from Yahoo Finance")
        payload = await resp.json(content_type=None)

    try:
        result = payload["chart"]["result"][0]
    except (KeyError, IndexError, TypeError) as err:
        chart_error = isinstance(payload, dict) and payload.get("chart", {}).get("error")
        raise StockChartError(chart_error or "No chart result for symbol") from err

    if not result.get("meta", {}).get("regularMarketPrice"):
        raise StockChartError("No regularMarketPrice in response")

    return result


class StockTickerCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that polls the Yahoo Finance chart endpoint for one symbol.

    Once an initial fetch has succeeded, skips the actual Yahoo request
    outside ASX trading hours — the sensor keeps its last known price
    instead of polling a market that isn't moving.
    """

    def __init__(self, hass: HomeAssistant, symbol: str) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"Stock Ticker ({symbol})",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.symbol = symbol

    async def _async_update_data(self) -> dict[str, Any]:
        if self.data is not None and not is_asx_market_open():
            return self.data
        try:
            return await fetch_chart_result(self.hass, self.symbol)
        except StockChartError as err:
            raise UpdateFailed(str(err)) from err
