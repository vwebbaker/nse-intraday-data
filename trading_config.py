# config.py
"""
Breeze API Configuration
Update BREEZE_SESSION_TOKEN daily before market open (9:15 AM)
"""

# Breeze API Credentials
BREEZE_API_KEY = "i701185!389x2WqT26591~26t0h25V5C"
BREEZE_API_SECRET = "6395Hw+0c5j5449g339q63v19uhw16i8"
BREEZE_SESSION_TOKEN = "53721243"  #⚠️ UPDATE DAILY - Get from: https://api.icicidirect.com/apiuser/login?api_key=i701185!389x2WqT26591~26t0h25V5C

# GitHub Configuration
GITHUB_USERNAME = "vwebbaker"
GITHUB_REPO = "nse-intraday-data"
GITHUB_TOKEN = ""  # Optional for private repos (not needed for public)

# File Paths
WATCHLIST_FILE = "watchlist_tokens.txt"
SNAPSHOT_DIR = "snapshots"

# Monitoring Settings
UPDATE_INTERVAL_SECONDS = 60  # 1 minute
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 15
MARKET_CLOSE_HOUR = 15
MARKET_CLOSE_MINUTE = 30

# Exchange Settings
EXCHANGE_CODE = "NFO"  # NSE Futures & Options
PRODUCT_TYPE = "futures"
