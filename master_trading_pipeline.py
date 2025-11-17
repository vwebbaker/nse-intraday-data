#!/usr/bin/env python3
"""
COMPLETE AUTOMATED TRADING PIPELINE
====================================
Runs entire workflow from data collection to live monitoring

PHASES:
1. Pre-market: Data collection (9:00-9:08 AM)
2. AI Analysis: Get stock recommendations
3. Live Monitoring: Real-time tick data (9:15 AM onwards)
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path
import time

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def run_script(script_name, description, critical=True):
    """Run a Python script and handle errors"""
    print(f"📍 {description}...")
    print("-" * 80)
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"❌ {description} - FAILED")
            if critical:
                print(f"\n⚠️  Critical step failed. Exiting pipeline.")
                return False
            return True
            
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        if critical:
            return False
        return True


def check_file_exists(filepath, description):
    """Check if required file exists"""
    if Path(filepath).exists():
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description} not found: {filepath}")
        return False


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():
    """Execute complete trading pipeline"""
    
    start_time = datetime.now()
    
    print_header("🚀 MASTER TRADING PIPELINE - AUTOMATED WORKFLOW")
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S IST')}\n")
    
    # ================================================================
    # PHASE 1: PRE-MARKET DATA COLLECTION (9:00-9:08 AM)
    # ================================================================
    
    print_header("📊 PHASE 1: PRE-MARKET DATA COLLECTION")
    
    print("This phase collects:")
    print("  • NSE EOD derivatives data (Previous day positions)")
    print("  • NSE F&O participant-wise data (FII/DII/Client)")
    print("  • Global market indices (Overnight sentiment)")
    print("  • Pre-open market data (Gap up/down stocks)")
    print("  • Updates analysis_prompt.txt with fresh URLs")
    print("  • Publishes all data to GitHub")
    print()
    
    # Run the master data fetcher (your updated script)
    if not run_script("preopen_fetcher.py", "Complete Data Collection Pipeline"):
        return
    
    # Verify data files
    print("\n📋 Verifying generated data files...")
    print("-" * 80)
    
    required_files = [
        ("analysis_prompt.txt", "Analysis prompt with updated URLs"),
    ]
    
    all_exist = True
    for filepath, desc in required_files:
        if not check_file_exists(filepath, desc):
            all_exist = False
    
    if not all_exist:
        print("\n❌ Required files missing. Cannot proceed.")
        return
    
    # Display what was collected
    print("\n📦 Data Collection Summary:")
    print("-" * 80)
    
    # Check for latest snapshots
    snapshot_folders = ['snapshots', 'global', 'preopen', 'data']
    for folder in snapshot_folders:
        folder_path = Path(folder)
        if folder_path.exists():
            files = sorted(folder_path.glob('*.*'), key=lambda x: x.stat().st_mtime, reverse=True)
            if files:
                latest = files[0]
                size = latest.stat().st_size / 1024  # KB
                print(f"   ✓ {folder:15} → {latest.name} ({size:.1f} KB)")
    
    # ================================================================
    # PHASE 2: AI ANALYSIS & RECOMMENDATION
    # ================================================================
    
    print_header("🤖 PHASE 2: AI ANALYSIS & STOCK SELECTION")
    
    print("This phase:")
    print("  • Sends analysis_prompt.txt to AI assistant (Perplexity)")
    print("  • AI analyzes: NSE derivatives + Global indices + Pre-open data")
    print("  • Gets TOP 3-5 FUTURES recommendations with reasoning")
    print("  • Extracts stock symbols from AI response")
    print("  • Generates Breeze API tokens for futures contracts")
    print("  • Creates watchlist for live monitoring")
    print()
    
    print("⚠️  MANUAL STEP REQUIRED:")
    print("   1. Open analysis_prompt.txt (updated with fresh URLs)")
    print("   2. Share it with AI assistant (Perplexity/ChatGPT)")
    print("   3. Save AI recommendations to recommendations/ folder")
    print()
    
    input("⏸️  Press ENTER when AI analysis is complete...")
    
    if not run_script("assistant_handler.py", "Extract Symbols & Generate Tokens"):
        print("\n⚠️  Token generation failed, but you can continue manually")
        print("   Create watchlist_tokens.txt with format: TOKEN:SYMBOL")
        input("\n⏸️  Press ENTER when watchlist is ready...")
    
    # Verify watchlist
    print("\n📋 Verifying watchlist...")
    print("-" * 80)
    
    if not check_file_exists("watchlist_tokens.txt", "Watchlist tokens"):
        print("\n❌ Watchlist not generated. Cannot proceed to monitoring.")
        print("\nCreate watchlist_tokens.txt manually with format:")
        print("   4.1!38447:TATASTEEL")
        print("   4.1!38505:RELIANCE")
        return
    
    # Display watchlist
    with open("watchlist_tokens.txt", 'r') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        print(f"\n✓ Watchlist contains {len(lines)} stocks")
        print("\n📋 Stocks to monitor:")
        for line in lines:
            if ':' in line:
                token, symbol = line.split(':', 1)
                print(f"   • {symbol:20} (Token: {token})")
    
    # ================================================================
    # PHASE 3: LIVE MARKET MONITORING (9:15 AM onwards)
    # ================================================================
    
    print_header("📡 PHASE 3: LIVE MARKET MONITORING")
    
    print("This phase:")
    print("  • Connects to Breeze API WebSocket")
    print("  • Streams real-time tick-by-tick data")
    print("  • Monitors TOP 3-5 FUTURES from AI recommendations")
    print("  • Saves tick data to CSV for analysis")
    print("  • Creates periodic snapshots")
    print()
    
    # Check Breeze credentials
    print("📋 Checking Breeze API configuration...")
    print("-" * 80)
    
    try:
        import trading_config as config
        if config.BREEZE_SESSION_TOKEN == "update_daily_before_market" or config.BREEZE_SESSION_TOKEN == "53684931":
            print("\n⚠️  WARNING: Update BREEZE_SESSION_TOKEN in trading_config.py!")
            print("   Get fresh session token from ICICI Breeze before 9:15 AM")
            print()
            
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                print("\n⏸️  Pipeline paused. Update trading_config.py and run again.")
                return
        else:
            print("✓ Breeze credentials configured")
            print(f"   API Key: {config.BREEZE_API_KEY[:10]}...")
            print(f"   Session: {config.BREEZE_SESSION_TOKEN[:10]}...")
    except ImportError:
        print("⚠️  trading_config.py not found")
        print("   Create it with your Breeze credentials")
    except Exception as e:
        print(f"⚠️  Could not verify config: {e}")
    
    print()
    
    # Check current time
    now = datetime.now()
    market_open = now.replace(hour=9, minute=15, second=0)
    
    if now < market_open:
        wait_seconds = (market_open - now).seconds
        wait_minutes = wait_seconds // 60
        print(f"⏰ Market opens in {wait_minutes} minutes")
        print(f"   Current time: {now.strftime('%H:%M:%S')}")
        print(f"   Market open: {market_open.strftime('%H:%M:%S')}")
        print()
        
        response = input("Wait until market opens? (y/n): ")
        if response.lower() == 'y':
            print(f"\n⏳ Waiting {wait_minutes} minutes until market open...")
            time.sleep(wait_seconds)
    
    input("⏸️  Press ENTER when ready to start live monitoring...")
    
    print("\n🔴 Starting live tick monitor...")
    print("   Monitoring stocks from AI recommendations")
    print("   Press Ctrl+C to stop monitoring")
    print()
    
    # Run live monitor (blocking)
    try:
        subprocess.run([sys.executable, "live_tick_monitor.py"])
    except KeyboardInterrupt:
        print("\n\n⏹️  Live monitoring stopped by user")
    
    # ================================================================
    # PIPELINE COMPLETE
    # ================================================================
    
    end_time = datetime.now()
    duration = (end_time - start_time).seconds
    
    print_header("✅ PIPELINE COMPLETE")
    
    print(f"Started:  {start_time.strftime('%H:%M:%S')}")
    print(f"Ended:    {end_time.strftime('%H:%M:%S')}")
    print(f"Duration: {duration // 60}m {duration % 60}s")
    print()
    
    print("📊 Generated Files:")
    print("-" * 80)
    
    # List generated files
    files_to_check = [
        ("analysis_prompt.txt", "Analysis prompt"),
        ("watchlist_tokens.txt", "Watchlist"),
        ("recommendations", "AI recommendations folder"),
        ("tick_data", "Live tick data folder"),
        ("snapshots", "Market snapshots folder"),
        ("global", "Global indices folder"),
        ("preopen", "Pre-open data folder"),
        ("data", "Raw data folder"),
    ]
    
    for filepath, desc in files_to_check:
        path = Path(filepath)
        if path.exists():
            if path.is_dir():
                files = list(path.glob('*'))
                print(f"   ✓ {desc:30} ({len(files)} files)")
            else:
                size = path.stat().st_size / 1024
                print(f"   ✓ {desc:30} ({size:.1f} KB)")
    
    print()
    print("="*80)
    print("📈 Happy Trading!")
    print("="*80 + "\n")
    
    print("💡 Next Steps:")
    print("   • Review tick_data/ for market movements")
    print("   • Analyze AI recommendations vs. actual performance")
    print("   • Update strategies based on results")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Pipeline interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
