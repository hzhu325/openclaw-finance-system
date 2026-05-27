# OpenClaw Multi-Agent Finance System

This project is a simulation-first MVP for the OpenClaw multi-agent finance
internship task.

It implements a small but complete workflow:

1. Load market bars from CSV or generate deterministic sample bars.
2. Load shared market context from `memory/`.
3. Calculate RSI, MACD, returns, VaR and CVaR.
4. Run a bull-vs-bear debate protocol.
5. Produce a strict JSON trade proposal.
6. Run an independent risk review.
7. Produce a human approval card and simulation-only order draft.
8. Write audit-friendly reports.

No real broker is connected. Every proposed order is a draft and requires
human approval before any future physical execution path.

## Quick Start

```powershell
cd "E:\project\基于OpenClaw的多智能体金融交易系统\openclaw-finance-system"
python .\scripts\run_mvp.py --symbol TEST
python .\scripts\run_mvp.py --symbol TEST --mode backtest
python -m unittest discover -s tests
```

Generated reports are written to `reports/`.

## Project Layout

- `agents/` - OpenClaw agent personalities and tool contracts.
- `src/finance_agents/` - local simulation, strategy, debate, HITL and risk code.
- `schemas/` - strict JSON schemas for model/tool outputs.
- `memory/` - shared project memory and decision log.
- `docs/` - architecture, agent design, runbook and analysis report.
- `config/` - OpenClaw-facing agent, gateway, news and schedule examples.
- `tests/` - standard-library workflow tests.

## Safety Rules

- Real-money execution is out of scope for this MVP.
- Trade proposals must be JSON and pass risk review.
- Human approval is mandatory before any non-HOLD physical execution.
- Prices, positions and limits must come from data or config, not free-form LLM
  text.
