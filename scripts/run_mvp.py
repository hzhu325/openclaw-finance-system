from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from finance_agents.backtest import run_backtest
from finance_agents.context import load_market_context
from finance_agents.data import load_or_generate
from finance_agents.debate import run_debate
from finance_agents.hitl import build_approval_card, build_simulated_order_draft, render_approval_card
from finance_agents.indicators import snapshot
from finance_agents.reporting import write_run_outputs
from finance_agents.risk import review_signal
from finance_agents.strategy import make_trade_signal


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the OpenClaw finance MVP.")
    parser.add_argument("--symbol", default="TEST", help="Symbol to analyze.")
    parser.add_argument("--mode", choices=["signal", "backtest"], default="signal")
    parser.add_argument("--equity", type=float, default=100_000.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bars, source = load_or_generate(args.symbol, ROOT / "data")
    market_context = load_market_context(ROOT / "memory")
    ind = snapshot(bars)
    debate = run_debate(args.symbol, ind)
    signal = make_trade_signal(args.symbol, ind, debate, account_equity=args.equity)
    risk = review_signal(signal, ind, account_equity=args.equity)
    approval_card = build_approval_card(signal, risk, source)
    order_draft = build_simulated_order_draft(signal, risk)
    backtest = run_backtest(bars, args.symbol, initial_cash=args.equity) if args.mode == "backtest" else None

    write_run_outputs(
        ROOT / "reports",
        signal=signal,
        risk=risk,
        debate_markdown=debate.markdown,
        data_source=source,
        backtest=backtest,
        approval_card=approval_card,
        approval_card_markdown=render_approval_card(approval_card),
        order_draft=order_draft,
        market_context=market_context,
    )

    print(f"symbol={signal['symbol']}")
    print(f"recommendation={signal['recommendation']}")
    print(f"risk_decision={risk.decision}")
    print(f"hitl_status={approval_card['status']}")
    print(f"reports={ROOT / 'reports'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
