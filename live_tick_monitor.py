"""
MODULAR LIVE MULTI-STOCK TICK MONITOR
- Config + watchlist-driven
- Efficient batch CSV writing
- Minute-wise snapshot JSON in "snapshots/" folder
- Auto git publish of snapshot every 5 min
"""

from breeze_connect import BreezeConnect
import pandas as pd
from datetime import datetime, time
import time as time_module
import os
import json
import subprocess
import trading_config as config

# ===========================
# FILE/PATH SETUP
# ===========================
CSV_FILE = 'all_ticks_FUTURES.csv'
SNAPSHOT_DIR = "snapshots"
WATCHLIST_FILE = config.WATCHLIST_FILE
MAX_BUFFER_SIZE = 600
BATCH_WRITE_SIZE = 60
PRINT_FREQUENCY = 10
SNAPSHOT_INTERVAL = 60         # seconds (every minute)
GIT_INTERVAL = 300             # seconds (every 5 min)
MARKET_START = time(9, 15, 0)
MARKET_END = time(15, 30, 0)

os.makedirs(SNAPSHOT_DIR, exist_ok=True)

# ===========================
# LOAD WATCHLIST
# ===========================
def load_watchlist(fname):
    assert os.path.exists(fname), f"Watchlist not found: {fname}"
    token_symbol_list = []
    with open(fname, 'r') as f:
        for line in f:
            l = line.strip()
            if not l or l.startswith('#'): continue
            if ':' in l:
                token, symbol = l.split(':', 1)
                token_symbol_list.append((token.strip(), symbol.strip()))
    return token_symbol_list

TOKENS = load_watchlist(WATCHLIST_FILE)
token_to_symbol = {token: symbol for token, symbol in TOKENS}

# ===========================
# CSV MANAGEMENT
# ===========================
tick_data = []
pending_writes = []
csv_initialized = False
write_counter = 0
first_tick_received = False
processed_tick_count = 0
session_start_time = datetime.now()

def initialize_csv():
    global csv_initialized
    if not os.path.exists(CSV_FILE):
        columns = [
            'Symbol', 'exchange_timestamp', 'last_price', 'volume_traded', 'last_traded_quantity',
            'open_interest', 'change_in_oi',
            'bid_price_1', 'bid_qty_1', 'bid_price_2', 'bid_qty_2',
            'bid_price_3', 'bid_qty_3', 'bid_price_4', 'bid_qty_4',
            'bid_price_5', 'bid_qty_5',
            'ask_price_1', 'ask_qty_1', 'ask_price_2', 'ask_qty_2',
            'ask_price_3', 'ask_qty_3', 'ask_price_4', 'ask_qty_4',
            'ask_price_5', 'ask_qty_5',
            'total_buy_qty', 'total_sell_qty'
        ]
        pd.DataFrame(columns=columns).to_csv(CSV_FILE, index=False)
        print(f"✓ Created new CSV: {CSV_FILE}")
    else:
        print(f"✓ Using existing CSV: {CSV_FILE}")
    csv_initialized = True

def append_to_csv_batch(ticks_to_write):
    if len(ticks_to_write) == 0:
        return
    try:
        df = pd.DataFrame(ticks_to_write)
        df.to_csv(CSV_FILE, mode='a', header=False, index=False)
        if len(ticks_to_write) >= 50:
            print(f"   💾 Wrote {len(ticks_to_write)} ticks to CSV")
    except Exception as e:
        print(f"   ⚠️ CSV write error: {e}")

# ===========================
# HELPER FUNCTIONS
# ===========================
def safe_int(value, default=0):
    if value is None or value == '' or value == "": return default
    try: return int(float(value))
    except (ValueError, TypeError): return default

def safe_float(value, default=0.0):
    if value is None or value == '' or value == "": return default
    try: return float(value)
    except (ValueError, TypeError): return default

def safe_get_depth(data, key, index=0, default=0):
    value = data.get(key, default)
    if isinstance(value, list): return value[index] if len(value) > index else default
    if isinstance(value, (int, float)): return value if index==0 else default
    return default

# ===========================
# SNAPSHOT + GIT FUNCTIONS
# ===========================
def create_snapshot():
    snapshot_quotes = []
    current_time = datetime.now()
    buffer = tick_data[-MAX_BUFFER_SIZE:] if len(tick_data) > MAX_BUFFER_SIZE else tick_data[:]
    for tick in buffer:
        snapshot_tick = tick.copy()
        snapshot_quotes.append(snapshot_tick)
    snap_time = current_time.strftime('%Y%m%d_%H%M%S')
    snap_file = os.path.join(SNAPSHOT_DIR, f"fut_snapshot_{snap_time}.json")
    with open(snap_file, 'w') as f:
        json.dump(snapshot_quotes, f, indent=2, default=str)  # default=str to handle timestamps
    print(f"✓ Snapshot written: {snap_file}")
    return snap_file

