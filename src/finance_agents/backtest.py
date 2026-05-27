from __future__ import annotations

from .debate import run_debate
from .indicators import max_drawdown, pct_returns, snapshot
from .models import MarketBar
from .strategy import make_trade_signal


def run_backtest(bars: list[MarketBar], symbol: str, initial_cash: float = 100_000.0) -> dict:
    if len(bars) < 80:
        raise ValueError("Need at least 80 bars for backtest")

    cash = initial_cash
    position = 0
    equity_curve: list[float] = []
    trades: list[dict] = []

    for idx in range(60, len(bars) - 1):
        history = bars[: idx + 1]
        ind = snapshot(history)
        debate = run_debate(symbol, ind)
        signal = make_trade_signal(symbol, ind, debate, account_equity=max(cash, 1.0))
        next_open = bars[idx + 1].open
        action = signal["recommendation"]
        quantity = int(signal["order"]["quantity"])

        if action == "BUY" and position == 0 and quantity > 0:
            cost = quantity * next_open
            if cost <= cash:
                cash -= cost
                position += quantity
                trades.append({"date": bars[idx + 1].date, "action": "BUY", "quantity": quantity, "price": next_open})
        elif action == "SELL" and position > 0:
            cash += position * next_open
            trades.append({"date": bars[idx + 1].date, "action": "SELL", "quantity": position, "price": next_open})
            position = 0

        equity_curve.append(cash + position * bars[idx + 1].close)

    final_equity = equity_curve[-1] if equity_curve else initial_cash
    returns = pct_returns(equity_curve) if len(equity_curve) > 1 else []
    avg_return = sum(returns) / len(returns) if returns else 0.0
    downside = [value for value in returns if value < 0]
    downside_vol = (sum(value * value for value in downside) / len(downside)) ** 0.5 if downside else 0.0
    sharpe_like = (avg_return / downside_vol) * (252**0.5) if downside_vol else 0.0

    return {
        "symbol": symbol.upper(),
        "initial_cash": round(initial_cash, 2),
        "final_equity": round(final_equity, 2),
        "total_return": round((final_equity / initial_cash) - 1.0, 6),
        "sharpe_like": round(sharpe_like, 4),
        "max_drawdown": round(max_drawdown(equity_curve), 6) if equity_curve else 0.0,
        "trade_count": len(trades),
        "trades": trades[-20:],
    }
