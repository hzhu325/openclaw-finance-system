from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from finance_agents.backtest import run_backtest
from finance_agents.context import load_market_context
from finance_agents.data import generate_sample_bars
from finance_agents.debate import run_debate
from finance_agents.hitl import build_approval_card, build_simulated_order_draft
from finance_agents.indicators import snapshot
from finance_agents.risk import review_signal
from finance_agents.strategy import make_trade_signal, validate_trade_signal


class WorkflowTest(unittest.TestCase):
    def test_signal_risk_and_hitl_are_consistent(self) -> None:
        bars = generate_sample_bars("TEST", days=180)
        ind = snapshot(bars)
        debate = run_debate("TEST", ind)
        signal = make_trade_signal("TEST", ind, debate)
        self.assertEqual(validate_trade_signal(signal), [])

        risk = review_signal(signal, ind)
        card = build_approval_card(signal, risk, "deterministic_sample")
        draft = build_simulated_order_draft(signal, risk)

        self.assertFalse(card["execution_released"])
        self.assertFalse(draft["execution_released"])
        if signal["recommendation"] == "HOLD":
            self.assertFalse(signal["human_approval_required"])
            self.assertEqual(card["status"], "NO_ORDER_ACTION")
            self.assertEqual(draft["execution_state"], "NO_ORDER")
        else:
            self.assertTrue(signal["human_approval_required"])
            self.assertIn(card["status"], {"PENDING_HUMAN_APPROVAL", "BLOCKED_BY_RISK"})

    def test_backtest_outputs_key_metrics(self) -> None:
        bars = generate_sample_bars("TEST", days=180)
        result = run_backtest(bars, "TEST")
        self.assertEqual(result["symbol"], "TEST")
        self.assertIn("total_return", result)
        self.assertIn("sharpe_like", result)
        self.assertIn("max_drawdown", result)

    def test_market_context_reads_shared_memory(self) -> None:
        context = load_market_context(ROOT / "memory")
        self.assertIn("event_count", context)
        self.assertIn("staleness_note", context)


if __name__ == "__main__":
    unittest.main()
