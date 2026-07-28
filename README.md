# Stock Ticker

A Home Assistant custom integration that polls Yahoo Finance for a stock's
current price and intraday chart data, and exposes it as a sensor — entirely
through the UI, no YAML required.

This is the backend half of a two-repo pair. Pair it with:

- **[ha-stock-ticker-card](https://github.com/wander00-1/ha-stock-ticker-card)**
  — a Lovelace card that displays the sensor(s) this integration creates,
  with tap-to-expand daily charts

(These are separate repos because HACS doesn't allow one repository to be
both an *Integration* and a *Dashboard* category.)

---

## How it works

Yahoo Finance's public chart endpoint returns everything needed for a stock
ticker — current price, previous close, and 5-minute intraday candles — in a
single call, but it doesn't send CORS headers, so nothing running in a
browser (e.g. a Lovelace card) can call it directly. This integration polls
it server-side instead, where CORS doesn't apply, and exposes the result as
one sensor per configured stock.

```
Yahoo Finance chart API  →  Stock Ticker integration  →  sensor.xxx_stock_price
```

---

## Installation

**HACS**
1. In HACS go to **Custom repositories**, add this repository URL, and
   select **Integration** as the category.
2. Install **Stock Ticker**, then restart Home Assistant.

**Manual**
1. Copy the `custom_components/ha_stock_ticker/` folder from this repo into
   your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.

## Adding a stock

1. Go to **Settings → Devices & Services → Add Integration**, search for
   **Stock Ticker**.
2. Enter a ticker symbol as Yahoo Finance lists it (e.g. `DRO.AX` for
   DroneShield on the ASX, `BHP.AX` for BHP) and an optional display name.
3. The symbol is validated against Yahoo Finance before the entry is
   created — an unknown symbol shows an error instead of a broken sensor.
4. Repeat for each additional stock you want to track — every instance of
   the integration creates one price sensor.

The integration polls every 5 minutes, but only actually calls Yahoo Finance
during ASX trading hours (Mon-Fri 10:00-16:00 Australia/Sydney) once it has
fetched successfully at least once. It always fetches once more on the
open→closed transition (so the last price/timestamp reflects the real close,
not whichever poll happened to land last before 4pm), then stays frozen on
that closing price until the market reopens. Public holidays aren't
accounted for.

## Sensor attributes

Each sensor's state is the current price. Its attributes carry the raw chart
data, shaped like Yahoo's `chart.result[0]`:

| Attribute | Description |
|-----------|-------------|
| `meta` | `previousClose`, `currency`, `longName`, `regularMarketTime`, etc. |
| `timestamp` | Array of unix timestamps, one per 5-minute candle |
| `indicators` | `quote[0].close` — array of close prices matching `timestamp` |
| `market_open` | Whether the ASX is currently in its Mon-Fri 10:00-16:00 session |

[ha-stock-ticker-card](https://github.com/wander00-1/ha-stock-ticker-card)
reads these directly to draw the daily chart.

---

## Alternative: manual YAML sensor (skip this integration)

If you'd rather not install a custom integration, a plain HA `rest` sensor
(built into core) can produce the same sensor shape the card expects — you
just have to write the YAML yourself and add stocks by hand:

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

## Testing

```
python -m unittest discover -s tests
```

Covers `market_hours.is_asx_market_open` (session boundaries, weekends,
timezone conversion) and `market_hours.should_poll` (the open→closed
transition-fetch logic). Both are kept in their own dependency-free module
specifically so this runs without installing Home Assistant. The
Yahoo-fetching and coordinator code isn't unit-tested — that needs a real HA
test harness and is checked manually against a live instance instead.

## Contributing

Issues and pull requests are welcome. Please update `CHANGELOG.md` and bump
the version in `custom_components/ha_stock_ticker/manifest.json` before
opening a release PR.

---

## License

MIT
