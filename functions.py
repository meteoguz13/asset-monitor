import pandas as pd

def check_daily_alarm(change, thresholds, t):
    if pd.isna(change):
        return 'No Data'
    elif change >= thresholds['Critical_up']:
        return t['critical_up']
    elif change >= thresholds['Warning_up']:
        return t['warning_up']
    elif change >= thresholds['Caution_up']:
        return t['caution_up']
    elif change <= thresholds['Critical_down']:
        return t['critical_down']
    elif change <= thresholds['Warning_down']:
        return t['warning_down']
    elif change <= thresholds['Caution_down']:
        return t['caution_down']
    else:
        return t['no_change']


def check_period_alarm(current_price, high, low, t):
    if current_price is None or pd.isna(current_price):
        return 'No Data'
    pct_from_high = ((high - current_price) / high) * 100
    pct_from_low  = ((current_price - low) / low) * 100
    if current_price >= high:
        return t['new_peak']
    elif pct_from_high <= 1:
        return f"{t['near_peak']} — {pct_from_high:.2f}% Below Peak"
    elif current_price <= low:
        return t['new_bottom']
    elif pct_from_low <= 1:
        return f"{t['near_bottom']} — {pct_from_low:.2f}% Above Bottom"
    else:
        return t['mid_range']


def get_trend(ma_3, ma_7, ma_30, asset, t):
    if ma_7[asset] > ma_30[asset] * 1.005:
        trend = t['uptrend']
    elif ma_7[asset] < ma_30[asset] * 0.995:
        trend = t['downtrend']
    else:
        trend = t['neutral']
    if ma_3[asset] > ma_7[asset]:
        momentum = t['accelerating']
    elif ma_3[asset] < ma_7[asset]:
        momentum = t['slowing']
    else:
        momentum = t['stable']
    return trend, momentum


def get_thresholds(daily_change):
    thresholds = {}
    for a in daily_change.columns:
        pos_mean = daily_change[a][daily_change[a] > 0].mean()
        pos_std  = daily_change[a][daily_change[a] > 0].std()
        neg_mean = daily_change[a][daily_change[a] < 0].mean()
        neg_std  = daily_change[a][daily_change[a] < 0].std()
        thresholds[a] = {
            'Caution_up':    round(pos_mean + 1 * pos_std, 2),
            'Warning_up':    round(pos_mean + 2 * pos_std, 2),
            'Critical_up':   round(pos_mean + 3 * pos_std, 2),
            'Caution_down':  round(neg_mean - 1 * neg_std, 2),
            'Warning_down':  round(neg_mean - 2 * neg_std, 2),
            'Critical_down': round(neg_mean - 3 * neg_std, 2)
        }
    return thresholds


def format_period(alarm, high, low, price, t):
    if t['new_peak'] in alarm or t['near_peak'] in alarm:
        emoji = '🔴'
        status = t['near_peak']
        ref_price = high
        ref_label = "Peak"
    elif t['new_bottom'] in alarm or t['near_bottom'] in alarm:
        emoji = '🟠'
        status = t['near_bottom']
        ref_price = low
        ref_label = "Bottom"
    else:
        return f"🟢 {t['mid_range']} / Now: {price:.2f}"
    return f"{emoji} {status} / {ref_label}: {ref_price:.2f} / Now: {price:.2f}"


    return f"{emoji} {status} / Peak: {high:.2f} / Now: {price:.2f}"

def get_rsi(close_series, period=14):
    delta = close_series.diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / loss
    rsi   = 100 - (100/(1+rs))
    return rsi


def get_impact (events, close):
    results = []
    for _, row in events.iterrows():
        date = row["date"] - pd.offsets.BDay(1)
        base_price = close.asof(date)
        price_t1 = close.asof(row["date"] + pd.offsets.BDay(1))
        price_t3 = close.asof(row["date"] + pd.offsets.BDay(3))
        price_t7 = close.asof(row["date"] + pd.offsets.BDay(7))
        change_t1 = (price_t1 - base_price) / base_price * 100
        change_t3 = (price_t3 - base_price) / base_price * 100
        change_t7 = (price_t7 - base_price) / base_price * 100
        results.append({
            'date': row["date"],
            'type': row["type"],
            'decision': row["decision"],
            'USD/TRY_t1': change_t1['USD/TRY'],
            'USD/TRY_t3': change_t3['USD/TRY'],
            'USD/TRY_t7': change_t7['USD/TRY'],
            'EUR/TRY_t1': change_t1['EUR/TRY'],
            'EUR/TRY_t3': change_t3['EUR/TRY'],
            'EUR/TRY_t7': change_t7['EUR/TRY'],
            'GBP/TRY_t1': change_t1['GBP/TRY'],
            'GBP/TRY_t3': change_t3['GBP/TRY'],
            'GBP/TRY_t7': change_t7['GBP/TRY'],
            'Gold_t1': change_t1['Gold'],
            'Gold_t3': change_t3['Gold'],
            'Gold_t7': change_t7['Gold'],
        })
    return pd.DataFrame(results)

def format_change(val):
    if val > 0:
        return f"+{val:.2f}% ↑"
    elif val < 0:
        return f"{val:.2f}% ↓"
    else:
        return f"{val:.2f}%"



