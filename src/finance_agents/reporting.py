import json
from pathlib import Path
from typing import Any

from .models import RiskReview, dataclass_to_dict


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def render_summary(signal: dict, risk: RiskReview, source: str, market_context: dict | None = None) -> str:
    order = signal["order"]
    lines = [
        "# Run Summary",
        "",
        f"Symbol: {signal['symbol']}",
        f"Data source: {source}",
        f"Recommendation: {signal['recommendation']}",
        f"Confidence: {signal['confidence']}",
        f"Order draft: {order['action']} {order['quantity']} {order['order_type']}",
        f"Risk decision: {risk.decision}",
        f"HITL required: {signal['human_approval_required']}",
        "",
        "## Rationale",
    ]
    lines.extend(f"- {item}" for item in signal["rationale"])
    lines.extend(["", "## Risk Reasons"])
    lines.extend(f"- {item}" for item in risk.reasons)
    if market_context is not None:
        lines.extend(["", "## Market Context"])
        lines.append(f"Events loaded: {market_context['event_count']}")
        lines.append(f"Staleness note: {market_context['staleness_note']}")
    lines.extend(["", "Human approval required before any non-simulated execution."])
    return "\n".join(lines) + "\n"


def write_run_outputs(
    reports_dir: Path,
    signal: dict,
    risk: RiskReview,
    debate_markdown: str,
    data_source: str,
    backtest: dict | None = None,
    approval_card: dict | None = None,
    approval_card_markdown: str | None = None,
    order_draft: dict | None = None,
    market_context: dict | None = None,
) -> None:
    write_json(reports_dir / "latest_signal.json", signal)
    write_json(reports_dir / "latest_risk_review.json", dataclass_to_dict(risk))
    write_text(reports_dir / "latest_debate.md", debate_markdown)
    write_text(reports_dir / "latest_summary.md", render_summary(signal, risk, data_source, market_context))
    if market_context is not None:
        write_json(reports_dir / "latest_market_context.json", market_context)
    if approval_card is not None:
        write_json(reports_dir / "latest_human_approval_card.json", approval_card)
    if approval_card_markdown is not None:
        write_text(reports_dir / "latest_human_approval_card.md", approval_card_markdown)
    if order_draft is not None:
        write_json(reports_dir / "latest_simulated_order_draft.json", order_draft)
    if backtest is not None:
        write_json(reports_dir / "latest_backtest.json", backtest)
