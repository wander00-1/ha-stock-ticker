"""Config flow for the Stock Ticker integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_SYMBOL, DOMAIN
from .coordinator import StockChartError, fetch_chart_result

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SYMBOL): str,
        vol.Optional("name"): str,
    }
)


class StockTickerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Stock Ticker."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Ask for a ticker symbol and validate it against Yahoo Finance."""
        errors: dict[str, str] = {}

        if user_input is not None:
            symbol = user_input[CONF_SYMBOL].strip().upper()
            await self.async_set_unique_id(symbol)
            self._abort_if_unique_id_configured()

            try:
                result = await fetch_chart_result(self.hass, symbol)
            except StockChartError:
                errors["base"] = "invalid_symbol"
            except Exception:
                _LOGGER.exception("Unexpected error validating symbol %s", symbol)
                errors["base"] = "cannot_connect"
            else:
                meta = result.get("meta", {})
                title = user_input.get("name") or meta.get("longName") or symbol
                return self.async_create_entry(
                    title=title,
                    data={CONF_SYMBOL: symbol},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
