# run_daily_analysis.py - Master orchestrator

import subprocess
import sys
from pathlib import Path
from datetime import datetime

def run_script(script_name):
    """Run a Python script"""
    print(f"\n{'='*70}")
    print(f"Running: {script_name}")
    print('='*70)
    
    result = subprocess.run([sys.executable, script_name], capture_output=False)
    return result.returncode == 0

def main():
    print("\n🚀 NSE Intraday Analysis Pipeline")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    print("="*70 + "\n")
    
    # Step 1: Download NSE data
    print("STEP 1: Downloading NSE Data...")
    if not run_script("nse_data_fetcher.py"):
        print("⚠️  Warning: Data fetch had issues, but continuing...")
        # Don't exit, some files might have downloaded
    
    # Step 2: Create snapshot and publish
    print("\n\nSTEP 2: Creating Snapshot & Publishing...")
    if not run_script("snapshot_and_publish.py"):
        print("❌ Snapshot/Publish failed!")
        return False
    
    print("\n\n" + "="*70)
    print("✅ PIPELINE COMPLETE!")
    print("="*70)
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    print("="*70 + "\n")
    
    # Show latest snapshot URL
    url_file = Path("snapshots") / "latest_snapshot_url.txt"
    if url_file.exists():
        with open(url_file, 'r') as f:
            url = f.read().strip()
            print("📎 Latest Snapshot URL:")
            print(url)
            print("\n💡 Send this URL to AI assistant for analysis!\n")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
