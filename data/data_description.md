# Short Answers to Data and Research Questions

This document answers the main data-availability and interpretation questions using the current repository checkpoint. Before/after figures are unadjusted 90-calendar-day comparisons from `analysis/event_window_comparison.csv`; they describe changes around an event but do not by themselves establish causality.

## 1. What spot data are available for CNY/RUB, USD/RUB and EUR/RUB?

Daily MOEX spot OHLC, VWAP, and number of trades are available for `CNYRUB_TOM`, `USD000UTSTOM`, and `EUR_RUB__TOM`. Bank of Russia official daily reference rates are also available. The combined panel contains 12,408 pair-days from 2013-01-08 to 2026-08-04. Historical pair-level spot volume, RUB turnover, bid, and ask are not populated in the free MOEX history.

## 2. How did USD/RUB and EUR/RUB trading change or collapse after sanctions?

The clearest collapse is in exchange spot trading after the 2024-06-13 suspension: average USD/RUB and EUR/RUB spot trade counts fell by 100% to zero in the following 90-day window. Futures did not disappear. Over the same window, nearby USD/RUB futures volume fell 6.9%, turnover 12.0%, and open interest 23.4%; EUR/RUB futures volume fell 1.0%, turnover 6.0%, and open interest 36.9%. Their futures market shares also declined as activity shifted toward CNY/RUB.

The earlier 2022-02-24 event was associated with a larger immediate futures contraction: in 90-day windows, USD/RUB futures volume fell about 55% and EUR/RUB volume about 78%, while turnover fell about 55% and 79%, respectively.

## 3. What data are available on exchange-rate changes, trading flows and volume?

Exchange-rate changes can be measured from daily spot and futures prices using log returns, percentage changes, absolute returns, cumulative spot changes, and daily ranges. Futures and options contain daily volume, RUB turnover, number of trades, and open interest. Spot contains number of trades, but historical spot volume and turnover are unavailable. Official reference rates contain no trading-flow information.

## 4. Is daily open interest available for each futures contract?

Yes. `open_interest_contracts` and `open_interest_value_rub` are available by futures `SECID` and trading date. Open interest is a stock of outstanding positions, whereas `volume_contracts` is the number of contracts traded during the day.

## 5. Are CNY vanilla put and call option data available?

Yes. The futures-option panel contains 1,648,342 daily observations: 824,171 calls and 824,171 puts, covering 30,328 option SECIDs from 2022-06-20 to 2026-08-03. Prices, strikes, expirations, volume, turnover, trades, and open interest are included.

## 6. Are the options written on spot CNY/RUB or on CNY/RUB futures?

The analytical option panel contains options whose exact MOEX underlying is a CNY/RUB futures `SECID`. They are futures options, not spot-FX options. Another 5,346 raw observations found by the broad collection query have a spot underlying; they remain in raw/audit data but are excluded from the futures-option panel.

## 7. Are option delta, implied volatility and volatility-surface data available?

Yes, but they are calculated rather than exchange-quoted. The option panel contains Black--76 implied volatility, futures delta, gamma, and vega. The surface file contains 9,690 underlying-expiry-day summaries with ATM, nearest observed 10-delta and 25-delta call/put IVs, risk reversals, and butterflies. Points are nearest observations, not exact interpolated delta quotes.

## 8. What futures price data are available for different contract maturities?

The full panel contains 56,515 daily observations for 188 resolved contracts: 22 CNY/RUB, 92 USD/RUB, and 74 EUR/RUB. Raw and normalized OHLC, settlement, VWAP, the selected analytical price, first/last trading dates, expiration, and remaining maturity are available. `futures_pricing_panel.csv` retains every maturity; `fx_nearby_daily.csv` selects the shortest positive-price non-expired contract for each pair-date.

## 9. Which Russian and Chinese funding rates are available by maturity?

- **RUB:** RUSFAR O/N, 1W, 2W, 1M, and 3M; RUONIA O/N; Bank of Russia key rate.
- **CNY:** CNY RUSFAR O/N and 1W; Shibor O/N, 1W, 2W, 1M, 3M, 6M, 9M, and 1Y; FR/FDR repo fixings at 1D, 7D, and 14D; LPR 1Y and 5Y; PBOC 7-day reverse-repo rate.

