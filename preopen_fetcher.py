import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import subprocess

class PreopenFetcher:
    
    def __init__(self, data_folder="preopen"):
        self.data_folder = Path(data_folder)
        self.data_folder.mkdir(exist_ok=True)
        
        # NSE headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json,text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.nseindia.com/'
        }
        
        self.session = requests.Session()
    
    def init_nse_session(self):
        """Initialize NSE session with cookies"""
        try:
            url = "https://www.nseindia.com/"
            response = self.session.get(url, headers=self.headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"⚠️ NSE session init failed: {e}")
            return False
    
    def fetch_preopen_data(self):
        """
        Fetch pre-open data from NSE API (handles compressed response)
        The page uses AJAX to load data from: /api/market-data-pre-open?key=ALL
        """
        try:
            # Initialize session first
            print("   Initializing NSE session...", end=" ")
            if not self.init_nse_session():
                print("❌ Failed")
                return None
            print("✓")
            
            # NSE Pre-open API endpoint (actual endpoint the webpage uses)
            api_url = "https://www.nseindia.com/api/market-data-pre-open?key=ALL"
            
            print("   Fetching pre-open data...", end=" ")
            
            # Update headers to accept JSON
            api_headers = self.headers.copy()
            api_headers['Accept'] = 'application/json, text/plain, */*'
            api_headers['Accept-Encoding'] = 'gzip, deflate, br'
            
            response = self.session.get(api_url, headers=api_headers, timeout=15)
            
            if response.status_code == 200:
                print("✓")
                
                # Response should auto-decode if it's gzip
                # But let's check encoding
                print("   Parsing response...", end=" ")
                
                try:
                    # Check if response is compressed
                    content_encoding = response.headers.get('Content-Encoding', '')
                    
                    if 'gzip' in content_encoding or 'br' in content_encoding:
                        # requests automatically decompresses gzip/deflate
                        # For brotli, we might need brotli library
                        print(f"(compressed: {content_encoding}) ", end="")
                    
                    # Try to parse JSON
                    data = response.json()
                    
                    # Validate data structure
                    if 'data' not in data:
                        print(f"❌ Invalid structure")
                        print(f"   Response keys: {list(data.keys())[:5]}")
                        
                        # Check if market is closed
                        if 'errors' in data or 'message' in data:
                            print(f"   Message: {data.get('message', data.get('errors'))}")
                        
                        return None
                    
                    if not data['data']:
                        print("⚠️  Empty (Market closed)")
                        return None
                    
                    print(f"✓ ({len(data['data'])} stocks)")
                    return data
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error")
                    
                    # Try to diagnose the issue
                    raw_content = response.content[:100]
                    
                    # Check if it's actually brotli compressed
                    if raw_content[:2] == b'\xce\xb2':  # Brotli magic number (rough check)
                        print("   ⚠️  Response is Brotli compressed")
                        print("   💡 Install brotli: pip install brotli")
                        
                        # Try to decompress with brotli
                        try:
                            import brotli
                            decompressed = brotli.decompress(response.content)
                            data = json.loads(decompressed)
                            print("   ✓ Brotli decompression successful!")
                            
                            if 'data' in data and data['data']:
                                return data
                            else:
                                print("   ⚠️  No data in response")
                                return None
                                
                        except ImportError:
                            print("   ❌ brotli library not installed")
                            print("   Run: pip install brotli")
                            return None
                        except Exception as br_error:
                            print(f"   ❌ Brotli decompression failed: {br_error}")
                            return None
                    else:
                        print(f"   First bytes (hex): {raw_content.hex()[:40]}")
                        print(f"   First chars: {str(raw_content[:50])}")
                        return None
                        
            elif response.status_code == 403:
                print("❌ Access denied (403)")
                print("   💡 NSE may have blocked requests. Try again later.")
                return None
            else:
                print(f"❌ Status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def parse_preopen_data(self, raw_data):
        """
        Parse and structure pre-open data
        Extract: gainers, losers, most active
        """
        if not raw_data or 'data' not in raw_data:
            print("⚠️ No data to parse")
            return None
        
        try:
            print("   Parsing pre-open data...", end=" ")
            
            preopen_stocks = []
            
            for item in raw_data['data']:
                metadata = item.get('metadata', {})
                detail = item.get('detail', {})
                preOpenMarket = detail.get('preOpenMarket', {})
                
                stock_info = {
                    'symbol': metadata.get('symbol', ''),
                    'series': metadata.get('series', ''),
                    'iep': detail.get('IEP', 0),  # Indicative Equilibrium Price
                    'prev_close': detail.get('lastPrice', 0),
                    'change': detail.get('change', 0),
                    'change_pct': detail.get('pChange', 0),
                    'final_quantity': detail.get('finalQuantity', 0),
                    'final_value': detail.get('value', 0),
                    'total_buy_qty': detail.get('totalBuyQuantity', 0),
                    'total_sell_qty': detail.get('totalSellQuantity', 0),
                    'atoBuyQty': preOpenMarket.get('atoBuyQty', 0),
                    'atoSellQty': preOpenMarket.get('atoSellQty', 0),
                }
                
                # Calculate buy/sell pressure
                total_qty = stock_info['total_buy_qty'] + stock_info['total_sell_qty']
                if total_qty > 0:
                    stock_info['buy_pressure'] = round(
                        (stock_info['total_buy_qty'] / total_qty) * 100, 2
                    )
                else:
                    stock_info['buy_pressure'] = 50.0
                
                preopen_stocks.append(stock_info)
            
            # Sort by change percentage
            preopen_stocks.sort(key=lambda x: x['change_pct'], reverse=True)
            
            # Categorize
            gainers = [s for s in preopen_stocks if s['change_pct'] > 0]
            losers = [s for s in preopen_stocks if s['change_pct'] < 0]
            
            # Most active by value
            most_active = sorted(
                preopen_stocks, 
                key=lambda x: x['final_value'], 
                reverse=True
            )
            
            print(f"✓ ({len(preopen_stocks)} stocks)")
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'date': datetime.now().strftime("%Y-%m-%d"),
                'time': datetime.now().strftime("%H:%M:%S IST"),
                'total_stocks': len(preopen_stocks),
                'advances': len(gainers),
                'declines': len(losers),
                'top_gainers': gainers[:20],
                'top_losers': losers[:20],
                'most_active': most_active[:20],
                'all_stocks': preopen_stocks
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Parse error: {e}")
            return None
    
    def save_data(self, parsed_data):
        """Save pre-open data to JSON and CSV"""
        if not parsed_data:
            return None, None
        
        print("   Saving data...", end=" ")
        
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON file with full data
        json_file = self.data_folder / f"preopen_{timestamp_str}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, indent=2, ensure_ascii=False)
        
        # Latest snapshot (fixed name for assistant)
        latest_json = self.data_folder / "latest_preopen_snapshot.json"
        with open(latest_json, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, indent=2, ensure_ascii=False)
        
        # CSV for top gainers/losers
        df_gainers = pd.DataFrame(parsed_data['top_gainers'][:10])
        df_losers = pd.DataFrame(parsed_data['top_losers'][:10])
        
        csv_file = self.data_folder / f"preopen_{timestamp_str}.csv"
        
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write("=== TOP 10 GAINERS (Pre-open) ===\n")
            if not df_gainers.empty:
                df_gainers.to_csv(f, index=False)
            f.write("\n=== TOP 10 LOSERS (Pre-open) ===\n")
            if not df_losers.empty:
                df_losers.to_csv(f, index=False)
        
        print("✓")
        
        return json_file, csv_file
    
    def publish_to_github(self, json_file):
        """Publish to GitHub"""
        try:
            print("   Publishing to GitHub...", end=" ")
            
            latest_file = self.data_folder / "latest_preopen_snapshot.json"
            
            subprocess.run(["git", "add", str(latest_file)], check=True, cwd=".")
            subprocess.run(["git", "add", str(json_file)], check=True, cwd=".")
            
            commit_msg = f"Pre-open data - {datetime.now().strftime('%Y-%m-%d %H:%M IST')}"
            subprocess.run(["git", "commit", "-m", commit_msg], check=True, cwd=".")
            subprocess.run(["git", "push"], check=True, cwd=".")
            
            # Generate URL
            github_user = "vwebbaker"  # Your username
            repo_name = "nse-intraday-data"
            
            raw_url = f"https://raw.githubusercontent.com/{github_user}/{repo_name}/main/preopen/latest_preopen_snapshot.json"
            
            print("✓")
            print(f"\n   📍 URL: {raw_url}")
            
            return raw_url
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git error: {e}")
            return None
        except Exception as e:
            print(f"❌ {e}")
            return None
    
    def print_summary(self, parsed_data):
        """Print pre-open summary"""
        if not parsed_data:
            return
        
        print("\n" + "="*70)
        print("📊 NSE PRE-OPEN MARKET SUMMARY (9:08 AM)")
        print("="*70)
        print(f"Total Stocks: {parsed_data['total_stocks']}")
        print(f"Advances: {parsed_data['advances']} | Declines: {parsed_data['declines']}")
        
        adv_dec_ratio = parsed_data['advances'] / max(parsed_data['declines'], 1)
        
        if adv_dec_ratio > 2.0:
            sentiment = "🟢 STRONG BULLISH"
        elif adv_dec_ratio > 1.2:
            sentiment = "🟢 BULLISH"
        elif adv_dec_ratio > 0.8:
            sentiment = "⚪ NEUTRAL"
        elif adv_dec_ratio > 0.5:
            sentiment = "🔴 BEARISH"
        else:
            sentiment = "🔴 STRONG BEARISH"
        
        print(f"Market Sentiment: {sentiment}")
        
        print("\n🟢 TOP 5 GAINERS:")
        print("-" * 70)
        for stock in parsed_data['top_gainers'][:5]:
            print(f"  {stock['symbol']:15s}  IEP: ₹{stock['iep']:>10.2f}  "
                  f"Change: {stock['change_pct']:>+6.2f}%  "
                  f"Buy: {stock['buy_pressure']:>5.1f}%")
        
        print("\n🔴 TOP 5 LOSERS:")
        print("-" * 70)
        for stock in parsed_data['top_losers'][:5]:
            print(f"  {stock['symbol']:15s}  IEP: ₹{stock['iep']:>10.2f}  "
                  f"Change: {stock['change_pct']:>+6.2f}%  "
                  f"Buy: {stock['buy_pressure']:>5.1f}%")
        
        print("\n💰 TOP 5 MOST ACTIVE (by value):")
        print("-" * 70)
        for stock in parsed_data['most_active'][:5]:
            value_cr = stock['final_value'] / 10000000  # Convert to crores
            print(f"  {stock['symbol']:15s}  Value: ₹{value_cr:>8.2f} Cr  "
                  f"Change: {stock['change_pct']:>+6.2f}%")
        
        print("\n" + "="*70)
    
    def run_preopen_routine(self, publish_github=True):
        """Complete pre-open routine"""
        print("\n" + "🕐"*40)
        print("      PRE-OPEN MARKET DATA - 9:08 AM IST")
        print("🕐"*40 + "\n")
        
        # Fetch data
        print("📍 Fetching NSE Pre-open Data")
        print("-" * 70)
        raw_data = self.fetch_preopen_data()
        
        if not raw_data:
            print("\n" + "="*70)
            print("⚠️  PRE-OPEN DATA NOT AVAILABLE")
            print("="*70)
            print("\nPossible reasons:")
            print("  • Market is closed (Weekend/Holiday)")
            print("  • Pre-open session hasn't started (Before 9:00 AM)")
            print("  • Pre-open session has ended (After 9:15 AM)")
            print("  • NSE API is temporarily unavailable")
            print("\n💡 Pre-open data is available only:")
            print("   Monday-Friday, 9:00 AM - 9:08 AM IST")
            print("="*70 + "\n")
            return None
        
        # Parse data
        parsed_data = self.parse_preopen_data(raw_data)
        
        if not parsed_data:
            print("\n✗ Failed to parse pre-open data")
            return None
        
        # Save data
        json_file, csv_file = self.save_data(parsed_data)
        
        if json_file:
            print(f"   JSON: {json_file}")
        if csv_file:
            print(f"   CSV: {csv_file}")
        
        # Print summary
        self.print_summary(parsed_data)
        
        # Publish to GitHub
        github_url = None
        if publish_github and json_file:
            print("\n📤 Publishing to GitHub")
            print("-" * 70)
            github_url = self.publish_to_github(json_file)
        
        print("\n" + "="*70)
        print("✅ PRE-OPEN ROUTINE COMPLETE")
        print("="*70 + "\n")
        
        return {
            'json_file': json_file,
            'csv_file': csv_file,
            'github_url': github_url,
            'parsed_data': parsed_data
        }


def main():
    """Main execution"""
    print("\n" + "="*70)
    print("🕐 NSE PRE-OPEN DATA FETCHER")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    print("="*70 + "\n")
    
    fetcher = PreopenFetcher()
    result = fetcher.run_preopen_routine(publish_github=True)
    
    if result and result.get('github_url'):
        print(f"🌐 GitHub URL: {result['github_url']}\n")


if __name__ == "__main__":
    main()
