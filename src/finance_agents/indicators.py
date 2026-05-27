import math

from .models import IndicatorSnapshot, MarketBar


def pct_returns(values: list[float]) -> list[float]:
    return [(values[idx] / values[idx - 1]) - 1.0 for idx in range(1, len(values))]


def sma(values: list[float], window: int) -> float:
    if len(values) < window:
        raise ValueError(f"Need {window} values")
    return sum(values[-window:]) / window


def ema_series(values: list[float], span: int) -> list[float]:
    if not values:
        return []
    alpha = 2.0 / (span + 1.0)
    out = [values[0]]
    for value in values[1:]:
        out.append(alpha * value + (1.0 - alpha) * out[-1])
    return out


def rsi(values: list[float], window: int = 14) -> float:
    if len(values) <= window:
        raise ValueError(f"Need more than {window} closes")
    gains: list[float] = []
    losses: list[float] = []
    for idx in range(1, len(values)):
        change = values[idx] - values[idx - 1]
        gains.append(max(change, 0.0))
        losses.append(max(-change, 0.0))
    avg_gain = sum(gains[-window:]) / window
    avg_loss = sum(losses[-window:]) / window
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def macd(values: list[float]) -> tuple[float, float, float]:
    fast = ema_series(values, 12)
    slow = ema_series(values, 26)
    macd_line = [f - s for f, s in zip(fast, slow)]
    signal = ema_series(macd_line, 9)
    return macd_line[-1], signal[-1], macd_line[-1] - signal[-1]


def annualized_volatility(returns: list[float], window: int = 20) -> float:
    sample = returns[-window:]
    if len(sample) < 2:
        return 0.0
    mean = sum(sample) / len(sample)
    variance = sum((value - mean) ** 2 for value in sample) / (len(sample) - 1)
    return math.sqrt(variance) * math.sqrt(252.0)


def max_drawdown(values: list[float]) -> float:
    peak = values[0]
    worst = 0.0
    for value in values:
        peak = max(peak, value)
        drawdown = (value / peak) - 1.0
        worst = min(worst, drawdown)
    return abs(worst)


def historical_var_cvar(returns: list[float], confidence: float = 0.95) -> tuple[float, float]:
    if not returns:
        return 0.0, 0.0
    ordered = sorted(returns)
    tail_count = max(1, int(math.ceil(len(ordered) * (1.0 - confidence))))
    tail = ordered[:tail_count]
    var_return = ordered[tail_count - 1]
    var_loss = max(0.0, -var_return)
    cvar_loss = max(0.0, -sum(tail) / len(tail))
    return var_loss, cvar_loss


def snapshot(bars: list[MarketBar]) -> IndicatorSnapshot:
    if len(bars) < 60:
        raise ValueError("Need at least 60 bars")
    closes = [bar.close for bar in bars]
    returns = pct_returns(closes)
    macd_line, signal, hist = macd(closes)
    var95, cvar95 = historical_var_cvar(returns[-120:], 0.95)
    return IndicatorSnapshot(
        close=closes[-1],
        return_1d=returns[-1],
        return_5d=(closes[-1] / closes[-6]) - 1.0,
        ma20=sma(closes, 20),
        ma50=sma(closes, 50),
        rsi14=rsi(closes, 14),
        macd=macd_line,
        macd_signal=signal,
        macd_hist=hist,
        volatility20=annualized_volatility(returns, 20),
        max_drawdown60=max_drawdown(closes[-60:]),
        var95=var95,
        cvar95=cvar95,
    )
