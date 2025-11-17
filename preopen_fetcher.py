# preopen_fetcher.py - Complete Data Fetcher with Groww Global Indices
import json
import os
import subprocess
from datetime import datetime
import requests
from pathlib import Path
from bs4 import BeautifulSoup


class SnapshotPublisher:
    def __init__(self, repo_path="."):
        self.repo_path = Path(repo_path).resolve()
        self.github_base_url = "https://raw.githubusercontent.com/vwebbaker/nse-intraday-data/refs/heads/main"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if not (self.repo_path / ".git").exists():
            print(f"⚠️  WARNING: No .git folder found in {self.repo_path}")
            print(f"   Make sure you're running from the git repository root")
    
    def fetch_nse_derivatives(self):
        """Fetch NSE derivatives snapshot"""
        url = "https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O"
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        try:
            print("\n📊 Fetching NSE Derivatives (F&O stocks)...")
            session = requests.Session()
            session.get("https://www.nseindia.com", headers=headers, timeout=10)
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            filename = f"nse_snapshot_{self.timestamp}.json"
            filepath = self.repo_path / "snapshots" / filename
            
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            stocks_count = len(data.get('data', []))
            print(f"✅ NSE Derivatives snapshot saved: {filename}")
            print(f"   Stocks count: {stocks_count}")
            
            return f"{self.github_base_url}/snapshots/{filename}"
            
        except Exception as e:
            print(f"❌ Error fetching NSE derivatives: {e}")
            return None
    
    def fetch_global_indices(self):
        """Fetch REAL global indices data from Groww.in"""
        url = "https://groww.in/indices/global-indices"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
        }
        
        try:
            print("\n🌍 Fetching Global Indices from Groww.in...")
            
            session = requests.Session()
            response = session.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            global_data = {
                'timestamp': datetime.now().isoformat(),
                'fetch_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S IST'),
                'source': 'Groww.in',
                'indices': {}
            }
            
            # Find all table rows
            rows = soup.find_all('tr')
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 7:
                    try:
                        # Extract index name
                        name_cell = cells[0]
                        index_name = name_cell.get_text(strip=True).split('\n')[0]
                        
                        # Skip if no valid name
                        if not index_name or len(index_name) < 2:
                            continue
                        
                        # Extract data
                        price = cells[1].get_text(strip=True).replace(',', '')
                        change_text = cells[2].get_text(strip=True)
                        high = cells[3].get_text(strip=True).replace(',', '')
                        low = cells[4].get_text(strip=True).replace(',', '')
                        open_price = cells[5].get_text(strip=True).replace(',', '')
                        prev_close = cells[6].get_text(strip=True).replace(',', '')
                        
                        # Parse change and percentage
                        change_val = ''
                        change_pct = ''
                        if '(' in change_text and ')' in change_text:
                            parts = change_text.split('(')
                            change_val = parts[0].strip()
                            change_pct = parts[1].replace(')', '').replace('%', '').strip()
                        else:
                            change_val = change_text
                            change_pct = '0'
                        
                        global_data['indices'][index_name] = {
                            'price': price,
                            'change': change_val,
                            'change_percent': change_pct,
                            'high': high,
                            'low': low,
                            'open': open_price,
                            'prev_close': prev_close,
                            'status': 'success'
                        }
                        
                        # Display with color indicator
                        indicator = "🟢" if change_pct.replace('-', '').replace('+', '') and float(change_pct) >= 0 else "🔴"
                        print(f"   {indicator} {index_name:20} {price:>12} ({change_pct:>6}%)")
                        
                    except Exception as e:
                        continue
            
            # Save to file
            filename = f"global_indices_{self.timestamp}.json"
            filepath = self.repo_path / "global" / filename
            
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(global_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Global indices saved: {filename}")
            print(f"   Total indices: {len(global_data['indices'])}")
            
            return f"{self.github_base_url}/global/{filename}"
            
        except Exception as e:
            print(f"❌ Error fetching global indices from Groww: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def fetch_preopen_data(self):
        """Fetch NSE pre-open market data"""
        url = "https://www.nseindia.com/api/market-data-pre-open?key=ALL"
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        try:
            print("\n📈 Fetching Pre-Open Market Data from NSE...")
            session = requests.Session()
            session.get("https://www.nseindia.com", headers=headers, timeout=10)
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Save JSON
            filename = f"preopen_{self.timestamp}.json"
            filepath = self.repo_path / "preopen" / filename
            
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            records_count = len(data.get('data', []))
            print(f"✅ Pre-open data snapshot saved: {filename}")
            print(f"   Records: {records_count}")
            
            return f"{self.github_base_url}/preopen/{filename}"
            
        except Exception as e:
            print(f"❌ Error fetching pre-open data: {e}")
            return None
    
    def git_publish(self):
        """Publish snapshots to GitHub"""
        try:
            print("\n📤 Publishing to GitHub...")
            
            original_dir = os.getcwd()
            os.chdir(self.repo_path)
            
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, check=True)
            
            if not result.stdout.strip():
                print("ℹ️  No changes to commit")
                os.chdir(original_dir)
                return True
            
            subprocess.run(['git', 'add', '.'], check=True)
            commit_msg = f"Data update: {self.timestamp}"
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            subprocess.run(['git', 'push'], check=True)
            
            print(f"✅ Git publish successful!")
            print(f"   Commit: {commit_msg}")
            os.chdir(original_dir)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git publish failed: {e}")
            os.chdir(original_dir)
            return False
    
    def update_analysis_prompt(self, urls):
        """Update analysis_prompt.txt with ONLY Pre-Open URL (not NSE/Global)"""
        prompt_path = self.repo_path / "analysis_prompt.txt"
        
        if not prompt_path.exists():
            print(f"❌ analysis_prompt.txt not found at: {prompt_path}")
            return False
        
        try:
            print("\n📝 Updating analysis_prompt.txt...")
            
            with open(prompt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            
            # ONLY update Pre-Open Market Data section
            preopen_url = urls.get('preopen', 'NOT_AVAILABLE')
            
            content = re.sub(
                r'### 3\. Pre-Open Market Data.*?\n\{[^}]*\}',
                f"### 3. Pre-Open Market Data (9:00-9:08 AM):\n{{{preopen_url}}}",
                content,
                flags=re.DOTALL
            )
            
            # Add/Update timestamp at the top
            timestamp_header = f"# 📊 LAST UPDATED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}\n\n"
            if '# 📊 LAST UPDATED:' in content:
                content = re.sub(
                    r'# 📊 LAST UPDATED:.*?\n\n',
                    timestamp_header,
                    content,
                    count=1,
                    flags=re.DOTALL
                )
            else:
                content = timestamp_header + content
            
            with open(prompt_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ analysis_prompt.txt updated successfully!")
            print(f"\n📋 Updated URL:")
            print(f"   Pre-Open Data: {preopen_url}")
            print(f"\nℹ️  NSE Derivatives & Global URLs unchanged (manual update required)")
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating analysis_prompt.txt: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_full_pipeline(self):
        """Execute complete snapshot + publish + update pipeline"""
        print("\n" + "="*70)
        print("🚀 COMPLETE DATA FETCHER PIPELINE")
        print("="*70)
        print(f"📁 Repository: {self.repo_path}")
        print(f"⏰ Timestamp: {self.timestamp}")
        print("="*70)
        
        # Step 1: Fetch all snapshots
        import time
        
        urls = {}
        
        urls['nse_snapshot'] = self.fetch_nse_derivatives()
        time.sleep(1)  # Rate limiting
        
        urls['global_indices'] = self.fetch_global_indices()
        time.sleep(1)
        
        urls['preopen'] = self.fetch_preopen_data()
        
        # Step 2: Update analysis prompt (ONLY Pre-Open URL)
        prompt_updated = False
        if urls.get('preopen'):
            prompt_updated = self.update_analysis_prompt(urls)
        
        # Step 3: Publish to Git
        git_success = self.git_publish()
        
        # Summary
        print("\n" + "="*70)
        print("📊 PIPELINE SUMMARY")
        print("="*70)
        print(f"✅ NSE Derivatives: {'Success' if urls.get('nse_snapshot') else 'Failed'}")
        print(f"✅ Global Indices (Groww): {'Success' if urls.get('global_indices') else 'Failed'}")
        print(f"✅ Pre-Open Data: {'Success' if urls.get('preopen') else 'Failed'}")
        print(f"✅ Prompt Updated: {'Yes (Pre-Open only)' if prompt_updated else 'No'}")
        print(f"✅ Git Published: {'Yes' if git_success else 'No'}")
        print("="*70)
        
        if all([urls.get('nse_snapshot'), urls.get('global_indices'), urls.get('preopen'), git_success]):
            print("\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
            print("📈 All data ready for AI analysis!")
            return True
        else:
            print("\n⚠️  PIPELINE COMPLETED WITH WARNINGS")
            return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='NSE & Global Data Fetcher')
    parser.add_argument('--repo-path', default='.', 
                       help='Path to git repository (default: current directory)')
    
    args = parser.parse_args()
    
    # Install check
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("⚠️  beautifulsoup4 not installed!")
        print("   Run: pip install beautifulsoup4")
        exit(1)
    
    publisher = SnapshotPublisher(repo_path=args.repo_path)
    success = publisher.run_full_pipeline()
    
    if success:
        print("\n✓ Ready for analysis - Check analysis_prompt.txt")
    else:
        print("\n✗ Some operations failed - Check logs above")
