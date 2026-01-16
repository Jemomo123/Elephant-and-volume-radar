# 🐘 MEXC Prop Sniper Radar (2026 Edition)

A professional-grade market scanner optimized for mobile and tailored for **Proprietary Trading**. This tool filters the MEXC exchange to find institutional entries using SMA crossovers, Volume-backed Elephant Bars, and real-time liquidity analysis.

## 🚀 Trading Strategy: The Elephant Core
This system identifies high-probability reversals and trend ignitions by waiting for "Big Money" to show its hand.

### 1. Core Technical Signals
The scanner monitors the **SMA 20** and **SMA 200** to find four primary setups:
* **GOLD 💎 / DEATH 💀**: Traditional trend reversals (Golden/Death Cross).
* **SQZ 🌀**: Volatility Squeeze where the 20 and 200 SMAs are tightly compressed.
* **KOL 💋 (Kiss of Life)**: Bullish rejection/bounce off the 200 SMA.
* **KOD 💀 (Kiss of Death)**: Bearish rejection/failure at the 200 SMA.

### 2. The Institutional "Elephant" Filter
A signal is only **CONFIRMED** if it is accompanied by an **Elephant Bar**:
* **Relative Size**: 
    * Low TFs (3m, 5m, 15m): Bar range must be **> 2.0x** the average of the last 20 bars.
    * High TFs (1h, 4h): Bar range must be **> 2.5x** the average of the last 20 bars.
* **Body Quality**: The candle body must be **> 70%** of the total range (no long wicks).
* **Volume Delta**: The bar must have **> 2x** the average volume (Relative Volume).

## 📊 Prop Trader Checklist
Before entering a trade on your funded account, verify the **Human Reasoning** column:

| Requirement | Bullish Setup (Long) | Bearish Setup (Short) |
| :--- | :--- | :--- |
| **Scanner Status** | `🐘 [SIGNAL] CONFIRMED (VOL)` | `🐘 [SIGNAL] CONFIRMED (VOL)` |
| **VWAP** | Price is **Below VWAP** (Discount) | Price is **Above VWAP** (Premium) |
| **RSI** | **Oversold (< 35)** or Neutral | **Overbought (> 65)** or Neutral |
| **Liquidity** | Look for `🕳️ LIQ HOLE` for fast moves | Look for `🕳️ LIQ HOLE` for fast moves |



## 🛠️ Mobile Setup & Usage
1. **Timeframes**: Optimized for `3m`, `5m`, `15m`, `1h`, and `4h`.
2. **Meme Mode**: Toggle on to automatically track **DOGE, PEPE, TRUMP, PENGU** and other trending meme coins.
3. **New Listings**: The app automatically detects and alerts you to new MEXC USDT listings in real-time.

### Deployment
* **Host**: Streamlit Cloud (GitHub Integrated).
* **Theme**: Sniper Dark Mode (configured via `.streamlit/config.toml`).

---
**Disclaimer**: This is a tool for professional prop traders. Always adhere to your firm's maximum daily loss and consistency rules.
