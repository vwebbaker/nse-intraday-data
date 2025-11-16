# live_tick_monitor.py
"""
OPTIMIZED MULTI-STOCK FUTURES TICK MONITOR
- Batch processing (no lag)
- Memory efficient
- Incremental CSV writes
- Multi-stock support from watchlist
"""

from breeze_connect import BreezeConnect
import pandas as pd
from datetime import datetime, time
import time as time_module
import os
import json
from pathlib import Path
import trading_config as config


# ============================================================================
# PERFORMANCE TUNING
# ============================================================================
MAX_BUFFER_SIZE = 600          # Last 10 min per stock
BATCH_WRITE_SIZE = 60          # Write every 60 ticks (~1 min)
PRINT_FREQUENCY = 10           # Status update every 10 ticks
SNAPSHOT_INTERVAL = 60         # Snapshot every 60 seconds

# Market hours
MARKET_START = time(9, 15, 0)
MARKET_END = time(15, 30, 0)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def safe_int(value, default=0):
    """Safely convert to int"""
    if value is None or value == '' or value == "":
        return default
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default


def safe_float(value, default=0.0):
    """Safely convert to float"""
    if value is None or value == '' or value == "":
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_get_depth(data, key, index=0, default=0):
    """Safely extract depth data"""
    value = data.get(key, default)
    if isinstance(value, list):
        return value[index] if len(value) > index else default
    elif isinstance(value, (int, float)):
        return value if index == 0 else default
    return default


