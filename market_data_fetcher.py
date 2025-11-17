# master_data_fetcher.py - Complete Data Pipeline
import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
import requests

class MasterDataFetcher:
    def __init__(self, repo_path="."):
        self.repo_path = Path(repo_path).resolve()
        self.github_base_url = "https://raw.githubusercontent.com/vwebbaker/nse-intraday-data/refs/heads/main"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session = requests.Session()
        
        # NSE headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nseindia.com/',
        }
        self.session.headers.update(self.headers)
        
        # Validate git repo
        if not (self.repo_path / ".git").exists():
            print(f"⚠️  WARNING: No .git folder found in {self.repo_path}")
    
    def init_nse_session(self):
        """Initialize NSE session with cookies"""
        try:
            print("🔐 Initializing NSE session...")
            self.session.get("https://www.nseindia.com", timeout=10)
            print("✅ NSE session initialized")
            time.sleep(1)
            return True
        except Exception as e:
            print(f"❌ Failed to initialize NSE session: {e}")
            return False
    
    def fetch_nse_derivatives(self):
        """Fetch NSE F&O derivatives data"""
        url = "https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O"
        
        try:
            print("\n📊 Fetching NSE Derivatives (F&O stocks)...")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            filename = f"nse_snapshot_{self.timestamp}.json"
            filepath = self.repo_path / "snapshots" / filename
            
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ NSE Derivatives saved: {filename}")
            print(f"   Stocks count: {len(data.get('data', []))}")
            
            return f"{self.github_base_url}/snapshots/{filename}"
            
        except Exception as e:
            print(f"❌ Error fetching NSE derivatives: {e}")
            return None
    
    def fetch_global_indices(self):
        """Fetch global market indices"""
        indices = {
            'Dow Jones': '^DJI',
            'S&P 500': '^GSPC',
            'Nasdaq': '^IXIC',
            'Nikkei 225': '^N225',
            'Hang Seng': '^HSI',
            'FTSE 100': '^FTSE',
            'DAX': '^GDAXI',
            'Gift Nifty': 'NIFTY_50_FUT.NS'
        }
        
        try:
            print("\n🌍 Fetching Global Market Indices...")
            
            global_data = {
                'timestamp': datetime.now().isoformat(),
                'fetch_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S IST'),
                'indices': {}
            }
            
            for name, symbol in indices.items():
                global_data['indices'][name] = {
                    'symbol': symbol,
                    'status': 'placeholder - integrate Yahoo Finance or other API'
                }
            
            filename = f"global_indices_{self.timestamp}.json"
            filepath = self.repo_path / "global" / filename
            
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(global_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Global indices saved: {filename}")
            print(f"   Indices count: {len(indices)}")
            
            return f"{self.github_base_url}/global/{filename}"
            
        except Exception as e:
            print(f"❌ Error fetching global indices: {e}")
            return None
    
    def fetch_preopen_data(self):
        """Fetch NSE Pre-Open market data (JSON + CSV)"""
        url = "https://www.nseindia.com/api/market-data-pre-open?key=ALL"
        
        try:
            print("\n📈 Fetching Pre-Open Market Data...")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Save JSON
            json_filename = f"preopen_{self.timestamp}.json"
            json_filepath = self.repo_path / "preopen" / json_filename
            json_filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Pre-open JSON saved: {json_filename}")
            
            # Also save as CSV for easy viewing
            csv_filename = f"preopen_{self.timestamp}.csv"
            csv_filepath = self.repo_path / "data" / csv_filename
            csv_filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(csv_filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print(f"✅ Pre-open CSV saved: {csv_filename}")
            print(f"   Records: {len(data.get('data', []))}")
            
            return f"{self.github_base_url}/preopen/{json_filename}"
            
        except Exception as e:
            print(f"❌ Error fetching pre-open data: {e}")
            return None
    
    def update_analysis_prompt(self, preopen_url):
        """Update analysis_prompt.txt with Pre-Open URL only"""
        prompt_path = self.repo_path / "analysis_prompt.txt"
        
        if not prompt_path.exists():
            print(f"⚠️  analysis_prompt.txt not found at: {prompt_path}")
            return False
        
        try:
            print("\n📝 Updating analysis_prompt.txt...")
            
            with open(prompt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            
            # Update Pre-Open section only
            content = re.sub(
                r'### 3\. Pre-Open Market Data.*?\n\{[^}]*\}',
                f"### 3. Pre-Open Market Data (9:00-9:08 AM):\n{{{preopen_url}}}",
                content,
                flags=re.DOTALL
            )
            
            # Update timestamp
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
            
            print(f"✅ analysis_prompt.txt updated!")
            print(f"   Pre-Open URL: {preopen_url}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating prompt: {e}")
            return False
    
    def git_publish(self):
        """Commit and push all changes to GitHub"""
        try:
            print("\n📤 Publishing to GitHub...")
            
            original_dir = os.getcwd()
            os.chdir(self.repo_path)
            
            # Check if there are changes
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, check=True)
            
            if not result.stdout.strip():
                print("ℹ️  No changes to commit")
                os.chdir(original_dir)
                return True
            
            # Git add, commit, push
            subprocess.run(['git', 'add', '.'], check=True)
            commit_msg = f"Data update: {self.timestamp}"
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            subprocess.run(['git', 'push'], check=True)
            
            print(f"✅ Successfully pushed to GitHub!")
            print(f"   Commit: {commit_msg}")
            
            os.chdir(original_dir)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git publish failed: {e}")
            os.chdir(original_dir)
            return False
    
    def run_complete_pipeline(self):
        """Execute the complete data fetching pipeline"""
        print("\n" + "="*70)
        print("🚀 MASTER DATA FETCHER - COMPLETE PIPELINE")
        print("="*70)
        print(f"📁 Repository: {self.repo_path}")
        print(f"⏰ Timestamp: {self.timestamp}")
        print("="*70)
        
        # Initialize NSE session
        if not self.init_nse_session():
            print("\n❌ Pipeline aborted - NSE session failed")
            return False
        
        # Fetch all data
        urls = {}
        
        urls['nse_derivatives'] = self.fetch_nse_derivatives()
        time.sleep(1)  # Rate limiting
        
        urls['global_indices'] = self.fetch_global_indices()
        time.sleep(1)
        
        urls['preopen'] = self.fetch_preopen_data()
        
        # Update prompt (Pre-Open only)
        prompt_updated = False
        if urls.get('preopen'):
            prompt_updated = self.update_analysis_prompt(urls['preopen'])
        
        # Publish to GitHub
        git_success = self.git_publish()
        
        # Summary
        print("\n" + "="*70)
        print("📊 PIPELINE SUMMARY")
        print("="*70)
        print(f"✅ NSE Derivatives: {'Success' if urls.get('nse_derivatives') else 'Failed'}")
        print(f"✅ Global Indices: {'Success' if urls.get('global_indices') else 'Failed'}")
        print(f"✅ Pre-Open Data: {'Success' if urls.get('preopen') else 'Failed'}")
        print(f"✅ Prompt Updated: {'Yes' if prompt_updated else 'No'}")
        print(f"✅ Git Published: {'Yes' if git_success else 'No'}")
        print("="*70)
        
        if all([urls.get('nse_derivatives'), urls.get('preopen'), git_success]):
            print("\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
            return True
        else:
            print("\n⚠️  PIPELINE COMPLETED WITH WARNINGS")
            return False


if __name__ == "__main__":
    print("NSE Master Data Fetcher")
    print("Fetching: Derivatives, Global Indices, Pre-Open Data")
    print("")
    
    fetcher = MasterDataFetcher(repo_path=".")
    success = fetcher.run_complete_pipeline()
    
    if success:
        print("\n✓ All systems operational - Ready for analysis!")
    else:
        print("\n✗ Some operations failed - Check logs above")
