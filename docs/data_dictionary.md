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

## Full field glossary for `contract_daily.csv` and `nearby_daily.csv`

The two files share 48 fields. Their different placement of `trade_date` and `boardid` in the header has no analytical meaning. `nearby_daily.csv` contains one additional field, `contract_changed`, and uses a roll-safe definition of `futures_log_return`.

| Output | Row definition | Special treatment |
|---|---|---|
| `contract_daily.csv` | One row for each CNY/RUB futures contract and trading date. | `futures_log_return` is calculated within the same `secid`. |
| `nearby_daily.csv` | One row per trading date for the available non-expired contract with the lowest nonnegative `days_to_maturity`. | Adds `contract_changed`; recomputes `futures_log_return` on the selected nearby series and leaves it missing on contract-change dates. |

### Identifiers and contract dates

| Field | Unit or format | Explanation |
|---|---|---|
| `trade_date` | Date | Trading-session date to which all futures, spot, and matched funding information in the row refers. |
| `boardid` | Text | MOEX trading-board identifier. `RFUD` is the main FORTS futures board used in this dataset. |
| `secid` | Text | Exact MOEX security identifier for the futures contract, such as `CRU2`. It is the contract key used for within-contract calculations. |
| `shortname` | Text | MOEX short contract name reported in daily trading history, such as `CNY-9.22`. |
| `assetcode` | Text | MOEX code for the underlying asset; `CNY` identifies Chinese-yuan futures. |
| `shortname_meta` | Text | Short name obtained separately from the MOEX contract-reference metadata. It is retained alongside `shortname` for identification and validation. |
| `expiry_date` | Date | Contract delivery/expiration date from the MOEX `LSTDELDATE` reference field. |
| `first_trade_date` | Date | First date on which MOEX lists the contract as tradable. |
| `last_trade_date` | Date | Scheduled final trading date from the MOEX `LSTTRADE` reference field. It is kept separately from `expiry_date`. |

### Futures-market fields

All futures price fields are quoted in RUB per CNY. Raw MOEX fields remain missing when the exchange did not report a value.

| Field | Unit or format | Explanation |
|---|---|---|
| `futures_open` | RUB per CNY | Price of the first reported futures trade in the session. |
| `futures_low` | RUB per CNY | Lowest reported futures trade price during the session. |
| `futures_high` | RUB per CNY | Highest reported futures trade price during the session. |
| `futures_close` | RUB per CNY | MOEX closing/last futures trade price for the session; it is distinct from the official settlement price. |
| `open_interest_value_rub` | RUB | MOEX-reported RUB notional value of outstanding open futures positions. It is not cash invested and is not a signed directional position. |
| `turnover_rub` | RUB per day | Total RUB value of futures trades reported by MOEX for the contract and session. |
| `volume_contracts` | Contracts per day | Total number of futures contracts traded during the session. |
| `open_interest_contracts` | Contracts | MOEX-reported open-interest count for the contract at the session date. It is a stock, not daily trading flow. |
| `futures_settle_price` | RUB per CNY | Official daily futures settlement price used by MOEX for clearing and margin calculations. |
| `swaprate` | MOEX native value | MOEX SwapRate/funding component intended principally for perpetual futures. It is normally missing and not applicable for the dated CNY/RUB contracts in these files. |
| `futures_wap_price` | RUB per CNY | Volume-weighted average futures trade price for the session. |
| `change` | Percent | MOEX-reported percentage change in the closing/last futures price relative to the previous trading session. It is retained as reported. |
| `qty` | Contracts | Number of contracts in the final reported trade of the session; it is not total daily volume. |
| `futures_num_trades` | Count per day | Number of futures trades executed during the session. |
| `futures_price` | RUB per CNY | Empirical futures-price series used in the analysis: `futures_settle_price`, otherwise `futures_wap_price`, otherwise `futures_close`. |

### Spot-market fields

The spot fields refer to the MOEX `CNYRUB_TOM` instrument and are quoted in RUB per CNY.