# ============================================================================
# MULTI-STOCK TICK MONITOR
# ============================================================================
class OptimizedTickMonitor:
    def __init__(self):
        """Initialize monitor with Breeze API"""
        print("=" * 80)
        print("🚀 OPTIMIZED MULTI-STOCK FUTURES TICK MONITOR")
        print("=" * 80)
        
        self.session_start = datetime.now()
        print(f"Started: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Data structures (per stock)
        self.tick_buffers = {}      # {token: [recent_ticks]}
        self.pending_writes = {}    # {token: [ticks_to_write]}
        self.write_counters = {}    # {token: count}
        self.total_ticks = {}       # {token: total_count}
        self.csv_files = {}         # {token: filepath}
        self.stock_info = {}        # {token: symbol_name}
        
        # Global counters
        self.total_processed = 0
        self.last_snapshot_time = time_module.time()
        
        # Directories
        Path(config.SNAPSHOT_DIR).mkdir(exist_ok=True)
        Path("tick_data").mkdir(exist_ok=True)
        
        # Initialize Breeze
        self.breeze = BreezeConnect(api_key=config.BREEZE_API_KEY)
        self._authenticate()
        
        # Load watchlist
        self.watchlist = self._load_watchlist()
        
        # Initialize data structures for each stock
        self._initialize_stocks()
    
    def _authenticate(self):
        """Authenticate with Breeze API"""
        print("🔐 Authenticating with Breeze API...")
        
        if config.BREEZE_SESSION_TOKEN == "update_daily_before_market":
            raise ValueError("⚠️ Update SESSION_TOKEN in config.py!")
        
        try:
            self.breeze.generate_session(
                api_secret=config.BREEZE_API_SECRET,
                session_token=config.BREEZE_SESSION_TOKEN
            )
            print("✅ Authenticated successfully!\n")
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            raise
    
    def _load_watchlist(self):
        """Load watchlist tokens"""
        print(f"📂 Loading watchlist from {config.WATCHLIST_FILE}...")
        
        if not os.path.exists(config.WATCHLIST_FILE):
            raise FileNotFoundError(f"Watchlist not found: {config.WATCHLIST_FILE}")
        
        watchlist = []
        with open(config.WATCHLIST_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and ':' in line:
                    token, symbol = line.split(':', 1)
                    watchlist.append({
                        'token': token.strip(),
                        'symbol': symbol.strip()
                    })
        
        print(f"✅ Loaded {len(watchlist)} stocks:")
        for stock in watchlist:
            print(f"   • {stock['symbol']} (Token: {stock['token']})")
        print()
        
        return watchlist
    
    def _initialize_stocks(self):
        """Initialize data structures for each stock"""
        for stock in self.watchlist:
            token = stock['token']
            symbol = stock['symbol']
            
            self.tick_buffers[token] = []
            self.pending_writes[token] = []
            self.write_counters[token] = 0
            self.total_ticks[token] = 0
            self.stock_info[token] = symbol
            
            # Create CSV file
            csv_file = f"tick_data/{symbol}_{datetime.now().strftime('%Y%m%d')}.csv"
            self.csv_files[token] = csv_file
            
            if not os.path.exists(csv_file):
                columns = [
                    'timestamp', 'ltp', 'volume', 'ltq', 'oi', 'change_oi',
                    'bid1', 'bid_qty1', 'bid2', 'bid_qty2', 'bid3', 'bid_qty3',
                    'bid4', 'bid_qty4', 'bid5', 'bid_qty5',
                    'ask1', 'ask_qty1', 'ask2', 'ask_qty2', 'ask3', 'ask_qty3',
                    'ask4', 'ask_qty4', 'ask5', 'ask_qty5',
                    'total_buy_qty', 'total_sell_qty'
                ]
                pd.DataFrame(columns=columns).to_csv(csv_file, index=False)
                print(f"   ✓ Created CSV: {csv_file}")
    
    def _append_to_csv_batch(self, token, ticks_to_write):
        """Batch write to CSV (incremental)"""
        if len(ticks_to_write) == 0:
            return
        
        try:
            df = pd.DataFrame(ticks_to_write)
            csv_file = self.csv_files[token]
            
            # Append mode - super fast
            df.to_csv(csv_file, mode='a', header=False, index=False)
            
        except Exception as e:
            symbol = self.stock_info[token]
            print(f"   ⚠️ CSV write error ({symbol}): {e}")
    
    def _on_ticks(self, ticks):
        """WebSocket callback for tick data"""
        current_time = datetime.now()
        
        # Convert to list
        if isinstance(ticks, dict):
            tick_list = [ticks]
        elif isinstance(ticks, list):
            tick_list = ticks
        else:
            return
        
        # Process each tick
        for tick in tick_list:
            # Identify token
            token = str(tick.get('token', ''))
            
            if token not in self.tick_buffers:
                continue  # Skip unknown tokens
            
            # Parse tick data
            new_tick = {
                'timestamp': current_time.isoformat(),
                'ltp': safe_float(tick.get('last', tick.get('ltp', 0))),
                'volume': safe_int(tick.get('ttq', tick.get('volume', 0))),
                'ltq': safe_int(tick.get('ltq', 0)),
                'oi': safe_int(tick.get('OI', 0)),
                'change_oi': safe_int(tick.get('CHNGOI', 0)),
            }
            
            # Bid/Ask depth (5 levels)
            for i in range(5):
                new_tick[f'bid{i+1}'] = safe_float(safe_get_depth(tick, 'bPrice', i, 0))
                new_tick[f'bid_qty{i+1}'] = safe_int(safe_get_depth(tick, 'bQty', i, 0))
                new_tick[f'ask{i+1}'] = safe_float(safe_get_depth(tick, 'sPrice', i, 0))
                new_tick[f'ask_qty{i+1}'] = safe_int(safe_get_depth(tick, 'sQty', i, 0))
            
            new_tick['total_buy_qty'] = safe_int(tick.get('totalBuyQt', 0))
            new_tick['total_sell_qty'] = safe_int(tick.get('totalSellQ', 0))
            
            # Add to buffers
            self.tick_buffers[token].append(new_tick)
            self.pending_writes[token].append(new_tick)
            self.write_counters[token] += 1
            self.total_ticks[token] += 1
            self.total_processed += 1
            
            # === BATCH WRITE ===
            if self.write_counters[token] >= BATCH_WRITE_SIZE:
                self._append_to_csv_batch(token, self.pending_writes[token])
                self.pending_writes[token] = []
                self.write_counters[token] = 0
            
            # === MEMORY ROTATION ===
            if len(self.tick_buffers[token]) > MAX_BUFFER_SIZE:
                self.tick_buffers[token] = self.tick_buffers[token][-MAX_BUFFER_SIZE:]
        
        # === STATUS PRINT (reduced frequency) ===
        if self.total_processed % PRINT_FREQUENCY == 0:
            runtime = (current_time - self.session_start).seconds
            print(f"📊 [{current_time.strftime('%H:%M:%S')}] "
                  f"Total: {self.total_processed:,} | "
                  f"Runtime: {runtime//60}m {runtime%60}s")
        
        # === SNAPSHOT GENERATION ===
        if time_module.time() - self.last_snapshot_time >= SNAPSHOT_INTERVAL:
            self._create_snapshot()
            self.last_snapshot_time = time_module.time()
    
    def _create_snapshot(self):
        """Create current market snapshot"""
        snapshot_quotes = []
        
        for token, buffer in self.tick_buffers.items():
            if len(buffer) == 0:
                continue
            
            latest_tick = buffer[-1]
            symbol = self.stock_info[token]
            
            quote = {
                'symbol': symbol,
                'token': token,
                'ltp': latest_tick['ltp'],
                'volume': latest_tick['volume'],
                'oi': latest_tick['oi'],
                'change_oi': latest_tick['change_oi'],
                'bid': latest_tick['bid1'],
                'ask': latest_tick['ask1'],
                'spread': latest_tick['ask1'] - latest_tick['bid1'],
                'timestamp': latest_tick['timestamp']
            }
            
            snapshot_quotes.append(quote)
        
        if snapshot_quotes:
            snapshot = {
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'total_stocks': len(snapshot_quotes)
                },
                'quotes': snapshot_quotes
            }
            
            # Save snapshot
            filename = f"live_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(config.SNAPSHOT_DIR, filename)
            
            with open(filepath, 'w') as f:
                json.dump(snapshot, f, indent=2)
            
            # Save as latest
            latest_path = os.path.join(config.SNAPSHOT_DIR, "latest_snapshot.json")
            with open(latest_path, 'w') as f:
                json.dump(snapshot, f, indent=2)
            
            print(f"   💾 Snapshot saved: {filename}")
    
    def _on_error(self, error):
        """WebSocket error callback"""
        print(f"❌ WebSocket Error: {error}")
    
    def run(self):
        """Main monitoring loop"""
        # Set callbacks
        self.breeze.on_ticks = self._on_ticks
        self.breeze.on_error = self._on_error
        
        # Connect WebSocket
        print("🔌 Connecting to WebSocket...")
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if retry_count > 0:
                    print(f"   ⏳ Retry {retry_count + 1}/{max_retries}...")
                    time_module.sleep(5)
                
                self.breeze.ws_connect()
                print("✅ WebSocket connected!\n")
                break
                
            except Exception as e:
                retry_count += 1
                print(f"   ⚠️ Attempt {retry_count} failed: {str(e)[:100]}")
                
                if retry_count >= max_retries:
                    print(f"\n❌ Failed after {max_retries} attempts.")
                    raise
        
        # Subscribe to all stocks
        print(f"📡 Subscribing to {len(self.watchlist)} stocks...")
        for stock in self.watchlist:
            try:
                # Breeze format: "exchange_code!token"
                stock_token = f"{config.EXCHANGE_CODE}!{stock['token']}"
                self.breeze.subscribe_feeds(stock_token=stock_token)
                print(f"   ✓ {stock['symbol']}")
                time_module.sleep(0.1)  # Small delay between subscriptions
            except Exception as e:
                print(f"   ✗ {stock['symbol']}: {e}")
        
        print("\n" + "=" * 80)
        print("🔴 LIVE STREAMING (OPTIMIZED)")
        print("=" * 80)
        print(f"Market: {MARKET_START.strftime('%H:%M')} - {MARKET_END.strftime('%H:%M')}")
        print(f"Stocks: {len(self.watchlist)}")
        print(f"Press Ctrl+C to stop\n")
        
        # Main loop
        try:
            while True:
                time_module.sleep(0.1)  # Prevent CPU spike
                
                # Auto-stop at market close
                current_time = datetime.now().time()
                if current_time >= MARKET_END:
                    print(f"\n⏰ Market closed at {MARKET_END.strftime('%H:%M')}. Stopping...")
                    break
                    
        except KeyboardInterrupt:
            print("\n\n⏹️  Monitoring stopped by user")
        except Exception as e:
            print(f"\n\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Final CSV writes
            print("\n\n📊 Final data write...")
            for token, pending in self.pending_writes.items():
                if pending:
                    self._append_to_csv_batch(token, pending)
                    symbol = self.stock_info[token]
                    print(f"   ✓ {symbol}: {len(pending)} ticks written")
            
            print(f"\n✅ Monitoring session complete")
            print(f"   Total ticks: {self.total_processed:,}")
            duration = (datetime.now() - self.session_start).seconds
            print(f"   Duration: {duration//3600}h {(duration%3600)//60}m {duration%60}s")


if __name__ == "__main__":
    monitor = OptimizedTickMonitor()
    monitor.run()
