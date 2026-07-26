"""Collect and prepare MOEX data for the CNY/RUB futures thesis."""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


BASE_URL = "https://iss.moex.com/iss"
FUTURES_ROOT = "CR"
FUTURES_MONTH_CODES = {3: "H", 6: "M", 9: "U", 12: "Z"}
FUNDING_TENORS = {
    "RUSFAR": ("RUB", 1),
    "RUSFAR1W": ("RUB", 7),
    "RUSFAR2W": ("RUB", 14),
    "RUSFAR1M": ("RUB", 30),
    "RUSFAR3M": ("RUB", 90),
    "RUSFARCNY": ("CNY", 1),
    "RUSFARCN1W": ("CNY", 7),
}
MAX_RATE_STALENESS_DAYS = 14


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="2022-07-01", help="First sample date (YYYY-MM-DD).")
    parser.add_argument("--end", default=date.today().isoformat(), help="Last sample date (YYYY-MM-DD).")
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parents[1] / "data"),
        help="Directory for raw and processed outputs.",
    )
    return parser.parse_args()


def make_session() -> requests.Session:
    retry = Retry(
        total=6,
        connect=6,
        read=6,
        backoff_factor=0.7,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(("GET",)),
    )
    session = requests.Session()
    session.headers.update({"User-Agent": "academic-cnyrub-thesis-data/1.0"})
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def frame_from_block(payload: dict[str, Any], block: str) -> pd.DataFrame:
    body = payload.get(block, {})
    return pd.DataFrame(body.get("data", []), columns=body.get("columns", []))


def concat_frames(frames: list[pd.DataFrame]) -> pd.DataFrame:
    """Concatenate ISS pages without pandas' all-null-column dtype warning."""
    if not frames:
        return pd.DataFrame()
    columns = list(dict.fromkeys(column for frame in frames for column in frame.columns))
    records = [record for frame in frames for record in frame.to_dict(orient="records")]
    return pd.DataFrame.from_records(records, columns=columns)


