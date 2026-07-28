# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2026-07-28

### Fixed
- The market-hours gate was a plain "skip while closed" check, so the last
  price/timestamp could freeze well before the actual 4pm close depending
  on where the coordinator's fixed 5-minute polling interval happened to
  land (it isn't aligned to wall-clock or to market close). Now always
  fetches once more on the open→closed transition, so the last update
  reflects the real closing print instead of an arbitrary earlier poll.
- New `should_poll` helper (in `market_hours.py`, unit tested) makes this
  decision independent of `DataUpdateCoordinator` for testability

## [0.2.0] - 2026-07-28

### Added
- Skips the Yahoo Finance request outside ASX trading hours (Mon-Fri
  10:00-16:00 Australia/Sydney) once an initial fetch has succeeded — the
  sensor keeps its last known price instead of polling a closed market.
  Public holidays aren't accounted for.
- New `market_open` sensor attribute reflecting current session status
- Trading-hours logic moved into its own dependency-free `market_hours.py`,
  with a `tests/` suite (`python -m unittest discover -s tests`) that runs
  without a full Home Assistant install

## [0.1.1] - 2026-07-28

### Changed
- Split the card out into its own repo,
  [ha-stock-ticker-card](https://github.com/wander00-1/ha-stock-ticker-card)
  — HACS doesn't allow one repository to be both an Integration and a
  Dashboard category, and adding this repo a second time under a different
  category silently failed to install anything, so "Stock Ticker" never
  appeared under Add Integration
- This repo now contains the `ha_stock_ticker` integration only

## [0.1.0] - 2026-07-28

### Added
- `ha_stock_ticker` custom integration with a config flow — add a stock via
  **Settings → Devices & Services → Add Integration**, no YAML editing needed
- Integration validates the ticker symbol against Yahoo Finance before
  creating the entry, and polls every 5 minutes
- Integration's sensor attributes (`meta`, `timestamp`, `indicators`) match
  the manual `rest` sensor shape, so the card works unchanged with either
