# Runbook

## Setup

Use Python 3.10 or newer. The MVP uses only the Python standard library.

```powershell
cd "E:\project\基于OpenClaw的多智能体金融交易系统\openclaw-finance-system"
python -m unittest discover -s tests
```

## Run A Signal

```powershell
python .\scripts\run_mvp.py --symbol TEST
```

By default the command reads `config/trading_policy.json`. Pass another policy
file with `--policy <PATH>` when testing different limits or scoring values.

Generated files:

- `reports/latest_signal.json`
- `reports/latest_risk_review.json`
- `reports/latest_human_approval_card.json`
- `reports/latest_human_approval_card.md`
- `reports/latest_simulated_order_draft.json`
- `reports/latest_market_context.json`
- `reports/latest_debate.md`
- `reports/latest_summary.md`

## Run A Backtest

```powershell
python .\scripts\run_mvp.py --symbol TEST --mode backtest
```

This also writes `reports/latest_backtest.json`.

The generated `reports/latest_*` files are local artifacts. They are useful for
the dashboard and submission screenshots, but they are not tracked in Git.

## Provide Real CSV Data

Create a file named `data/<SYMBOL>_bars.csv` with this header:

```csv
date,open,high,low,close,volume
```

The loader requires at least 60 rows for indicators and at least 80 rows for
backtests.

## Shared Memory

Put manually curated market events in `memory/market_events.md` as markdown
bullet points. Browser automation can later update that file using the contract
documented in `config/news_sources.example.json`.

Record human decisions in `memory/decision_log.md` before any future broker
adapter is allowed to consume an order draft.

## HITL Approval

For BUY or SELL signals, review:

- `reports/latest_human_approval_card.md`
- `reports/latest_risk_review.json`
- `reports/latest_simulated_order_draft.json`

The local MVP never releases execution. The order draft remains blocked until a
human writes an explicit APPROVED decision and a future broker adapter verifies
that decision.

## Scheduling

`config/cron.example.json` contains pre-market and close-review schedules. In an
OpenClaw deployment, map those commands to the scheduler or WebUI job runner.

## Message Gateway

`config/message_gateway.example.json` shows Slack, Telegram and WeCom targets.
All entries are disabled by default and use environment variables for secrets.
