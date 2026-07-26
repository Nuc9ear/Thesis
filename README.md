# CNY/RUB futures thesis data

This workspace contains a reproducible collector for the daily data described in the thesis proposal, starting on 2022-07-01 by default.

## What it collects

- Quarterly MOEX CNY/RUB futures (`CR` root): OHLC, settlement price, VWAP, volume, turnover, trades, and open interest.
- MOEX CNY/RUB tomorrow-settlement spot (`CNYRUB_TOM`, board `CETS`): OHLC, VWAP, and number of trades.
- RUB RUSFAR rates: overnight, 1 week, 2 weeks, 1 month, and 3 months.
- CNY RUSFAR rates: overnight and 1 week.
- Contract listing and expiration metadata.

The processed contract panel matches the available funding tenor closest to each contract's remaining maturity and calculates the continuous-compounding cost-of-carry benchmark:

`theoretical futures = spot * exp((RUB rate - CNY rate) * years to expiry)`

Rates are converted from percent to decimals in that calculation. A previously published rate can be carried forward by at most 14 calendar days when futures trade on a day without a new rate publication; this covers the Russian New Year exchange calendar. The collector does not fill data before an indicator's official launch. In particular, `RUSFARCNY` begins on 2022-09-26 and `RUSFARCN1W` begins on 2023-12-04.

## Run

From PowerShell:

```powershell
python -m pip install -r requirements.txt
python src/collect_moex_data.py
```

Optional dates:

```powershell
python src/collect_moex_data.py --start 2022-07-01 --end 2026-07-17
```

Outputs are written to:

- `data/raw/futures_daily.csv`
- `data/raw/spot_daily.csv`
- `data/raw/funding_daily.csv`
- `data/raw/contracts.csv`
- `data/processed/contract_daily.csv`
- `data/processed/nearby_daily.csv`
- `data/manifest.json`

`nearby_daily.csv` is a front-contract series. `futures_log_return` is deliberately blank on roll dates so that a mechanical contract-price jump is not mistaken for a market return.

## Methodological choices to revisit

- `spot_price` uses CETS daily VWAP, falling back to the close if VWAP is unavailable. Both raw values are retained.
- `futures_price` uses the official settlement price, then VWAP, then close as fallbacks.
- A nearest-tenor rate is a proxy for a full funding curve. The selected tenor and tenor distance are stored in the processed panel.
- The public historical spot endpoint exposes prices and trade count but not historical spot volume. Futures volume and open interest are available.
- Academic outputs using MOEX index values should cite Moscow Exchange as the source and comply with its data-use terms.

See [docs/data_dictionary.md](docs/data_dictionary.md) for column definitions.
