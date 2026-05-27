from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .models import RiskReview


def build_approval_card(signal: dict[str, Any], risk: RiskReview, data_source: str) -> dict[str, Any]:
    approval_required = bool(signal.get("human_approval_required"))
    order = signal["order"]
    if approval_required and not risk.approved:
        status = "BLOCKED_BY_RISK"
    elif approval_required:
        status = "PENDING_HUMAN_APPROVAL"
    else:
        status = "NO_ORDER_ACTION"

    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "symbol": signal["symbol"],
        "recommendation": signal["recommendation"],
        "confidence": signal["confidence"],
        "data_source": data_source,
        "risk_decision": risk.decision,
        "risk_reasons": risk.reasons,
        "risk_metrics": risk.metrics,
        "order": {
            "action": order["action"],
            "quantity": order["quantity"],
            "order_type": order["order_type"],
            "limit_price": order.get("limit_price"),
            "stop_loss": order.get("stop_loss"),
            "take_profit": order.get("take_profit"),
            "time_in_force": order.get("time_in_force"),
        },
        "approval_required": approval_required,
        "approval_state": "NOT_REQUESTED" if not approval_required else "AWAITING_HUMAN",
        "execution_released": False,
        "approval_instruction": (
            "Record an explicit APPROVED or REJECTED decision in memory/decision_log.md "
            "before any broker adapter is allowed to consume this order draft."
        ),
    }


def build_simulated_order_draft(signal: dict[str, Any], risk: RiskReview) -> dict[str, Any]:
    approval_required = bool(signal.get("human_approval_required"))
    if signal["recommendation"] == "HOLD":
        state = "NO_ORDER"
    elif not risk.approved:
        state = "BLOCKED_BY_RISK"
    elif approval_required:
        state = "BLOCKED_PENDING_HUMAN_APPROVAL"
    else:
        state = "SIMULATION_READY"

    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "simulation_only": True,
        "execution_state": state,
        "execution_released": False,
        "symbol": signal["symbol"],
        "order": signal["order"],
        "risk_decision": risk.decision,
        "human_approval_required": approval_required,
    }


def render_approval_card(card: dict[str, Any]) -> str:
    order = card["order"]
    lines = [
        "# Human Approval Card",
        "",
        f"Status: {card['status']}",
        f"Symbol: {card['symbol']}",
        f"Recommendation: {card['recommendation']}",
        f"Confidence: {card['confidence']}",
        f"Risk decision: {card['risk_decision']}",
        f"Order: {order['action']} {order['quantity']} {order['order_type']}",
        f"Limit price: {order['limit_price']}",
        f"Stop loss: {order['stop_loss']}",
        f"Take profit: {order['take_profit']}",
        f"Approval state: {card['approval_state']}",
        f"Execution released: {card['execution_released']}",
        "",
        "## Risk Reasons",
    ]
    lines.extend(f"- {item}" for item in card["risk_reasons"])
    lines.extend(["", card["approval_instruction"]])
    return "\n".join(lines) + "\n"
