# Data Description and Data Dictionary

## 1. Overview

The dataset contains daily foreign-exchange, futures-market, contract-specification and funding-rate data used to study the pricing of CNY/RUB futures traded on the Moscow Exchange.

The core empirical period begins in the second half of 2022, when the Chinese yuan became substantially more important in the Russian foreign-exchange and derivatives markets. The CNY/RUB dataset extends from this period to the latest date available at the time of data collection.

Historical USD/RUB and EUR/RUB data from the period before 2022 are also included for comparison. These historical currency pairs provide a benchmark for examining whether the pricing and trading characteristics of CNY/RUB futures differ from those of the Russian derivatives market before the major structural changes that occurred in 2022.

The main frequency of the dataset is daily. Each observation normally represents one trading date for a particular market instrument or futures contract.

## 2. Main Data Sources

The data are collected primarily from the following sources:

### Moscow Exchange

The Moscow Exchange provides:

- CNY/RUB spot-market data;
- CNY/RUB futures prices;
- USD/RUB and EUR/RUB historical futures data;
- trading volume;
- number of transactions;
- open interest;
- turnover;
- settlement prices;
- futures contract expiration dates;
- futures contract specifications;
- Russian-ruble and Chinese-yuan money-market benchmarks.

### Bank of Russia

The Bank of Russia provides official foreign-exchange and monetary data used to describe conditions in the Russian currency and money markets.

These data may include:

- official foreign-exchange rates;
- key monetary-policy rates;
- money-market indicators;
- historical Russian foreign-exchange information.

### Official Chinese financial-market sources

Chinese interest-rate information is obtained from official institutions and market administrators, including:

- the People’s Bank of China;
- the China Foreign Exchange Trade System;
- the National Interbank Funding Center.

The Chinese data include interbank interest rates such as SHIBOR and, where available, relevant secured or repo-market rates.

---

## 3. CNY/RUB Spot-Market Data

The principal spot-market instrument is `CNYRUB_TOM` traded on the Moscow Exchange.

`CNYRUB_TOM` represents the exchange rate between the Chinese yuan and the Russian ruble with settlement on the next business day. Therefore, it is a next-day-settlement foreign-exchange instrument rather than an immediate cash transaction.

The spot-market dataset contains daily trading information published by the Moscow Exchange.

### Spot-market variables

| Variable | Description |
|---|---|
| `trade_date` | Calendar date on which the spot-market observation was recorded. |
| `security_id` | Exchange identifier of the financial instrument, such as `CNYRUB_TOM`. |
| `spot_open` | First recorded trading price of the instrument during the trading session. |
| `spot_low` | Lowest traded spot price recorded during the trading session. |
| `spot_high` | Highest traded spot price recorded during the trading session. |
| `spot_close` | Last or closing spot price recorded for the trading session. |
| `spot_wap_price` | Volume-weighted average price reported by the exchange for the trading session. |
| `spot_num_trades` | Total number of transactions executed in the spot instrument during the trading session. |

The spot prices are expressed as the number of Russian rubles paid for one Chinese yuan, subject to the quotation convention reported by the Moscow Exchange.

The opening, highest, lowest, closing and weighted-average prices are separate original exchange observations. No single analytical spot-price measure is defined in this raw-data description.

---

## 4. CNY/RUB Futures Data

The futures dataset contains daily observations for CNY/RUB futures contracts traded on the Moscow Exchange Derivatives Market.

Unlike a continuous futures series, the contract-level data preserve the identity of each individual futures contract. Consequently, different contracts may be observed on the same trading day because contracts with different expiration dates can trade simultaneously.

The basic unit of observation is therefore:

> One futures contract on one trading date.

### Futures price variables

| Variable | Description |
|---|---|
| `trade_date` | Date on which the futures-market observation was recorded. |
| `security_id` | Unique Moscow Exchange identifier of the futures contract. |
| `contract_code` | Exchange code or ticker identifying the individual futures contract. |
| `futures_low` | Lowest traded price of the futures contract during the trading session. |
| `futures_high` | Highest traded price of the futures contract during the trading session. |
| `futures_close` | Closing or last reported price of the futures contract for the trading session. |
| `futures_settle_price` | Official settlement price established by the Moscow Exchange for the contract on the relevant trading day. |
| `futures_wap_price` | Volume-weighted average trading price of the futures contract during the session. |
| `change` | Daily price change reported directly by the Moscow Exchange. Although this field represents a change in price, it is retained as an exchange-provided observation and is not calculated by the researcher. |
| `swaprate` | Swap-rate field reported by the source for the relevant instrument, where available. |

The settlement price is the official value used by the exchange for daily contract settlement and variation-margin calculations. It is not necessarily equal to the final transaction price.

The volume-weighted average price represents the average execution price during the trading session, with transactions weighted by their trading quantities.

The closing price represents the final or officially reported closing market price. It may differ from both the settlement price and the volume-weighted average price.

