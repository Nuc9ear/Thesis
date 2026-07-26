# Data dictionary

## Raw tables

### `futures_daily.csv`

One row per contract and trading day. Important MOEX fields are `SETTLEPRICE` (official daily settlement price, RUB per CNY), `WAPRICE`, `CLOSE`, `VOLUME` (contracts), `OPENPOSITION` (contracts), `OPENPOSITIONVALUE`, `VALUE` (turnover), and `NUMTRADES`.

### `spot_daily.csv`

One row per trading day for `CNYRUB_TOM` on the main CETS board. Prices are RUB per CNY. `WAPRICE` is used as the empirical spot-price proxy in the processed files.

### `funding_daily.csv`

Long-format observations for the MOEX money-market indicators. `CLOSE` is an annual percentage rate. `VALUE` is the underlying transaction value reported by MOEX, where available.

| SECID | Currency | Nominal tenor days |
|---|---:|---:|
| RUSFAR | RUB | 1 |
| RUSFAR1W | RUB | 7 |
| RUSFAR2W | RUB | 14 |
| RUSFAR1M | RUB | 30 |
| RUSFAR3M | RUB | 90 |
| RUSFARCNY | CNY | 1 |
| RUSFARCN1W | CNY | 7 |

### `contracts.csv`

Contract identifiers and MOEX reference data. `expiry_date` comes from `LSTDELDATE`; `last_trade_date` comes from `LSTTRADE`.

## Processed tables

### `contract_daily.csv`

One row per futures contract and trading day.

- `trade_date`, `secid`, `shortname`, `expiry_date`: observation and contract keys.
- `days_to_maturity`, `ttm_years`: calendar days and Actual/365 years to expiration.
- `futures_price`: settlement, VWAP, or close in that priority order.
- `spot_price`: spot VWAP, or close when VWAP is missing.
- `rub_rate_pct`, `cny_rate_pct`: closest available annual funding rates, in percent.
- `rub_rate_tenor`, `cny_rate_tenor`: selected MOEX indicators.
- `rub_rate_observation_date`, `cny_rate_observation_date`: publication dates of the selected rates. Prior observations are carried forward by at most 14 calendar days, never backward from a future date.
- `rub_tenor_distance_days`, `cny_tenor_distance_days`: absolute distance between remaining maturity and the proxy tenor.
- `theoretical_futures_price`: continuous-compounding cost-of-carry value.
- `basis_rub_per_cny`: observed minus theoretical price.
- `basis_pct`: basis divided by theoretical price, multiplied by 100.
- `log_basis`: log of observed divided by theoretical price.
- `futures_log_return`: within-contract log return.
- `spot_log_return`: daily spot log return.
- `spot_volatility_20d_ann`: 20-observation rolling standard deviation of spot log returns, annualized by `sqrt(252)`.

### `nearby_daily.csv`

One row per trading day for the listed contract with the smallest nonnegative time to expiration. `contract_changed` flags rolls. `futures_log_return` is set to missing on the first date and on roll dates; `spot_log_return` is the ordinary daily spot return.
