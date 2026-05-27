from pathlib import Path

from .models import DebateResult, IndicatorSnapshot
from .policy import TradingPolicy


def pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def load_agent_briefs(agents_dir: Path) -> dict[str, str]:
    briefs: dict[str, str] = {}
    for role in ("analyst", "risk"):
        soul = agents_dir / role / "SOUL.md"
        if not soul.exists():
            continue
        lines = [
            line.strip("- ").strip()
            for line in soul.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        ]
        briefs[role] = " ".join(lines[:3])
    return briefs


def add_case(points: list[str], text: str, score: float) -> float:
    points.append(text)
    return score


def strongest(points: list[str]) -> str:
    if not points:
        return "the available evidence"
    return max(points, key=len)


def run_debate(
    symbol: str,
    ind: IndicatorSnapshot,
    policy: TradingPolicy | None = None,
    agent_briefs: dict[str, str] | None = None,
) -> DebateResult:
    policy = policy or TradingPolicy()
    debate = policy.debate
    agent_briefs = agent_briefs or {}
    bull_points: list[str] = []
    bear_points: list[str] = []
    bull_score = 0.0
    bear_score = 0.0

    if ind.close > ind.ma20 > ind.ma50:
        bull_score += add_case(
            bull_points,
            f"Price {ind.close:.2f} is above MA20 {ind.ma20:.2f} and MA50 {ind.ma50:.2f}.",
            debate.trend_score,
        )
    else:
        bear_score += add_case(
            bear_points,
            f"Trend is not aligned: close={ind.close:.2f}, MA20={ind.ma20:.2f}, MA50={ind.ma50:.2f}.",
            debate.trend_penalty,
        )

    if ind.macd_hist > 0:
        bull_score += add_case(
            bull_points,
            f"MACD histogram is positive at {ind.macd_hist:.6f}, so momentum is still supportive.",
            debate.momentum_score,
        )
    else:
        bear_score += add_case(
            bear_points,
            f"MACD histogram is negative at {ind.macd_hist:.6f}, which weakens the momentum case.",
            debate.momentum_score,
        )

    if 45 <= ind.rsi14 <= 68:
        bull_score += add_case(
            bull_points,
            f"RSI14={ind.rsi14:.2f} is constructive without being extremely overbought.",
            debate.rsi_constructive_score,
        )
    elif ind.rsi14 > 72:
        bear_score += add_case(
            bear_points,
            f"RSI14={ind.rsi14:.2f} is stretched, so pullback risk is higher.",
            debate.rsi_constructive_score,
        )
    elif ind.rsi14 < 35:
        bull_score += add_case(
            bull_points,
            f"RSI14={ind.rsi14:.2f} is depressed enough to allow a mean-reversion argument.",
            debate.rsi_reversal_score,
        )
        bear_score += add_case(
            bear_points,
            "The same low RSI can also mean selling pressure has not cleared yet.",
            debate.rsi_reversal_score,
        )

    if ind.return_5d > 0:
        bull_score += add_case(bull_points, f"Five-day return is positive at {pct(ind.return_5d)}.", debate.five_day_return_score)
    else:
        bear_score += add_case(bear_points, f"Five-day return is negative at {pct(ind.return_5d)}.", debate.five_day_return_score)

    if ind.cvar95 > debate.tail_cvar_watch or ind.max_drawdown60 > debate.tail_drawdown_watch:
        bear_score += add_case(
            bear_points,
            f"Tail risk needs attention: CVaR95={pct(ind.cvar95)}, max drawdown60={pct(ind.max_drawdown60)}.",
            debate.tail_risk_penalty,
        )

    if not bull_points:
        bull_points.append("Bull case is thin; no strong positive evidence was found.")
    if not bear_points:
        bear_points.append("Bear case is limited; no major measured risk dominated the snapshot.")

    cross_bull = (
        f"Bull challenges whether the bear case overweights {strongest(bear_points).lower()} "
        f"while ignoring any rebound setup in the latest indicators."
    )
    cross_bear = (
        f"Bear challenges whether the bull case leans too heavily on {strongest(bull_points).lower()} "
        "without enough confirmation from risk-adjusted reward."
    )
    final_bull = (
        "Bull would proceed only after the risk role confirms position size, stop loss and approval state; "
        f"analyst brief: {agent_briefs.get('analyst', 'no analyst profile loaded')}"
    )
    final_bear = (
        "Bear prefers HOLD or a smaller draft when tail loss or trend weakness remains unresolved; "
        f"risk brief: {agent_briefs.get('risk', 'no risk profile loaded')}"
    )

    rounds = [
        {"round": "thesis", "bull": " ".join(bull_points), "bear": " ".join(bear_points)},
        {"round": "cross_examination", "bull": cross_bull, "bear": cross_bear},
        {"round": "final_argument", "bull": final_bull, "bear": final_bear},
    ]
    net = bull_score - bear_score
    markdown = "\n".join(
        [
            f"# Debate: {symbol.upper()}",
            "",
            "## Round 1 - Thesis",
            f"**Bull:** {rounds[0]['bull']}",
            f"**Bear:** {rounds[0]['bear']}",
            "",
            "## Round 2 - Cross Examination",
            f"**Bull:** {rounds[1]['bull']}",
            f"**Bear:** {rounds[1]['bear']}",
            "",
            "## Round 3 - Final Argument",
            f"**Bull:** {rounds[2]['bull']}",
            f"**Bear:** {rounds[2]['bear']}",
            "",
            f"Net score: {net:.3f}",
        ]
    )
    return DebateResult(
        bull_score=round(bull_score, 4),
        bear_score=round(bear_score, 4),
        net_score=round(net, 4),
        markdown=markdown,
        rounds=rounds,
    )
