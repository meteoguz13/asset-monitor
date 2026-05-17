import pandas as pd

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
        return 'No Significant Change'


def check_period_alarm(current_price, high, low):
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

def get_thresholds(daily_change):
    thresholds = {}
    for a in daily_change.columns:
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
    return thresholds

def format_period(alarm, high, low, price):
    if 'NEW PEAK' in alarm or 'Near Peak' in alarm:
        emoji = '🔴'
        status = 'Near Peak'
    elif 'NEW BOTTOM' in alarm or 'Near Bottom' in alarm:
        emoji = '🟠'
        status = 'Near Bottom'
    else:
        emoji = '🟢'
        status = 'Mid Range'
    return f"{emoji} {status} / Peak: {high:.2f} / Now: {price:.2f}"