Each wide funding series includes its source observation date and staleness in days.

## 10. What proxy funding rates can be used when direct rates are unavailable?

For RUB, RUONIA is the main overnight fallback to RUSFAR. For CNY, the closest Shibor tenor is the main fallback to CNY RUSFAR. FR/FDR repo fixings are useful secured-market robustness proxies. The CBR key rate, PBOC reverse-repo rate, and LPR are policy or published-reference proxies and should be kept distinct from marginal market funding.

## 11. How did pricing, liquidity, funding rates and volatility change before and after sanctions?

The strongest descriptive changes are:

- Around 2022-02-24, 20-day annualized spot volatility rose from 11.6% to 55.2% for CNY/RUB, from 10.4% to 44.0% for USD/RUB, and from 11.0% to 40.9% for EUR/RUB. USD/RUB and EUR/RUB futures volume and turnover contracted sharply.
- Around the 2024-06-13 suspension, CNY/RUB nearby volume rose 65.9%, turnover 55.7%, and futures trades 102.9%. Its futures-volume share rose from 78.1% to 85.9%.
- The mean CNY/RUB basis moved from -0.50% to -1.53%, while the observed RUB-minus-CNY funding differential rose from 13.91 to 14.66 percentage points.
- Amihud illiquidity increased about 21% for CNY/RUB, 89% for USD/RUB, and 92% for EUR/RUB. ATM CNY/RUB option IV rose from 14.8% to 19.4%.

These are short-window descriptive comparisons. They do not isolate sanctions from simultaneous policy, volatility, liquidity, and macroeconomic changes.

## 12. What variables, frequency, units and coverage does each dataset contain?

| Dataset | Frequency and row unit | Main variables and units | Current coverage |
|---|---|---|---|
| `fx_spot_panel.csv` | Daily pair-day | Prices in RUB per foreign-currency unit; trades as counts; returns/volatility as decimals; changes/ranges as percent | 12,408 rows; 2013-01-08--2026-08-04 |
| `futures_pricing_panel.csv` | Daily pair-contract-day | Raw/source and normalized RUB-per-unit prices; volume/OI in contracts; turnover/OI value in RUB; rates and basis in percent | 56,515 rows; 2009-01-11--2026-08-03 |
| `fx_nearby_daily.csv` | Daily pair-day | Same units as full futures panel plus roll indicator | 9,885 rows; 2009-01-11--2026-08-03 |
| `funding_curve_daily.csv` | Daily/as-of date | Rates in annual percent; source dates; staleness in calendar days | 5,128 rows; calendar 2009-01-11--2026-08-04, with rate values mainly from 2022 |
| `currency_market_share_daily.csv` | Daily pair-day | Spot trades as counts; futures contracts, RUB turnover, OI and trades; shares as fractions | 14,363 rows; 2009-01-11--2026-08-04 |
| `market_pressure_daily.csv` | Daily pair-day | Price/activity products, ratios, z-scores, Amihud return per RUB million, basis percent | 9,885 rows; 2009-01-11--2026-08-03 |
| `options_panel.csv` | Daily option-contract-day | Prices/strikes in RUB per CNY; volume/OI in contracts; turnover in RUB; IV as annualized decimal; Greeks/model fields | 1,648,342 rows; 2022-06-20--2026-08-03 |
| `volatility_surface_daily.csv` | Daily underlying-expiry-day | IV and risk measures as decimal volatility; strikes in RUB per CNY; deltas dimensionless | 9,690 rows; 2022-06-20--2026-07-17 |
| `sanctions_regime_daily.csv` | Daily date | Regime category, Boolean event flags, signed calendar days from events | 5,128 rows; 2009-01-11--2026-08-04 |
| `contract_daily.csv` | Legacy daily CNY contract-day | CNY futures, spot, funding, maturity, and basis fields | 6,042 rows; 2022-07-01--2026-07-17 |
| `nearby_daily.csv` | Legacy daily CNY date | Legacy shortest-maturity CNY futures series and roll flag | 1,030 rows; 2022-07-01--2026-07-17 |

For complete column-level definitions, see [`data_dictionary.md`](data_dictionary.md). For detailed formulas and interpretation, see [`data_description.md`](data_description.md).
