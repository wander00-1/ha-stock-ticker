# HA Stock Ticker Card

A Home Assistant integration + Lovelace card that displays ASX stock prices.
Tap a stock to expand an intraday line chart for the day. Add stocks entirely
from the UI — no YAML required.

---

## How it works

Yahoo Finance's public chart endpoint returns everything needed for this card
— current price, previous close, and 5-minute intraday candles — in a single
call, but it doesn't send CORS headers, so the card can't fetch it directly
from the browser (confirmed by testing). Instead, a small custom integration
polls it server-side (where CORS doesn't apply) and exposes the data as
sensor state + attributes. The card just reads that sensor.

```
Yahoo Finance chart API  →  Stock Ticker integration  →  ha-stock-ticker-card
```

This repo contains two separate HACS installs:
- **`ha_stock_ticker`** (category: *Integration*) — the backend. Adds a config
  flow so you add a stock via **Settings → Devices & Services → Add
  Integration**, no YAML.
- **`ha-stock-ticker-card`** (category: *Dashboard*) — the frontend card that
  reads the sensor(s) the integration creates.

---

## Installation

### 1. Integration (backend — one stock per instance)

**HACS**
1. In HACS go to **Custom repositories**, add this repository URL, and select
   **Integration** as the category (not Dashboard — that's the card, added
   separately below).
2. Install **Stock Ticker**, then restart Home Assistant.
3. Go to **Settings → Devices & Services → Add Integration**, search for
   **Stock Ticker**, and enter a ticker symbol as Yahoo Finance lists it
   (e.g. `DRO.AX` for DroneShield on the ASX) and an optional display name.
4. Repeat step 3 for each additional stock you want — every instance creates
   one price sensor.

**Manual**
1. Copy the `custom_components/ha_stock_ticker/` folder from this repo into
   your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant, then follow steps 3–4 above.

The integration polls Yahoo every 5 minutes (matching the candle resolution
— ASX only trades 10am–4pm AEST anyway, so there's no benefit to polling
faster) and creates one sensor per stock with the current price as its state
and the raw chart data (previous close, currency, intraday candles) as
attributes.

### 2. Card (frontend)

**HACS**
1. In HACS go to **Custom repositories**, add this same repository URL, and
   select **Dashboard** as the category this time.
2. Install **HA Stock Ticker Card** — HACS adds the resource automatically.

**Manual**
1. Download [`dist/ha-stock-ticker-card.js`](dist/ha-stock-ticker-card.js) and copy it to your Home Assistant `/config/www/` directory.
2. In Home Assistant go to **Settings → Dashboards → Resources** and add:
   - **URL:** `/local/ha-stock-ticker-card.js`
   - **Type:** JavaScript module
3. Reload the browser, then add the card via the dashboard editor, picking
   the sensor(s) the integration created in step 1.

---

## Alternative: manual YAML sensor (skip the integration)

If you'd rather not install a custom integration, a plain HA `rest` sensor
(built into core) can produce the same sensor shape the card expects —
you just have to write the YAML yourself and add stocks by hand:

```yaml
rest:
  - resource: https://query1.finance.yahoo.com/v8/finance/chart/DRO.AX?interval=5m&range=1d
    scan_interval: 300
    sensor:
      - name: "DRO Stock Price"
        unique_id: stock_dro
        value_template: "{{ value_json.chart.result[0].meta.regularMarketPrice }}"
        unit_of_measurement: "AUD"
        json_attributes_path: "$.chart.result[0]"
        json_attributes:
          - meta
          - timestamp
          - indicators
```

Duplicate the block with a new resource URL, name, and `unique_id` per
additional stock, then restart Home Assistant after editing.

---

## Card configuration

```yaml
type: custom:ha-stock-ticker-card
title: Watchlist          # optional — card header text
stocks:
  - name: DroneShield      # optional — defaults to the ticker symbol
    entity: sensor.dro_stock_price
  - entity: sensor.bhp_stock_price
```

### Options

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `title` | string | No | Card header text |
| `stocks` | list | Yes | One or more stock definitions (see below) |

**Stock definition**

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `name` | string | No | Display label — defaults to the ticker symbol from the sensor |
| `entity` | string | Yes | Entity ID of the price sensor for this stock (created by the integration, or your own `rest` sensor) |

---

## Behaviour

- Tap a stock row to expand/collapse its intraday chart
- Price change and % change (vs previous close) shown in green (up), red
  (down), or grey (flat)
- Dashed reference line in the chart marks the previous close
- Card colours follow the active HA theme; override the up/down colours with
  `--stock-up-color`/`--stock-down-color` CSS variables in your theme if
  desired

---

## Contributing

Issues and pull requests are welcome. Please update `CHANGELOG.md` and bump
the version in `dist/ha-stock-ticker-card.js` before opening a release PR.

---

## License

MIT
