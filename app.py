import streamlit as st
import ccxt
import pandas as pd
import pandas_ta as ta
from streamlit_autorefresh import st_autorefresh
import time

# --- 1. CONFIG & MOBILE THEME ---
st.set_page_config(page_title="Prop Sniper Radar", layout="wide")
st_autorefresh(interval=60000, key="mexc_refresh")

@st.cache_resource
def init_mexc():
    return ccxt.mexc({'enableRateLimit': True, 'timeout': 25000})

mexc = init_mexc()

# Session State for Meme List and Discovery
if 'meme_list' not in st.session_state:
    st.session_state.meme_list = ['DOGE', 'SHIB', 'PEPE', 'TRUMP', 'BONK', 'PENGU', 'SPX', 'FLOKI', 'WIF', 'FARTCOIN', 'POPCAT', 'MOODENG']
if 'known_coins' not in st.session_state:
    st.session_state.known_coins = set()

# --- 2. ANALYTICS ENGINE ---
def analyze_market(symbol, tf):
    try:
        # Fetch 250 candles to ensure SMA 200 stability
        ohlcv = mexc.fetch_ohlcv(symbol, timeframe=tf, limit=250)
        df = pd.DataFrame(ohlcv, columns=['ts', 'o', 'h', 'l', 'c', 'v'])
        curr_p, prev_p = df['c'].iloc[-1], df['c'].iloc[-2]
        
        # Core SMAs
        sma20 = ta.sma(df['c'], 20)
        sma200 = ta.sma(df['c'], 200)
        s20, s200 = sma20.iloc[-1], sma200.iloc[-1]
        ps20, ps200 = sma20.iloc[-2], sma200.iloc[-2]
        
        # Elephant Bar Logic (Dynamic Mult: 2.5x for 1h/4h, 2x for others)
        df['range'] = df['h'] - df['l']
        df['body'] = (df['c'] - df['o']).abs()
        avg_range_20 = df['range'].rolling(20).mean().iloc[-2]
        
        mult = 2.5 if tf in ['1h', '4h'] else 2.0
        is_elephant = df['range'].iloc[-1] > (avg_range_20 * mult)
        is_strong_body = df['body'].iloc[-1] > (df['range'].iloc[-1] * 0.7)
        
        # Volume Delta (Relative Volume > 2x)
        avg_vol_20 = df['v'].rolling(20).mean().iloc[-2]
        is_high_vol = df['v'].iloc[-1] > (avg_vol_20 * 2.0)
        
        # State: RSI, VWAP, Spread
        rsi = ta.rsi(df['c'], 14).iloc[-1]
        vwap = ta.vwap(df['h'], df['l'], df['c'], df['v']).iloc[-1]
        ob = mexc.fetch_order_book(symbol, limit=5)
        spread = ((ob['asks'][0][0] - ob['bids'][0][0]) / ob['bids'][0][0]) * 100
        
        # Signal Detection
        core = None
        if ps20 < ps200 and s20 > s200: core = "GOLD 💎"
        elif ps20 > ps200 and s20 < s200: core = "DEATH 💀"
        elif abs(s20 - s200) / s200 < 0.003: core = "SQZ 🌀"
        
        # Kiss of Life/Death
        if abs(s20 - s200) / s200 < 0.005:
            if prev_p < s200 and curr_p >= s200: core = "KOL 💋"
            elif prev_p > s200 and curr_p <= s200: core = "KOD 💀"

        # Signal Status
        status = "·"
        if core and is_elephant and is_high_vol and is_strong_body:
            status = f"🐘 {core} CONFIRMED (VOL)"
        elif core:
            status = f"⏳ {core} (Pending Vol)"
        elif is_elephant and is_high_vol:
            status = "🐘 High Vol Bar"

        # Human Reasoning Column
        reasons = []
        reasons.append("RSI OB" if rsi > 70 else "RSI OS" if rsi < 30 else f"RSI:{int(rsi)}")
        reasons.append("Above VWAP" if curr_p > vwap else "Below VWAP")
        if spread > 0.12: reasons.append("🕳️ LIQ HOLE")

        return status, " | ".join(reasons)
    except:
        return "err", "..."

# --- 3. UI & LISTING DETECTOR ---
st.title("⚡ PROP SNIPER RADAR")

# Fetch all USDT pairs & Update Listing Detection
tickers = mexc.fetch_tickers()
all_pairs = [s for s in tickers.keys() if '/USDT' in s]
current_coins = {s.split('/')[0] for s in all_pairs}

if st.session_state.known_coins:
    new_discovery = current_coins - st.session_state.known_coins
    for coin in new_discovery:
        if coin not in st.session_state.meme_list:
            st.session_state.meme_list.append(coin)
            st.toast(f"New MEXC Listing: {coin}", icon="🚀")
st.session_state.known_coins = current_coins

# Mobile Interface Controls
col1, col2 = st.columns(2)
with col1:
    mode = st.toggle("Meme + New Listings", value=True)
with col2:
    selected_tf = st.selectbox("Timeframe", ['3min', '5min', '15min', '1h', '4h'], index=2)

# Convert display TFs to MEXC format
tf_map = {'3min': '3m', '5min': '5m', '15min': '15m', '1h': '1h', '4h': '4h'}
mexc_tf = tf_map[selected_tf]

# Filter Symbols
if mode:
    targets = [s for s in all_pairs if s.split('/')[0] in st.session_state.meme_list]
else:
    targets = sorted(all_pairs, key=lambda x: tickers[x]['quoteVolume'] or 0, reverse=True)[:25]

# Process Table
data = []
for s in targets:
    sig, reasoning = analyze_market(s, mexc_tf)
    data.append({
        "Coin": s.replace('/USDT', ''),
        "Signal": sig,
        "Human Reasoning (RFE)": reasoning,
        "Action": f'<a href="https://www.mexc.com/exchange/{s.replace("/", "_")}" target="_blank" style="color: #00FF85; text-decoration: none; font-weight: bold;">TRADE</a>'
    })
    time.sleep(0.01)

# Display Table with HTML support for the Trade link
st.write(pd.DataFrame(data).to_html(escape=False, index=False), unsafe_allow_html=True)
