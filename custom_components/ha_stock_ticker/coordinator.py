"""Data update coordinator for the Stock Ticker integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CHART_URL, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


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
    """Coordinator that polls the Yahoo Finance chart endpoint for one symbol."""

    def __init__(self, hass: HomeAssistant, symbol: str) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"Stock Ticker ({symbol})",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.symbol = symbol

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await fetch_chart_result(self.hass, self.symbol)
        except StockChartError as err:
            raise UpdateFailed(str(err)) from err
