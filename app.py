import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
from functions import check_daily_alarm, check_period_alarm, get_trend, get_thresholds, format_period
import plotly.graph_objects as go

st.set_page_config(
    page_title="Asset Monitor",
    page_icon="📈",
    layout="wide"
)

# ── Language ──────────────────────────────────────────────────────────────────
lang = st.selectbox("🌐 Language", ["English", "Türkçe"], label_visibility="collapsed")

labels = {
    "English": { ... },  # az önce yazdığım sözlük
    "Türkçe": { ... }
}

t = labels[lang]

st.title(f"📈 {t['title']}")
st.caption(t['caption'])

# ── Symbols ───────────────────────────────────────────────────────────────────
symbols = {
    'USD/TRY': 'USDTRY=X',
    'EUR/TRY': 'EURTRY=X',
    'GBP/TRY': 'GBPTRY=X',
    'Gold':    'GC=F'
}

display_names = {
    'USD/TRY': '1 $ / {:.2f} ₺',
    'EUR/TRY': '1 € / {:.2f} ₺',
    'GBP/TRY': '1 £ / {:.2f} ₺',
    'Gold': '1 ons / {:.2f} $'
}

# ── Data Functions ────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def get_live_prices(symbols):
    prices = {}
    for name, ticker_code in symbols.items():
        try:
            ticker = yf.Ticker(ticker_code)
            price = ticker.fast_info.last_price
            if price is None or pd.isna(price):
                price = ticker.history(period='1d')['Close'].iloc[-1]
            prices[name] = price
        except:
            prices[name] = None
    return prices

@st.cache_data(ttl=3600)
def get_historical_data(symbols):
    data = yf.download(list(symbols.values()), period='1y', interval='1d')
    close = data['Close']
    close.columns = ['EUR/TRY', 'GBP/TRY', 'Gold', 'USD/TRY']
    data_5y = yf.download(list(symbols.values()), period='5y', interval='1d')
    close_5y = data_5y['Close']
    close_5y.columns = ['EUR/TRY', 'GBP/TRY', 'Gold', 'USD/TRY']
    return close, close_5y

# ── Load Data ─────────────────────────────────────────────────────────────────
live_prices = get_live_prices(symbols)
close, close_5y = get_historical_data(symbols)

daily_change = close.pct_change(fill_method=None) * 100
yesterday    = close.iloc[-2]
thresholds   = get_thresholds(daily_change)

daily_change_pct = {}
for a in live_prices.keys():
    if live_prices[a] is not None and not pd.isna(yesterday[a]):
        daily_change_pct[a] = ((live_prices[a] - yesterday[a]) / yesterday[a]) * 100
    else:
        daily_change_pct[a] = None

# Period data
high_30d = close.tail(30).max()
low_30d  = close.tail(30).min()
high_52w = close.tail(252).max()
low_52w  = close.tail(252).min()
high_5y  = close_5y.max()
low_5y   = close_5y.min()

# Trend data
ma_3  = close.tail(3).mean()
ma_7  = close.tail(7).mean()
ma_30 = close.tail(30).mean()

# ── Filter ────────────────────────────────────────────────────────────────────
st.caption(f"{t['last_updated']}: {datetime.now().strftime('%H:%M:%S')}")

selected = st.multiselect(
    t['select_assets'],
    options=list(live_prices.keys()),
    default=list(live_prices.keys())
)

if not selected:
    st.warning(t['no_asset_warning'])

# ── Asset Cards ───────────────────────────────────────────────────────────────
cols = st.columns(len(selected))
for i, a in enumerate(selected):
    with cols[i]:
        price  = live_prices[a]
        change = daily_change_pct[a]

        # Price & daily change
        if price and not pd.isna(yesterday[a]):
            st.metric(
                label=a,
                value=display_names[a].format(price),
                delta=f"{change:.2f}%" if change else "N/A"
            )
        else:
            st.metric(label=a, value="N/A")

        # Chart
        with st.expander(t['chart']):
            period = st.selectbox(
                t['period'],
                t['period_options'],
                key=f"period_{a}"
            )
            period_map = dict(zip(t['period_options'], [7, 30, 90, 180, 252]))
            days = period_map[period]
            chart_data = close[a].tail(days)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data.values, mode='lines', name=a))
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=250)
            st.plotly_chart(fig, use_container_width=True)

        # Daily alarm
        if change is not None:
            alarm = check_daily_alarm(change, thresholds[a], t)
            if 'CRITICAL' in alarm:
                st.error(f"🚨 {alarm}")
            elif 'WARNING' in alarm:
                st.warning(f"⚠️ {alarm}")
            elif 'CAUTION' in alarm:
                st.warning(f"⚠️ {alarm}")
            else:
                st.success(f"✅ {alarm}")

        st.divider()

        # Trend
        trend, momentum = get_trend(ma_3, ma_7, ma_30, a, t)
        st.markdown(f"**{t['trend_label']}:** {trend} / {momentum}")

        st.divider()

        # Period alarms
        p30 = format_period(check_period_alarm(price, high_30d[a], low_30d[a], t), high_30d[a], low_30d[a], price, t)
        p52 = format_period(check_period_alarm(price, high_52w[a], low_52w[a], t), high_52w[a], low_52w[a], price, t)
        p5y = format_period(check_period_alarm(price, high_5y[a], low_5y[a], t), high_5y[a], low_5y[a], price, t)

        st.markdown(f"**{t['period_label']}:**")
        st.dataframe(
            pd.DataFrame(
                [[t['30d'], p30], [t['52w'], p52], [t['5y'], p5y]],
                columns=[t['period_col'], t['status_col']]
            ),
            hide_index=True,
            use_container_width=True
        )

        st.divider()

        # Projection
        roc         = close[a].pct_change(30, fill_method=None).dropna() * 100
        current_roc = roc.tail(7).mean()
        scenario_lo = round(price * (1 + (current_roc * 0.5) / 100), 2)
        base        = round(price * (1 + (current_roc * 1.0) / 100), 2)
        scenario_hi = round(price * (1 + (current_roc * 1.5) / 100), 2)
        best_case   = max(scenario_lo, scenario_hi)
        worst_case  = min(scenario_lo, scenario_hi)
        st.markdown(f"**{t['projection_label']}:**")
        st.dataframe(
            pd.DataFrame({
                t['scenario_col']: [t['best_case'], t['base'], t['worst_case']],
                t['price_col']: [best_case, base, worst_case]
            }),
            hide_index=True,
            use_container_width=True
        )

