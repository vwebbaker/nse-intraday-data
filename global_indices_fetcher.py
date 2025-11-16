import yfinance as yf
import pandas as pd
from datetime import datetime
import json
import os
import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import subprocess
import shutil

class GlobalIndicesFetcher:
    
    INDICES_CONFIG = {
        "US": {
            "Dow Jones": "^DJI",
            "S&P 500": "^GSPC",
            "NASDAQ": "^IXIC",
            "Russell 2000": "^RUT",
            "VIX": "^VIX"
        },
        "EUROPE": {
            "FTSE 100": "^FTSE",
            "DAX": "^GDAXI",
            "CAC 40": "^FCHI",
            "Euro Stoxx 50": "^STOXX50E"
        },
        "ASIA": {
            "Nikkei 225": "^N225",
            "Hang Seng": "^HSI",
            "Shanghai": "000001.SS",
            "KOSPI": "^KS11",
            "Taiwan": "^TWII"
        },
        "INDIA": {
            "Gift Nifty": "GIFT_NIFTY",
            "Nifty 50": "^NSEI",
            "Bank Nifty": "^NSEBANK",
            "Sensex": "^BSESN",
            "Nifty IT": "^CNXIT"
        },
        "COMMODITIES": {
            "Crude Oil": "CL=F",
            "Gold": "GC=F",
            "Bitcoin": "BTC-USD"
        }
    }
    
    def __init__(self, data_folder="global", github_user="YOUR_USERNAME", repo_name="nse-intraday-data"):
        self.data_folder = Path(data_folder)
        self.data_folder.mkdir(exist_ok=True)
        self.all_data = {}
        self.regional_sentiment = {}
        self.github_user = github_user
        self.repo_name = repo_name
        
    def fetch_gift_nifty_groww(self):
        """Fetch Gift Nifty from Groww.in"""
        try:
            url = "https://groww.in/indices/global-indices"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                rows = soup.find_all('tr')
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    
                    for i, cell in enumerate(cells):
                        text = cell.get_text(strip=True)
                        
                        if 'GIFT' in text.upper() or 'SGX' in text.upper():
                            try:
                                if len(cells) > i + 1:
                                    price_text = cells[i + 1].get_text(strip=True).replace(',', '')
                                    current = float(price_text)
                                    
                                    change_pct = None
                                    if len(cells) > i + 2:
                                        change_text = cells[i + 2].get_text(strip=True)
                                        import re
                                        pct_match = re.search(r'([+-]?\d+\.?\d*)\s*%', change_text)
                                        if pct_match:
                                            change_pct = float(pct_match.group(1))
                                    
                                    if 20000 < current < 30000:
                                        return {
                                            'current': round(current, 2),
                                            'change_pct': round(change_pct, 2) if change_pct else None,
                                            'source': 'Groww.in'
                                        }
                            except (ValueError, IndexError):
                                continue
            
            return None
            
        except Exception as e:
            return None
    
    def fetch_gift_nifty_fallback(self):
        """Use Nifty 50 as proxy"""
        try:
            ticker = yf.Ticker("^NSEI")
            data = ticker.history(period="5d")
            
            if not data.empty:
                current = data['Close'].iloc[-1]
                previous = data['Close'].iloc[-2] if len(data) > 1 else current
                change_pct = ((current - previous) / previous) * 100
                
                return {
                    'current': round(current, 2),
                    'change_pct': round(change_pct, 2),
                    'source': 'Nifty 50 Proxy'
                }
            return None
        except:
            return None
    
    def fetch_gift_nifty(self):
        """Master Gift Nifty fetch function"""
        gift_data = self.fetch_gift_nifty_groww()
        if gift_data:
            return gift_data
        
        return self.fetch_gift_nifty_fallback()
    
    def fetch_index_data(self, ticker_symbol):
        """Fetch data for a single index"""
        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period="5d")
            
            if hist.empty:
                return None
            
            current = hist['Close'].iloc[-1]
            previous = hist['Close'].iloc[-2] if len(hist) > 1 else current
            change_pct = ((current - previous) / previous) * 100
            
            return {
                'current': round(current, 2),
                'change_pct': round(change_pct, 2),
                'day_high': round(hist['High'].iloc[-1], 2),
                'day_low': round(hist['Low'].iloc[-1], 2)
            }
        except:
            return None
    
    def fetch_all_indices(self):
        """Fetch all indices"""
        print("\n" + "="*80)
        print("📊 FETCHING GLOBAL INDICES DATA")
        print("="*80 + "\n")
        
        for region, indices in self.INDICES_CONFIG.items():
            self.all_data[region] = {}
            
            print(f"📍 {region}")
            print("-" * 80)
            
            for index_name, ticker_symbol in indices.items():
                
                if index_name == "Gift Nifty":
                    print(f"   Fetching {index_name:20s}...", end=" ")
                    gift_data = self.fetch_gift_nifty()
                    if gift_data:
                        self.all_data[region][index_name] = gift_data
                        status = "🟢" if gift_data.get('change_pct', 0) >= 0 else "🔴"
                        print(f"{status} {gift_data['current']:>12,.2f}  ({gift_data.get('change_pct', 0):>+6.2f}%)")
                    else:
                        print(f"❌ Failed")
                    continue
                
                print(f"   Fetching {index_name:20s}...", end=" ")
                data = self.fetch_index_data(ticker_symbol)
                
                if data:
                    self.all_data[region][index_name] = data
                    status = "🟢" if data['change_pct'] >= 0 else "🔴"
                    print(f"{status} {data['current']:>12,.2f}  ({data['change_pct']:>+6.2f}%)")
                else:
                    print(f"❌ Failed")
            
            print()
        
        return self.all_data
    
    def calculate_sentiment(self):
        """Calculate sentiment"""
        weights = {"US": 0.40, "ASIA": 0.25, "EUROPE": 0.20, "INDIA": 0.15}
        
        for region, indices in self.all_data.items():
            changes = [d['change_pct'] for d in indices.values() if d.get('change_pct')]
            self.regional_sentiment[region] = round(sum(changes) / len(changes), 2) if changes else 0.0
        
        score = sum(self.regional_sentiment.get(r, 0) * w for r, w in weights.items())
        
        if score > 1.0:
            label = "🟢 STRONG BULLISH"
        elif score > 0.3:
            label = "🟢 BULLISH"
        elif score > -0.3:
            label = "⚪ NEUTRAL"
        elif score > -1.0:
            label = "🔴 BEARISH"
        else:
            label = "🔴 STRONG BEARISH"
        
        return round(score, 2), label
    
    def generate_trading_bias(self, score):
        """Generate trading bias"""
        if score > 1.0:
            return {"bias": "STRONG BUY", "strategy": "Bullish opening. Look for LONG setups.", "watchlist": "Index heavyweights"}
        elif score > 0.3:
            return {"bias": "BUY", "strategy": "Positive bias. Selective longs.", "watchlist": "Breakout candidates"}
        elif score > -0.3:
            return {"bias": "NEUTRAL", "strategy": "Wait for direction post 9:30 AM.", "watchlist": "Range trades"}
        elif score > -1.0:
            return {"bias": "SELL/HEDGE", "strategy": "Bearish opening. SHORT setups or cash.", "watchlist": "Short hedges"}
        else:
            return {"bias": "STRONG SELL", "strategy": "Sharp negative opening. Defensive mode.", "watchlist": "PUT options, VIX"}
    
    def save_to_json(self):
        """Save data to JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        output = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S IST"),
            "indices": self.all_data,
            "regional_sentiment": self.regional_sentiment
        }
        
        json_file = self.data_folder / f"global_indices_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        latest_file = self.data_folder / "latest_global_snapshot.json"
        with open(latest_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        return json_file
    
    def publish_to_github(self, json_file):
        """Publish to GitHub"""
        try:
            latest = self.data_folder / "latest_global_snapshot.json"
            
            subprocess.run(["git", "add", str(latest)], check=True, cwd=".")
            subprocess.run(["git", "add", str(json_file)], check=True, cwd=".")
            
            msg = f"Global indices - {datetime.now().strftime('%Y-%m-%d %H:%M IST')}"
            subprocess.run(["git", "commit", "-m", msg], check=True, cwd=".")
            subprocess.run(["git", "push"], check=True, cwd=".")
            
            url = f"https://raw.githubusercontent.com/{self.github_user}/{self.repo_name}/main/global/latest_global_snapshot.json"
            
            print(f"\n✅ Published to GitHub!")
            print(f"📍 URL: {url}")
            
            return url
        except Exception as e:
            print(f"⚠️ GitHub publish failed: {e}")
            return None
    
    def print_summary(self, score, label, bias):
        """Print summary"""
        print("\n" + "="*70)
        print("🌍 GLOBAL MARKET SENTIMENT ANALYSIS")
        print("="*70)
        print(f"\n📊 Overall Score: {score:.2f}")
        print(f"📈 Sentiment: {label}")
        print(f"🎯 Trading Bias: {bias['bias']}")
        print(f"\n💡 Strategy: {bias['strategy']}")
        print(f"📋 Watchlist: {bias['watchlist']}")
        print("\n" + "="*70 + "\n")
    
    def run_git_command(self, command):
        """Run git command"""
        try:
            import subprocess
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr
    
    def update_analysis_prompt_with_global_url(self, github_url):
        """
        Update analysis_prompt.txt with latest global indices URL
        """
        try:
            prompt_file = "analysis_prompt.txt"
            
            if not os.path.exists(prompt_file):
                print(f"⚠ Analysis prompt file not found: {prompt_file}")
                return False
            
            # Read current prompt
            with open(prompt_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # Find Global Market Sentiment section and update URL
            updated = False
            for i, line in enumerate(lines):
                # Look for Global Market Sentiment header
                if 'Global Market' in line and ('Sentiment' in line or 'Data' in line or 'Overnight' in line):
                    # Check next few lines for URL or placeholder
                    for j in range(i+1, min(i+5, len(lines))):
                        if '{' in lines[j] or 'URL will be' in lines[j]:
                            lines[j] = '{' + github_url + '}\n'
                            updated = True
                            break
                    if updated:
                        break
            
            # If no old URL found, add new section
            if not updated:
                # Find "## Data Available:" section
                for i, line in enumerate(lines):
                    if "## Data Available:" in line:
                        # Look ahead to find where to insert
                        insert_index = i + 1
                        
                        # Skip empty lines
                        while insert_index < len(lines) and lines[insert_index].strip() == '':
                            insert_index += 1
                        
                        # Check if snapshot URL exists
                        has_snapshot = False
                        for j in range(insert_index, min(insert_index + 10, len(lines))):
                            if 'snapshots/nse_snapshot_' in lines[j]:
                                has_snapshot = True
                                # Insert global URL after snapshot section
                                insert_pos = j + 1
                                # Skip until next empty line or section
                                while insert_pos < len(lines) and lines[insert_pos].strip() != '' and not lines[insert_pos].startswith('##'):
                                    insert_pos += 1
                                
                                # Insert global market data section
                                lines.insert(insert_pos, '\n')
                                lines.insert(insert_pos + 1, '### Global Market Data:\n')
                                lines.insert(insert_pos + 2, '{' + github_url + '}\n')
                                updated = True
                                break
                        
                        if not has_snapshot:
                            # No snapshot URL, just add both sections
                            lines.insert(insert_index, '\n')
                            lines.insert(insert_index + 1, '### Global Market Data:\n')
                            lines.insert(insert_index + 2, '{' + github_url + '}\n')
                            updated = True
                        
                        break
            
            if updated:
                # Write updated prompt
                with open(prompt_file, "w", encoding="utf-8") as f:
                    f.writelines(lines)
                
                print(f"\n✓ Updated analysis prompt with global indices URL")
                print(f"  File: {prompt_file}")
                print(f"  URL: {github_url}")
                return True
            else:
                print(f"\n⚠ Could not find insertion point in {prompt_file}")
                return False
            
        except Exception as e:
            print(f"\n✗ Error updating analysis prompt: {e}")
            return False
    
    def publish_to_github(self, json_file):
        """Publish global indices JSON to GitHub"""
        print("\n" + "="*70)
        print("🚀 Publishing to GitHub...")
        print("="*70 + "\n")
        
        # Check if git repo exists
        if not Path(".git").exists():
            print("✗ Not a git repository!")
            return None
        
        # Git add
        print("  ↓ Staging global indices file...")
        success, _ = self.run_git_command(f"git add {json_file}")
        if not success:
            print("✗ Git add failed")
            return None
        
        # Git commit
        from datetime import datetime
        commit_msg = f"Global Indices Update - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        print(f"  ↓ Committing: {commit_msg}")
        success, output = self.run_git_command(f'git commit -m "{commit_msg}"')
        
        if not success and "nothing to commit" not in output:
            print("✗ Git commit failed")
            return None
        
        # Git push
        print("  ↓ Pushing to remote...")
        success, _ = self.run_git_command("git push")
        
        if not success:
            print("✗ Git push failed")
            return None
        
        # Generate GitHub raw URL
        filename = json_file.name
        github_url = f"https://raw.githubusercontent.com/vwebbaker/nse-intraday-data/refs/heads/main/global/{filename}"
        
        print(f"\n✅ Published to GitHub!")
        print(f"📎 URL: {github_url}")
        print("\n" + "="*70 + "\n")
        
        # Update analysis_prompt.txt with this URL
        self.update_analysis_prompt_with_global_url(github_url)
        
        return github_url
    
    def run_morning_routine(self):
        """Complete morning routine"""
        print("\n" + "🌅"*40)
        print("      MORNING MARKET ROUTINE - 8:30 AM IST")
        print("🌅"*40 + "\n")
        
        # Fetch data
        self.fetch_all_indices()
        
        # Analyze
        score, label = self.calculate_sentiment()
        bias = self.generate_trading_bias(score)
        
        # Print
        self.print_summary(score, label, bias)
        
        # Save
        json_file = self.save_to_json()
        print(f"✅ Data saved: {json_file}")
        
        # Publish to GitHub
        github_url = self.publish_to_github(json_file)
        
        if github_url:
            print(f"🌐 GitHub URL: {github_url}\n")
        
        return json_file


def main():
    """Main execution"""
    print("\n" + "="*70)
    print("🚀 Global Indices Fetcher - Started")
    print("="*70 + "\n")
    
    fetcher = GlobalIndicesFetcher()
    fetcher.run_morning_routine()


if __name__ == "__main__":
    main()
