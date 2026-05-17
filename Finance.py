import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.max_colwidth", None)
pd.set_option("display.width", 100000)

# ── Symbols ───────────────────────────────────────────────────────────────────
symbols = {
    'USD/TRY': 'USDTRY=X',
    'EUR/TRY': 'EURTRY=X',
    'GBP/TRY': 'GBPTRY=X',
    'Gold':    'GC=F'
}

# ── Download Historical Data ──────────────────────────────────────────────────
data = yf.download(list(symbols.values()), period='1y', interval='1d')
close = data['Close']
close.columns = ['EUR/TRY', 'GBP/TRY', 'Gold', 'USD/TRY']
print("1-year data shape:", close.shape)

data_5y = yf.download(list(symbols.values()), period='5y', interval='1d')
close_5y = data_5y['Close']
close_5y.columns = ['EUR/TRY', 'GBP/TRY', 'Gold', 'USD/TRY']
print("5-year data shape:", close_5y.shape)

# ── Live Prices ───────────────────────────────────────────────────────────────
live_prices = {}
for name, ticker_code in symbols.items():
    ticker = yf.Ticker(ticker_code)
    live_prices[name] = ticker.info.get('regularMarketPrice', None)

print("\n=== Live Prices ===")
for name, price in live_prices.items():
    print(f"  {name}: {price}")

# ── Basic Statistics ──────────────────────────────────────────────────────────
print("\n=== Basic Statistics ===")
for asset in close.columns:
    print(f"\n{asset}")
    print(f"  Mean : {close[asset].mean():.2f}")
    print(f"  Min  : {close[asset].min():.2f}")
    print(f"  Max  : {close[asset].max():.2f}")
    print(f"  Std  : {close[asset].std():.2f}")

# ── Plots ─────────────────────────────────────────────────────────────────────
close.plot()
plt.title('Asset Prices - Last 1 Year')
plt.ylabel('Price')
plt.xlabel('Date')
plt.show(block=True)

daily_change = close.pct_change(fill_method=None) * 100

daily_change.plot()
plt.title('Daily Change % - Last 1 Year')
plt.ylabel('Change %')
plt.xlabel('Date')
plt.axhline(y=0, color='red', linestyle='--')
plt.show(block=True)

daily_change.tail(90).plot()
plt.title('Daily Change % - Last 90 Days')
plt.ylabel('Change %')
plt.xlabel('Date')
plt.axhline(y=0, color='red', linestyle='--')
plt.show(block=True)

# ── Directional Statistics ────────────────────────────────────────────────────
print("\n=== Positive Moves ===")
print("Mean:"); print(daily_change[daily_change > 0].mean())
print("Std:");  print(daily_change[daily_change > 0].std())

print("\n=== Negative Moves ===")
print("Mean:"); print(daily_change[daily_change < 0].mean())
print("Std:");  print(daily_change[daily_change < 0].std())

# ── Alarm Thresholds (Statistical) ───────────────────────────────────────────
thresholds = {}
for a in close.columns:
    pos_mean = daily_change[a][daily_change[a] > 0].mean()
    pos_std  = daily_change[a][daily_change[a] > 0].std()
    neg_mean = daily_change[a][daily_change[a] < 0].mean()
    neg_std  = daily_change[a][daily_change[a] < 0].std()

    thresholds[a] = {
        'Caution_up':   round(pos_mean + 1 * pos_std, 2),
        'Warning_up':   round(pos_mean + 2 * pos_std, 2),
        'Critical_up':  round(pos_mean + 3 * pos_std, 2),
        'Caution_down':  round(neg_mean - 1 * neg_std, 2),
        'Warning_down':  round(neg_mean - 2 * neg_std, 2),
        'Critical_down': round(neg_mean - 3 * neg_std, 2)
    }

print("\n=== Thresholds ===")
for a in thresholds:
    print(f"\n{a}")
    for level, value in thresholds[a].items():
        print(f"  {level}: {value}")

# ── Functions ─────────────────────────────────────────────────────────────────
def check_daily_alarm(change, thresholds):
    if pd.isna(change):
        return 'No Data'
    elif change >= thresholds['Critical_up']:
        return 'CRITICAL UP'
    elif change >= thresholds['Warning_up']:
        return 'WARNING UP'
    elif change >= thresholds['Caution_up']:
        return 'CAUTION UP'
    elif change <= thresholds['Critical_down']:
        return 'CRITICAL DOWN'
    elif change <= thresholds['Warning_down']:
        return 'WARNING DOWN'
    elif change <= thresholds['Caution_down']:
        return 'CAUTION DOWN'
    else:
        return 'Normal'

