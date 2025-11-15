# run_analysis_pipeline.py

import subprocess
import sys
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
        print("\n✗ Could not find snapshot URL file")
        print("  Check if Git push was successful\n")

if __name__ == "__main__":
    main()
