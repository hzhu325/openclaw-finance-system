from .models import IndicatorSnapshot, RiskReview
from .policy import TradingPolicy
from .strategy import validate_trade_signal


def review_signal(
    signal: dict,
    ind: IndicatorSnapshot,
    account_equity: float | None = None,
    policy: TradingPolicy | None = None,
) -> RiskReview:
    policy = policy or TradingPolicy()
    account_equity = policy.account_equity if account_equity is None else account_equity
    risk_policy = policy.risk
    reasons: list[str] = []
    schema_errors = validate_trade_signal(signal)
    reasons.extend(f"Schema: {error}" for error in schema_errors)

    action = signal.get("recommendation", "HOLD")
    order = signal.get("order", {})
    quantity = int(order.get("quantity", 0) or 0)
    notional = quantity * ind.close
    exposure_pct = notional / account_equity if account_equity else 0.0

    max_position_pct = float(signal.get("risk", {}).get("max_position_pct", policy.position.max_position_pct))
    if exposure_pct > max_position_pct + risk_policy.exposure_buffer:
        reasons.append(f"Exposure {exposure_pct:.2%} exceeds limit {max_position_pct:.2%}.")
    if ind.var95 > risk_policy.var95_limit:
        reasons.append(f"VaR95 {ind.var95:.2%} exceeds {risk_policy.var95_limit:.2%} threshold.")
    if ind.cvar95 > risk_policy.cvar95_limit:
        reasons.append(f"CVaR95 {ind.cvar95:.2%} exceeds {risk_policy.cvar95_limit:.2%} threshold.")
    if ind.max_drawdown60 > risk_policy.max_drawdown60_limit:
        reasons.append(
            f"60-day max drawdown {ind.max_drawdown60:.2%} exceeds {risk_policy.max_drawdown60_limit:.2%} threshold."
        )

    if action == "HOLD" and not schema_errors:
        decision = "APPROVE_HOLD"
        approved = True
        reasons.append("HOLD action has no execution risk.")
    elif reasons:
        decision = "REJECT"
        approved = False
    else:
        decision = "APPROVE_WITH_HUMAN_CONFIRMATION"
        approved = True
        reasons.append("Risk checks passed; human confirmation remains mandatory.")

    return RiskReview(
        decision=decision,
        approved=approved,
        reasons=reasons,
        metrics={
            "notional": round(notional, 4),
            "exposure_pct": round(exposure_pct, 6),
            "var95": round(ind.var95, 6),
            "cvar95": round(ind.cvar95, 6),
            "max_drawdown60": round(ind.max_drawdown60, 6),
        },
        human_approval_required=action != "HOLD",
    )
