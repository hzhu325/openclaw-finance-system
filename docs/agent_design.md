# Agent Design

The system separates decision work into four agents so that analysis,
execution planning and risk veto power do not collapse into one model.

## Coordinator / CIO

Workspace: `agents/coordinator`

Responsibilities:

- Decompose a run into analyst, trader and risk-manager tasks.
- Aggregate debate output into an auditable recommendation.
- Prefer HOLD when evidence is incomplete.
- Require structured JSON and risk-manager review before any order draft.

## Research / Analyst

Workspace: `agents/analyst`

Responsibilities:

- Load market bars and shared market context.
- Compute local technical and risk indicators before reasoning.
- Produce both bull and bear arguments for every symbol.
- Record missing or stale data rather than inventing facts.

## Trader / Ops

Workspace: `agents/trader`

Responsibilities:

- Convert approved signals into simulation-only order drafts.
- Preserve action, quantity, order type, limit price, stop loss, take profit
  and time-in-force.
- Never change HOLD into BUY or SELL.
- Never bypass risk review or HITL.

## Risk Manager

Workspace: `agents/risk`

Responsibilities:

- Validate trade-signal structure.
- Check exposure, VaR, CVaR and max drawdown limits.
- Veto proposals that exceed capital-protection rules.
- Require human approval for every non-HOLD action.

## Debate Protocol

The debate engine uses three rounds:

1. Thesis: bull and bear cases are built from trend, momentum, RSI and tail
   risk evidence.
2. Cross-examination: each side challenges the other side's weakest assumption.
3. Final argument: both sides state the conditions under which a trade should
   proceed or be blocked.

The coordinator receives both the debate text and a numeric net score. The
strategy layer can act only after this protocol is complete.
