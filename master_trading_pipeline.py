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
    print("  • NSE derivatives data (FII/DII positions)")
    print("  • Global market indices (sentiment)")
    print("  • Pre-open market data (gap up/down stocks)")
    print()
    
    if not run_script("run_analysis_pipeline.py", "Data Collection Pipeline"):
        return
    
    # Verify data files
    print("\n📋 Verifying generated data files...")
    print("-" * 80)
    
    required_files = [
        ("analysis_prompt.txt", "Analysis prompt"),
    ]
    
    all_exist = True
    for filepath, desc in required_files:
        if not check_file_exists(filepath, desc):
            all_exist = False
    
    if not all_exist:
        print("\n❌ Required files missing. Cannot proceed.")
        return
    
    # ================================================================
    # PHASE 2: AI ANALYSIS & RECOMMENDATION
    # ================================================================
    
    print_header("🤖 PHASE 2: AI ANALYSIS & STOCK SELECTION")
    
    print("This phase:")
    print("  • Sends data to AI assistant (Perplexity)")
    print("  • Gets TOP 5 stock recommendations")
    print("  • Extracts symbols and generates futures tokens")
    print("  • Creates watchlist for live monitoring")
    print()
    
    input("⏸️  Press ENTER when ready to proceed with AI analysis...")
    
    if not run_script("assistant_handler.py", "AI Analysis & Token Generation"):
        return
    
    # Verify watchlist
    print("\n📋 Verifying watchlist...")
    print("-" * 80)
    
    if not check_file_exists("watchlist_tokens.txt", "Watchlist tokens"):
        print("\n❌ Watchlist not generated. Cannot proceed to monitoring.")
        return
    
    # Display watchlist
    with open("watchlist_tokens.txt", 'r') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        print(f"\n✓ Watchlist contains {len(lines)} stocks")
        print("\nStocks to monitor:")
        for line in lines:
            if ':' in line:
                token, symbol = line.split(':', 1)
                print(f"   • {symbol} (Token: {token})")
    
    # ================================================================
    # PHASE 3: LIVE MARKET MONITORING (9:15 AM onwards)
    # ================================================================
    
    print_header("📡 PHASE 3: LIVE MARKET MONITORING")
    
    print("This phase:")
    print("  • Connects to Breeze API WebSocket")
    print("  • Streams real-time tick-by-tick data")
    print("  • Monitors TOP 5 stocks from AI recommendations")
    print("  • Saves tick data for analysis")
    print()
    
    # Check Breeze credentials
    print("📋 Checking Breeze API configuration...")
    print("-" * 80)
    
    try:
        import trading_config as config
        if config.BREEZE_SESSION_TOKEN == "update_daily_before_market" or config.BREEZE_SESSION_TOKEN == "53684931":
            print("\n⚠️  WARNING: Update BREEZE_SESSION_TOKEN in config.py!")
            print("   Get fresh session token from ICICI Breeze before 9:15 AM")
            print()
            
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                print("\n⏸️  Pipeline paused. Update config.py and run again.")
                return
        else:
            print("✓ Breeze credentials configured")
    except Exception as e:
        print(f"⚠️  Could not verify config: {e}")
    
    print()
    input("⏸️  Press ENTER when ready to start live monitoring...")
    
    print("\n🔴 Starting live tick monitor...")
    print("   (Press Ctrl+C to stop monitoring)")
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
        "analysis_prompt.txt",
        "watchlist_tokens.txt",
        "recommendations/recommendations_*.txt",
        "tick_data/*.csv",
        "snapshots/latest_snapshot.json"
    ]
    
    for pattern in files_to_check:
        if '*' in pattern:
            folder = Path(pattern.split('/')[0])
            if folder.exists():
                files = list(folder.glob(pattern.split('/')[-1]))
                if files:
                    latest = sorted(files)[-1]
                    print(f"   ✓ {latest}")
        else:
            if Path(pattern).exists():
                print(f"   ✓ {pattern}")
    
    print()
    print("="*80)
    print("Happy Trading! 📈")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Pipeline interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()

