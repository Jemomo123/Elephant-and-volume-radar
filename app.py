import streamlit as st
import ccxt
import pandas as pd
import pandas_ta as ta
from streamlit_autorefresh import st_autorefresh
import time

# Rate limit safe for 2026 standards
@st.cache_resource
def init_mexc():
    return ccxt.mexc({'enableRateLimit': True, 'timeout': 30000})

mexc = init_mexc()
st_autorefresh(interval=60000, key="mexc_refresh")

def analyze_market(symbol, tf):
    try:
        ohlcv = mexc.fetch_ohlcv(symbol, timeframe=tf, limit=250)
        df = pd.DataFrame(ohlcv, columns=['ts', 'o', 'h', 'l', 'c', 'v'])
        
        # Pattern Logic: 20/200 SMA
        sma20 = ta.sma(df['c'], 20)
        sma200 = ta.sma(df['c'], 200)
        s20, s200 = sma20.iloc[-1], sma200.iloc[-1]
        ps20, ps200 = sma20.iloc[-2], sma200.iloc[-2]

        signal = "·"
        # Golden/Death Cross
        if ps20 < ps200 and s20 > s200: signal = "GOLD 💎"
        elif ps20 > ps200 and s20 < s200: signal = "DEATH 💀"
        # Squeeze
        elif abs(s20 - s200)/s200 < 0.003: signal = "SQZ 🌀"
        
        return signal, f"20s: {s20:.4f}"
    except:
        return "err", "..."

st.title("⚡ PROP SNIPER RADAR")
selected_tf = st.selectbox("Timeframe", ['3m', '5m', '15m', '1h', '4h'], index=2)

# Simple display logic
tickers = ['PEPE/USDT', 'DOGE/USDT', 'WIF/USDT', 'BONK/USDT']
results = []
for t in tickers:
    sig, det = analyze_market(t, selected_tf)
    results.append({"Coin": t, "Signal": sig, "Detail": det})

st.table(pd.DataFrame(results))
