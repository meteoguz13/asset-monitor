import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
from functions import check_daily_alarm, check_period_alarm, get_trend, get_thresholds, format_period, get_rsi
import plotly.graph_objects as go

st.set_page_config(
    page_title="Asset Monitor",
    page_icon="📈",
    layout="wide"
)

# ── Language ──────────────────────────────────────────────────────────────────
lang = st.selectbox("🌐 Language", ["English", "Türkçe"], label_visibility="collapsed")

labels = {
    "English": {
        "title": "Asset Monitor",
        "rsi_info": "ℹ️ What is RSI?",
        "caption": "Live prices, alerts and trend analysis for USD/TRY, EUR/TRY, GBP/TRY and Gold",
        "tab_main": "🏠 Main",
        "tab_rsi": "📈 RSI",
        "tab_drawdown": "📉 Drawdown",
        "last_updated": "Last updated",
        "select_assets": "Select assets to display",
        "no_asset_warning": "Please select at least one asset.",
        "chart": "📊 Chart",
        "period": "Period",
        "period_options": ["1 Week", "1 Month", "3 Months", "6 Months", "1 Year"],
        "trend_label": "📈 Trend",
        "uptrend": "Uptrend ↑",
        "downtrend": "Downtrend ↓",
        "neutral": "Neutral →",
        "accelerating": "Accelerating ↑",
        "slowing": "Slowing ↓",
        "stable": "Stable",
        "period_label": "📊 Period",
        "period_col": "Period",
        "status_col": "Status",
        "30d": "30 Days",
        "52w": "52 Weeks",
        "5y": "5 Years",
        "projection_label": "🔮 Projection",
        "scenario_col": "Scenario",
        "price_col": "Price",
        "best_case": "🟢 Best Case",
        "base": "🟡 Base",
        "worst_case": "🔴 Worst Case",
        "no_change": "No Significant Change",
        "critical_up": "CRITICAL UP",
        "warning_up": "WARNING UP",
        "caution_up": "CAUTION UP",
        "critical_down": "CRITICAL DOWN",
        "warning_down": "WARNING DOWN",
        "caution_down": "CAUTION DOWN",
        "new_peak": "NEW PEAK",
        "near_peak": "Near Peak",
        "new_bottom": "NEW BOTTOM",
        "near_bottom": "Near Bottom",
        "mid_range": "Mid Range",
        "info_title": "ℹ️ How does this app work?",
        "rsi_title": "RSI Analysis",
        "overbought": "🔴️ Overbought",
        "oversold": "🟠 Oversold",
        "neutral": "🟡 Neutral",
    },
    "Türkçe": {
        "title": "Varlık Takip",
        "caption": "USD/TRY, EUR/TRY, GBP/TRY ve Altın için canlı fiyat, alarm ve trend analizi",
        "tab_main": "🏠 Ana Sayfa",
        "tab_rsi": "📈 RSI",
        "tab_drawdown": "📉 Drawdown",
        "rsi_info": "ℹ️ RSI Nedir?",
        "last_updated": "Son güncelleme",
        "select_assets": "Görüntülenecek varlıkları seçin",
        "no_asset_warning": "Lütfen en az bir varlık seçin.",
        "chart": "📊 Grafik",
        "period": "Dönem",
        "period_options": ["1 Hafta", "1 Ay", "3 Ay", "6 Ay", "1 Yıl"],
        "trend_label": "📈 Trend",
        "uptrend": "Yükseliş ↑",
        "downtrend": "Düşüş ↓",
        "neutral": "Yatay →",
        "accelerating": "Hızlanıyor ↑",
        "slowing": "Yavaşlıyor ↓",
        "stable": "Stabil",
        "period_label": "📊 Dönem",
        "period_col": "Dönem",
        "status_col": "Durum",
        "30d": "30 Gün",
        "52w": "52 Hafta",
        "5y": "5 Yıl",
        "projection_label": "🔮 Projeksiyon",
        "scenario_col": "Senaryo",
        "price_col": "Fiyat",
        "best_case": "🟢 En İyi Senaryo",
        "base": "🟡 Baz",
        "worst_case": "🔴 En Kötü Senaryo",
        "no_change": "Önemli Değişim Yok",
        "critical_up": "KRİTİK YÜKSELİŞ",
        "warning_up": "UYARI YÜKSELİŞ",
        "caution_up": "DİKKAT YÜKSELİŞ",
        "critical_down": "KRİTİK DÜŞÜŞ",
        "warning_down": "UYARI DÜŞÜŞ",
        "caution_down": "DİKKAT DÜŞÜŞ",
        "new_peak": "YENİ ZİRVE",
        "near_peak": "Zirveye Yakın",
        "new_bottom": "YENİ DİP",
        "near_bottom": "Dibe Yakın",
        "mid_range": "Orta Bölge",
        "info_title": "ℹ️ Bu uygulama nasıl çalışır?",
        "rsi_title": "RSI Analizi",
        "overbought": "🔴️ Aşırı Alım",
        "oversold": "🟠 Aşırı Satım",
        "neutral": "🟡  Nötr",
    }
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
    st.stop()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    t['tab_main'],
    t['tab_rsi'],
    t['tab_drawdown']
])

