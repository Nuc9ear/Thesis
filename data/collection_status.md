# Collection and availability status

## Successfully collected

| Area | Variables available | Principal source |
|---|---|---|
| CNY/RUB, USD/RUB, EUR/RUB spot | Date, board/instrument IDs, OHLC, VWAP, number of trades; official/reference RUB rates | Moscow Exchange ISS; Bank of Russia |
| All-pair futures | Contract and pair IDs, listing/last-trade/expiry dates, OHLC, settlement, VWAP, selected price, contract volume, RUB turnover, trade count, open interest count and value | Moscow Exchange ISS |
| Russian funding | RUSFAR tenors, CNY RUSFAR tenors, RUONIA, Bank of Russia key rate and RUONIA market statistics | Moscow Exchange; Bank of Russia |
| Chinese funding | Shibor O/N--1Y, CFETS FR/FDR repo fixings, LPR 1Y/5Y, PBOC 7-day reverse-repo change points | CFETS/ChinaMoney; PBOC |
| CNY/RUB futures options | Exact option and futures identifiers, call/put, strike, expiries, OHLC, settlement, VWAP, volume, turnover, trades, open interest, exchange theoretical price | Moscow Exchange ISS |
| Events | February 2022, MOEX/NCC/NSD designation, USD/EUR exchange-trading suspension, and 2026 RUB-settled USD/RUB event | Config file with official source URLs |

## Calculated variables

- Spot and futures log returns, percentage and absolute changes, rolling realized volatility, and cumulative FX change.
- Changes in volume, turnover, trades, open interest, and percentage open-interest change, with roll-safe nearby returns.
- Price/volume, return/volume, price-direction/OI, volume/OI, turnover/OI-value, abnormal activity, Amihud, spread, trade-count, and basis pressure proxies.
- Backward-as-of funding matches with tenor, source family, observation date, maturity distance, staleness, and method.
- CNY/RUB theoretical futures price, basis level/percentage/log, implied and observed funding differential, excess differential, annualized basis, and convergence change.
- Black--76 price inversion, futures delta, gamma, vega, moneyness, bounds, parity residual, validity flag, and rejection reason.
- Nearest-observed ATM, 25-delta, and 10-delta implied-volatility points, risk reversals, butterflies, and observation counts.
- Three-pair market shares, regime indicators, regime descriptive statistics, and 90-calendar-day event-window comparisons.

## Unavailable or incomplete public variables

| Variable | Status and reason |
|---|---|
| Historical spot volume and RUB turnover | The free MOEX spot-history response used here does not expose consistent pair-level values. Fields remain NA. |
| Historical spot bid/ask and spread | Bid/ask are absent from the free history response; spreads remain NA. |
| Historical option bid/ask and midpoint | The daily history response does not supply bid/ask. Settlement normally supplies the selected option price. |
| Direct buyer-/seller-initiated order flow | No order-level signed trades were collected. Pressure measures are aggregate proxies only. |
| Exact trader-specific funding cost | Not publicly observable. Market, repo, policy, and published lending rates are distinguishable proxies. |
| Full executable-arbitrage cost | Margin financing, transaction costs, capital controls, sanctions, settlement restrictions, and convertibility are not fully observed. |
| Exact American early-exercise value | The requested Black--76 framework does not value early exercise. IVs and Greeks are documented approximations. |
| Interpolated exact-delta market quotes | Surface points are nearest actual observations and are labelled as such; no synthetic value is presented as directly observed. |
| Pre-February-2022 CNY/RUB futures/options | These instruments were not yet listed in the collected MOEX contract histories. Pre/post-2022 CNY derivatives comparisons are therefore structurally unavailable; USD/EUR futures and three-pair spot histories provide the earlier benchmark. |

## Proxy hierarchy

- RUB funding: closest-tenor RUSFAR, with RUONIA fallback; key rate is a policy robustness series.
- CNY funding: closest-tenor CNY RUSFAR followed by Shibor; CFETS repo fixings, PBOC operations, and LPR are separate robustness families.
- Spot activity: number of trades where volume/turnover are unavailable.
- Option market price: bid--ask midpoint if ever available, then settlement, VWAP, close.
- Volatility surface: nearest observed strike/delta, with actual delta and support count disclosed.

## Reproducibility and quality

The full command sequence is in [`README.md`](../README.md). Strict validation currently has zero failed error checks. Four large parity residuals and 93,479 rejected futures-option observations remain in `data/quality/`; 5,346 spot-underlying CNY option rows are retained in a separate out-of-scope audit file.
