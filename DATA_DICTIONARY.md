# Data Dictionary — Sample Datasets

Covers the three CSV datasets provided to the seller (Assets 2, 4, 7). All data is
**synthetic** but seasonally and economically plausible for Bengaluru auto-rickshaw
operations. Deterministic (fixed seed) — regenerable from `_generators/gen_datasets.py`.

---

## Asset 2 — `02_driver_logs/member_driver_logs_sample.csv`
24 months of anonymised daily logs (Jan 2023 – Dec 2024) from 200 consenting members.
~131k rows. One row = one driver-day (off-days are omitted; sick days appear as zero-activity rows).

| Column | Type | Unit | Notes |
|---|---|---|---|
| `driver_id` | string | — | Anonymised stable ID, `BARDWS-1000`…`BARDWS-1199` |
| `log_date` | date | YYYY-MM-DD | Activity date |
| `demand_zone` | string | — | Primary operating zone (e.g. Koramangala, MG Road) |
| `hours_worked` | float | hours | 0 on sick days |
| `km_driven` | float | km | Includes deadheading to pickups; **~1.5% missing** |
| `rides_completed` | int | count | Completed trips |
| `gross_fare_inr` | float | ₹ | Pre-fuel, pre-commission; **~0.6% missing** |
| `fuel_topped_up_litres` | float | litres | Lumpy — `0` on days not refuelled |
| `sick_day` | int | 0/1 | `1` = self-reported sick day (other fields zero) |

**Deliberate dirtiness (for the data-quality validation step):**
- ~1.5% missing `km_driven`, ~0.6% missing `gross_fare_inr`.
- 80 fully duplicated driver-day rows (same driver + date logged twice).
- 12 impossible outliers: `hours_worked = 26`.
- A mid-window fare revision (effective 2024-01-15) shifts the fare base — see Asset 5.

---

## Asset 4 — `04_fuel_prices/bengaluru_fuel_prices_2018_2024.csv`
Daily IndianOil & HP Bengaluru retail prices, 2018-01-01 → 2024-12-31 (PPAC-style). ~10k rows
(2 oil companies × 2 fuel types × ~2,557 days).

| Column | Type | Unit | Notes |
|---|---|---|---|
| `date` | date | YYYY-MM-DD | |
| `city` | string | — | `Bengaluru` |
| `oil_company` | string | — | `IndianOil` / `HP` |
| `fuel_type` | string | — | `Petrol` / `Diesel` |
| `retail_price_inr_per_litre` | float | ₹/L | |
| `source` | string | — | PPAC open data portal (provenance) |

---

## Asset 7 — `07_weather/imd_bengaluru_weather_2018_2024.csv`
IMD Bengaluru station daily weather, 2018–2024. ~2,557 rows. Join to driver logs on `date`.

| Column | Type | Unit | Notes |
|---|---|---|---|
| `date` | date | YYYY-MM-DD | |
| `station` | string | — | `Bengaluru City (IMD 43295)` |
| `rainfall_mm` | float | mm | Twin monsoons (SW Jun–Sep, NE Oct–Nov) |
| `temp_max_c` | float | °C | |
| `temp_min_c` | float | °C | |
| `humidity_pct` | int | % | **40 missing** readings (intentional) |

---

### Suggested joins
- `driver_logs.log_date` → `weather.date` (rain suppresses hours; surge lifts fare).
- `driver_logs.log_date` → `fuel_prices.date` (filter `oil_company`, `fuel_type`) for cost.
- `driver_logs.log_date` → fare regime via **Asset 5** effective dates.
