from datetime import datetime, timezone
from typing import Any

from .models import DebateResult, IndicatorSnapshot
from .policy import TradingPolicy


def _round_dict(values: dict[str, float], digits: int = 6) -> dict[str, float]:
    return {key: round(value, digits) for key, value in values.items()}


def make_trade_signal(
    symbol: str,
    ind: IndicatorSnapshot,
    debate: DebateResult,
    account_equity: float | None = None,
    policy: TradingPolicy | None = None,
) -> dict[str, Any]:
    policy = policy or TradingPolicy()
    account_equity = policy.account_equity if account_equity is None else account_equity
    strategy = policy.strategy
    position = policy.position

    if debate.net_score >= strategy.buy_score and ind.rsi14 < strategy.max_buy_rsi:
        recommendation = "BUY"
    elif debate.net_score <= strategy.sell_score:
        recommendation = "SELL"
    else:
        recommendation = "HOLD"

    quantity = 0
    order_type = "NONE"
    limit_price = None
    stop_loss = None
    take_profit = None

    if recommendation != "HOLD":
        notional = account_equity * position.max_position_pct
        quantity = max(1, int(notional // ind.close))
        order_type = "LIMIT"
        if recommendation == "BUY":
            limit_price = round(ind.close * (1.0 + position.buy_limit_offset), 4)
            stop_loss = round(ind.close * (1.0 - position.max_loss_pct), 4)
            take_profit = round(ind.close * (1.0 + position.take_profit_pct), 4)
        else:
            limit_price = round(ind.close * (1.0 - position.sell_limit_offset), 4)
            stop_loss = round(ind.close * (1.0 + position.max_loss_pct), 4)
            take_profit = round(ind.close * (1.0 - position.take_profit_pct), 4)

    confidence = min(
        strategy.confidence_cap,
        max(strategy.confidence_floor, strategy.confidence_base + abs(debate.net_score) * strategy.confidence_scale),
    )
    rationale = [
        f"Debate net score is {debate.net_score:.3f}.",
        f"RSI14={ind.rsi14:.2f}, MACD histogram={ind.macd_hist:.6f}.",
        f"VaR95={ind.var95:.4f}, CVaR95={ind.cvar95:.4f}.",
        "All non-HOLD actions require risk review and human approval.",
    ]

    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "symbol": symbol.upper(),
        "horizon": policy.horizon,
        "recommendation": recommendation,
        "confidence": round(confidence, 4),
        "rationale": rationale,
        "indicators": _round_dict(
            {
                "close": ind.close,
                "return_1d": ind.return_1d,
                "return_5d": ind.return_5d,
                "ma20": ind.ma20,
                "ma50": ind.ma50,
                "rsi14": ind.rsi14,
                "macd": ind.macd,
                "macd_signal": ind.macd_signal,
                "macd_hist": ind.macd_hist,
                "volatility20": ind.volatility20,
                "max_drawdown60": ind.max_drawdown60,
                "var95": ind.var95,
                "cvar95": ind.cvar95,
            }
        ),
        "order": {
            "action": recommendation,
            "quantity": quantity,
            "order_type": order_type,
            "limit_price": limit_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "time_in_force": "DAY",
        },
        "risk": {
            "max_position_pct": position.max_position_pct,
            "max_loss_pct": position.max_loss_pct,
        },
        "human_approval_required": recommendation != "HOLD",
    }


def validate_trade_signal(signal: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = [
        "schema_version",
        "generated_at",
        "symbol",
        "horizon",
        "recommendation",
        "confidence",
        "rationale",
        "indicators",
        "order",
        "risk",
        "human_approval_required",
    ]
    for key in required:
        if key not in signal:
            errors.append(f"Missing required field: {key}")
    if signal.get("recommendation") not in {"BUY", "SELL", "HOLD"}:
        errors.append("recommendation must be BUY, SELL or HOLD")
    approval_required = signal.get("human_approval_required")
    if not isinstance(approval_required, bool):
        errors.append("human_approval_required must be a boolean")
    elif signal.get("recommendation") != "HOLD" and approval_required is not True:
        errors.append("human_approval_required must be true for non-HOLD orders")
    order = signal.get("order", {})
    if order.get("action") != signal.get("recommendation"):
        errors.append("order.action must match recommendation")
    if signal.get("recommendation") != "HOLD" and order.get("quantity", 0) <= 0:
        errors.append("non-HOLD order must have quantity > 0")
    return errors
