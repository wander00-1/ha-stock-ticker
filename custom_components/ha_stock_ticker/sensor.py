"""Sensor platform for the Stock Ticker integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import StockTickerCoordinator, is_asx_market_open


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Stock Ticker sensor from a config entry."""
    coordinator: StockTickerCoordinator = entry.runtime_data
    async_add_entities([StockTickerSensor(coordinator, entry)])


class StockTickerSensor(CoordinatorEntity[StockTickerCoordinator], SensorEntity):
    """Sensor exposing a stock's current price, with chart data as attributes.

    Attributes mirror the shape of Yahoo's chart.result[0] (meta, timestamp,
    indicators) so ha-stock-ticker-card works identically whether the price
    comes from this integration or a hand-written REST sensor.
    """

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:chart-line"

    def __init__(self, coordinator: StockTickerCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_name = entry.title
        self._attr_unique_id = f"{entry.entry_id}_price"

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.get("meta", {}).get("regularMarketPrice")

    @property
    def native_unit_of_measurement(self) -> str | None:
        return self.coordinator.data.get("meta", {}).get("currency")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data
        return {
            "meta": data.get("meta", {}),
            "timestamp": data.get("timestamp", []),
            "indicators": data.get("indicators", {}),
            "market_open": is_asx_market_open(),
        }
