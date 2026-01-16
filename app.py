import streamlit as st
import ccxt
import pandas as pd
import pandas_ta as ta
from streamlit_autorefresh import st_autorefresh
import time

st.set_page_config(page_title="Prop Sniper", layout="wide")
st_autorefresh(interval=60000, key="mexc_refresh")

@st.cache_resource
def init_mexc():
    return ccxt.mexc({'enableRateLimit': True, 'timeout': 30000})

mexc = init_mexc()

# Session State for discovery
if 'meme_list' not in st.session_state:
    st.session_state.meme_list = ['DOGE', 'PEPE', 'TRUMP', 'PENGU', 'BONK', 'WIF', 'POPCAT']
if 'known_coins' not in st.session_state:
    st.session_state.known_coins = set()

def analyze_market(symbol, tf):
    for attempt in range(3):
        try:
            ohlcv = mexc.fetch_ohlcv(symbol, timeframe=tf, limit=250)
            df = pd.DataFrame(ohlcv, columns=['ts', 'o', 'h', 'l', 'c', 'v'])
            
            # Indicators
            sma20 = ta.sma(df['c'], 20)
            sma200 = ta.sma(df['c'], 200)
            s20, s200, ps20, ps200 = sma20.iloc[-1], sma200.iloc[-1], sma20.iloc[-2], sma200.iloc[-2]
            
            # Elephant & Volume Logic
            df['range'], df['body'] = (df['h'] - df['l']), (df['c'] - df['o']).abs()
            avg_r, avg_v = df['range'].rolling(20).mean().iloc[-2], df['v'].rolling(20).mean().iloc[-2]
            
            mult = 2.5 if tf in ['1h', '4h'] else 2.0
            is_elephant = (df['range'].iloc[-1] > avg_r * mult) and (df['body'].iloc[-1] > df['range'].iloc[-1] * 0.7)
            is_high_vol = df['v'].iloc[-1] > (avg_v * 2.0)
            
            # Signals
            core = None
            if ps20 < ps200 and s20 > s200: core = "GOLD 💎"
            elif ps20 > ps200 and s20 < s200: core = "DEATH 💀"
            elif abs(s20 - s200)/s200 < 0.003: core = "SQZ 🌀"
            
            status = f"🐘 {core} CONFIRMED (VOL)" if (core and is_elephant and is_high_vol) else (f"⏳ {core}" if core else "·")
            
            rsi = ta.rsi(df['c'], 14).iloc[-1]
            vwap = ta.vwap(df['h'], df['l'], df['c'], df['v']).iloc[-1]
            reason = f"RSI:{int(rsi)} | {'Above' if df['c'].iloc[-1] > vwap else 'Below'} VWAP"
            
            return status, reason
        except:
            time.sleep(1)
            continue
    return "Error", "Retry"

# UI Logic
st.title("⚡ PROP SNIPER")
tickers = mexc.fetch_tickers()
all_pairs = [s for s in tickers.keys() if '/USDT' in s]

# Auto-Listing Detector
current_coins = {s.split('/')[0] for s in all_pairs}
if st.session_state.known_coins:
    new_ones = current_coins - st.session_state.known_coins
    for c in new_ones:
        if c not in st.session_state.meme_list: st.session_state.meme_list.append(c)
st.session_state.known_coins = current_coins

sel_tf = st.selectbox("TF", ['3min', '5min', '15min', '1h', '4h'], index=2)
tf_m = {'3min':'3m', '5min':'5m', '15min':'15m', '1h':'1h', '4h':'4h'}

targets = [s for s in all_pairs if s.split('/')[0] in st.session_state.meme_list]
data = []
for s in targets:
    sig, res = analyze_market(s, tf_m[sel_tf])
    data.append({"Coin": s.replace('/USDT',''), "Signal": sig, "Reason": res})
    time.sleep(0.02)

st.table(pd.DataFrame(data))
