import csv
import math
from datetime import date, timedelta
from pathlib import Path

from .models import MarketBar


def generate_sample_bars(symbol: str, days: int = 180) -> list[MarketBar]:
    """Generate deterministic bars so the MVP runs without a data vendor."""
    seed = sum(ord(ch) for ch in symbol.upper()) or 1
    start = date.today() - timedelta(days=days * 2)
    bars: list[MarketBar] = []
    price = 80.0 + seed % 40
    day = start

    while len(bars) < days:
        if day.weekday() >= 5:
            day += timedelta(days=1)
            continue

        idx = len(bars)
        drift = 0.0008 + ((seed % 9) - 4) * 0.00008
        cycle = math.sin(idx / 7.0 + seed) * 0.012
        shock = math.sin(idx / 17.0 + seed / 3.0) * 0.006
        daily_ret = drift + cycle + shock
        open_price = price
        close = max(1.0, open_price * (1.0 + daily_ret))
        high = max(open_price, close) * (1.0 + 0.004 + abs(cycle) / 6.0)
        low = min(open_price, close) * (1.0 - 0.004 - abs(shock) / 6.0)
        volume = int(800_000 + (seed % 100) * 4_000 + abs(math.sin(idx / 5.0)) * 220_000)
        bars.append(
            MarketBar(
                date=day.isoformat(),
                open=round(open_price, 4),
                high=round(high, 4),
                low=round(low, 4),
                close=round(close, 4),
                volume=volume,
            )
        )
        price = close
        day += timedelta(days=1)

    return bars


def load_bars_csv(path: Path) -> list[MarketBar]:
    bars: list[MarketBar] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"date", "open", "high", "low", "close", "volume"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV missing columns: {', '.join(sorted(missing))}")
        for row in reader:
            bars.append(
                MarketBar(
                    date=row["date"],
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=int(float(row["volume"])),
                )
            )
    if len(bars) < 60:
        raise ValueError("Need at least 60 bars for the MVP indicators")
    return bars


def load_or_generate(symbol: str, data_dir: Path) -> tuple[list[MarketBar], str]:
    csv_path = data_dir / f"{symbol.upper()}_bars.csv"
    if csv_path.exists():
        return load_bars_csv(csv_path), str(csv_path)
    return generate_sample_bars(symbol), "deterministic_sample"
