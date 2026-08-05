# Data Description

## Page 1: Scope, sources, and market panels

### Table 1. Design and current coverage

| Component | Current processed coverage | Contents and research role |
|---|---:|---|
| Spot FX panel | 12,408 pair-days; 2013-01-08--2026-08-04 | CNY/RUB, USD/RUB, and EUR/RUB OHLC, VWAP, trade count, Bank of Russia reference rate, returns, percentage changes, cumulative change, range, 20-observation volatility, and availability flags. |
| Full futures panel | 56,515 contract-days; 2009-01-11--2026-08-03 | All resolved maturities: CNY/RUB 6,108, USD/RUB 30,769, EUR/RUB 19,638. Raw and RUB-per-unit normalized prices, volume, turnover, trades, open interest, maturity, changes, returns, funding, pricing, and regimes are retained. |
| Roll-safe nearby futures | 9,885 pair-days | Shortest positive-price non-expired maturity by pair. Returns and activity changes are missing on contract-change dates. |
| Daily futures options | 1,648,342 in-scope rows; 2022-06-20--2026-08-03 | Balanced calls and puts on CNY/RUB futures. Exact underlying, strike, expiries, OHLC, settlement, VWAP, activity, Black--76 IV/Greeks, moneyness, parity residual, and rejection flags. |
| Valid option observations | 1,554,863 rows | Observations satisfying maturity, price, underlying, bounds, and IV-solver rules. The 93,479 rejected rows remain separate and explained. |
| Volatility-surface summaries | 9,690 underlying-expiry-days; through 2026-07-17 | Nearest observed ATM, 25-delta call/put, 10-delta call/put, risk reversals, butterflies, and actual supporting-observation counts. |
| Funding curve | 5,128 calendar/trading dates; 2009-01-11--2026-08-04 | Backward-as-of Russian and Chinese market, repo, policy, and published lending benchmarks with source dates and staleness. |
| Pressure, market share, regimes | 9,885 pressure rows; 14,363 pair-share rows; 5,128 regime dates | Activity/price proxies, three-pair shares, and event indicators used for before/after comparisons. |

### Table 2. Official sources and collected fields

| Source | Series or instruments | Treatment |
|---|---|---|
| Moscow Exchange ISS | CNY/RUB, USD/RUB, EUR/RUB spot; CR, Si, Eu futures; CNY futures options; RUSFAR | Raw exchange observations and exact contract descriptions. Si/Eu prices quoted per 1,000 currency units are also normalized per unit. |
| Bank of Russia | Official FX rates, key rate, RUONIA | Reference FX is kept distinct from exchange prices. RUONIA is matched by publication date to prevent look-ahead. |
| CFETS/ChinaMoney | Shibor and FR/FDR repo fixings | Unsecured interbank and secured repo families remain distinguishable. FDR007 is used as a DR007-related fixing proxy, not relabelled as transaction-level DR007. |
| People's Bank of China | Loan prime rates and 7-day reverse-repo rate changes | Policy/published rates are robustness or background proxies rather than automatic marginal trader funding costs. |
| Configuration | Events dated 2022-02-24, 2024-06-12, 2024-06-13, and 2026-02-16 | Dates and labels live in `config/research_config.json` and can be changed without editing processing code. |

### Table 3. Flow, stock, and market-pressure construction

| Variable family | Formula or definition | Interpretation boundary |
|---|---|---|
| Currency change | Log return, percentage change, absolute return, cumulative exchange-rate change, 20-observation annualized volatility | Returns are not joined across a spot-source switch or a futures roll. |
| Trading activity | First changes in volume, turnover, trades, and open interest; percentage OI change | Volume/turnover are flows; open interest is a stock. |
| Price/activity pressure | Price change × volume; log return × volume; sign(return) × change in OI | Directional proxies only; not signed order flow. |
| Relative pressure | Volume/OI; turnover/open-interest value; rolling abnormal-volume and abnormal-OI z-scores | Ratios are missing for zero denominators. |
| Liquidity | Bid--ask spread where available; Amihud absolute return per RUB million turnover; trade count | Free historical spot/option bid and ask are unavailable, so spread fields are normally missing. |
| Relative market importance | CNY/RUB, USD/RUB, and EUR/RUB shares of available spot trades and futures activity | Missing spot volume prevents a genuine spot-volume market share; trade-count share is explicitly named. |

