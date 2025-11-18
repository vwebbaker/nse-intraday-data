import requests
import os
from datetime import datetime, timedelta
import zipfile
from pathlib import Path
import time
import glob
import pandas as pd
import json
import subprocess

class NSEDataFetcher:
    def __init__(self, base_path="./nse_data"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.nseindia.com/',
        }

        self.session = requests.Session()

    def get_cookies(self):
        try:
            self.session.get("https://www.nseindia.com", headers=self.headers, timeout=10)
            time.sleep(2)
            return True
        except:
            return False

    def get_previous_trading_day(self):
        today = datetime.now()
        if today.weekday() == 5:
            return today - timedelta(days=1)
        elif today.weekday() == 6:
            return today - timedelta(days=2)
        elif today.weekday() == 0 and today.hour < 9:
            return today - timedelta(days=3)
        elif today.hour < 9:
            return today - timedelta(days=1)
        else:
            return today

    def format_date(self, date_obj, format_type="default"):
        if format_type == "default":
            return date_obj.strftime("%d%m%Y")
        elif format_type == "dash":
            return date_obj.strftime("%d-%b-%Y")
        elif format_type == "udiff":
            return date_obj.strftime("%Y%m%d")
        elif format_type == "upper":
            month = date_obj.strftime("%b").upper()
            return date_obj.strftime(f"%d-{month}-%Y")

    def download_file(self, url, filename, retry=3):
        filepath = self.base_path / filename
        if filepath.exists():
            file_time = datetime.fromtimestamp(filepath.stat().st_mtime)
            if (datetime.now() - file_time).seconds < 3600:
                print(f"⊙ Skipped (already exists): {filename}")
                return True

        for attempt in range(retry):
            try:
                print(f"↓ Downloading {filename}... [{attempt+1}/{retry}]")
                response = self.session.get(url, headers=self.headers, timeout=30)
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    print(f"✓ Downloaded: {filename} ({len(response.content)} bytes)")
                    return True
                else:
                    print(f"✗ HTTP {response.status_code}: {filename}")
            except Exception as e:
                print(f"✗ Error: {str(e)}")
            time.sleep(2)
        print(f"✗ FAILED after {retry} attempts: {filename}")
        return False

    def get_file_urls(self, target_date=None):
        if target_date is None:
            target_date = self.get_previous_trading_day()
        d_default = self.format_date(target_date, "default")
        d_dash = self.format_date(target_date, "dash")
        d_upper = self.format_date(target_date, "upper")
        d_udiff = self.format_date(target_date, "udiff")

        prev_day = target_date - timedelta(days=1)
        if prev_day.weekday() >= 5:
            prev_day -= timedelta(days=prev_day.weekday() - 4)
        p_default = self.format_date(prev_day, "default")

        next_day = target_date + timedelta(days=1)
        while next_day.weekday() >= 5:
            next_day += timedelta(days=1)
        n_default = self.format_date(next_day, "default")

        files = {
            f"fii_stats_{d_dash}.xls": f"https://nsearchives.nseindia.com/content/fo/fii_stats_{d_dash}.xls",
            f"fao_participant_oi_{d_default}.csv": f"https://nsearchives.nseindia.com/content/nsccl/fao_participant_oi_{d_default}.csv",
            f"fao_participant_vol_{d_default}.csv": f"https://nsearchives.nseindia.com/content/nsccl/fao_participant_vol_{d_default}.csv",
            f"combineoi_{d_default}.zip": f"https://nsearchives.nseindia.com/archives/nsccl/volt/combineoi_{d_default}.zip",
            f"FOVOLT_{d_default}.csv": f"https://nsearchives.nseindia.com/content/fo/FOVOLT_{d_default}.csv",
            f"fo_secban_{n_default}.csv": f"https://nsearchives.nseindia.com/content/fo/fo_secban_{n_default}.csv",
            f"oi_cli_limit_{d_upper}.lst": f"https://nsearchives.nseindia.com/content/nsccl/oi_cli_limit_{d_upper}.lst",
            f"mwpl_cli_{p_default}.xls": f"https://nsearchives.nseindia.com/archives/nsccl/mwpl/mwpl_cli_{p_default}.xls",
            f"FOSett_prce_{d_default}.csv": f"https://nsearchives.nseindia.com/content/fo/FOSett_prce_{d_default}.csv",
            f"fo{d_default}.zip": f"https://nsearchives.nseindia.com/archives/fo/mkt/fo{d_default}.zip",
        }
        return files, target_date

    def download_all(self):
        print(f"\n{'='*70}")
        print(f"NSE Data Auto-Fetcher - {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
        print(f"{'='*70}\n")
        if not self.get_cookies():
            print("⚠ Warning: Failed to get NSE cookies. Downloads might fail.")
        files, target_date = self.get_file_urls()
        print(f"Target Date: {target_date.strftime('%d-%b-%Y')}")
        print(f"Total Files: {len(files)}\n")
        results = {}
        for filename, url in files.items():
            results[filename] = self.download_file(url, filename)
            time.sleep(1.5)
        success = sum(1 for v in results.values() if v)
        print(f"\n{'='*70}")
        print(f"✓ Success: {success}/{len(results)} files")
        print(f"{'='*70}\n")
        return results

    def extract_zips(self):
        print("\nExtracting ZIP files...")
        zip_count = 0
        for zip_file in self.base_path.glob("*.zip"):
            try:
                extract_path = self.base_path / zip_file.stem
                extract_path.mkdir(exist_ok=True)
                with zipfile.ZipFile(zip_file, 'r') as zf:
                    zf.extractall(extract_path)
                print(f"✓ Extracted: {zip_file.name}")
                zip_count += 1
            except Exception as e:
                print(f"✗ Extract failed: {zip_file.name} - {e}")
        if zip_count == 0:
            print("⊙ No ZIP files to extract")

def generate_snapshot(base_path="./nse_data"):
    print("Generating JSON snapshot...")
    snapshot = {}
    for file in glob.glob(f"{base_path}/**/*.csv", recursive=True):
        try:
            df = pd.read_csv(file)
            snapshot[os.path.relpath(file, base_path)] = df.head(10).to_dict(orient="records")
        except Exception as e:
            snapshot[os.path.relpath(file, base_path)] = f"Error: {e}"
    for file in glob.glob(f"{base_path}/**/*.xls", recursive=True):
        try:
            df = pd.read_excel(file)
            snapshot[os.path.relpath(file, base_path)] = df.head(10).to_dict(orient="records")
        except Exception as e:
            snapshot[os.path.relpath(file, base_path)] = f"Error: {e}"
    snap_file = f"{base_path}/snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(snap_file, "w") as f:
        json.dump(snapshot, f, indent=2)
    print(f"✓ Snapshot JSON Generated: {snap_file}")
    return snap_file

def push_to_git(base_path="./nse_data"):
    print("Pushing to Git repo...")
    subprocess.run(["git", "add", "."], cwd=base_path)
    subprocess.run(["git", "commit", "-m", f"Auto snapshot: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"], cwd=base_path)
    subprocess.run(["git", "push"], cwd=base_path)
    print("✓ Git push complete!")

if __name__ == "__main__":
    fetcher = NSEDataFetcher()
    fetcher.download_all()
    fetcher.extract_zips()
    generate_snapshot()
    push_to_git()
