# 🤖 AI-Powered Multi-Timeframe Trading Bot

A professional-grade cryptocurrency signal engine designed for **Quality over Quantity**. This bot utilizes Triple-Timeframe alignment, AI regime detection, and ATR-based volatility filters to identify high-conviction trade setups.

## 🌟 Core Philosophy
* **Top-Down Analysis:** Only executes if 1D, 4H, and 1H timeframes align in direction.
* **Volatility Aware:** Stop Loss and Take Profit levels are dynamically calculated using **Average True Range (ATR)**.
* **ML-Ready:** Every scan collects Volume Ratios, ADX Trend Strength, and Time-of-Day data for future model training.

## 🛠 Project Architecture
| File | Function |
| :--- | :--- |
| `main.py` | The Scanner. Runs hourly to find high-quality alignments. |
| `monitor.py` | The Watchdog. Runs every 30m to check TP/SL hits. |
| `data_collection.py` | Handles API connections (Gate.io/Bitget) and Discord alerts. |
| `technical_analysis.py` | Calculates indicators (RSI, EMA, ATR, ADX, Volume SMA). |
| `ai_regime.py` | Interprets market structure using AI logic. |
| `database_manager.py` | Manages the SQLite `signals.db` for persistent memory. |
| `backtester.py` | Validates historical signals against actual price movement. |

## 🚀 Getting Started

### 1. Configuration (GitHub Secrets)
Add the following secrets to your GitHub Repository:
* `GATEIO_API_KEY` / `GATEIO_SECRET`
* `DISCORD_WEBHOOK_URL`
* `HF_TOKEN` (HuggingFace API)

### 2. Running Locally
```bash
pip install pandas requests ccxt pandas-ta-classic
python main.py