# ── Tab 1: Main ───────────────────────────────────────────────────────────────
with tab1:
    cols = st.columns(len(selected))
    for i, a in enumerate(selected):
        with cols[i]:
            price  = live_prices[a]
            change = daily_change_pct[a]

            if price and not pd.isna(yesterday[a]):
                st.metric(
                    label=a,
                    value=display_names[a].format(price),
                    delta=f"{change:.2f}%" if change else "N/A"
                )
            else:
                st.metric(label=a, value="N/A")

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

            if change is not None:
                alarm = check_daily_alarm(change, thresholds[a], t)
                if t['critical_up'] in alarm or t['critical_down'] in alarm:
                    st.error(f"🚨 {alarm}")
                elif t['warning_up'] in alarm or t['warning_down'] in alarm:
                    st.warning(f"⚠️ {alarm}")
                elif t['caution_up'] in alarm or t['caution_down'] in alarm:
                    st.warning(f"⚠️ {alarm}")
                else:
                    st.success(f"✅ {alarm}")

            st.divider()

            trend, momentum = get_trend(ma_3, ma_7, ma_30, a, t)
            st.markdown(f"**{t['trend_label']}:** {trend} / {momentum}")

            st.divider()

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

# ── Tab 2: RSI ────────────────────────────────────────────────────────────────
with tab2:
    st.subheader(f"📈 {t['rsi_title']}")
    cols = st.columns(len(selected))
    for i, a in enumerate(selected):
        with cols[i]:
            rsi_value = get_rsi(close[a]).iloc[-1]
            if rsi_value >= 70:
                yorum = t['overbought']
            elif rsi_value <= 30:
                yorum = t['oversold']
            else:
                yorum = t['neutral']
            st.markdown(f"**{a}**")
            st.metric(label="RSI", value=f"{rsi_value:.1f}")
            st.write(yorum)

with st.expander(t['rsi_info']):
    if lang == "English":
        st.write("""
        RSI measures how fast and how much a price has moved in the last 14 days.

        - 🔴 Above 70 → Price rose too fast → may slow down soon
        - 🟠 Below 30 → Price dropped too fast → may recover soon  
        - 🟡 Between 30-70 → Normal movement
        """)
    else:
        st.write("""
        RSI son 14 günde fiyatın ne kadar hızlı hareket ettiğini ölçer.

        - 🔴 70 üzeri → Fiyat çok hızlı yükseldi → yavaşlayabilir
        - 🟠 30 altı → Fiyat çok hızlı düştü → toparlanabilir
        - 🟡 30-70 arası → Normal hareket
        """)

# ── Tab 3: Drawdown ───────────────────────────────────────────────────────────
with tab3:
    st.info("Drawdown coming soon...")

# ── Auto Refresh ──────────────────────────────────────────────────────────────
time.sleep(60)
st.rerun()