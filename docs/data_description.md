# Data Description

The collected data form a reproducible public-source panel for analysing CNY/RUB pricing, market activity, funding conditions, derivatives, and the structural break of 13 June 2024.

## Page 1: Scope and market data

### Table 1. Research design and coverage

| Aspect | Description |
|---|---|
| Research purpose | Examine CNY/RUB spot and futures pricing, cost of carry, market activity, option-implied risk, and changes surrounding the June 2024 sanctions event. |
| Official sources | Moscow Exchange (MOEX); Bank of Russia; China Foreign Exchange Trade System (CFETS/ChinaMoney); People's Bank of China (PBOC). |
| Main empirical window | 1 July 2022--28 July 2026; MOEX futures and spot observations end on 27 July 2026 where 28 July was not yet a trading-data date. |
| Extended histories | Five-pair spot panel from January 2013; USD/RUB and EUR/RUB futures benchmark from 2009 through 2021. |
| Main event date | 13 June 2024, the first trading day after the designation of MOEX, the National Clearing Centre, and the National Settlement Depository. |
| Quote and time conventions | CNY/RUB prices are RUB per CNY; futures maturity is measured using calendar days and Actual/365 years. |

### Table 2. Market datasets collected

| Component | Coverage and size | Main contents and research use |
|---|---|---|
| CNY/RUB futures | 22 contracts; 6,078 contract-day rows; 1 July 2022--27 July 2026 | Contract identifier, expiry, time to maturity, OHLC, settlement, volume, RUB turnover, open interest, and trade count. Futures price uses settlement, then VWAP, then close. |
| CNY/RUB spot | 1,036 daily observations | MOEX spot VWAP, with close as fallback; used for returns, realised volatility, cost of carry, and basis measurement. |
| Continuous nearby futures | 1,036 trading days; 17 selected contracts; 16 rolls | Selects the observed non-expired contract with the shortest maturity. Returns are missing on roll dates to prevent artificial price changes. |
| Six focal maturities | 1,511 rows for CRM6, CRU6, CRZ6, CRH7, CRM7, and CRU7 | Post-event contract histories containing prices, activity, funding matches, theoretical values, basis, and event indicators. |
| Canonical spot-FX panel | 20,161 pair-day rows through 28 July 2026 | CNY/RUB: 4,111; USD/RUB: 4,037; USD/CNY: 4,013; EUR/RUB: 4,012; EUR/CNY: 3,988. Supports cross-market and regime comparisons. |
| Spot activity panel | 3,424 daily rows | MOEX trade counts for CNY/RUB, USD/RUB, EUR/RUB, and USD/CNY; includes CNY/RUB's share of activity among RUB pairs. |
| Historical USD/EUR futures | 134 contracts; 32,109 contract-day rows; 6,472 market-day nearby rows; 2009--2021 | USD/RUB (`Si`): 20,067 rows; EUR/RUB (`Eu`): 12,042. RUB-per-1,000-unit prices are retained and normalized per USD or EUR. |

### Table 3. Spot-price source hierarchy

| Priority | Source and condition | Treatment |
|---:|---|---|
| 1 | Direct MOEX row with a positive price and positive trade count | Retains OHLC, VWAP, and `NUMTRADES`; classified as an exchange observation. |
| 2 | MOEX cross-implied rate when active component pairs are available | USD/CNY and EUR/CNY are derived from RUB pairs; daily highs and lows are bounds because component extrema may not be simultaneous. |
| 3 | Bank of Russia official rate or official-rate cross | Provides price continuity but is labelled as a reference rate, not an exchange close. |
| Return rule | Any change in selected source | The one-day log return is left missing rather than joining unlike price regimes. |

<div style="page-break-after: always;"></div>

## Page 2: Funding, derived variables, options, and limitations

### Table 4. Funding and policy-rate data

