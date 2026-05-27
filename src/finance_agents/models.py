from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class MarketBar:
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


@dataclass(frozen=True)
class IndicatorSnapshot:
    close: float
    return_1d: float
    return_5d: float
    ma20: float
    ma50: float
    rsi14: float
    macd: float
    macd_signal: float
    macd_hist: float
    volatility20: float
    max_drawdown60: float
    var95: float
    cvar95: float


@dataclass(frozen=True)
class DebateResult:
    bull_score: float
    bear_score: float
    net_score: float
    markdown: str
    rounds: list[dict[str, str]]


@dataclass(frozen=True)
class RiskReview:
    decision: str
    approved: bool
    reasons: list[str]
    metrics: dict[str, float]
    human_approval_required: bool


def dataclass_to_dict(value: Any) -> dict[str, Any]:
    return asdict(value)
