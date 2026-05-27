# System Architecture

This repository implements a simulation-first OpenClaw-style multi-agent
finance workflow. It is designed to satisfy the internship task requirements
without enabling live trading by default.

## Requirement Mapping

| Task stage | Local implementation |
| --- | --- |
| Environment and agent setup | `config/agents.json` plus one `SOUL.md` and `TOOLS.md` pair for each agent under `agents/` |
| Communication gateway | `config/message_gateway.example.json` defines Slack, Telegram and WeCom approval targets in disabled simulation mode |
| Structured market data | `src/finance_agents/data.py` loads `<SYMBOL>_bars.csv` or generates deterministic bars |
| Unstructured context | `memory/market_events.md` is read by `src/finance_agents/context.py`; `config/news_sources.example.json` documents browser automation handoff |
| Shared memory | `memory/market_events.md` and `memory/decision_log.md` are shared across agents |
| Strategy and schema | `src/finance_agents/strategy.py` emits strict JSON-compatible trade signals; schema lives in `schemas/trade_signal.schema.json`; thresholds are read from `config/trading_policy.json` |
| Adversarial debate | `src/finance_agents/debate.py` runs thesis, cross-examination and final-argument rounds using current indicators and local agent briefs |
| VaR/CVaR risk checks | `src/finance_agents/risk.py` applies exposure, VaR, CVaR and drawdown constraints from the trading policy |
| HITL safety | `src/finance_agents/hitl.py` writes approval cards and keeps execution release disabled |
| Scheduling and test | `config/cron.example.json`, `scripts/run_mvp.py`, and `tests/test_workflow.py` |
| Backtest and report | `src/finance_agents/backtest.py` and generated files under `reports/` |

## Runtime Flow

1. The coordinator starts `scripts/run_mvp.py` for a symbol.
2. Market bars are loaded from CSV when present, otherwise deterministic sample
   data is generated for reproducible local runs.
3. Trading limits and scoring values are loaded from `config/trading_policy.json`.
4. Shared memory is loaded from `memory/market_events.md` and written into the
   run report as market context.
5. The analyst layer computes RSI, MACD, moving averages, volatility, VaR,
   CVaR and drawdown.
6. Bull and bear agents run a three-round debate protocol.
7. The strategy layer converts indicators and debate score into a strict trade
   proposal JSON object.
8. The risk manager validates schema, exposure, VaR, CVaR and drawdown.
9. HITL creates a human approval card and a simulation-only order draft.
10. Reports are written to `reports/`.

## Safety Boundary

The repository does not contain a live broker adapter. All order drafts are
simulation-only, and `execution_released` is always `false`. A future broker
adapter must read the approval card, verify an explicit human decision in
`memory/decision_log.md`, and refuse execution when the risk decision is not
approved.

## Extension Points

- Replace deterministic or CSV data with YFinance, Finnhub, Tushare or AKShare
  adapters behind `load_or_generate`.
- Connect `config/news_sources.example.json` to OpenClaw browser automation and
  write summarized context into `memory/market_events.md`.
- Connect `config/message_gateway.example.json` to a real messaging gateway for
  approval cards.
- Add benchmark strategies to `backtest.py` for single-AI and multi-factor
  comparisons.