---

## 5. Futures Trading-Activity Data

The futures dataset also contains original exchange observations describing market activity and liquidity.

| Variable | Description |
|---|---|
| `qty` | Trading quantity reported by the Moscow Exchange for the relevant contract and date. |
| `futures_num_trades` | Number of transactions executed in the futures contract during the trading session. |
| `volume_contracts` | Total number of futures contracts traded during the trading session. |
| `turnover_rub` | Total value of trading activity expressed in Russian rubles, as reported by the exchange. |
| `open_interest_contracts` | Number of outstanding futures contracts remaining open at the end of the trading session. |
| `open_interest_value_rub` | Exchange-reported monetary value of outstanding open positions, expressed in Russian rubles. |

### Trading volume

Trading volume measures the number of contracts exchanged during a particular trading day. It reflects the level of market activity but does not show how many positions remained open after trading ended.

A purchase and sale together constitute a futures transaction. The exact counting convention follows the methodology used by the Moscow Exchange.

### Number of trades

The number of trades records how many individual transactions occurred during the session. It differs from contract volume because one transaction may involve more than one contract.

### Turnover

Turnover represents the exchange-reported monetary value associated with trading activity. It provides an additional measure of market size and activity.

Turnover is taken directly from the source and is not reconstructed by multiplying price and volume in the analytical dataset.

### Open interest

Open interest measures the number of futures contracts that remained outstanding at the end of the trading day.

It differs from trading volume:

- trading volume measures contracts traded during the day;
- open interest measures contracts that remained open after the trading session.

An increase in open interest indicates that new outstanding positions have been created. A decrease indicates that existing positions have been closed, expired or otherwise removed.

---

## 6. Futures Contract Information

Contract-level information is used to identify individual futures instruments and determine their contractual characteristics.

| Variable | Description |
|---|---|
| `security_id` | Unique exchange identifier assigned to the contract. |
| `contract_code` | Trading code or ticker of the futures contract. |
| `short_name` | Abbreviated contract name published by the exchange. |
| `underlying_asset` | Currency pair or financial instrument underlying the futures contract. |
| `trade_date` | Date of the relevant market observation. |
| `expiry_date` | Official expiration date of the futures contract. |
| `last_trading_date` | Final date on which the contract may be traded, where this information is separately provided. |
| `contract_size` | Standard quantity of the underlying currency represented by one futures contract, where provided in the contract specification. |
| `quotation_unit` | Unit in which the futures price is quoted. |
| `board_id` | Moscow Exchange trading-board identifier associated with the instrument. |

The expiration date is obtained from the exchange contract specification. It is not calculated from the contract code.

Several futures contracts may be active simultaneously. For example, a short-maturity contract and a longer-maturity contract may both have valid price and trading observations on the same date.

---

## 7. Nearby Futures Contract Data

The project contains a nearby-contract dataset that identifies the shortest-maturity active futures contract for each trading date.

The underlying market observations remain original exchange data. However, the selection of which contract is treated as the nearby contract is part of the dataset-construction procedure rather than an original variable published by the exchange.

The nearby dataset may contain the following original fields copied from the selected contract:

| Field | Description |
|---|---|
| `trade_date` | Trading date of the observation. |
| `security_id` | Identifier of the selected futures contract. |
| `contract_code` | Code of the selected futures contract. |
| `expiry_date` | Official contract expiration date. |
| `futures_settle_price` | Exchange-reported settlement price. |
| `futures_wap_price` | Exchange-reported weighted-average price. |
| `futures_close` | Exchange-reported closing price. |
| `volume_contracts` | Exchange-reported trading volume. |
| `open_interest_contracts` | Exchange-reported open interest. |
| `futures_num_trades` | Exchange-reported number of transactions. |
| `turnover_rub` | Exchange-reported trading turnover. |

The term “nearby” describes the contract-selection rule. It is not the name of a separate financial instrument traded on the exchange.

---

## 8. Historical USD/RUB and EUR/RUB Data

Historical USD/RUB and EUR/RUB futures and spot-market observations are included as comparison datasets.

These data mainly cover the Russian foreign-exchange market before 2022. They provide a benchmark for examining how futures pricing, liquidity and market participation changed after the Chinese yuan became one of the principal currencies traded in Russia.

The historical datasets may contain the same types of original market variables as the CNY/RUB dataset:

- trading date;
- contract identifier;
- expiration date;
- closing price;
- settlement price;
- weighted-average price;
- daily high and low prices;
- trading volume;
- number of trades;
- turnover;
- open interest.

The USD/RUB and EUR/RUB observations are not mechanically combined with the CNY/RUB observations. They represent separate instruments, quotation conventions, market environments and historical periods.

---

## 9. Funding-Rate Data

Funding-rate data describe the cost of borrowing or lending Russian rubles and Chinese yuan over different maturities.

