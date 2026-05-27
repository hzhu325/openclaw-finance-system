from __future__ import annotations

from .models import DebateResult, IndicatorSnapshot


def _pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def run_debate(symbol: str, ind: IndicatorSnapshot) -> DebateResult:
    bull_points: list[str] = []
    bear_points: list[str] = []
    bull_score = 0.0
    bear_score = 0.0

    if ind.close > ind.ma20 > ind.ma50:
        bull_points.append("Price is above both MA20 and MA50, showing positive trend alignment.")
        bull_score += 0.35
    else:
        bear_points.append("Trend alignment is weak because price is not cleanly above MA20 and MA50.")
        bear_score += 0.25

    if ind.macd_hist > 0:
        bull_points.append("MACD histogram is positive, implying upward momentum.")
        bull_score += 0.25
    else:
        bear_points.append("MACD histogram is negative, implying fading momentum.")
        bear_score += 0.25

    if 45 <= ind.rsi14 <= 68:
        bull_points.append("RSI is constructive without being extremely overbought.")
        bull_score += 0.20
    elif ind.rsi14 > 72:
        bear_points.append("RSI is stretched, raising pullback risk.")
        bear_score += 0.20
    elif ind.rsi14 < 35:
        bull_points.append("RSI is depressed, creating a possible mean-reversion setup.")
        bull_score += 0.10
        bear_points.append("Low RSI may also reflect persistent selling pressure.")
        bear_score += 0.10

    if ind.return_5d > 0:
        bull_points.append(f"Five-day return is positive at {_pct(ind.return_5d)}.")
        bull_score += 0.10
    else:
        bear_points.append(f"Five-day return is negative at {_pct(ind.return_5d)}.")
        bear_score += 0.10

    if ind.cvar95 > 0.04 or ind.max_drawdown60 > 0.12:
        bear_points.append(
            f"Tail risk is elevated: CVaR95={_pct(ind.cvar95)}, max drawdown60={_pct(ind.max_drawdown60)}."
        )
        bear_score += 0.25

    if not bull_points:
        bull_points.append("Bull case is weak; no strong positive evidence was found.")
    if not bear_points:
        bear_points.append("Bear case is limited; no major technical risk was found.")

    rounds = [
        {
            "round": "thesis",
            "bull": " ".join(bull_points),
            "bear": " ".join(bear_points),
        },
        {
            "round": "cross_examination",
            "bull": "Bull asks whether risk is already reflected in the price and whether momentum is improving.",
            "bear": "Bear asks whether the signal depends too much on recent trend and ignores tail loss.",
        },
        {
            "round": "final_argument",
            "bull": "Proceed only if risk manager approves position sizing and downside controls.",
            "bear": "Prefer HOLD or reduced size unless reward clearly compensates for measured tail risk.",
        },
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