def fetch_iss_block(
    session: requests.Session,
    path: str,
    block: str,
    params: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """Fetch an ISS table, following its cursor until all rows are collected."""
    request_params = {"iss.meta": "off", "limit": 100}
    if params:
        request_params.update(params)
    rows: list[pd.DataFrame] = []
    start = 0

    while True:
        request_params["start"] = start
        response = session.get(f"{BASE_URL}/{path.lstrip('/')}", params=request_params, timeout=45)
        response.raise_for_status()
        payload = response.json()
        page = frame_from_block(payload, block)
        if not page.empty:
            rows.append(page)

        cursor = frame_from_block(payload, f"{block}.cursor")
        if cursor.empty:
            break
        total = int(cursor.iloc[0]["TOTAL"])
        page_size = int(cursor.iloc[0]["PAGESIZE"])
        if page_size <= 0 or start + page_size >= total:
            break
        start += page_size
        time.sleep(0.03)

    return concat_frames(rows)


def candidate_contracts(start: pd.Timestamp, end: pd.Timestamp) -> list[str]:
    # Include the following year because longer-dated contracts trade before their contract year.
    contracts = []
    for year in range(start.year, end.year + 2):
        for month in FUTURES_MONTH_CODES:
            contracts.append(f"{FUTURES_ROOT}{FUTURES_MONTH_CODES[month]}{year % 10}")
    return contracts


def contract_metadata(session: requests.Session, secid: str) -> dict[str, Any] | None:
    response = session.get(
        f"{BASE_URL}/securities/{secid}.json",
        params={"iss.meta": "off", "iss.only": "description,boards"},
        timeout=45,
    )
    response.raise_for_status()
    payload = response.json()
    description = frame_from_block(payload, "description")
    boards = frame_from_block(payload, "boards")
    if description.empty or boards.empty:
        return None

    values = dict(zip(description["name"], description["value"]))
    board = boards.loc[boards["boardid"].eq("RFUD")]
    if board.empty:
        return None
    board_row = board.iloc[0]
    if values.get("ASSETCODE") != "CNY":
        return None

    return {
        "secid": secid,
        "shortname": values.get("SHORTNAME"),
        "contract_name": values.get("CONTRACTNAME"),
        "asset_code": values.get("ASSETCODE"),
        "first_trade_date": values.get("FRSTTRADE"),
        "last_trade_date": values.get("LSTTRADE"),
        "expiry_date": values.get("LSTDELDATE"),
        "boardid": board_row.get("boardid"),
        "decimals": board_row.get("decimals"),
        "history_from": board_row.get("history_from"),
        "history_till": board_row.get("history_till"),
        "listed_from": board_row.get("listed_from"),
        "listed_till": board_row.get("listed_till"),
    }


def collect_contracts_and_futures(
    session: requests.Session, start: pd.Timestamp, end: pd.Timestamp
) -> tuple[pd.DataFrame, pd.DataFrame]:
    metadata_rows: list[dict[str, Any]] = []
    history_frames: list[pd.DataFrame] = []

    candidates = candidate_contracts(start, end)
    with ThreadPoolExecutor(max_workers=6) as executor:
        tasks = {executor.submit(contract_metadata, make_session(), secid): secid for secid in candidates}
        metadata_by_secid = {}
        for task in as_completed(tasks):
            secid = tasks[task]
            metadata_by_secid[secid] = task.result()

    for secid in candidates:
        metadata = metadata_by_secid[secid]
        if metadata is None:
            continue
        first_trade = pd.to_datetime(metadata["first_trade_date"], errors="coerce")
        last_trade = pd.to_datetime(metadata["last_trade_date"], errors="coerce")
        if pd.isna(first_trade) or pd.isna(last_trade) or last_trade < start or first_trade > end:
            continue

        metadata_rows.append(metadata)

    def fetch_contract(metadata: dict[str, Any]) -> tuple[str, pd.DataFrame]:
        secid = str(metadata["secid"])
        history = fetch_iss_block(
            make_session(),
            f"history/engines/futures/markets/forts/boards/RFUD/securities/{secid}.json",
            "history",
            {"from": start.date().isoformat(), "till": end.date().isoformat()},
        )
        return secid, history

    with ThreadPoolExecutor(max_workers=6) as executor:
        tasks = [executor.submit(fetch_contract, metadata) for metadata in metadata_rows]
        for task in as_completed(tasks):
            secid, history = task.result()
            if not history.empty:
                history_frames.append(history)
            print(f"futures {secid}: {len(history):,} rows", flush=True)

    contracts = pd.DataFrame(metadata_rows)
    futures = concat_frames(history_frames)
    return contracts, futures


def collect_spot(session: requests.Session, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    return fetch_iss_block(
        session,
        "history/engines/currency/markets/selt/boards/CETS/securities/CNYRUB_TOM.json",
        "history",
        {"from": start.date().isoformat(), "till": end.date().isoformat()},
    )


def collect_funding(session: requests.Session, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    def fetch_rate(secid: str) -> tuple[str, pd.DataFrame]:
        frame = fetch_iss_block(
            make_session(),
            f"history/engines/stock/markets/index/boards/MMIX/securities/{secid}.json",
            "history",
            {"from": start.date().isoformat(), "till": end.date().isoformat()},
        )
        return secid, frame

    with ThreadPoolExecutor(max_workers=6) as executor:
        tasks = [executor.submit(fetch_rate, secid) for secid in FUNDING_TENORS]
        for task in as_completed(tasks):
            secid, frame = task.result()
            if not frame.empty:
                frames.append(frame)
            print(f"funding {secid}: {len(frame):,} rows", flush=True)
    return concat_frames(frames)


def lower_columns(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    output.columns = [str(column).lower() for column in output.columns]
    return output


def numeric(frame: pd.DataFrame, columns: list[str]) -> None:
    for column in columns:
        if column in frame:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")


def funding_asof(funding: pd.DataFrame, dates: pd.Series) -> pd.DataFrame:
    """Carry each published rate backward-as-of across nonpublication days."""
    output = pd.DataFrame({"trade_date": pd.Series(dates.unique()).sort_values().reset_index(drop=True)})
    for secid in FUNDING_TENORS:
        observations = funding.loc[funding["secid"].eq(secid), ["tradedate", "close"]].copy()
        observations = observations.dropna().sort_values("tradedate")
        observations = observations.rename(columns={"tradedate": f"{secid}__date", "close": secid})
        output = pd.merge_asof(
            output.sort_values("trade_date"),
            observations,
            left_on="trade_date",
            right_on=f"{secid}__date",
            direction="backward",
            tolerance=pd.Timedelta(days=MAX_RATE_STALENESS_DAYS),
        )
    return output


def closest_rate(row: pd.Series, currency: str) -> pd.Series:
    choices: list[tuple[int, str, float, Any]] = []
    for secid, (rate_currency, tenor_days) in FUNDING_TENORS.items():
        if rate_currency != currency:
            continue
        value = row.get(secid)
        if pd.notna(value):
            choices.append((tenor_days, secid, float(value), row.get(f"{secid}__date")))
    if not choices or pd.isna(row["days_to_maturity"]):
        return pd.Series([pd.NA, math.nan, math.nan, pd.NaT])
    tenor_days, secid, value, observation_date = min(
        choices, key=lambda choice: abs(choice[0] - row["days_to_maturity"])
    )
    return pd.Series([secid, value, abs(tenor_days - row["days_to_maturity"]), observation_date])


def prepare_panel(
    futures_raw: pd.DataFrame,
    spot_raw: pd.DataFrame,
    funding_raw: pd.DataFrame,
    contracts_raw: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    futures = lower_columns(futures_raw)
    spot = lower_columns(spot_raw)
    funding = lower_columns(funding_raw)
    contracts = lower_columns(contracts_raw)

    if futures.empty or spot.empty or contracts.empty:
        raise RuntimeError("Required futures, spot, or contract data are empty.")

    futures["tradedate"] = pd.to_datetime(futures["tradedate"])
    spot["tradedate"] = pd.to_datetime(spot["tradedate"])
    funding["tradedate"] = pd.to_datetime(funding["tradedate"])
    contracts["expiry_date"] = pd.to_datetime(contracts["expiry_date"])
    numeric(
        futures,
        [
            "open",
            "low",
            "high",
            "close",
            "settleprice",
            "waprice",
            "volume",
            "value",
            "openposition",
            "openpositionvalue",
            "numtrades",
        ],
    )
    numeric(spot, ["open", "low", "high", "close", "waprice", "numtrades"])
    numeric(funding, ["close", "value"])

    futures = futures.rename(
        columns={
            "tradedate": "trade_date",
            "open": "futures_open",
            "low": "futures_low",
            "high": "futures_high",
            "close": "futures_close",
            "settleprice": "futures_settle_price",
            "waprice": "futures_wap_price",
            "volume": "volume_contracts",
            "value": "turnover_rub",
            "openposition": "open_interest_contracts",
            "openpositionvalue": "open_interest_value_rub",
            "numtrades": "futures_num_trades",
        }
    )
    futures["futures_price"] = (
        futures["futures_settle_price"].combine_first(futures["futures_wap_price"]).combine_first(futures["futures_close"])
    )

    spot = spot.rename(
        columns={
            "tradedate": "trade_date",
            "open": "spot_open",
            "low": "spot_low",
            "high": "spot_high",
            "close": "spot_close",
            "waprice": "spot_wap_price",
            "numtrades": "spot_num_trades",
        }
    )
    spot["spot_price"] = spot["spot_wap_price"].combine_first(spot["spot_close"])
    spot = spot.sort_values("trade_date").reset_index(drop=True)
    spot["spot_log_return"] = spot["spot_price"].map(math.log).diff()
    spot["spot_volatility_20d_ann"] = spot["spot_log_return"].rolling(20, min_periods=10).std() * math.sqrt(252)

    funding_wide = funding_asof(funding, futures["trade_date"])

    contract_columns = ["secid", "shortname", "expiry_date", "first_trade_date", "last_trade_date"]
    panel = futures.merge(contracts[contract_columns], on="secid", how="left", suffixes=("", "_meta"))
    panel = panel.merge(
        spot[
            [
                "trade_date",
                "spot_open",
                "spot_low",
                "spot_high",
                "spot_close",
                "spot_wap_price",
                "spot_num_trades",
                "spot_price",
                "spot_log_return",
                "spot_volatility_20d_ann",
            ]
        ],
        on="trade_date",
        how="left",
    )
    panel = panel.merge(funding_wide, on="trade_date", how="left")
    panel["days_to_maturity"] = (panel["expiry_date"] - panel["trade_date"]).dt.days
    panel["ttm_years"] = panel["days_to_maturity"] / 365.0

    rub = panel.apply(closest_rate, axis=1, currency="RUB")
    rub.columns = ["rub_rate_tenor", "rub_rate_pct", "rub_tenor_distance_days", "rub_rate_observation_date"]
    cny = panel.apply(closest_rate, axis=1, currency="CNY")
    cny.columns = ["cny_rate_tenor", "cny_rate_pct", "cny_tenor_distance_days", "cny_rate_observation_date"]
    panel = pd.concat([panel, rub, cny], axis=1)

    valid = (
        panel["futures_price"].gt(0)
        & panel["spot_price"].gt(0)
        & panel["rub_rate_pct"].notna()
        & panel["cny_rate_pct"].notna()
        & panel["ttm_years"].ge(0)
    )
    carry = ((panel["rub_rate_pct"] - panel["cny_rate_pct"]) / 100.0) * panel["ttm_years"]
    panel["theoretical_futures_price"] = pd.NA
    panel.loc[valid, "theoretical_futures_price"] = panel.loc[valid, "spot_price"] * carry.loc[valid].map(math.exp)
    panel["theoretical_futures_price"] = pd.to_numeric(panel["theoretical_futures_price"], errors="coerce")
    panel["basis_rub_per_cny"] = panel["futures_price"] - panel["theoretical_futures_price"]
    panel["basis_pct"] = 100.0 * panel["basis_rub_per_cny"] / panel["theoretical_futures_price"]
    panel["log_basis"] = panel.apply(
        lambda row: math.log(row["futures_price"] / row["theoretical_futures_price"])
        if row["futures_price"] > 0 and row["theoretical_futures_price"] > 0
        else math.nan,
        axis=1,
    )
    panel = panel.sort_values(["secid", "trade_date"])
    panel["futures_log_return"] = panel.groupby("secid")["futures_price"].transform(
        lambda series: series.map(math.log).diff()
    )

    raw_rate_columns = list(FUNDING_TENORS) + [f"{secid}__date" for secid in FUNDING_TENORS]
    panel = panel.drop(columns=[column for column in raw_rate_columns if column in panel], errors="ignore")
    panel = panel.sort_values(["trade_date", "days_to_maturity", "secid"]).reset_index(drop=True)

    eligible = panel.loc[panel["days_to_maturity"].ge(0) & panel["futures_price"].notna()].copy()
    nearby = eligible.groupby("trade_date", as_index=False, sort=True).first()
    nearby = nearby.sort_values("trade_date").reset_index(drop=True)
    nearby["contract_changed"] = nearby["secid"].ne(nearby["secid"].shift())
    nearby["futures_log_return"] = nearby["futures_price"].map(math.log).diff()
    nearby.loc[nearby["contract_changed"], "futures_log_return"] = math.nan
    nearby["spot_log_return"] = nearby["spot_price"].map(math.log).diff()
    return panel, nearby


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    output = frame.copy()
    for column in output.columns:
        if pd.api.types.is_datetime64_any_dtype(output[column]):
            output[column] = output[column].dt.strftime("%Y-%m-%d")
    output.to_csv(path, index=False, encoding="utf-8")


def quality_summary(panel: pd.DataFrame, nearby: pd.DataFrame) -> dict[str, Any]:
    basis = panel["basis_pct"].dropna()
    summary = {
        "panel_duplicate_contract_dates": int(panel.duplicated(["trade_date", "secid"]).sum()),
        "nearby_duplicate_dates": int(nearby["trade_date"].duplicated().sum()),
        "nonpositive_futures_prices": int(panel["futures_price"].le(0).sum()),
        "nonpositive_spot_prices": int(panel["spot_price"].le(0).sum()),
        "negative_days_to_maturity": int(panel["days_to_maturity"].lt(0).sum()),
        "nearby_series_starts": int(nearby["contract_changed"].sum()),
        "nearby_roll_transitions": max(int(nearby["contract_changed"].sum()) - 1, 0),
        "nearby_distinct_contracts": int(nearby["secid"].nunique()),
        "basis_pct_quantiles": {
            "p01": float(basis.quantile(0.01)),
            "median": float(basis.quantile(0.50)),
            "p99": float(basis.quantile(0.99)),
        },
    }
    hard_failures = [
        summary["panel_duplicate_contract_dates"],
        summary["nearby_duplicate_dates"],
        summary["nonpositive_futures_prices"],
        summary["nonpositive_spot_prices"],
        summary["negative_days_to_maturity"],
    ]
    if any(hard_failures):
        raise RuntimeError(f"Data-quality checks failed: {summary}")
    return summary


def main() -> int:
    args = parse_args()
    start = pd.Timestamp(args.start)
    end = pd.Timestamp(args.end)
    if end < start:
        raise ValueError("--end must be on or after --start")

    output_dir = Path(args.output_dir).resolve()
    raw_dir = output_dir / "raw"
    processed_dir = output_dir / "processed"
    session = make_session()

    contracts, futures = collect_contracts_and_futures(session, start, end)
    spot = collect_spot(session, start, end)
    print(f"spot CNYRUB_TOM: {len(spot):,} rows", flush=True)
    funding = collect_funding(session, start, end)

    if futures.empty:
        raise RuntimeError("No CNY/RUB futures history was returned by MOEX ISS.")
    if spot.empty:
        raise RuntimeError("No CNYRUB_TOM spot history was returned by MOEX ISS.")
    if funding.empty:
        raise RuntimeError("No RUSFAR funding history was returned by MOEX ISS.")

    panel, nearby = prepare_panel(futures, spot, funding, contracts)
    quality = quality_summary(panel, nearby)
    write_csv(futures, raw_dir / "futures_daily.csv")
    write_csv(spot, raw_dir / "spot_daily.csv")
    write_csv(funding, raw_dir / "funding_daily.csv")
    write_csv(contracts, raw_dir / "contracts.csv")
    write_csv(panel, processed_dir / "contract_daily.csv")
    write_csv(nearby, processed_dir / "nearby_daily.csv")

    manifest = {
        "created_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source": "Moscow Exchange ISS",
        "base_url": BASE_URL,
        "requested_start": start.date().isoformat(),
        "requested_end": end.date().isoformat(),
        "rows": {
            "contracts": len(contracts),
            "futures_daily": len(futures),
            "spot_daily": len(spot),
            "funding_daily": len(funding),
            "contract_daily": len(panel),
            "nearby_daily": len(nearby),
        },
        "coverage": {
            "futures_min": str(pd.to_datetime(futures["TRADEDATE"]).min().date()),
            "futures_max": str(pd.to_datetime(futures["TRADEDATE"]).max().date()),
            "spot_min": str(pd.to_datetime(spot["TRADEDATE"]).min().date()),
            "spot_max": str(pd.to_datetime(spot["TRADEDATE"]).max().date()),
            "funding_min": str(pd.to_datetime(funding["TRADEDATE"]).min().date()),
            "funding_max": str(pd.to_datetime(funding["TRADEDATE"]).max().date()),
        },
        "processed_missing": {
            "spot_price": int(panel["spot_price"].isna().sum()),
            "rub_rate": int(panel["rub_rate_pct"].isna().sum()),
            "cny_rate": int(panel["cny_rate_pct"].isna().sum()),
            "theoretical_futures_price": int(panel["theoretical_futures_price"].isna().sum()),
        },
        "rate_asof_tolerance_calendar_days": MAX_RATE_STALENESS_DAYS,
        "quality": quality,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (requests.RequestException, ValueError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
