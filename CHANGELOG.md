# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-07-28

### Added
- `ha_stock_ticker` custom integration with a config flow — add a stock via
  **Settings → Devices & Services → Add Integration**, no YAML editing needed
- Integration validates the ticker symbol against Yahoo Finance before
  creating the entry, and polls every 5 minutes
- Integration's sensor attributes (`meta`, `timestamp`, `indicators`) match
  the manual `rest` sensor shape, so the card works unchanged with either

## [0.1.0] - 2026-07-28

### Added
- Initial release
- Displays price, change, and %change per stock, colour-coded green/down red
- Tap a stock row to expand an intraday line chart for the day
- Support for multiple stocks in one card, added/removed via the visual editor
- Reads price and 5-minute intraday candles from a Home Assistant `rest` sensor (see README) — no custom integration required
- `getStubConfig` for the Lovelace card picker preview
- HACS-compatible `hacs.json`
