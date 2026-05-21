import yfinance as yf
import pandas as pd
import os
from datetime import datetime

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.max_colwidth", None)
pd.set_option("display.width", 100000)

# ── Symbols ───────────────────────────────────────────────────────────────────
symbols = {
    'USD/TRY': 'USDTRY=X',
    'EUR/TRY': 'EURTRY=X',
    'GBP/TRY': 'GBPTRY=X',
    'Gold':    'GC=F',
    'EUR/USD': 'EURUSD=X'
}

# ── Fiyat Verisi ──────────────────────────────────────────────────────────────
data = yf.download(list(symbols.values()), period='2y', interval='1d')
close = data['Close']
close.columns = ['EUR/TRY', 'EUR/USD', 'GBP/TRY', 'Gold', 'USD/TRY']
close = close.reset_index()

assets = ['EUR/TRY', 'EUR/USD', 'GBP/TRY', 'Gold', 'USD/TRY']

# ── Volatilite ────────────────────────────────────────────────────────────────
for a in assets:
    close[a + '_std7']  = close[a].rolling(7).std()
    close[a + '_std30'] = close[a].rolling(30).std()

# ── Z-Score ───────────────────────────────────────────────────────────────────
for a in assets:
    daily_change = close[a].pct_change(fill_method=None) * 100
    mean = daily_change.mean()
    std  = daily_change.std()
    close[a + '_zscore'] = (daily_change - mean) / std

# ── Rolling Return ────────────────────────────────────────────────────────────
for a in assets:
    close[a + '_return30']  = close[a].pct_change(30,  fill_method=None) * 100
    close[a + '_return90']  = close[a].pct_change(90,  fill_method=None) * 100
    close[a + '_return180'] = close[a].pct_change(180, fill_method=None) * 100

# ── Drawdown ──────────────────────────────────────────────────────────────────
for a in assets:
    rolling_max = close[a].cummax()
    close[a + '_drawdown'] = (close[a] - rolling_max) / rolling_max * 100

# ── RSI ───────────────────────────────────────────────────────────────────────
for a in assets:
    delta = close[a].diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss
    close[a + '_rsi'] = 100 - (100 / (1 + rs))
print(close[[a + '_rsi' for a in assets]].tail(5))

# ── Bollinger Bands ────────────────────────────────────────────────────────────────

for a in assets:
    ma20  = close[a].rolling(20).mean()
    std20 = close[a].rolling(20).std()
    close[a + "_bb_upper"] = ma20 + (2 * std20)
    close[a + "_bb_mid"]   = ma20
    close[a + "_bb_lower"] = ma20 - (2 * std20)
print(close[[a + s for a in assets for s in ['_bb_upper', '_bb_mid', '_bb_lower']]].tail(5))

# ──────────────────────────────────────────────────────────────

close["usd_base"] = close["USD/TRY"].iloc[0]
close["real_return_usd"] = (close["USD/TRY"] / close["USD/TRY"].iloc[0] - 1) * 100
print(close[['Date', 'USD/TRY', 'real_return_usd']].tail(5))

# ── CSV Kaydet ────────────────────────────────────────────────────────────────
os.makedirs('powerbi-dashboard/data', exist_ok=True)
close.to_csv('powerbi-dashboard/data/prices.csv', index=False, decimal=',')
print(f"prices.csv kaydedildi → {close.shape[1]} sütun, {len(close)} satır")

# ── Korelasyon ────────────────────────────────────────────────────────────────
corr = close[assets].corr()
corr.to_csv('powerbi-dashboard/data/correlation.csv', decimal=',')
print("correlation.csv kaydedildi")


from functions import get_rsi
print(get_rsi(close['USD/TRY']).tail(5))