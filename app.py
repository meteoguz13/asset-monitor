import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime



from functions import check_daily_alarm, format_change, check_period_alarm, \
get_trend, get_thresholds, format_period, get_rsi,get_impact

import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
from streamlit_autorefresh import st_autorefresh
from events import events

st.set_page_config(
    page_title="Asset Monitor",
    page_icon="📈",
    layout="wide"
)

# ── Language ──────────────────────────────────────────────────────────────────
with st.sidebar:
    lang = st.selectbox("🌐 Language", ["English", "Türkçe"])

labels = {
    "English": {
        "tab_volatility": "📊 Volatility",
        "vol_title": "Monthly Volatility",
        "vol_caption": "Higher = more turbulent month. Lower = calmer, more predictable price movement.",
        "top10_title": "Top 10 Single-Day Moves",
        "top10_up": "📈 Biggest Up Days",
        "top10_down": "📉 Biggest Down Days",
        "select_asset": "Select Asset",
        "cut": "Rate Cut ✂️",
        "hike": "Rate Hike 📈",
        "hold": "Hold ⏸️",
        "avg_caption": "Historical average asset reaction by decision type",
        "impact_caption": "% change after the decision (vs. day before)",
        "tcmb_title": "## 🏦 TCMB",
        "fed_title": "## 🏦 Fed",
        "cb_intro": "This tab shows how TCMB and Fed interest rate decisions impact USD/TRY, EUR/TRY, GBP/TRY and Gold in the following days.",
        "cb_info_title": "ℹ️ How to read this page?",
        "t1_label": "1 Day After",
        "t3_label": "3 Days After",
        "t7_label": "1 Week After",
        "new_rate": "🆕 New Rate",
        "prev_rate": "🔙 Previous Rate",
        "decision_label": "📋 Decision",
        "date_label": "📅 Date",
        "last_tcmb": "Last TCMB Decision",
        "last_fed": "Last Fed Decision",
        "title": "Asset Monitor",
        "caption": "Live prices, alerts and trend analysis for USD/TRY, EUR/TRY, GBP/TRY and Gold",
        "tab_main": "🏠 Main",
        "tab_gold_analysis": "🪙 Gold Analysis",
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
        "rsi_info": "ℹ️ What is RSI & Drawdown?",
        "overbought": "🔴 Overbought — Price rose too fast",
        "oversold": "🟠 Oversold — Price dropped too fast",
        "rsi_neutral": "🟢 Normal range — No extreme movement",
        "drawdown_title": "How Far From the Peak?",
        "drawdown_peak": "🏔️ At Peak — No drawdown",
        "drawdown_normal": "✅ Normal pullback — within safe range",
        "drawdown_warning": "⚠️ Notable drop — monitor closely",
        "drawdown_bear": "🔴 Bear territory — significant loss from peak",
        "recovery_label": "To recover the loss: +",
        "tab_cb": "🏦 Central Bank Rate Impact (TCMB/Fed)",
        "avg_impact_title": "Average Impact by Decision",
        "vol_intro": "Explore how volatile each asset has been over time and discover the most extreme single-day price moves.",
        "vol_info_title": "ℹ️ How to read this page?",

    },
    "Türkçe": {
        "tab_volatility": "📊 Volatilite",
        "vol_title": "Aylık Volatilite",
        "vol_caption": "Yüksek = daha hareketli ay. Düşük = daha sakin, daha öngörülebilir fiyat hareketi.",
        "top10_title": "En Büyük 10 Günlük Hareket",
        "top10_up": "📈 En Büyük Yükselişler",
        "top10_down": "📉 En Büyük Düşüşler",
        "select_asset": "Varlık Seçin",
        "cut": "Faiz İndirimi ✂️",
        "hike": "Faiz Artırımı 📈",
        "hold": "Sabit ⏸️",
        "avg_caption": "Karar tipine göre tarihsel ortalama varlık tepkisi",
        "tcmb_title": "## 🏦 TCMB",
        "fed_title": "## 🏦 Fed",
        "cb_intro": "Bu sekme TCMB ve Fed faiz kararlarının USD/TRY, EUR/TRY, GBP/TRY ve Altın üzerindeki etkisini gösterir.",
        "cb_info_title": "ℹ️ Bu sayfa nasıl okunur?",
        "impact_caption": "Karar sonrası % değişim (karar öncesi güne göre)",
        "t1_label": "1 Gün Sonra",
        "t3_label": "3 Gün Sonra",
        "t7_label": "1 Hafta Sonra",
        "new_rate": "🆕 Yeni Faiz",
        "prev_rate": "🔙 Önceki Faiz",
        "decision_label": "📋 Karar",
        "date_label": "📅 Tarih",
        "last_tcmb": "Son TCMB Kararı",
        "last_fed": "Son Fed Kararı",
        "title": "Varlık Takip",
        "caption": "USD/TRY, EUR/TRY, GBP/TRY ve Altın için canlı fiyat, alarm ve trend analizi",
        "tab_main": "🏠 Ana Sayfa",
        "tab_gold_analysis": "🪙 Altın Analizi",
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
        "rsi_info": "ℹ️ RSI ve Drawdown Nedir?",
        "overbought": "🔴 Aşırı Alım — Fiyat çok hızlı yükseldi",
        "oversold": "🟠 Aşırı Satım — Fiyat çok hızlı düştü",
        "rsi_neutral": "🟢 Normal bölge — Aşırı hareket yok",
        "drawdown_title": "Zirveden Ne Kadar Uzaktayız?",
        "drawdown_peak": "🏔️ Zirvede — Düşüş yok",
        "drawdown_normal": "✅ Normal — Güvenli bölge",
        "drawdown_warning": "⚠️ Dikkat çekici düşüş — Yakından takip et",
        "drawdown_bear": "🔴 Ayı bölgesi — Zirveden ciddi kayıp",
        "recovery_label": "Kaybı telafi etmek için: +",
        "tab_cb": "🏦 Merkez Bankası Faiz Etkileri (TCMB/Fed)",
        "avg_impact_title": "Karara Göre Ortalama Etki",
        "vol_intro": "Her varlığın zaman içinde ne kadar hareketli olduğunu keşfedin ve en aşırı tek günlük fiyat hareketlerini görün.",
        "vol_info_title": "ℹ️ Bu sayfa nasıl okunur?",
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
    'Gold': 'GC=F'
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
    data = yf.download(list(symbols.values()), period='2y', interval='1d')
    close = data['Close']
    close.columns = ['EUR/TRY', 'GBP/TRY', 'Gold', 'USD/TRY']
    data_5y = yf.download(list(symbols.values()), period='5y', interval='1d')
    close_5y = data_5y['Close']
    close_5y.columns = ['EUR/TRY', 'GBP/TRY', 'Gold', 'USD/TRY']
    return close, close_5y


# ── Load Data ─────────────────────────────────────────────────────────────────
live_prices = get_live_prices(symbols)
with st.sidebar:
    st.divider()
    for a, price in live_prices.items():
        if price:
            with st.container(border=True):
                st.metric(label=a, value=display_names[a].format(price))
close, close_5y = get_historical_data(symbols)
st_autorefresh(interval=60000)

daily_change = close.pct_change(fill_method=None) * 100
yesterday = close.iloc[-2]
thresholds = get_thresholds(daily_change)

daily_change_pct = {}
for a in live_prices.keys():
    if live_prices[a] is not None and not pd.isna(yesterday[a]):
        daily_change_pct[a] = ((live_prices[a] - yesterday[a]) / yesterday[a]) * 100
    else:
        daily_change_pct[a] = None

# Period data
high_30d = close.tail(30).max()
low_30d = close.tail(30).min()
high_52w = close.tail(252).max()
low_52w = close.tail(252).min()
high_5y = close_5y.max()
low_5y = close_5y.min()

# Trend data
ma_3 = close.tail(3).mean()
ma_7 = close.tail(7).mean()
ma_30 = close.tail(30).mean()

# ── Filter ────────────────────────────────────────────────────────────────────
st.caption(f"{t['last_updated']}: {datetime.now(timezone(timedelta(hours=3))).strftime('%H:%M:%S')}")
# ── Tabs ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
button[data-baseweb="tab"] {
    font-size: 40px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    t['tab_main'],
    t['tab_gold_analysis'],
    t['tab_cb'],
    t['tab_volatility']
])

# ── Tab 1: Main ───────────────────────────────────────────────────────────────
with tab1:
    selected = st.multiselect(
        t['select_assets'],
        options=list(live_prices.keys()),
        default=list(live_prices.keys())
    )

    if not selected:
        st.warning(t['no_asset_warning'])
        st.stop()

    cols = st.columns(len(selected))
    for i, a in enumerate(selected):
        with cols[i]:
            price = live_prices[a]
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
                fig.add_trace(go.Scatter(
                    x=chart_data.index,
                    y=chart_data.values,
                    mode='lines',
                    name=a,
                    connectgaps=True
                ))
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

            p30 = format_period(check_period_alarm(price, high_30d[a], low_30d[a], t), high_30d[a], low_30d[a], price,
                                t)
            p52 = format_period(check_period_alarm(price, high_52w[a], low_52w[a], t), high_52w[a], low_52w[a], price,
                                t)
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

            roc = close[a].pct_change(30, fill_method=None).dropna() * 100
            current_roc = roc.tail(7).mean()
            scenario_lo = round(price * (1 + (current_roc * 0.5) / 100), 2)
            base = round(price * (1 + (current_roc * 1.0) / 100), 2)
            scenario_hi = round(price * (1 + (current_roc * 1.5) / 100), 2)
            best_case = max(scenario_lo, scenario_hi)
            worst_case = min(scenario_lo, scenario_hi)
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
            - ✅ No Significant Change → Normal movement
            - ⚠️ Caution → Slightly above average movement
            - ⚠️ Warning → Notably above average movement
            - 🚨 Critical → Extreme movement, very rare

            ---

            **📊 Period Alarms**
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
            - ✅ Önemli Değişim Yok → Normal hareket
            - ⚠️ Dikkat → Ortalamanın biraz üzerinde
            - ⚠️ Uyarı → Belirgin şekilde yüksek hareket
            - 🚨 Kritik → Çok nadir görülen aşırı hareket

            ---

            **📊 Dönem Alarmlari**
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
            - 🟢 En İyi Senaryo: en olumlu fiyat yönü
            - 🟡 Baz: mevcut trend aynı hızda devam eder
            - 🔴 En Kötü Senaryo: en olumsuz fiyat yönü
            """)

# ── Tab 2: Gold Analysis ──────────────────────────────────────────────────────
with tab2:
    st.subheader(t['tab_gold_analysis'])

    gold_usd = live_prices.get('Gold')
    gold_change = daily_change_pct.get('Gold')

    col1, col2 = st.columns(2)

    with col1:
        # RSI
        st.markdown(f"**{t['rsi_title']}**")
        rsi_value = get_rsi(close['Gold']).dropna().iloc[-1]
        st.metric(label="RSI", value=f"{rsi_value:.1f}")
        if rsi_value >= 70:
            st.warning(t['overbought'])
        elif rsi_value <= 30:
            st.warning(t['oversold'])
        else:
            st.success(t['rsi_neutral'])

    with col2:
        # Drawdown
        st.markdown(f"**{t['drawdown_title']}**")
        rolling_max = close['Gold'].dropna().cummax()
        drawdown = (close['Gold'].dropna() - rolling_max) / rolling_max * 100
        current_drawdown = drawdown.iloc[-1]
        recovery_needed = (rolling_max.iloc[-1] / close['Gold'].dropna().iloc[-1] - 1) * 100

        st.metric(label="Drawdown", value=f"{current_drawdown:.1f}%")
        if current_drawdown == 0:
            st.caption("—")
            st.success(t["drawdown_peak"])
        elif current_drawdown > -10:
            st.success(t["drawdown_normal"])
            st.markdown(f"**{t['recovery_label']}{recovery_needed:.1f}%**")
        elif current_drawdown > -20:
            st.warning(t["drawdown_warning"])
            st.markdown(f"**{t['recovery_label']}{recovery_needed:.1f}%**")
        else:
            st.error(t["drawdown_bear"])
            st.markdown(f"**{t['recovery_label']}{recovery_needed:.1f}%**")

    st.divider()

    with st.expander(t['rsi_info']):
        if lang == "English":
            st.write("""
            **RSI (Relative Strength Index)**
            Measures how fast and how much a price has moved in the last 14 days.
            - 🔴 Above 70 → Price rose too fast → may slow down soon
            - 🟠 Below 30 → Price dropped too fast → may recover soon
            - 🟢 Between 30-70 → Normal movement

            ---

            **Drawdown**
            Shows how far the current price is from its all-time high.
            - 🏔️ 0% → At peak
            - ✅ 0% to -10% → Normal pullback
            - ⚠️ -10% to -20% → Notable drop, monitor closely
            - 🔴 Below -20% → Bear territory, significant loss
            """)
        else:
            st.write("""
            **RSI (Göreceli Güç Endeksi)**
            Son 14 günde fiyatın ne kadar hızlı hareket ettiğini ölçer.
            - 🔴 70 üzeri → Fiyat çok hızlı yükseldi → yavaşlayabilir
            - 🟠 30 altı → Fiyat çok hızlı düştü → toparlanabilir
            - 🟢 30-70 arası → Normal hareket

            ---

            **Drawdown**
            Fiyatın zirvesinden ne kadar uzakta olduğunu gösterir.
            - 🏔️ %0 → Zirvede
            - ✅ %0 ile -%10 → Normal düzeltme
            - ⚠️ -%10 ile -%20 → Dikkat çekici düşüş
            - 🔴 -%20 altı → Ayı bölgesi, ciddi kayıp
            """)
    st.divider()


# ── Tab 3: TCMB/Fed Analysis ──────────────────────────────────────────────────────

with tab3:
    st.subheader(t['tab_cb'])
    st.caption(t['cb_intro'])

    impact = get_impact(events, close)
    cols = impact.select_dtypes(include='number').columns
    avg_impact = impact.groupby(["type", "decision"])[cols].mean().round(2)

    son_tcmb = events[events["type"] == "TCMB"].iloc[-1]
    son_fed = events[events["type"] == "Fed"].iloc[-1]
    prev_tcmb = events[events["type"] == "TCMB"].iloc[-2]
    prev_fed = events[events["type"] == "Fed"].iloc[-2]
    tcmb_impact = impact[impact["date"] == son_tcmb["date"]]
    fed_impact = impact[impact["date"] == son_fed["date"]]

    assets = ['USD/TRY', 'EUR/TRY', 'GBP/TRY', 'Gold']
    asset_symbols = {
        'USD/TRY': '$ USD/TRY',
        'EUR/TRY': '€ EUR/TRY',
        'GBP/TRY': '£ GBP/TRY',
        'Gold': '🪙 Gold'
    }

    # ── Bölüm 1: Son Kararlar ─────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**🏦 {t['last_tcmb']}**")
        st.write(f"{t['date_label']}: {son_tcmb['date'].strftime('%d.%m.%Y')}")
        st.write(f"{t['prev_rate']}: %{prev_tcmb['rate']}")
        st.write(f"{t['new_rate']}: %{son_tcmb['rate']}")
        st.write(f"{t['decision_label']}: {son_tcmb['decision']}")
        rows = []
        for a in assets:
            rows.append({
                'Asset': asset_symbols[a],
                t['t1_label']: tcmb_impact[f'{a}_t1'].values[0],
                t['t3_label']: tcmb_impact[f'{a}_t3'].values[0],
                t['t7_label']: tcmb_impact[f'{a}_t7'].values[0],
            })
        st.caption(t['impact_caption'])
        df = pd.DataFrame(rows).set_index('Asset').T
        styled_df = df.style.format(format_change).map(
            lambda v: 'color: green' if v > 0 else ('color: red' if v < 0 else '')
        )
        st.dataframe(styled_df, use_container_width=True)

    with col2:
        st.markdown(f"**🏦 {t['last_fed']}**")
        st.write(f"{t['date_label']}: {son_fed['date'].strftime('%d.%m.%Y')}")
        st.write(f"{t['prev_rate']}: %{prev_fed['rate']}")
        st.write(f"{t['new_rate']}: %{son_fed['rate']}")
        st.write(f"{t['decision_label']}: {son_fed['decision']}")
        rows = []
        for a in assets:
            rows.append({
                'Asset': asset_symbols[a],
                t['t1_label']: fed_impact[f'{a}_t1'].values[0],
                t['t3_label']: fed_impact[f'{a}_t3'].values[0],
                t['t7_label']: fed_impact[f'{a}_t7'].values[0],
            })
        st.caption(t['impact_caption'])
        df = pd.DataFrame(rows).set_index('Asset').T
        styled_df = df.style.format(format_change).map(
            lambda v: 'color: green' if v > 0 else ('color: red' if v < 0 else '')
        )
        st.dataframe(styled_df, use_container_width=True)

    # ── Bölüm 2: Ortalama Etki ────────────────────────────────────────────────
    st.divider()
    st.markdown(f"**📊 {t['avg_impact_title']}**")

    col3, col4 = st.columns(2)

    with col3:
        st.markdown(t['tcmb_title'])
        st.caption(t['avg_caption'])
        decision_labels = {'Cut': t['cut'], 'Hike': t['hike'], 'Hold': t['hold']}
        tcmb_avg = avg_impact.loc["TCMB"]
        for decision in tcmb_avg.index:
            rows = []
            for a in assets:
                rows.append({
                    'Asset': asset_symbols[a],
                    t['t1_label']: float(tcmb_avg.loc[decision, f'{a}_t1']),
                    t['t3_label']: float(tcmb_avg.loc[decision, f'{a}_t3']),
                    t['t7_label']: float(tcmb_avg.loc[decision, f'{a}_t7']),
                })
            df = pd.DataFrame(rows).set_index('Asset').T
            df.index.name = decision_labels.get(decision, decision)
            styled_df = df.style.format(format_change).map(
                lambda v: 'color: green' if v > 0 else ('color: red' if v < 0 else '')
            )
            st.dataframe(styled_df, use_container_width=True)

    with col4:
        st.markdown(t['fed_title'])
        st.caption(t['avg_caption'])
        decision_labels = {'Cut': t['cut'], 'Hike': t['hike'], 'Hold': t['hold']}
        fed_avg = avg_impact.loc["Fed"]
        for decision in fed_avg.index:
            rows = []
            for a in assets:
                rows.append({
                    'Asset': asset_symbols[a],
                    t['t1_label']: float(fed_avg.loc[decision, f'{a}_t1']),
                    t['t3_label']: float(fed_avg.loc[decision, f'{a}_t3']),
                    t['t7_label']: float(fed_avg.loc[decision, f'{a}_t7']),
                })
            df = pd.DataFrame(rows).set_index('Asset').T
            df.index.name = decision_labels.get(decision, decision)
            styled_df = df.style.format(format_change).map(
                lambda v: 'color: green' if v > 0 else ('color: red' if v < 0 else '')
            )
            st.dataframe(styled_df, use_container_width=True)

    st.divider()
    with st.expander(t['cb_info_title']):
        if lang == "English":
            st.write("""
            **Last Decisions**
            Shows the most recent TCMB and Fed interest rate decisions and how assets reacted in the following 1, 3 and 7 days.

            ---

            **Average Impact**
            Shows the historical average asset reaction grouped by decision type (Cut / Hike / Hold).
            - 🟢 Green = asset gained value
            - 🔴 Red = asset lost value

            ---

            **Note:** TCMB Hike shows 0% for t+1 and t+3 because the decision date fell on a market holiday.
            """)
        else:
            st.write("""
            **Son Kararlar**
            En son TCMB ve Fed faiz kararlarını ve varlıkların sonraki 1, 3 ve 7 günde nasıl tepki verdiğini gösterir.

            ---

            **Ortalama Etki**
            Karar tipine göre (İndirim / Artırım / Sabit) varlıkların tarihsel ortalama tepkisini gösterir.
            - 🟢 Yeşil = varlık değer kazandı
            - 🔴 Kırmızı = varlık değer kaybetti

            ---

            **Not:** TCMB Artırım kararında t+1 ve t+3 %0 görünüyor çünkü karar tarihi piyasa tatiline denk geldi.
            """)

with tab4:
    st.subheader(t['tab_volatility'])
    st.caption(t['vol_intro'])

    selected_asset = st.selectbox(t['select_asset'], options=list(symbols.keys()), key="vol_asset")
    monthly_vol = daily_change[selected_asset].groupby(daily_change.index.to_period('M')).std().round(2)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly_vol.index.astype(str),
        y=monthly_vol.values,
        name=selected_asset
    ))
    fig.update_layout(
        title=t['vol_title'],
        xaxis_title="",
        yaxis_title="%",
        margin=dict(l=0, r=0, t=40, b=0),
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(t['vol_caption'])

    st.divider()
    st.markdown(f"**{t['top10_title']}**")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(t['top10_up'])
        top10_up = daily_change[selected_asset].nlargest(10).reset_index()
        top10_up.columns = ['Date', '%']
        top10_up['Date'] = top10_up['Date'].dt.strftime('%d.%m.%Y')
        top10_up['%'] = top10_up['%'].apply(format_change)
        styled_up = top10_up.style.map(
            lambda v: 'color: green' if '↑' in str(v) else '',
            subset=['%']
        )
        st.dataframe(styled_up, hide_index=True, use_container_width=True)
    with col2:
        st.markdown(t['top10_down'])
        top10_down = daily_change[selected_asset].nsmallest(10).reset_index()
        top10_down.columns = ['Date', '%']
        top10_down['Date'] = top10_down['Date'].dt.strftime('%d.%m.%Y')
        top10_down['%'] = top10_down['%'].apply(format_change)
        styled_down = top10_down.style.map(
            lambda v: 'color: red' if v else '',
            subset=['%']
        )
        st.dataframe(styled_down, hide_index=True, use_container_width=True)

    with st.expander(t['vol_info_title']):
        if lang == "English":
            st.write("""
            **Monthly Volatility Chart**
            Shows the standard deviation of daily returns for each month. Higher bars mean the asset moved more unpredictably that month.

            ---

            **Top 10 Single-Day Moves**
            The biggest single-day percentage changes in the selected asset's price history.
            - 📈 Biggest Up Days: largest positive moves
            - 📉 Biggest Down Days: largest negative moves
            """)

        else:
            st.write("""
            **Aylık Volatilite Grafiği**
            Her ay için günlük getirilerin standart sapmasını gösterir. Yüksek bar = o ay fiyat daha öngörülemez şekilde hareket etti.
            
            ---
            
            **En Büyük 10 Günlük Hareket**
            Seçilen varlığın fiyat tarihindeki en büyük tek günlük yüzde değişimleri.
            - 📈 En Büyük Yükselişler: en yüksek pozitif hareketler
            - 📉 En Büyük Düşüşler: en büyük negatif hareketler
             """)












