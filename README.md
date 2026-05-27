# OpenClaw Multi-Agent Finance System

A simulation-first MVP that explores how an OpenClaw-style multi-agent workflow
can support cautious financial decision-making: market data → technical
indicators → adversarial bull/bear debate → strict JSON trade proposal →
independent risk review → human-in-the-loop approval → audit-friendly reports.

Real-money execution is **out of scope by design**. Every non-HOLD proposal
must pass schema validation, an independent risk review, and an explicit human
approval card before any execution path could be released.

This project was developed as one of three iterations of a multi-agent finance
system built during my data science internship at BONC (东方国信), April – June
2026. The earlier iterations (`fintrade` and `stocklab`) explored single-stock
pipelines and persona-driven analysis. **OpenClaw is the iteration that
focuses on safety, schema discipline, and HITL governance**, which were the
parts I found most under-treated in the earlier versions.

---

## Workflow

```text
   market bars (CSV / deterministic sample)
              │
              ▼
       shared memory + context
              │
              ▼
   RSI · MACD · returns · VaR · CVaR · drawdown
              │
              ▼
   bull ⇄ bear  3-round debate protocol
              │
              ▼
   strict JSON TradeSignal (schema-validated)
              │
              ▼
   independent risk review
   (schema · exposure · VaR · CVaR · drawdown)
              │
              ▼
   human approval card  (execution_released = false)
              │
              ▼
   reports + dashboard + backtest
```

## Quick Start

```powershell
# from the project root
python .\scripts\run_mvp.py --symbol TEST
python .\scripts\run_mvp.py --symbol TEST --mode backtest
python -m unittest discover -s tests
```

Generated reports are written to `reports/`. The HTML dashboard at
`dashboard.html` summarises the most recent run. The same unit tests run in
CI via `.github/workflows/tests.yml`.

## Project Layout

| Path | Purpose |
| --- | --- |
| `agents/` | Per-role `SOUL.md` and `TOOLS.md` defining behavior and tool boundaries for analyst / coordinator / risk / trader |
| `config/agents.json` · `cron.example.json` · `message_gateway.example.json` · `news_sources.example.json` | Agent registration, scheduling and gateway examples |
| `config/trading_policy.json` | Strategy, position and risk thresholds — all tunable parameters live here, not in code |
| `src/finance_agents/policy.py` | Typed dataclasses that load `trading_policy.json`; consumed by strategy and risk layers |
| `src/finance_agents/` | Core code: data loader, indicators, debate, strategy, risk, HITL, backtest, reporting |
| `schemas/` | `trade_signal.schema.json` — strict JSON schema for every trade proposal |
| `memory/` | Shared market events and decision log used by all agents |
| `scripts/run_mvp.py` | End-to-end CLI entrypoint |
| `tests/` | Standard-library workflow tests |
| `.github/workflows/tests.yml` | CI runner for the same workflow tests |
| `docs/` | Architecture, agent design, runbook, analysis and final report |
| `reports/` | Output directory for the most recent run (signal, risk, HITL, backtest); generated artifacts are git-ignored |
| `dashboard.html` | Local browser view of the latest run |

## Safety Boundary

- No live broker integration; market data is loaded from CSV or generated
  deterministically.
- Trade proposals must be valid JSON that passes the schema in `schemas/`.
- Independent risk review may downgrade any non-HOLD proposal to `REJECT` or
  `APPROVE_WITH_HUMAN_CONFIRMATION`.
- HITL cards always set `execution_released = false`. There is no code path
  that turns this `true` in the current MVP.
- Prices, positions and risk limits come from data and config
  (`config/trading_policy.json`), never from free-form LLM text.

## Limitations

This is an MVP. Known limitations include:

- The debate is rule-based with deterministic scoring; an LLM-driven debate
  would change tone but not the schema or risk contract.
- Indicators are computed on closing-price series only; intraday, volume and
  news-event features are out of scope for this iteration.
- Backtest is single-symbol and long-only.
- The policy values in `config/trading_policy.json` are starter parameters,
  not calibrated against a broad set of symbols; they exist to demonstrate
  the contract between policy and code, not strategy performance.

## Acknowledgements and Development Notes

This project was written with the help of AI-assisted coding. Design
decisions — the simulation-first scope, the
HITL-mandatory contract, the schema-first interface between agents, the
externalization of policy thresholds into `config/trading_policy.json`, and
the choice to keep the debate deterministic in this iteration — were mine, as
was the iteration plan that produced `fintrade`, `stocklab` and `OpenClaw` in
sequence. The code itself was produced through iterative prompting, manual
review and integration testing on my side.

No agent prompts, persona libraries or strategy code were forked into this
repository. The four agent roles in `agents/` are written specifically for
the OpenClaw task description; ideas from prior reading or open-source work
were re-implemented to fit this system rather than copied.

If you are reading this as part of an application review, the parts that
best reflect my own design contribution are:

- The workflow contract: `src/finance_agents/strategy.py` →
  `risk.py` → `hitl.py`
- The schema in `schemas/trade_signal.schema.json`
- The policy externalisation in `config/trading_policy.json` /
  `src/finance_agents/policy.py`
- The safety rules in `agents/*/SOUL.md`
- The integration test in `tests/test_workflow.py`

**A note on the Git history**: during the internship the project was developed
locally and originally pushed in a few large commits authored under a
generic placeholder identity. After the internship I grouped the files into
a small number of cleanup commits under my own name to make the repository
easier to read. The commits therefore share a recent date, but the code
they record reflects the work done between April and June 2026. The
original snapshot is preserved under the `pre-cleanup-backup` tag for full
transparency.

---

Author: Hongtao Zhu · hzhu325@wisc.edu · github.com/hzhu325