<div style="page-break-after: always;"></div>

## Page 2: Funding, pricing, options, validation, and limits

### Table 4. Maturity matching and futures pricing

| Item | Definition |
|---|---|
| Quotation | Spot and normalized futures prices are RUB per one CNY, USD, or EUR. For CNY/RUB, RUB is domestic/quote currency and CNY is foreign/base currency. |
| Time | `days_to_maturity = expiry_date - trade_date`; `ttm_years = days_to_maturity / 365`. |
| Rate match | Closest available tenor to remaining maturity, using backward as-of observations only. Market-rate maximum staleness is 14 calendar days; monthly LPR allows 45. Tenor, distance, date, staleness, method, and source family are stored. |
| Theoretical price | $F^*_{t,T}=S_t\exp[(r^{RUB}_{t,T}-r^{foreign}_{t,T})T]$, using annual percentage rates divided by 100. Pricing outputs are currently populated for CNY/RUB; USD/EUR histories support activity comparisons. |
| Deviations | Observed minus theoretical price; percentage and log basis; annualized log basis; implied, observed, and excess funding differentials; change in absolute basis toward expiry. |
| Interpretation | A positive basis means the observed future exceeds this simple benchmark. It is not proof of executable arbitrage after costs, margin, access restrictions, controls, sanctions, settlement risk, and convertibility. |

### Table 5. Option model and volatility surface

| Item | Implementation |
|---|---|
| Instrument scope | Vanilla calls and puts whose exact MOEX `UNDERLYINGASSET` is a CNY/RUB futures SECID. The 5,346 spot-underlying option rows found by the broad archive query are preserved in raw/audit data but excluded from the futures-options panel. |
| Market-price hierarchy | Bid--ask midpoint, settlement, VWAP, close. Historical bid/ask are unavailable, so settlement normally has priority. Nonpositive prices stay rejected. |
| Model | Black--76 on the underlying futures. MOEX contracts are futures-style/margined, so the model discount factor is one. American early exercise is not modelled and is a limitation. |
| Delta convention | Unadjusted Black--76 futures delta: $N(d_1)$ for calls and $N(d_1)-1$ for puts. It is not OTC spot delta, forward delta, or premium-adjusted FX delta. |
| Moneyness and ATM | $K/F$ and $\ln(K/F)$; ATM is the valid observation with minimum absolute log moneyness. |
| Standard points | Nearest actual 25-delta and 10-delta call/put observations. Risk reversal is call IV minus put IV; butterfly is their average minus ATM IV. Counts disclose supporting actual observations. No interpolated point is presented as a direct quote. |
| Rejections | Invalid/nonpositive maturity or price, absent dated underlying price, no-arbitrage-bound failure, or no stable IV within 0.01%--500% annualized volatility. |

### Table 6. Validation result and missing variables

| Check or limitation | Result |
|---|---|
| Required integrity checks | Strict validation reports zero failed error checks: no duplicate processed keys, negative futures maturity, nonpositive selected futures/spot prices, future-dated rate matches, stale matched market rates, invalid futures underlyings, or roll returns. |
| Warnings | Four large put--call parity residuals and 93,479 rejected option rows are retained for audit rather than silently deleted. |
| Spot activity gaps | Historical spot volume, turnover, bid, and ask are not exposed consistently by the free MOEX history endpoint. They remain missing; number of trades is available. |
| Option quote gaps | Historical bid and ask are unavailable; midpoint and spread cannot be reconstructed. |
| Funding proxies | Exact maturity curves are not always available. Closest-tenor RUSFAR/Shibor matching is primary; RUONIA is a fallback. Repo, policy, and LPR series are retained as distinct robustness measures. |
| Market-pressure limitation | Proxies combine prices with public aggregate activity. They do not identify buyer- versus seller-initiated orders. |
| Reproducibility | Raw checkpoints, source URLs, configuration, processing scripts, unit tests, variable catalogue, analysis tables, and quality reports are all stored in the repository. |

The complete source/original-field/unit/frequency/transformation/missing-value/interpretation/limitation record for every CSV column is in [`variable_catalog.csv`](variable_catalog.csv).
