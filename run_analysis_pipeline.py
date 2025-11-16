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
            lines = f.readlines()
        
        # Find NSE Derivatives Snapshot section and update URL
        updated = False
        for i, line in enumerate(lines):
            # Look for NSE Derivatives Snapshot header
            if 'NSE Derivatives Snapshot' in line or 'NSE DERIVATIVES SNAPSHOT' in line.upper():
                # Check next few lines for URL or placeholder
                for j in range(i+1, min(i+5, len(lines))):
                    if '{' in lines[j] or 'URL will be' in lines[j]:
                        lines[j] = '{' + github_raw_url + '}\n'
                        updated = True
                        break
                if updated:
                    break
        
        if updated:
            # Write updated prompt
            with open(prompt_file, "w", encoding="utf-8") as f:
                f.writelines(lines)
            
            print(f"  ✓ Updated NSE snapshot URL")
            print(f"    URL: {github_raw_url}")
            return True
        else:
            print(f"  ⚠ Could not find NSE snapshot URL to update")
            return False
        
    except Exception as e:
        print(f"\n✗ Error updating analysis prompt: {e}")
        return False

def update_preopen_url_in_prompt(preopen_filename):
    """
    Update analysis_prompt.txt with latest pre-open data URL
    """
    try:
        github_raw_url = f"https://raw.githubusercontent.com/vwebbaker/nse-intraday-data/refs/heads/main/preopen/{preopen_filename}"
        
        prompt_file = "analysis_prompt.txt"
        
        if not os.path.exists(prompt_file):
            print(f"⚠ Analysis prompt file not found: {prompt_file}")
            return False
        
        # Read current prompt
        with open(prompt_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Find Pre-open Market Data section and update URL
        updated = False
        for i, line in enumerate(lines):
            # Look for Pre-open Market Data header
            if 'Pre-Open Market Data' in line or 'Pre-open Market Data' in line or 'PRE-OPEN' in line.upper():
                # Check next few lines for URL or placeholder
                for j in range(i+1, min(i+5, len(lines))):
                    if '{' in lines[j] or 'URL will be' in lines[j]:
                        lines[j] = '{' + github_raw_url + '}\n'
                        updated = True
                        break
                if updated:
                    break
        
        # If no URL found, add it after Global Market Data
        if not updated:
            for i, line in enumerate(lines):
                if 'Global Market Data:' in line:
                    # Find the next URL line
                    j = i + 1
                    while j < len(lines) and lines[j].strip().startswith('{'):
                        j += 1
                    
                    # Insert pre-open section
                    lines.insert(j, '\n')
                    lines.insert(j + 1, '### Pre-open Market Data (9:00-9:08 AM):\n')
                    lines.insert(j + 2, '{' + github_raw_url + '}\n')
                    updated = True
                    break
        
        if updated:
            # Write updated prompt
            with open(prompt_file, "w", encoding="utf-8") as f:
                f.writelines(lines)
            
            print(f"  ✓ Updated Pre-open URL")
            print(f"    URL: {github_raw_url}")
            return True
        else:
            print(f"  ⚠ Could not update pre-open URL")
            return False
        
    except Exception as e:
        print(f"\n✗ Error updating pre-open URL: {e}")
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
    
    # Step 2.5: Update NSE Snapshot URL in analysis_prompt.txt
    snapshots_dir = Path("snapshots")
    snapshot_files = sorted(snapshots_dir.glob("nse_snapshot_*.json"))
    if snapshot_files:
        latest_snapshot = snapshot_files[-1]
        snapshot_filename = latest_snapshot.name
        print(f"\n✓ Updating NSE snapshot URL: {snapshot_filename}")
        update_analysis_prompt_url(snapshot_filename)
    
    # Step 3: Run Global Indices Fetcher
    print("\n" + "="*70)
    print("🌍 FETCHING GLOBAL MARKET DATA")
    print("="*70 + "\n")
    
    if not run_script("global_indices_fetcher.py", "Fetch Global Indices & Publish"):
        print("⚠ Global indices fetch failed, but continuing...")
    
    # Step 4: Run Pre-open Market Fetcher (9:00-9:08 AM)
    print("\n" + "="*70)
    print("🕐 FETCHING PRE-OPEN MARKET DATA")
    print("="*70 + "\n")
    
    if not run_script("preopen_fetcher.py", "Fetch Pre-open Market Data"):
        print("⚠ Pre-open data fetch failed (may be outside 9:00-9:08 AM window)")
        print("  This is normal if running outside pre-open hours")
    
    # Step 4.5: Update Pre-open URL in analysis_prompt.txt
    preopen_dir = Path("preopen")
    preopen_files = sorted(preopen_dir.glob("preopen_*.json"))
    if preopen_files:
        latest_preopen = preopen_files[-1]
        preopen_filename = latest_preopen.name
        print(f"\n✓ Updating Pre-open URL: {preopen_filename}")
        update_preopen_url_in_prompt(preopen_filename)
    
    # Step 5: Find the latest snapshot files
    snapshots_dir = Path("snapshots")
    global_dir = Path("global")
    preopen_dir = Path("preopen")
    
    # Find the latest snapshot JSON files
    snapshot_files = sorted(snapshots_dir.glob("nse_snapshot_*.json"))
    global_files = sorted(global_dir.glob("global_indices_*.json"))
    preopen_files = sorted(preopen_dir.glob("preopen_*.json"))
    
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
    
    if preopen_files:
        latest_preopen = preopen_files[-1]
        preopen_filename = latest_preopen.name
        preopen_url = f"https://raw.githubusercontent.com/vwebbaker/nse-intraday-data/refs/heads/main/preopen/{preopen_filename}"
        
        print("🕐 Pre-open Market:")
        print(f"   File: {preopen_filename}")
        print(f"   URL: {preopen_url}\n")
    else:
        print("🕐 Pre-open Market:")
        print(f"   ⚠️  No data (run during 9:00-9:08 AM for live data)\n")
    
    print("="*70)
    print("📋 FILES UPDATED:")
    print("="*70)
    print("\n✓ analysis_prompt.txt - Updated with all market data URLs:")
    print("   • NSE Snapshot (derivatives, FII/DII data)")
    print("   • Global Indices (market sentiment)")
    print("   • Pre-open Data (gap up/down stocks)")
    print("✓ All data published to GitHub")
    print()
    
    print("="*70)
    print("💡 NEXT STEPS:")
    print("="*70)
    print("\n1. Check analysis_prompt.txt for complete market data")
    print("2. NSE + Global + Pre-open data are ready")
    print("3. Send all URLs to AI for comprehensive analysis!")
    print("\n⏰ Note: Pre-open data is most valuable when run at 9:00-9:08 AM IST\n")
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