def git_publish(filepath):
    try:
        subprocess.run(["git", "add", filepath], check=True)
        subprocess.run(["git", "commit", "-m", f"Auto-snapshot {os.path.basename(filepath)}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✓ Snapshot published on git")
    except Exception as e:
        print(f"   ⚠️ Git publish error: {e}")

# ===========================
# BREEZE API SETUP (ALL FROM CONFIG)
# ===========================
breeze = BreezeConnect(api_key=config.BREEZE_API_KEY)
print("Connecting to API...")
try:
    breeze.generate_session(api_secret=config.BREEZE_API_SECRET, session_token=config.BREEZE_SESSION_TOKEN)
    print("Session connected.")
except Exception as e:
    print(f"❌ Session Error: {e}")
    exit(1)

# ===========================
# TICK CALLBACK
# ===========================
def on_ticks(ticks):
    global tick_data, pending_writes, write_counter, processed_tick_count, first_tick_received
    if not csv_initialized:
        initialize_csv()
    if not first_tick_received and ticks:
        print(f"\n🔍 First tick received! {str(ticks)[:150]}")
        first_tick_received = True
    current_time = datetime.now()
    tick_list = ticks if isinstance(ticks, list) else [ticks]
    if processed_tick_count % PRINT_FREQUENCY == 0:
        runtime = (current_time - session_start_time).seconds
        print(f"📊 [{current_time.strftime('%H:%M:%S')}] "
              f"Processed: {processed_tick_count:,} | "
              f"Buffer: {len(tick_data)} | "
              f"Runtime: {runtime//60}m {runtime%60}s")
    for tick in tick_list:
        token = tick.get('symbol')
        symbol = token_to_symbol.get(token, "UNKNOWN")
        new_tick = {
            'Symbol': symbol,
            'exchange_timestamp': current_time,
            'last_price': safe_float(tick.get('last', tick.get('ltp', 0))),
            'volume_traded': safe_int(tick.get('ttq', tick.get('volume', 0))),
            'last_traded_quantity': safe_int(tick.get('ltq', 0)),
            'open_interest': safe_int(tick.get('OI', 0)),
            'change_in_oi': safe_int(tick.get('CHNGOI', 0)),
        }
        for i in range(5):
            new_tick[f'bid_price_{i+1}'] = safe_float(safe_get_depth(tick, 'bPrice', i, 0))
            new_tick[f'bid_qty_{i+1}'] = safe_int(safe_get_depth(tick, 'bQty', i, 0))
            new_tick[f'ask_price_{i+1}'] = safe_float(safe_get_depth(tick, 'sPrice', i, 0))
            new_tick[f'ask_qty_{i+1}'] = safe_int(safe_get_depth(tick, 'sQty', i, 0))
        new_tick['total_buy_qty'] = safe_int(tick.get('totalBuyQt', 0))
        new_tick['total_sell_qty'] = safe_int(tick.get('totalSellQ', 0))
        tick_data.append(new_tick)
        pending_writes.append(new_tick)
        processed_tick_count += 1
    write_counter += len(tick_list)
    if write_counter >= BATCH_WRITE_SIZE:
        append_to_csv_batch(pending_writes)
        pending_writes = []
        write_counter = 0
    if len(tick_data) > MAX_BUFFER_SIZE:
        removed = len(tick_data) - MAX_BUFFER_SIZE
        tick_data = tick_data[-MAX_BUFFER_SIZE:]
        print(f"   🧹 Memory buffer cleared ({removed} old ticks removed)")

def on_error(error):
    print(f"❌ WebSocket Error: {error}")

breeze.on_ticks = on_ticks
breeze.on_error = on_error

print("\n🔌 Connecting to websocket...")
max_retries = 3
retry_count = 0
connected = False
while retry_count < max_retries and not connected:
    try:
        if retry_count > 0:
            print(f"   ⏳ Retry {retry_count + 1}/{max_retries}...")
            time_module.sleep(5)
        breeze.ws_connect()
        print("✓ Websocket connected!")
        connected = True
    except Exception as e:
        retry_count += 1
        print(f"   ⚠️  Attempt {retry_count} failed: {str(e)[:100]}")
        if retry_count >= max_retries:
            print(f"\n❌ Failed after {max_retries} attempts.")
            exit(1)

print(f"\n📡 Subscribing to feeds...")
for token, symbol in TOKENS:
    breeze.subscribe_feeds(stock_token=token)
    print(f"✓ Subscribed: {symbol} ({token})")
    time_module.sleep(1)

print("\n" + "="*80)
print("🔴 LIVE STREAMING (MULTI-STOCK)")
print("="*80)
print(f"Tracking: {', '.join([symbol for token, symbol in TOKENS])}")
print(f"Market: {MARKET_START.strftime('%H:%M')} - {MARKET_END.strftime('%H:%M')}")
print(f"Press Ctrl+C to stop\n")

# ===========================
# MAIN LOOP + SNAPSHOT + GIT PUBLISH
# ===========================
last_snapshot_time = time_module.time()
last_git_time = time_module.time()
last_snapshot_file = None

try:
    while True:
        time_module.sleep(0.25)
        now_ts = time_module.time()
        # Snapshot every minute
        if now_ts - last_snapshot_time >= SNAPSHOT_INTERVAL:
            last_snapshot_file = create_snapshot()
            last_snapshot_time = now_ts
        # Git publish every 5 min
        if last_snapshot_file and (now_ts - last_git_time >= GIT_INTERVAL):
            git_publish(last_snapshot_file)
            last_git_time = now_ts
        # Market close check
        if datetime.now().time() >= MARKET_END:
            print("\nMarket closed. Auto-stopping...")
            break
except KeyboardInterrupt:
    print("⏹️ MANUAL STOP")

print("Disconnecting...")
breeze.ws_disconnect()
if len(pending_writes) > 0:
    append_to_csv_batch(pending_writes)
    print(f"✓ Wrote final {len(pending_writes)} ticks")
if last_snapshot_file:
    git_publish(last_snapshot_file)
print("🎉 Multi-stock collector script completed!")
