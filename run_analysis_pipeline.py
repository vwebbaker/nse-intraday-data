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
    print("🎯 NSE INTRADAY ANALYSIS PIPELINE")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    print("="*70 + "\n")
    
    # Step 1: Download NSE Data
    if not run_script("nse_data_fetcher.py", "Download NSE Data"):
        print("⚠ Data download incomplete. Continue? (y/n)")
        if input().lower() != 'y':
            return
    
    # Step 2: Create Snapshot & Publish to Git
    if not run_script("snapshot_and_publish.py", "Create Snapshot & Publish"):
        print("✗ Pipeline failed at snapshot creation")
        return
    
    # Step 3: Read the latest snapshot URL
    url_file = Path("snapshots/latest_snapshot_url.txt")
    
    if url_file.exists():
        with open(url_file, 'r') as f:
            snapshot_url = f.read().strip()
        
        # Extract snapshot filename from URL
        snapshot_filename = snapshot_url.split('/')[-1]
        
        print("\n" + "="*70)
        print("✓ Published to GitHub!")
        print("="*70)
        
        # NEW CODE: Update analysis prompt automatically
        update_analysis_prompt_url(snapshot_filename)
        
        print("\n" + "="*70)
        print("📋 ANALYSIS PROMPT GENERATED")
        print("="*70 + "\n")
        
        # Generate prompt
        analysis_prompt = generate_analysis_prompt(snapshot_url)
        
        # Save to file
        prompt_file = Path("analysis_prompt_generated.txt")
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(analysis_prompt)
        
        print(f"✓ Prompt saved to: {prompt_file}\n")
        print("="*70)
        print("📎 SNAPSHOT URL:")
        print("="*70)
        print(f"\n{snapshot_url}\n")
        print("="*70)
        print("\n💡 NEXT STEPS:")
        print("="*70)
        print("\n1. Copy the prompt from: analysis_prompt_generated.txt")
        print("2. Send it to assistant (ChatGPT/Claude/etc.)")
        print("3. Get your TOP 5 intraday stock recommendations!\n")
        print("="*70 + "\n")
        
    else:
        # Verify Git push by checking git status
        result = subprocess.run(
            ["git", "status", "--porcelain"], 
            capture_output=True, 
            text=True
        )
        if result.stdout.strip() == "":
            print("\n✓ All changes pushed to GitHub successfully\n")
        else:
            print("\n⚠ Uncommitted changes remain:")
            print(result.stdout)
            print()

if __name__ == "__main__":
    main()
