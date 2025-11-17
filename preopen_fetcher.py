# preopen_fetcher.py (CORRECTED VERSION)
import json
import os
import subprocess
from datetime import datetime
import requests
from pathlib import Path

class SnapshotPublisher:
    def __init__(self, repo_path="."):  # Changed default to current directory
        self.repo_path = Path(repo_path).resolve()
        self.github_base_url = "https://raw.githubusercontent.com/vwebbaker/nse-intraday-data/refs/heads/main"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Validate we're in the right directory
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
            session = requests.Session()
            session.get("https://www.nseindia.com", headers=headers)
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            filename = f"nse_snapshot_{self.timestamp}.json"
            filepath = self.repo_path / "snapshots" / filename  # Direct path, no nesting
            
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ NSE Derivatives snapshot saved: {filename}")
            return f"{self.github_base_url}/snapshots/{filename}"
            
        except Exception as e:
            print(f"❌ Error fetching NSE derivatives: {e}")
            return None
    
    def fetch_global_indices(self):
        """Fetch global indices data"""
        indices = {
            'Dow Jones': '^DJI',
            'S&P 500': '^GSPC',
            'Nasdaq': '^IXIC',
            'Nikkei': '^N225',
            'Hang Seng': '^HSI',
            'FTSE 100': '^FTSE',
            'DAX': '^GDAXI',
            'Gift Nifty': 'NIFTY_50_NOV_FUT.NS'
        }
        
        global_data = {
            'timestamp': datetime.now().isoformat(),
            'indices': {}
        }
        
        try:
            for name, symbol in indices.items():
                global_data['indices'][name] = {
                    'symbol': symbol,
                    'status': 'fetching...'
                }
            
            filename = f"global_indices_{self.timestamp}.json"
            filepath = self.repo_path / "global" / filename
            
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(global_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Global indices snapshot saved: {filename}")
            return f"{self.github_base_url}/global/{filename}"
            
        except Exception as e:
            print(f"❌ Error fetching global indices: {e}")
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
            session = requests.Session()
            session.get("https://www.nseindia.com", headers=headers)
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            filename = f"preopen_{self.timestamp}.json"
            filepath = self.repo_path / "preopen" / filename
            
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Pre-open data snapshot saved: {filename}")
            return f"{self.github_base_url}/preopen/{filename}"
            
        except Exception as e:
            print(f"❌ Error fetching pre-open data: {e}")
            return None
    
    def git_publish(self):
        """Publish snapshots to GitHub"""
        try:
            original_dir = os.getcwd()
            os.chdir(self.repo_path)
            
            # Check git status first
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, check=True)
            
            if not result.stdout.strip():
                print(f"ℹ️  No changes to commit")
                os.chdir(original_dir)
                return True
            
            # Git commands
            subprocess.run(['git', 'add', '.'], check=True)
            commit_msg = f"Snapshot update: {self.timestamp}"
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            subprocess.run(['git', 'push'], check=True)
            
            print(f"✅ Git publish successful: {commit_msg}")
            os.chdir(original_dir)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git publish failed: {e}")
            os.chdir(original_dir)
            return False
    
    def update_analysis_prompt(self, urls):
        """Update analysis_prompt.txt with new URLs"""
        prompt_path = self.repo_path / "analysis_prompt.txt"
        
        if not prompt_path.exists():
            print(f"❌ analysis_prompt.txt not found at: {prompt_path}")
            return False
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace URLs in the data sources section
            import re
            
            replacements = {
                'nse_snapshot': urls.get('nse_snapshot', 'NOT_AVAILABLE'),
                'global_indices': urls.get('global_indices', 'NOT_AVAILABLE'),
                'preopen': urls.get('preopen', 'NOT_AVAILABLE')
            }
            
            # Update NSE Derivatives Snapshot
            content = re.sub(
                r'### 1\. NSE Derivatives Snapshot.*?\n\{[^}]*\}',
                f"### 1. NSE Derivatives Snapshot (Previous Day EOD):\n{{{replacements['nse_snapshot']}}}",
                content,
                flags=re.DOTALL
            )
            
            # Update Global Market Sentiment
            content = re.sub(
                r'### 2\. Global Market Sentiment.*?\n\{[^}]*\}',
                f"### 2. Global Market Sentiment (Overnight):\n{{{replacements['global_indices']}}}",
                content,
                flags=re.DOTALL
            )
            
            # Update Pre-Open Market Data
            content = re.sub(
                r'### 3\. Pre-Open Market Data.*?\n\{[^}]*\}',
                f"### 3. Pre-Open Market Data (9:00-9:08 AM):\n{{{replacements['preopen']}}}",
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
            
            # Save updated content
            with open(prompt_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ analysis_prompt.txt updated successfully!")
            print(f"\n📋 Updated URLs:")
            print(f"   NSE Snapshot: {replacements['nse_snapshot']}")
            print(f"   Global Indices: {replacements['global_indices']}")
            print(f"   Pre-Open Data: {replacements['preopen']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating analysis_prompt.txt: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_full_pipeline(self):
        """Execute complete snapshot + publish + update pipeline"""
        print("\n" + "="*60)
        print("🚀 STARTING SNAPSHOT PUBLISHER PIPELINE")
        print("="*60)
        print(f"📁 Working directory: {self.repo_path}")
        print(f"⏰ Timestamp: {self.timestamp}")
        print("="*60 + "\n")
        
        # Step 1: Fetch all snapshots
        print("📡 STEP 1: Fetching snapshots...")
        urls = {
            'nse_snapshot': self.fetch_nse_derivatives(),
            'global_indices': self.fetch_global_indices(),
            'preopen': self.fetch_preopen_data()
        }
        
        # Step 2: Update analysis prompt FIRST (before git push)
        print("\n📝 STEP 2: Updating analysis_prompt.txt...")
        prompt_updated = self.update_analysis_prompt(urls)
        
        # Step 3: Publish to Git
        print("\n📤 STEP 3: Publishing to GitHub...")
        git_success = self.git_publish()
        
        if not git_success:
            print("⚠️  Git publish failed, but files are saved locally")
        
        print("\n" + "="*60)
        print("✅ PIPELINE COMPLETED!")
        print("="*60)
        
        # Summary
        print("\n📊 SUMMARY:")
        print(f"   Timestamp: {self.timestamp}")
        print(f"   Snapshots created: {sum(1 for url in urls.values() if url)}/3")
        print(f"   Prompt updated: {'Yes' if prompt_updated else 'No'}")
        print(f"   Git published: {'Yes' if git_success else 'No'}")
        
        return urls


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='NSE Snapshot Publisher')
    parser.add_argument('--repo-path', default='.', 
                       help='Path to git repository (default: current directory)')
    
    args = parser.parse_args()
    
    publisher = SnapshotPublisher(repo_path=args.repo_path)
    publisher.run_full_pipeline()
