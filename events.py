import pandas as pd
import yfinance as yf
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.max_colwidth", None)
pd.set_option("display.width", 100000)


symbols = {
    'USD/TRY': 'USDTRY=X',
    'EUR/TRY': 'EURTRY=X',
    'GBP/TRY': 'GBPTRY=X',
    'Gold':    'GC=F'
}


data = yf.download(list(symbols.values()), period='2y', interval='1d')
close = data['Close']
close.columns = ['EUR/TRY', 'GBP/TRY', 'Gold', 'USD/TRY']
print("1-year data shape:", close.shape)


tcmb_events = [
    # Mayıs 2024 - sabit 50.0
    {'date': '2024-05-23', 'event': 'TCMB Faiz Kararı', 'type': 'TCMB', 'rate': 50.0},
    {'date': '2024-06-27', 'event': 'TCMB Faiz Kararı', 'type': 'TCMB', 'rate': 50.0},
    {'date': '2024-07-23', 'event': 'TCMB Faiz Kararı', 'type': 'TCMB', 'rate': 50.0},
    {'date': '2024-08-20', 'event': 'TCMB Faiz Kararı', 'type': 'TCMB', 'rate': 50.0},
    {'date': '2024-09-19', 'event': 'TCMB Faiz Kararı', 'type': 'TCMB', 'rate': 50.0},
    {'date': '2024-10-17', 'event': 'TCMB Faiz Kararı', 'type': 'TCMB', 'rate': 50.0},
    {'date': '2024-11-21', 'event': 'TCMB Faiz Kararı', 'type': 'TCMB', 'rate': 50.0},
    {'date': '2024-12-26', 'event': 'TCMB Faiz Kararı', 'type': 'TCMB', 'rate': 47.5},
    # 2025
    {'date': '2025-01-23', 'event': 'TCMB Faiz Kararı', 'type': 'TCMB', 'rate': 45.0},
    {'date': '2025-03-06', 'event': 'TCMB Faiz Kararı', 'type': 'TCMB', 'rate': 42.5},
    {'date': '2025-03-20', 'event': 'TCMB Faiz Kararı', 'type': 'TCMB', 'rate': 42.5},
    {'date': '2025-04-18', 'event': 'TCMB Faiz Kararı', 'type': 'TCMB', 'rate': 46.0},
    {'date': '2025-06-19', 'event': 'TCMB Faiz Kararı', 'type': 'TCMB', 'rate': 46.0},
    {'date': '2025-07-24', 'event': 'TCMB Faiz Kararı', 'type': 'TCMB', 'rate': 43.0},
    {'date': '2025-09-11', 'event': 'TCMB Faiz Kararı', 'type': 'TCMB', 'rate': 40.5},
    {'date': '2025-10-23', 'event': 'TCMB Faiz Kararı', 'type': 'TCMB', 'rate': 39.5},
    {'date': '2025-12-11', 'event': 'TCMB Faiz Kararı', 'type': 'TCMB', 'rate': 38.0},
    #2026
    {'date': '2026-01-22', 'event': 'TCMB Faiz Kararı', 'type': 'TCMB', 'rate': 37.0},
    {'date': '2026-03-12', 'event': 'TCMB Faiz Kararı', 'type': 'TCMB', 'rate': 37.0},
    {'date': '2026-04-22', 'event': 'TCMB Faiz Kararı', 'type': 'TCMB', 'rate': 37.0},
    {'date': '2026-05-14', 'event': 'TCMB Faiz Kararı', 'type': 'TCMB', 'rate': 37.0},
]

fed_events = [
    {'date': '2024-05-01', 'event': 'Fed Faiz Kararı', 'type': 'Fed', 'rate': 5.50},
    {'date': '2024-06-12', 'event': 'Fed Faiz Kararı', 'type': 'Fed', 'rate': 5.50},
    {'date': '2024-07-31', 'event': 'Fed Faiz Kararı', 'type': 'Fed', 'rate': 5.50},
    {'date': '2024-09-18', 'event': 'Fed Faiz Kararı', 'type': 'Fed', 'rate': 5.00},
    {'date': '2024-11-07', 'event': 'Fed Faiz Kararı', 'type': 'Fed', 'rate': 4.75},
    {'date': '2024-12-18', 'event': 'Fed Faiz Kararı', 'type': 'Fed', 'rate': 4.50},
    #2025
    {'date': '2025-01-29', 'event': 'Fed Faiz Kararı', 'type': 'Fed', 'rate': 4.50},
    {'date': '2025-03-19', 'event': 'Fed Faiz Kararı', 'type': 'Fed', 'rate': 4.50},
    {'date': '2025-05-07', 'event': 'Fed Faiz Kararı', 'type': 'Fed', 'rate': 4.50},
    {'date': '2025-06-18', 'event': 'Fed Faiz Kararı', 'type': 'Fed', 'rate': 4.50},
    {'date': '2025-07-30', 'event': 'Fed Faiz Kararı', 'type': 'Fed', 'rate': 4.50},
    {'date': '2025-09-17', 'event': 'Fed Faiz Kararı', 'type': 'Fed', 'rate': 4.25},
    {'date': '2025-10-29', 'event': 'Fed Faiz Kararı', 'type': 'Fed', 'rate': 4.00},
    {'date': '2025-12-10', 'event': 'Fed Faiz Kararı', 'type': 'Fed', 'rate': 3.75},
    #2026
    {'date': '2026-01-28', 'event': 'Fed Faiz Kararı', 'type': 'Fed', 'rate': 3.75},
    {'date': '2026-03-18', 'event': 'Fed Faiz Kararı', 'type': 'Fed', 'rate': 3.75},
    {'date': '2026-04-29', 'event': 'Fed Faiz Kararı', 'type': 'Fed', 'rate': 3.75},
]

import os
events = pd.DataFrame(tcmb_events + fed_events)
events['date'] = pd.to_datetime(events['date'])
events = events.sort_values('date').reset_index(drop=True)
print(events.head())

events["rate_change"] = events.groupby("type")["rate"].diff()

events["decision"] = events["rate_change"].apply(lambda x:"Hike" if x > 0 else
("Cut" if x < 0 else "Hold"))

print(events.to_string())


def get_impact (events, close):
    results = []
    for _, row in events.iterrows():
        date = row["date"] - pd.Timedelta(days=1)
        base_price = close.asof(date)
        price_t1 = close.asof(row["date"] + pd.Timedelta(days=1))
        price_t3 = close.asof(row["date"] + pd.Timedelta(days=3))
        price_t7 = close.asof(row["date"] + pd.Timedelta(days=7))
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


print(get_impact(events, close).to_string())

impact = get_impact(events, close)

cols = impact.select_dtypes(include='number').columns
print(impact.groupby(["type","decision"])[cols].mean())









