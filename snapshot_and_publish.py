# snapshot_and_publish.py (Merged Step 2 + 3)

import json
import pandas as pd
import zipfile
import subprocess
from pathlib import Path
from datetime import datetime

class NSESnapshotPublisher:
    def __init__(self, data_path="./nse_data", snapshot_path="./snapshots"):
        self.data_path = Path(data_path)
        self.snapshot_path = Path(snapshot_path)
        self.snapshot_path.mkdir(exist_ok=True)
        
    # ==================== DATA PARSING ====================
    
    def parse_fii_stats(self):
        """Parse FII derivatives statistics"""
        try:
            files = list(self.data_path.glob("fii_stats_*.xls"))
            if not files:
                return {"error": "FII stats file not found"}
            
            df = pd.read_excel(files[0], skiprows=3)
            
            data = {
                "file": files[0].name,
                "data": df.to_dict('records') if not df.empty else []
            }
            return data
        except Exception as e:
            return {"error": str(e)}
    
    def parse_participant_data(self):
        """Parse participant OI and Volume"""
        data = {}
        
        try:
            # Participant OI
            oi_files = list(self.data_path.glob("fao_participant_oi_*.csv"))
            if oi_files:
                df_oi = pd.read_csv(oi_files[0])
                data["oi"] = df_oi.to_dict('records')
            
            # Participant Volume
            vol_files = list(self.data_path.glob("fao_participant_vol_*.csv"))
            if vol_files:
                df_vol = pd.read_csv(vol_files[0])
                data["volume"] = df_vol.to_dict('records')
            
            return data
        except Exception as e:
            return {"error": str(e)}
    
    def parse_volatility(self):
        """Parse daily volatility - Top 50 high volatile stocks"""
        try:
            files = list(self.data_path.glob("FOVOLT_*.csv"))
            if not files:
                return {"error": "Volatility file not found"}
            
            df = pd.read_csv(files[0])
            
            # Find volatility column
            vol_col = None
            for col in ['VOLATILITY', 'Volatility', 'vola', 'VOLA']:
                if col in df.columns:
                    vol_col = col
                    break
            
            if vol_col:
                high_vol = df.nlargest(50, vol_col).to_dict('records')
            else:
                high_vol = df.head(50).to_dict('records')
            
            return {
                "top_50_volatile": high_vol,
                "total_stocks": len(df)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def parse_eod_data(self):
        """Parse EOD OHLC + OI + Volume from fo*.zip"""
        try:
            # Find extracted folder
            extract_folders = [d for d in self.data_path.iterdir() 
                             if d.is_dir() and d.name.startswith('fo') and len(d.name) == 10]
            
            if not extract_folders:
                return {"error": "Market activity folder not found"}
            
            folder = extract_folders[0]
            csv_files = list(folder.glob("*.csv"))
            
            if not csv_files:
                return {"error": "No CSV in market activity folder"}
            
            # Read main EOD data
            df = pd.read_csv(csv_files[0])
            
            # Extract stock futures only (filter by instrument type)
            if 'INSTRUMENT' in df.columns:
                stock_futures = df[df['INSTRUMENT'].str.contains('FUTSTK|STK', case=False, na=False)]
            else:
                stock_futures = df  # If no filter, take all
            
            return {
                "file": folder.name,
                "eod_data": stock_futures.to_dict('records'),
                "total_records": len(df),
                "stock_futures_count": len(stock_futures)
            }
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== SNAPSHOT CREATION ====================
    
    def create_snapshot(self):
        """Create comprehensive snapshot"""
        
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_file = self.snapshot_path / f"nse_snapshot_{date_str}.json"
        
        snapshot = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M:%S IST"),
                "version": "2.0",
                "data_source": "NSE Archives"
            },
            "analysis_ready_data": {}
        }
        
        print("\n" + "="*70)
        print("📸 Creating NSE Data Snapshot...")
        print("="*70 + "\n")
        
        # Parse all data
        print("  ↓ Parsing FII Statistics...")
        snapshot["analysis_ready_data"]["fii_statistics"] = self.parse_fii_stats()
        
        print("  ↓ Parsing Participant Activity...")
        snapshot["analysis_ready_data"]["participant_activity"] = self.parse_participant_data()
        
        print("  ↓ Parsing Volatility Data...")
        snapshot["analysis_ready_data"]["volatility"] = self.parse_volatility()
        
        print("  ↓ Parsing EOD Data (OHLC + OI + Volume)...")
        snapshot["analysis_ready_data"]["eod_market_data"] = self.parse_eod_data()
        
        # Save snapshot
        with open(snapshot_file, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Snapshot Created: {snapshot_file.name}")
        print(f"  Size: {snapshot_file.stat().st_size / 1024:.2f} KB\n")
        
        return snapshot_file
    
    # ==================== GIT PUBLISHING ====================
    
    def run_git_command(self, command):
        """Run git command"""
        try:
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
    
    def publish_to_git(self, snapshot_file):
        """Publish snapshot to GitHub"""
        print("="*70)
        print("🚀 Publishing to GitHub...")
        print("="*70 + "\n")
        
        # Check if git repo exists
        if not Path(".git").exists():
            print("✗ Not a git repository!")
            print("  Initialize with: git init")
            return False, None
        
        # Git add
        print("  ↓ Staging files...")
        success, _ = self.run_git_command("git add .")
        if not success:
            print("✗ Git add failed")
            return False, None
        
        # Git commit
        commit_msg = f"NSE Snapshot - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        print(f"  ↓ Committing: {commit_msg}")
        success, output = self.run_git_command(f'git commit -m "{commit_msg}"')
        
        if not success and "nothing to commit" not in output:
            print("✗ Git commit failed")
            return False, None
        
        # Git push
        print("  ↓ Pushing to remote...")
        success, _ = self.run_git_command("git push")
        
        if not success:
            print("✗ Git push failed")
            return False, None
        
        # Get raw URL
        raw_url = self.get_raw_url(snapshot_file)
        
        print(f"\n✓ Published to GitHub!")
        print("="*70 + "\n")
        
        return True, raw_url
    
    def get_raw_url(self, snapshot_file):
        """Generate GitHub raw URL"""
        try:
            success, output = self.run_git_command("git remote get-url origin")
            
            if not success:
                return None
            
            repo_url = output.strip()
            
            # Convert to raw URL
            if repo_url.endswith(".git"):
                repo_url = repo_url[:-4]
            
            repo_url = repo_url.replace("github.com", "raw.githubusercontent.com")
            
            # Relative path from repo root
            rel_path = snapshot_file.relative_to(Path.cwd())
            raw_url = f"{repo_url}/main/{rel_path.as_posix()}"
            
            return raw_url
        except:
            return None
    
    # ==================== MAIN WORKFLOW ====================
    
    def run(self):
        """Complete workflow: Parse + Snapshot + Publish"""
        
        print("\n" + "="*70)
        print("🎯 NSE Snapshot & Publisher")
        print("="*70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
        print("="*70 + "\n")
        
        # Step 1: Create snapshot
        snapshot_file = self.create_snapshot()
        
        # Step 2: Publish to GitHub
        success, raw_url = self.publish_to_git(snapshot_file)
        
        if success and raw_url:
            print("="*70)
            print("✅ READY FOR ANALYSIS!")
            print("="*70)
            print(f"\n📎 Raw URL:\n{raw_url}\n")
            print("="*70)
            print("\n💡 Copy this URL and send to assistant for analysis!\n")
            
            # Save URL to file for easy access
            url_file = self.snapshot_path / "latest_snapshot_url.txt"
            with open(url_file, 'w') as f:
                f.write(raw_url)
            
            return raw_url
        else:
            print("\n⚠ Snapshot created but not published to GitHub")
            print(f"Local file: {snapshot_file}")
            return None


if __name__ == "__main__":
    publisher = NSESnapshotPublisher()
    publisher.run()