| Field | Unit or format | Explanation |
|---|---|---|
| `spot_open` | RUB per CNY | Price of the first reported CNY/RUB spot trade in the session. |
| `spot_low` | RUB per CNY | Lowest reported CNY/RUB spot trade price in the session. |
| `spot_high` | RUB per CNY | Highest reported CNY/RUB spot trade price in the session. |
| `spot_close` | RUB per CNY | Closing/last reported CNY/RUB spot trade price. |
| `spot_wap_price` | RUB per CNY | Volume-weighted average CNY/RUB spot price reported by MOEX. |
| `spot_num_trades` | Count per day | Number of CNY/RUB spot trades during the session. It is a trade count, not volume or turnover. |
| `spot_price` | RUB per CNY | Spot-price series used in the analysis: `spot_wap_price`, otherwise `spot_close`. |
| `spot_log_return` | Decimal log return | `ln(spot_price[t] / spot_price[t-1])` across consecutive spot observations. |
| `spot_volatility_20d_ann` | Annualized decimal | Rolling standard deviation of the latest 20 spot log returns, annualized by multiplying by `sqrt(252)`. At least 10 returns are required; `0.20` means approximately 20% annualized volatility. |

### Maturity and matched funding fields

Funding observations are matched backward as-of: a future publication is never used. The maximum allowed staleness is 14 calendar days.

| Field | Unit or format | Explanation |
|---|---|---|
| `days_to_maturity` | Calendar days | `expiry_date - trade_date`. Only nonnegative values are eligible for nearby-contract selection. |
| `ttm_years` | Years | Time to maturity calculated as `days_to_maturity / 365` under an Actual/365 convention. |
| `rub_rate_tenor` | MOEX SECID | Selected RUB RUSFAR instrument whose nominal tenor is closest to `days_to_maturity`. |
| `rub_rate_pct` | Percent per annum | Annualized rate reported for the selected RUB funding tenor. Divide by 100 before using it as a decimal rate. |
| `rub_tenor_distance_days` | Calendar days | Absolute difference between `days_to_maturity` and the selected RUB tenor's nominal number of days. |
| `rub_rate_observation_date` | Date | Actual observation/publication date of the RUB rate used in the row. It may precede `trade_date` by no more than 14 calendar days. |
| `cny_rate_tenor` | MOEX SECID | Selected CNY RUSFAR instrument whose nominal tenor is closest to `days_to_maturity`. |
| `cny_rate_pct` | Percent per annum | Annualized rate reported for the selected CNY funding tenor. Divide by 100 before using it as a decimal rate. |
| `cny_tenor_distance_days` | Calendar days | Absolute difference between `days_to_maturity` and the selected CNY tenor's nominal number of days. |
| `cny_rate_observation_date` | Date | Actual observation/publication date of the CNY rate used in the row. It may precede `trade_date` by no more than 14 calendar days. |

### Derived pricing, basis, and return fields

| Field | Unit or format | Explanation |
|---|---|---|
| `theoretical_futures_price` | RUB per CNY | Continuous-compounding cost-of-carry value: `spot_price * exp(((rub_rate_pct - cny_rate_pct) / 100) * ttm_years)`. It is missing if a valid positive price, nonnegative maturity, or funding rate is unavailable. |
| `basis_rub_per_cny` | RUB per CNY | Pricing deviation in level form: `futures_price - theoretical_futures_price`. Positive values mean the observed futures price exceeds the simple carry benchmark. |
| `basis_pct` | Percent | `100 * basis_rub_per_cny / theoretical_futures_price`. |
| `log_basis` | Decimal log difference | `ln(futures_price / theoretical_futures_price)`. It is defined only when both prices are positive. |
| `futures_log_return` | Decimal log return | In `contract_daily.csv`, `ln(futures_price[t] / futures_price[t-1])` within the same `secid`. In `nearby_daily.csv`, the log change in the selected nearby price, set to missing on the first row and every contract-change date. |
| `contract_changed` | Boolean; nearby only | `TRUE` on the first nearby row and whenever the selected `secid` differs from the preceding trading date; otherwise `FALSE`. It flags rolls or other changes in the selected nearby contract. |

### Interpretation notes

- Missing values are genuine unavailable or inapplicable observations; they are not automatically zeros.
- `volume_contracts`, `turnover_rub`, `open_interest_contracts`, and `open_interest_value_rub` are different concepts and should not be used interchangeably.
- `futures_close`, `futures_settle_price`, and `futures_wap_price` are distinct exchange measures; `futures_price` documents the priority used to obtain one analytical series.
- The cost-of-carry basis is a pricing deviation, not proof of executable arbitrage after funding access, capital controls, margin, spreads, settlement, and sanctions constraints.
