# Coordinator Tools

Allowed tools:

- Read shared memory in `memory/`.
- Read reports in `reports/`.
- Run `python scripts/run_mvp.py --symbol <SYMBOL>`.
- Ask analyst, trader and risk agents for explicit review.

Forbidden tools:

- Broker APIs.
- Credential stores for live trading.
- Any command that sends a live order.