def check_period_alarm(current_price, high, low, asset):
    if current_price is None or pd.isna(current_price):
        return 'No Data'
    pct_from_high = ((high - current_price) / high) * 100
    pct_from_low  = ((current_price - low) / low) * 100
    if current_price >= high:
        return 'NEW PEAK'
    elif pct_from_high <= 1:
        return f'Near Peak — {pct_from_high:.2f}% Below Peak'
    elif current_price <= low:
        return 'NEW BOTTOM'
    elif pct_from_low <= 1:
        return f'Near Bottom — {pct_from_low:.2f}% Above Bottom'
    else:
        return f'Mid Range — {pct_from_high:.2f}% Below Peak'

def get_trend(ma_3, ma_7, ma_30, asset):
    # Trend: based on 7-day vs 30-day moving average
    # Momentum: based on 3-day vs 7-day moving average
    # Uptrend: ma_7 > ma_30 * 1.005 (0.5% threshold)
    # Downtrend: ma_7 < ma_30 * 0.995
    # Accelerating: ma_3 > ma_7
    # Slowing: ma_3 < ma_7
    if ma_7[asset] > ma_30[asset] * 1.005:
        trend = 'Uptrend ↑'
    elif ma_7[asset] < ma_30[asset] * 0.995:
        trend = 'Downtrend ↓'
    else:
        trend = 'Neutral →'

    if ma_3[asset] > ma_7[asset]:
        momentum = 'Accelerating ↑'
    elif ma_3[asset] < ma_7[asset]:
        momentum = 'Slowing ↓'
    else:
        momentum = 'Stable'

    return trend, momentum

def get_projection(close, live_prices, days=30):
    print("\n=== 30-Day Price Projections ===")
    for asset in close.columns:
        current_price = live_prices[asset]
        roc = close[asset].pct_change(days, fill_method=None).dropna() * 100
        current_roc = roc.iloc[-1]

        pessimistic = current_price * (1 + (current_roc * 0.5) / 100)
        base        = current_price * (1 + (current_roc * 1.0) / 100)
        optimistic  = current_price * (1 + (current_roc * 1.5) / 100)

        print(f"\n{asset}")
        print(f"  Current     : {current_price}")
        print(f"  Pessimistic : {round(pessimistic, 2)}  ({round(current_roc * 0.5, 2):+.2f}%)")
        print(f"  Base        : {round(base, 2)}  ({round(current_roc, 2):+.2f}%)")
        print(f"  Optimistic  : {round(optimistic, 2)}  ({round(current_roc * 1.5, 2):+.2f}%)")
    print("\n  * Trend projection only, not a forecast.")

# ── Alarm System 1 — Daily Move Alarm ────────────────────────────────────────
yesterday        = close.iloc[-2]
daily_change_pct = {}
for a in close.columns:
    if live_prices[a] is not None and not pd.isna(yesterday[a]):
        daily_change_pct[a] = ((live_prices[a] - yesterday[a]) / yesterday[a]) * 100
    else:
        daily_change_pct[a] = None

print("\n=== Daily Alarm Check ===")
for a in close.columns:
    change = daily_change_pct[a]
    if change is None:
        print(f"{a}: No Data")
    else:
        alarm = check_daily_alarm(change, thresholds[a])
        print(f"{a}: {change:.2f}% → {alarm}")

# ── Alarm System 2 — Period High/Low Alarm ───────────────────────────────────
high_30d = close.tail(30).max()
low_30d  = close.tail(30).min()
high_52w = close.tail(252).max()
low_52w  = close.tail(252).min()
high_5y  = close_5y.max()
low_5y   = close_5y.min()

for period_name, high, low in [
    ('30-Day',  high_30d, low_30d),
    ('52-Week', high_52w, low_52w),
    ('5-Year',  high_5y,  low_5y)
]:
    print(f"\n=== {period_name} Period Alarm ===")
    for a in close.columns:
        alarm = check_period_alarm(live_prices[a], high[a], low[a], a)
        print(f"  {a}: {live_prices[a]} → {alarm}")

# ── Trend Analysis ────────────────────────────────────────────────────────────
ma_3  = close.tail(3).mean()
ma_7  = close.tail(7).mean()
ma_30 = close.tail(30).mean()

print("\n=== Trend Analysis ===")
for a in close.columns:
    trend, momentum = get_trend(ma_3, ma_7, ma_30, a)
    print(f"  {a}: {trend} | {momentum}")

# ── Price Projection ──────────────────────────────────────────────────────────
get_projection(close, live_prices)