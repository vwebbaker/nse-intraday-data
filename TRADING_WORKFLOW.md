# 🚀 Complete Automated Trading Pipeline

## 📋 Overview

This is a **3-phase automated trading system** that combines:
- Pre-market data collection
- AI-powered stock selection  
- Real-time tick-by-tick monitoring

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1: PRE-MARKET DATA (9:00-9:08 AM)                        │
│  Script: run_analysis_pipeline.py                               │
├─────────────────────────────────────────────────────────────────┤
│  ✓ Downloads NSE derivatives data                               │
│  ✓ Fetches global market indices                                │
│  ✓ Captures pre-open market data                                │
│  ✓ Creates analysis_prompt.txt with URLs                        │
│  ✓ Publishes data to GitHub                                     │
│                                                                  │
│  Output: analysis_prompt.txt (ready for AI)                     │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 2: AI ANALYSIS (Manual Step)                             │
│  Script: assistant_handler.py                                   │
├─────────────────────────────────────────────────────────────────┤
│  ✓ Sends analysis_prompt.txt to AI (Perplexity)                 │
│  ✓ Gets TOP 5 stock recommendations                             │
│  ✓ Extracts stock symbols automatically                         │
│  ✓ Generates futures tokens                                     │
│  ✓ Creates watchlist_tokens.txt                                 │
│                                                                  │
│  Output: watchlist_tokens.txt (TOP 5 stocks with tokens)        │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 3: LIVE MONITORING (9:15 AM - 3:30 PM)                   │
│  Script: live_tick_monitor.py                                   │
├─────────────────────────────────────────────────────────────────┤
│  ✓ Connects to Breeze API WebSocket                             │
│  ✓ Streams tick-by-tick data for watchlist stocks               │
│  ✓ Saves to CSV (incremental writes)                            │
│  ✓ Creates JSON snapshots every 60 seconds                      │
│  ✓ Real-time monitoring of TOP 5 AI-selected stocks             │
│                                                                  │
│  Output: tick_data/*.csv + snapshots/*.json                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Quick Start

### **Option 1: Run Complete Pipeline (One Command)**

```bash
python master_trading_pipeline.py
```

This runs all 3 phases sequentially with prompts between each step.

---

### **Option 2: Run Individual Phases**

```bash
# Phase 1: Pre-market data collection
python run_analysis_pipeline.py

# Phase 2: AI analysis & token generation  
python assistant_handler.py

# Phase 3: Live monitoring
python live_tick_monitor.py
```

---

## 📂 File Structure

```
nse-intraday-data/
│
├── 🎯 MASTER ORCHESTRATOR
│   └── master_trading_pipeline.py      # Run this for complete automation
│
├── 📊 PHASE 1 SCRIPTS (Data Collection)
│   ├── run_analysis_pipeline.py        # Main orchestrator
│   ├── nse_data_fetcher.py             # Downloads NSE files
│   ├── snapshot_and_publish.py         # Creates JSON snapshots
│   ├── global_indices_fetcher.py       # Fetches global data
│   └── preopen_fetcher.py              # Fetches pre-open data
│
├── 🤖 PHASE 2 SCRIPTS (AI Analysis)
│   ├── assistant_handler.py            # AI interaction & token gen
│   ├── token_parser.py                 # Futures token parser
│   └── symbol_mapper.py                # Symbol normalization
│
├── 📡 PHASE 3 SCRIPTS (Live Monitoring)
│   └── live_tick_monitor.py            # Breeze WebSocket monitor
│
├── ⚙️ CONFIGURATION
│   └── config.py                       # Breeze API credentials
│
├── 📄 DATA FILES
│   ├── future_tokens.txt               # NSE futures token database
│   ├── analysis_prompt.txt             # AI analysis prompt
│   └── watchlist_tokens.txt            # Generated watchlist
│
└── 📁 OUTPUT FOLDERS
    ├── snapshots/                      # NSE snapshots
    ├── global/                         # Global indices
    ├── preopen/                        # Pre-open data
    ├── recommendations/                # AI recommendations
    └── tick_data/                      # Live tick CSVs
```

---

## ⚙️ Configuration

### **1. Update Breeze API Credentials**

Edit `config.py`:

```python
BREEZE_API_KEY = "your_api_key"
BREEZE_API_SECRET = "your_api_secret"
BREEZE_SESSION_TOKEN = "get_fresh_token_daily"  # ⚠️ Update daily!
```

### **2. Get Session Token (Daily)**

Login to ICICI Breeze web portal and extract session token from:
- Browser Developer Tools → Application → Cookies → session_token

---

## 🕐 Recommended Schedule

```
⏰ 9:00 AM  →  Run Phase 1 (Data Collection)
               Takes: ~2 minutes

⏰ 9:05 AM  →  Run Phase 2 (AI Analysis)
               Takes: ~2-3 minutes (manual AI interaction)

⏰ 9:15 AM  →  Run Phase 3 (Live Monitoring)
               Runs until 3:30 PM or Ctrl+C
```

---

## 📊 What Gets Generated

### **Phase 1 Output:**
```
✓ snapshots/nse_snapshot_YYYYMMDD_HHMMSS.json
✓ global/global_indices_YYYYMMDD_HHMMSS.json
✓ preopen/preopen_YYYYMMDD_HHMMSS.json
✓ analysis_prompt.txt (updated with URLs)
```

### **Phase 2 Output:**
```
✓ recommendations/recommendations_YYYYMMDD_HHMMSS.txt
✓ watchlist_tokens.txt (format: token:symbol)

Example watchlist_tokens.txt:
45678:TATSTE
45679:RELIND
45680:INFY
45681:TCS
45682:HDFBAN
```

### **Phase 3 Output:**
```
✓ tick_data/TATSTE_YYYYMMDD.csv (tick-by-tick data)
✓ tick_data/RELIND_YYYYMMDD.csv
✓ snapshots/latest_snapshot.json (updated every 60s)
```

---

## 🔧 Dependencies

```bash
pip install pandas numpy requests beautifulsoup4 pyperclip breezepy yfinance brotli
```

---

## 🎯 Key Features

### **Phase 1: Data Collection**
- ✅ Auto-downloads from NSE archives
- ✅ Handles compressed responses (Brotli)
- ✅ Multi-source global indices (fallback mechanisms)
- ✅ Auto-publishes to GitHub
- ✅ Updates analysis_prompt.txt with latest URLs

### **Phase 2: AI Analysis**
- ✅ Opens Perplexity AI in browser
- ✅ Auto-copies prompt to clipboard
- ✅ Extracts stock symbols from AI response
- ✅ Normalizes symbols (TATASTEEL → TATSTE)
- ✅ Generates futures tokens automatically
- ✅ Creates watchlist for monitoring

### **Phase 3: Live Monitoring**
- ✅ Real-time WebSocket streaming
- ✅ Multi-stock support (5-20 stocks)
- ✅ Batch writes (optimized performance)
- ✅ 5-level bid/ask depth
- ✅ OI tracking
- ✅ Auto-stops at market close (3:30 PM)

---

## 🐛 Troubleshooting

### **Error: "ModuleNotFoundError: No module named 'breezepy'"**
```bash
pip install breezepy
```

### **Error: "Authentication failed"**
```
⚠️ Update BREEZE_SESSION_TOKEN in config.py
   Get fresh token daily from Breeze web portal
```

### **Error: "Watchlist not found"**
```
⚠️ Run Phase 2 first to generate watchlist_tokens.txt
   OR manually create watchlist_tokens.txt with format:
   token:symbol (one per line)
```

### **Error: "Symbol not found in token parser"**
```
⚠️ Check symbol_mapper.py for correct symbol mappings
   Example: TATASTEEL → TATSTE
```

---

## 📈 Trading Workflow Example

```
9:00 AM  → Run: python master_trading_pipeline.py
            ✓ Downloads data (NSE + Global + Pre-open)

9:05 AM  → AI Analysis
            ✓ Sends prompt to Perplexity
            ✓ Gets TOP 5 recommendations:
              • TATASTEEL (TATSTE)
              • RELIANCE (RELIND)
              • INFOSYS (INFY)
              • TCS (TCS)
              • HDFC BANK (HDFBAN)

9:10 AM  → Token Generation
            ✓ Creates watchlist_tokens.txt
            ✓ Maps symbols to futures tokens

9:15 AM  → Live Monitoring
            ✓ WebSocket connects to Breeze
            ✓ Streams tick data for TOP 5 stocks
            ✓ Saves to CSV (TATSTE_20251116.csv, etc.)

3:30 PM  → Auto-stops at market close
            ✓ All tick data saved
            ✓ Ready for post-market analysis
```

---

## 🔒 Security Notes

- ✅ Never commit `config.py` with real credentials
- ✅ Use `.gitignore` to exclude sensitive files
- ✅ Session tokens expire daily - update before 9:15 AM
- ✅ Keep API keys secure

---

## 📞 Support

For issues or questions, check:
1. `config.py` - Credentials updated?
2. `watchlist_tokens.txt` - Exists and valid?
3. Breeze session token - Fresh (daily)?
4. Market hours - 9:15 AM - 3:30 PM?

---

## 📝 License

MIT License - Free to use and modify

---

**Happy Trading! 📊🚀**