| Series | Coverage or frequency | Role in the analysis |
|---|---|---|
| Daily funding curve | 1,489 rows | As-of panel combining Russian and Chinese funding measures without using future information. |
| MOEX RUSFAR | RUB and CNY tenors from overnight onward | Primary exchange-based RUB and CNY funding proxies matched to futures maturity. |
| Bank of Russia key rate | 1,037 daily observations | Russian monetary-policy benchmark. |
| RUONIA and term RUONIA | 1,004 overnight observations plus one-, three-, and six-month averages | Transaction-based RUB interbank conditions; merged by publication date to prevent look-ahead. |
| SHIBOR | 1,015 days; overnight to one year | Official unsecured onshore CNY benchmark and alternative CNY cost-of-carry specification. |
| CFETS repo fixings | 1,015 days, including FDR007 | Secured Chinese funding proxy; FDR007 is a morning fixing based on DR007 transactions. |
| Loan prime rate | 51 monthly observations for one and five years | Chinese lending benchmark retained as background, not treated as an interbank funding rate. |
| PBOC reverse-repo rate | Seven official changes in the seven-day policy rate | Effective-date monetary-policy series carried forward until the next official change. |
| As-of rule | Maximum 14 calendar days; 45 days for monthly LPR | Each contract is matched to the closest tenor; source date and tenor distance remain recorded. |

### Table 5. Constructed analytical variables

| Variable | Construction and interpretation |
|---|---|
| Theoretical futures price | $F^{*}_{t,T}=S_t\exp[(r^{RUB}_{t,T}-r^{CNY}_{t,T})T]$, where $T$ is Actual/365 time to expiration. |
| Futures basis | Observed minus theoretical futures price, reported in RUB per CNY, percentage, and logarithmic form. |
| SHIBOR robustness basis | Replaces the MOEX CNY rate with the closest SHIBOR maturity. |
| Basis z-score | Within-contract 60-observation standardization used to identify unusually large pricing deviations. |
| Returns and volatility | Within-contract futures log returns, spot log returns, and annualized rolling 20-observation spot volatility. |
| Market-activity measures | Trade counts, CNY/RUB share of RUB-pair trades, pre-event activity ratios, and signed activity-pressure z-scores. |
| Event variables | Pre/post indicator, regime label, and calendar distance from 13 June 2024. |

### Table 6. CNY/RUB option data

| Output | Size | Variables and use |
|---|---:|---|
| Raw weekly archive | 30,698 metadata rows; 330,174 contract-snapshot rows; 214 dates | Type, strike, expiry, underlying futures, settlement, volume, turnover, open interest, and trades. |
| Valid surface | 13,570 strike-expiry points | Positive volume or open interest; log-moneyness, Black--76 implied volatility, and futures delta. |
| Expiry summaries | 2,009 rows | ATM volatility, 25-delta risk reversal and butterfly, put/call ratios, and ATM implied variance less trailing realised spot variance. |

### Table 7. Event evidence, limitations, and validation

| Item | Recorded result or interpretation boundary |
|---|---|
| Pre-suspension activity | During the 90 calendar days before suspension, CNY/RUB averaged 54,339 trades per observed day; USD/RUB plus EUR/RUB averaged 29,355. |
| Suspension regime | CNY/RUB averaged 62,520 trades, while recorded MOEX USD/RUB and EUR/RUB exchange trading fell to zero. |
| 2026 USD/RUB regime | From 16 February 2026, 112 positive-price USD/RUB rows reappear and are classified as RUB-settled and non-deliverable. |
| Spot-data limitation | Free MOEX history does not report pair-level historical volume, turnover, bid, ask, or spreads. `NUMTRADES` is an activity count, not volume. |
| Option limitation | Weekly records are snapshot-day observations, not weekly flow totals. Black--76 approximates American-style, futures-style options; delta is futures delta. |
| Pricing limitation | A large basis is not proof of arbitrage because funding access, capital controls, margin, sanctions, settlement risk, spreads, and costs are not fully observed. |
| Sample limitation | The six focal 2026--2027 futures trade only after the June 2024 event and cannot alone identify a pre/post change. |
| Validation | No duplicate processed keys or non-positive canonical prices were found. A total of 162 contract-day rows lack a sufficiently recent CNY funding rate and therefore a theoretical price. |
