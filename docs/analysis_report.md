# Analysis Report

This report documents the simulation evidence produced by the local MVP. The
latest concrete values are generated in `reports/` by the runbook commands.

## Evaluation Scope

- Symbol: `TEST`
- Data mode: deterministic sample bars when no CSV is present
- Trading mode: simulation-only
- Risk controls: exposure cap, VaR95, CVaR95, 60-day max drawdown and HITL
- Decision protocol: technical indicators plus three-round bull/bear debate

## Metrics Captured

The backtest report records:

- Initial and final equity
- Total return
- Sharpe-like downside-volatility metric
- Max drawdown
- Trade count
- Last 20 simulated trades

The signal report records:

- Recommendation and confidence
- RSI14, MACD, MA20, MA50, volatility, VaR95 and CVaR95
- Order draft parameters
- Human-approval requirement

The risk report records:

- Schema validation outcome
- Notional exposure
- VaR95, CVaR95 and drawdown checks
- Final risk decision and reasons

## Latest Local Sample

Generated on 2026-05-24 from deterministic `TEST` data:

- Recommendation: SELL
- Confidence: 0.9000
- Risk decision: APPROVE_WITH_HUMAN_CONFIRMATION
- HITL status: PENDING_HUMAN_APPROVAL
- Draft order: SELL 92 LIMIT at 107.3259
- Exposure: 9.8938%
- VaR95: 1.5662%
- CVaR95: 1.6523%
- 60-day max drawdown: 17.4073%

Backtest sample:

- Initial cash: 100000.00
- Final equity: 102427.23
- Total return: 2.4272%
- Sharpe-like metric: 3.7674
- Max drawdown: 0.5531%
- Trade count: 4

## Baseline Comparison Plan

The current code produces the multi-agent strategy result. The next benchmark
step is to add two baselines to `backtest.py`:

- Single-AI style baseline: use the strategy score without adversarial debate.
- Traditional multi-factor baseline: combine RSI, MACD and moving-average
  signals without agent reasoning.

These baselines should be compared on annualized return, Sharpe ratio, maximum
drawdown, trade count and rejection rate from the risk manager.

## Current Limitations

- Live broker execution is intentionally absent.
- External real-time data providers are optional extension points.
- Browser/news automation is represented by config and shared-memory contracts,
  not by a running external crawler in this local MVP.
- HITL approval cards are written locally; message delivery is disabled until
  gateway credentials are configured.
