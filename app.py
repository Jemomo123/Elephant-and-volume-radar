import streamlit as st
import ccxt
import pandas as pd
import pandas_ta as ta
from streamlit_autorefresh import st_autorefresh
import time

# --- 1. CONFIG & SNIPER THEME ---
st.set_page_config(page_title="MEXC Prop Sniper", layout="wide")
st_autorefresh(interval=60000, key="mexc_refresh")

@st.cache_resource
def init_mexc():
    # 2026-Ready Rate Limit Pacing
    return ccxt.mexc({'enableRateLimit': True, 'timeout': 30000})

mexc = init_mexc()

# --- 2. ANALYTICS ENGINE (The Strategy) ---
def analyze_market(symbol, tf):
    try:
        # Fetch Data
        ohlcv = mexc.fetch_ohlcv(symbol, timeframe=tf, limit=250)
        df = pd.DataFrame(ohlcv, columns=['ts', 'o', 'h', 'l', 'c', 'v'])
        curr_p = df['c'].iloc[-1]
        
        # SMAs (20/200)
        sma20 = ta.sma(df['c'], 20)
        sma200 = ta.sma(df['c'], 200)
        s20, s200 = sma20.iloc[-1], sma200.iloc[-1]
        ps20, ps200 = sma20.iloc[-2], sma200.iloc[-2]

        # Elephant Bar Logic (Range > 2x/2.5x, Body > 70%)
        df['range'] = df['h'] - df['l']
        df['body'] = (df['c'] - df['o']).abs()
        avg_r = df['range'].rolling(20).mean().iloc[-2]
        mult = 2.5 if tf in ['1h', '4h'] else 2.0
        
        is_elephant = (df['range'].iloc[-1] > avg_r * mult) and (df['body'].iloc[-1] > df['range'].iloc[-1] * 0.7)
        
        # Volume Delta (2x Relative Volume)
        avg_v = df['v'].rolling(20).mean().iloc[-2]
        is_high_vol = df['v'].iloc[-1] > (avg_v * 2.0)

        # LIQUIDITY HOLE DETECTION (Order Book Depth)
        # We check depth within 0.5% of current price
        ob = mexc.fetch_order_book(symbol, limit=20)
        depth_05_asks = sum(q for p, q in ob['asks'] if p <= curr_p * 1.005)
        depth_05_bids = sum(q for p, q in ob['bids'] if p >= curr_p * 0.995)
        
        # A hole exists if the 0.5% depth is < 20% of the average 1-min volume
        avg_vol_min = df['v'].iloc[-20:].mean() / (60 if 'h' in tf else 1) 
        liq_hole_above = depth_05_asks < (avg_vol_min * 0.2)
        liq_hole_below = depth_05_bids < (avg_vol_min * 0.2)

        # Signal Logic
        core = None
        if ps20 < ps200 and s20 > s200: core = "GOLD 💎"
        elif ps20 > ps200 and s20 < s200: core = "DEATH 💀"
        elif abs(s20 - s200)/s200 < 0.003: core = "SQZ 🌀"
        
        status = "·"
        if core and is_elephant and is_high_vol:
            if liq_hole_above and s20 > s200:
                status = f"🚀 {core} EXPLOSIVE LONG"
            elif liq_hole_below and s20 < s200:
                status = f"🔻 {core} EXPLOSIVE SHORT"
            else:
                status = f"🐘 {core} CONFIRMED"
        elif core:
            status = f"⏳ {core}"

        # Human Reasoning (RSI/VWAP)
        rsi = ta.rsi(df['c'], 14).iloc[-1]
        vwap = ta.vwap(df['h'], df['l'], df['c'], df['v']).iloc[-1]
        reason = f"RSI:{int(rsi)} | {'↑' if curr_p > vwap else '↓'} VWAP"
        if liq_hole_above or liq_hole_below:
            reason += " | 🕳️ HOLE"

        return status, reason
    except:
        return "err", "..."

# --- 3. MOBILE UI LAYER ---
st.title("⚡ PROP SNIPER RADAR")
tickers = mexc.fetch_tickers()
all_pairs = [s for s in tickers.keys() if '/USDT' in s]

# Filter for Meme Coins & High Volume
meme_list = ['PEPE', 'DOGE', 'TRUMP', 'PENGU', 'WIF', 'BONK', 'POPCAT']
targets = [s for s in all_pairs if any(m in s for m in meme_list)]
targets = targets[:30] # Limit for mobile performance

selected_tf = st.selectbox("Timeframe", ['3m', '5m', '15m', '1h', '4h'], index=2)

results = []
for symbol in targets:
    sig, res = analyze_market(symbol, selected_tf)
    results.append({"Coin": symbol.replace('/USDT', ''), "Signal": sig, "Reasoning": res})
    time.sleep(0.02) # Rate limit safety

st.table(pd.DataFrame(results))
