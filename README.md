# HA Stock Ticker Card

A Home Assistant Lovelace custom card that displays ASX stock prices. Tap a
stock to expand an intraday line chart for the day. Supports multiple stocks
in one card.

---

## How it works

Yahoo Finance's public chart endpoint returns everything needed for this card
— current price, previous close, and 5-minute intraday candles — in a single
call, but it doesn't send CORS headers, so the card can't fetch it directly
from the browser. Instead, a small [`rest`](https://www.home-assistant.io/integrations/rest/)
sensor (built into HA core — no custom integration to install) polls it
server-side and exposes the data as sensor state + attributes. The card just
reads that sensor.

```
Yahoo Finance chart API  →  HA `rest` sensor (YAML)  →  ha-stock-ticker-card
```

---

## Installation

### 1. Card

**Manual**
1. Download [`dist/ha-stock-ticker-card.js`](dist/ha-stock-ticker-card.js) and copy it to your Home Assistant `/config/www/` directory.
2. In Home Assistant go to **Settings → Dashboards → Resources** and add:
   - **URL:** `/local/ha-stock-ticker-card.js`
   - **Type:** JavaScript module
3. Reload the browser, then add the card via the dashboard editor.

**HACS**
1. In HACS go to **Frontend → Custom repositories**.
2. Add this repository URL and select **Lovelace** as the category.
3. Install **HA Stock Ticker Card**, then add the resource as above.

### 2. Sensor (one per stock)

Add to `configuration.yaml` (or a package). This example is for DroneShield
(`DRO.AX`) — duplicate the block and change the symbol to add another stock:

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

To add a second stock (e.g. BHP), copy the whole block again with a new
resource URL, name, and `unique_id`:

```yaml
  - resource: https://query1.finance.yahoo.com/v8/finance/chart/BHP.AX?interval=5m&range=1d
    scan_interval: 300
    sensor:
      - name: "BHP Stock Price"
        unique_id: stock_bhp
        value_template: "{{ value_json.chart.result[0].meta.regularMarketPrice }}"
        unit_of_measurement: "AUD"
        json_attributes_path: "$.chart.result[0]"
        json_attributes:
          - meta
          - timestamp
          - indicators
```

Restart Home Assistant (or reload YAML) after editing. `scan_interval: 300`
(5 minutes) matches the candle resolution and is well within Yahoo's
tolerance — there's no need to poll faster, and ASX only trades 10am–4pm AEST
anyway.

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
| `entity` | string | Yes | Entity ID of the `rest` sensor for this stock |

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