# ── Info ──────────────────────────────────────────────────────────────────────
st.divider()
with st.expander(t['info_title']):
    if lang == "English":
        st.write("""
        **What is this app?**
        This app tracks live prices for USD/TRY, EUR/TRY, GBP/TRY and Gold. 
        It automatically refreshes every 60 seconds.

        ---

        **💰 Live Prices**
        Shows the current market price and the daily change (%) compared to yesterday's closing price.
        🔴 Red = price dropped today | 🟢 Green = price rose today

        ---

        **🚨 Daily Alarm**
        Alerts you when today's price movement is unusually large.
        Thresholds are calculated from 1 year of historical data using statistics:
        - ✅ No Significant Change → Normal movement
        - ⚠️ Caution → Slightly above average movement
        - ⚠️ Warning → Notably above average movement  
        - 🚨 Critical → Extreme movement, very rare

        ---

        **📊 Period Alarms**
        Shows where the current price stands compared to recent highs and lows:
        - 30-Day: compared to the last 30 days
        - 52-Week: compared to the last 52 weeks
        - 5-Year: compared to the last 5 years

        ---

        **📈 Trend Analysis**
        - Uptrend / Downtrend / Neutral based on 7-day vs 30-day average
        - Accelerating / Slowing based on 3-day vs 7-day average

        ---

        **🔮 30-Day Projection**
        Not a forecast. Shows where the price might go if the current trend continues.
        Trend is calculated as a 7-day average of the 30-day rate of change for stability:
        - 🟢 Best Case: most favorable price direction
        - 🟡 Base: current trend continues at the same pace
        - 🔴 Worst Case: least favorable price direction
        """)
    else:
        st.write("""
        **Bu uygulama ne işe yarar?**
        USD/TRY, EUR/TRY, GBP/TRY ve Altın için canlı fiyatları takip eder.
        Her 60 saniyede bir otomatik güncellenir.

        ---

        **💰 Canlı Fiyatlar**
        Güncel piyasa fiyatını ve dünün kapanışına göre günlük değişimi (%) gösterir.
        🔴 Kırmızı = fiyat düştü | 🟢 Yeşil = fiyat yükseldi

        ---

        **🚨 Günlük Alarm**
        Günlük fiyat hareketi alışılmadık büyüklükte olduğunda uyarır.
        Eşikler 1 yıllık geçmiş veriden istatistiksel olarak hesaplanır:
        - ✅ Önemli Değişim Yok → Normal hareket
        - ⚠️ Dikkat → Ortalamanın biraz üzerinde
        - ⚠️ Uyarı → Belirgin şekilde yüksek hareket
        - 🚨 Kritik → Çok nadir görülen aşırı hareket

        ---

        **📊 Dönem Alarmlari**
        Güncel fiyatın son yüksek ve düşüklere göre nerede olduğunu gösterir:
        - 30 Gün: son 30 günle karşılaştırma
        - 52 Hafta: son 52 haftayla karşılaştırma
        - 5 Yıl: son 5 yılla karşılaştırma

        ---

        **📈 Trend Analizi**
        - 7 günlük ve 30 günlük ortalamaya göre Yükseliş / Düşüş / Yatay
        - 3 günlük ve 7 günlük ortalamaya göre Hızlanıyor / Yavaşlıyor

        ---

        **🔮 30 Günlük Projeksiyon**
        Tahmin değildir. Mevcut trendin devam etmesi durumunda fiyatın nereye gidebileceğini gösterir.
        Trend, kararlılık için 30 günlük değişim oranının 7 günlük ortalaması olarak hesaplanır:
        - 🟢 En İyi Senaryo: en olumlu fiyat yönü
        - 🟡 Baz: mevcut trend aynı hızda devam eder
        - 🔴 En Kötü Senaryo: en olumsuz fiyat yönü
        """)

# ── Auto Refresh ──────────────────────────────────────────────────────────────
time.sleep(60)
st.rerun()