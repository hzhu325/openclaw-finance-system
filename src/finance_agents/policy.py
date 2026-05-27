import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class StrategyPolicy:
    buy_score: float = 0.25
    sell_score: float = -0.35
    max_buy_rsi: float = 75.0
    confidence_floor: float = 0.1
    confidence_base: float = 0.5
    confidence_scale: float = 0.5
    confidence_cap: float = 0.9


@dataclass(frozen=True)
class PositionPolicy:
    max_position_pct: float = 0.1
    max_loss_pct: float = 0.02
    buy_limit_offset: float = 0.002
    sell_limit_offset: float = 0.002
    take_profit_pct: float = 0.04


@dataclass(frozen=True)
class RiskPolicy:
    exposure_buffer: float = 0.001
    var95_limit: float = 0.035
    cvar95_limit: float = 0.055
    max_drawdown60_limit: float = 0.2


@dataclass(frozen=True)
class DebatePolicy:
    trend_score: float = 0.35
    trend_penalty: float = 0.25
    momentum_score: float = 0.25
    rsi_constructive_score: float = 0.2
    rsi_reversal_score: float = 0.1
    five_day_return_score: float = 0.1
    tail_risk_penalty: float = 0.25
    tail_cvar_watch: float = 0.04
    tail_drawdown_watch: float = 0.12


@dataclass(frozen=True)
class TradingPolicy:
    account_equity: float = 100000.0
    horizon: str = "1-5 trading days"
    strategy: StrategyPolicy = field(default_factory=StrategyPolicy)
    position: PositionPolicy = field(default_factory=PositionPolicy)
    risk: RiskPolicy = field(default_factory=RiskPolicy)
    debate: DebatePolicy = field(default_factory=DebatePolicy)
    notes: list[str] = field(default_factory=list)


def _section(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key, {})
    return value if isinstance(value, dict) else {}


def load_policy(path: Path) -> TradingPolicy:
    if not path.exists():
        return TradingPolicy()

    data = json.loads(path.read_text(encoding="utf-8"))
    notes = data.get("notes", [])
    return TradingPolicy(
        account_equity=float(data.get("account_equity", TradingPolicy.account_equity)),
        horizon=str(data.get("horizon", TradingPolicy.horizon)),
        strategy=StrategyPolicy(**_section(data, "strategy")),
        position=PositionPolicy(**_section(data, "position")),
        risk=RiskPolicy(**_section(data, "risk")),
        debate=DebatePolicy(**_section(data, "debate")),
        notes=notes if isinstance(notes, list) else [],
    )