These observations are required because futures prices are connected to the financing conditions of the two currencies. However, this section describes only the original published interest-rate observations and not any calculated interest-rate differential.

### Russian-ruble funding data

Russian-ruble funding conditions are represented using official or exchange-published money-market indicators, including the relevant MOEX and RUSFAR benchmarks.

RUSFAR is a secured Russian money-market benchmark based on transactions or quotations involving ruble funding secured by eligible collateral.

### Chinese-yuan funding data

Chinese-yuan funding conditions are represented using relevant yuan-denominated money-market benchmarks.

Depending on availability, the dataset may include:

- MOEX yuan funding benchmarks;
- Chinese interbank offered rates;
- SHIBOR observations;
- secured repo-market rates;
- other official Chinese interbank funding indicators.

### Funding-rate variables

| Variable | Description |
|---|---|
| `observation_date` | Date for which the interest-rate observation was reported. |
| `rate_id` | Identifier of the money-market rate or benchmark. |
| `rate_name` | Name of the relevant interest-rate series. |
| `currency` | Currency in which the funding instrument is denominated, normally RUB or CNY. |
| `tenor` | Published maturity of the interest-rate instrument, such as overnight, one week, one month or three months. |
| `rate` | Published interest rate for the relevant date and tenor. |
| `source` | Institution or market platform that published the observation. |

The reported interest rates are retained in the units used by the original source, normally annual percentage rates. Unit conversions, interpolation and maturity matching are analytical procedures and are not part of the raw-data description.

---

## 10. Frequency and Unit of Observation

Most market data are observed at a daily frequency.

The exact unit of observation depends on the dataset:

| Dataset | Unit of observation |
|---|---|
| Spot-market dataset | One currency instrument on one trading date |
| Contract-level futures dataset | One futures contract on one trading date |
| Nearby futures dataset | One selected futures contract on one trading date |
| Contract-specification dataset | One futures contract |
| Funding-rate dataset | One interest-rate instrument or tenor on one observation date |
| Historical comparison dataset | One currency instrument or futures contract on one trading date |

Weekends, public holidays and exchange closure dates normally have no trading observations.

Different sources may follow different holiday calendars. For example, Russian and Chinese money markets may not be open on exactly the same dates.

---

## 11. Price Units and Currency Conventions

CNY/RUB prices represent the value of the Chinese yuan in Russian rubles according to the quotation convention of the relevant Moscow Exchange instrument.

Futures prices follow the quotation rules specified by the Moscow Exchange for each contract.

Monetary trading indicators such as turnover and the value of open interest are generally reported in Russian rubles.

Interest rates are normally reported as annual percentage rates unless the original source specifies another convention.

Contract size and quotation units should be interpreted using the official specification of each futures contract.

---

## 12. Raw and Standardised Variables

Some variable names in the project differ from the original names used by the data provider. For example, an exchange field may be renamed to `futures_settle_price` or `spot_wap_price` to make its meaning clearer and to maintain consistent naming across files.

Renaming a field does not change the underlying value. These standardised variables still represent original source observations.

The following operations do not constitute the calculation of a new economic variable:

- renaming columns;
- converting dates into a consistent date format;
- converting text-formatted numbers into numeric format;
- arranging columns in a consistent order;
- attaching source and instrument identifiers;
- combining observations from different dates into one table.

---

## 13. Variables Excluded from This Raw-Data Description

The following variables are generated during data processing or empirical analysis and are therefore not described as original data:

- selected analytical spot price;
- selected analytical futures price;
- spot or futures returns;
- logarithmic returns;
- futures basis;
- percentage basis;
- annualised basis;
- theoretical futures price;
- cost-of-carry value;
- deviation from theoretical value;
- implied interest rate;
- interest-rate differential;
- days to contract expiration;
- time to maturity expressed in years;
- interpolated funding rates;
- matched-maturity funding rates;
- rolling volatility;
- realised volatility;
- price range indicators;
- bid–ask spread proxies;
- turnover-based liquidity indicators;
- volume-based liquidity indicators;
- open-interest changes;
- rolling averages;
- standardised or normalised variables;
- market-pressure indicators;
- regression variables;
- interaction terms;
- dummy variables;
- outlier flags;
- structural-break indicators;
- hedging-effectiveness measures.

These variables are constructed from the original observations described above and should be documented separately in the methodology or derived-variable section.

---

## 14. Summary

The raw dataset combines daily spot-market prices, futures-contract prices, trading activity, open interest, contract specifications and money-market interest rates.

The principal focus is the CNY/RUB market from the second half of 2022 onward. Historical USD/RUB and EUR/RUB data provide a pre-2022 comparison.

The data structure preserves both individual futures contracts and the original market information reported for each trading date. This makes it possible to analyse pricing across contracts, maturities and market conditions while maintaining a clear distinction between externally obtained observations and variables constructed by the researcher.
