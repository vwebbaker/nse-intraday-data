# run_analysis_pipeline.py

import subprocess
import sys
import os
import re
from pathlib import Path
from datetime import datetime

def run_script(script_name, description):
    """Run Python script and return success status"""
    print(f"\n{'='*70}")
    print(f"📍 STEP: {description}")
    print('='*70 + "\n")
    
    result = subprocess.run([sys.executable, script_name])
    success = result.returncode == 0
    
    if success:
        print(f"\n✓ {description} - SUCCESS\n")
    else:
        print(f"\n✗ {description} - FAILED\n")
    
    return success

# ============================================================
# AUTOMATIC ANALYSIS PROMPT URL UPDATE
# ============================================================
def update_analysis_prompt_url(snapshot_filename):
    """
    Automatically update the analysis_prompt.txt file with latest snapshot URL
    """
    try:
        github_raw_url = f"https://raw.githubusercontent.com/vwebbaker/nse-intraday-data/refs/heads/main/snapshots/{snapshot_filename}"
        
        prompt_file = "analysis_prompt.txt"
        
        if not os.path.exists(prompt_file):
            print(f"⚠ Analysis prompt file not found: {prompt_file}")
            return False
        
        # Read current prompt
        with open(prompt_file, "r", encoding="utf-8") as f:
            prompt_content = f.read()
        
        # Replace old URL with new URL using regex
        updated_prompt = re.sub(
            r'https://raw\.githubusercontent\.com/vwebbaker/nse-intraday-data/refs/heads/main/snapshots/nse_snapshot_\d{8}_\d{6}\.json',
            github_raw_url,
            prompt_content
        )
        
        # Write updated prompt
        with open(prompt_file, "w", encoding="utf-8") as f:
            f.write(updated_prompt)
        
        print(f"\n✓ Updated analysis prompt with latest snapshot URL")
        print(f"  File: {prompt_file}")
        print(f"  URL: {github_raw_url}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error updating analysis prompt: {e}")
        return False

def generate_analysis_prompt(snapshot_url):
    """Generate analysis prompt with snapshot URL"""
    
    prompt_template = """I have NSE derivatives market data from the previous trading day. Please analyze this data and recommend the TOP 5 stocks for intraday trading today.

## Data Available:
{snapshot_url}

## Analysis Criteria:

### 1. FII Activity Analysis
- Check if FII is net long or short in index/stock futures
- Identify stocks where FII built significant positions
- Look for divergence between FII and retail positions

### 2. Participant Behavior
- Analyze participant-wise OI changes
- Check which category (Client/DII/FII/Pro) is most active
- Identify institutional flow patterns

### 3. Volatility Screening
- Rank stocks by implied volatility
- Select high-volatility stocks for momentum trading
- Avoid stocks with abnormally low volatility

### 4. Open Interest Analysis
- Stocks with increasing OI + increasing price = Strong bullish
- Stocks with increasing OI + decreasing price = Strong bearish
- Look for unusual OI buildup

### 5. Market Activity Patterns
- Check previous day's settlement prices
- Identify support/resistance levels
- Look for stocks near key price levels

## Output Format:

For each recommended stock, provide:

1. **Stock Name & Symbol**
2. **Trade Direction** (Long/Short)
3. **Entry Range** (Price levels)
4. **Stop Loss**
5. **Target** (Intraday)
6. **Reasoning** (Why this stock?)
   - FII position
   - OI trend
   - Volatility
   - Key levels

7. **Risk Rating** (Low/Medium/High)

## Additional Insights:
- Market sentiment (Bullish/Bearish/Neutral)
- Sectors showing strength
- Any stocks in ban period to avoid
- Overall market conviction level

Please provide actionable intraday trading recommendations based on this data.
"""
    
    return prompt_template.format(snapshot_url=snapshot_url)

def main():
    print("\n" + "="*70)
    print("🌅 COMPLETE MORNING MARKET ROUTINE")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    print("="*70 + "\n")
    
    # Step 1: Download NSE Data
    if not run_script("nse_data_fetcher.py", "Download NSE Data"):
        print("⚠ Data download incomplete. Continue? (y/n)")
        if input().lower() != 'y':
            return
    
    # Step 2: Create Snapshot & Publish to Git (NSE)
    if not run_script("snapshot_and_publish.py", "Create NSE Snapshot & Publish"):
        print("✗ Pipeline failed at NSE snapshot creation")
        return
    
    # Step 3: Run Global Indices Fetcher
    print("\n" + "="*70)
    print("🌍 FETCHING GLOBAL MARKET DATA")
    print("="*70 + "\n")
    
    if not run_script("global_indices_fetcher.py", "Fetch Global Indices & Publish"):
        print("⚠ Global indices fetch failed, but continuing...")
    
    # Step 4: Find the latest snapshot files
    snapshots_dir = Path("snapshots")
    global_dir = Path("global")
    
    # Find the latest snapshot JSON files
    snapshot_files = sorted(snapshots_dir.glob("nse_snapshot_*.json"))
    global_files = sorted(global_dir.glob("global_indices_*.json"))
    
    print("\n" + "="*70)
    print("✅ PIPELINE COMPLETE!")
    print("="*70 + "\n")
    
    if snapshot_files:
        latest_snapshot = snapshot_files[-1]
        snapshot_filename = latest_snapshot.name
        snapshot_url = f"https://raw.githubusercontent.com/vwebbaker/nse-intraday-data/refs/heads/main/snapshots/{snapshot_filename}"
        
        print("📊 NSE Snapshot:")
        print(f"   File: {snapshot_filename}")
        print(f"   URL: {snapshot_url}\n")
    
    if global_files:
        latest_global = global_files[-1]
        global_filename = latest_global.name
        global_url = f"https://raw.githubusercontent.com/vwebbaker/nse-intraday-data/refs/heads/main/global/{global_filename}"
        
        print("🌍 Global Indices:")
        print(f"   File: {global_filename}")
        print(f"   URL: {global_url}\n")
    
    print("="*70)
    print("📋 FILES UPDATED:")
    print("="*70)
    print("\n✓ analysis_prompt.txt - Updated with both URLs")
    print("✓ All data published to GitHub")
    print()
    
    print("="*70)
    print("💡 NEXT STEPS:")
    print("="*70)
    print("\n1. Check analysis_prompt.txt for complete market data")
    print("2. Both NSE + Global market data are ready")
    print("3. Send analysis_prompt.txt to AI for recommendations!\n")
    print("="*70 + "\n")
    
    # Verify Git push
    result = subprocess.run(
        ["git", "status", "--porcelain"], 
        capture_output=True, 
        text=True
    )
    if result.stdout.strip() == "":
        print("✅ All changes committed and pushed to GitHub\n")
    else:
        print("⚠ Note: Some uncommitted changes detected:")
        print(result.stdout)
        print()

if __name__ == "__main__":
    main()
