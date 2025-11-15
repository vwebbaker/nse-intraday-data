# nse_data_fetcher.py (Windows Compatible)

import requests
import os
from datetime import datetime, timedelta
import zipfile
from pathlib import Path
import time

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
        """Get fresh cookies from NSE"""
        try:
            self.session.get("https://www.nseindia.com", headers=self.headers, timeout=10)
            time.sleep(2)
            return True
        except:
            return False
    
    def get_previous_trading_day(self):
        """Get last trading day (skip weekends)"""
        today = datetime.now()
        
        # If Saturday, get Friday
        if today.weekday() == 5:  
            return today - timedelta(days=1)
        # If Sunday, get Friday
        elif today.weekday() == 6:  
            return today - timedelta(days=2)
        # If Monday before 9 AM, get Friday
        elif today.weekday() == 0 and today.hour < 9:
            return today - timedelta(days=3)
        # Other days before 9 AM, get previous day
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
            # Manual uppercase for Windows compatibility
            month = date_obj.strftime("%b").upper()
            return date_obj.strftime(f"%d-{month}-%Y")
    
    def download_file(self, url, filename, retry=3):
        filepath = self.base_path / filename
        
        # Skip if already downloaded today
        if filepath.exists():
            file_time = datetime.fromtimestamp(filepath.stat().st_mtime)
            if (datetime.now() - file_time).seconds < 3600:  # Downloaded within 1 hour
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
        d_upper = self.format_date(target_date, "upper")  # 14-NOV-2025
        d_udiff = self.format_date(target_date, "udiff")
        
        # T-1 for some files
        prev_day = target_date - timedelta(days=1)
        if prev_day.weekday() >= 5:  # Skip weekends
            prev_day -= timedelta(days=prev_day.weekday() - 4)
        p_default = self.format_date(prev_day, "default")
        
        # T+1 for ban list (next trading day's ban)
        next_day = target_date + timedelta(days=1)
        while next_day.weekday() >= 5:  # Skip weekends
            next_day += timedelta(days=1)
        n_default = self.format_date(next_day, "default")
        
        files = {
            # FII Statistics
            f"fii_stats_{d_dash}.xls": 
                f"https://nsearchives.nseindia.com/content/fo/fii_stats_{d_dash}.xls",
            
            # Participant Activity
            f"fao_participant_oi_{d_default}.csv": 
                f"https://nsearchives.nseindia.com/content/nsccl/fao_participant_oi_{d_default}.csv",
            
            f"fao_participant_vol_{d_default}.csv": 
                f"https://nsearchives.nseindia.com/content/nsccl/fao_participant_vol_{d_default}.csv",
            
            # Combined OI
            f"combineoi_{d_default}.zip": 
                f"https://nsearchives.nseindia.com/archives/nsccl/volt/combineoi_{d_default}.zip",
            
            # Volatility
            f"FOVOLT_{d_default}.csv": 
                f"https://nsearchives.nseindia.com/content/fo/FOVOLT_{d_default}.csv",
            
            # Ban List - Next trading day
            f"fo_secban_{n_default}.csv": 
                f"https://nsearchives.nseindia.com/content/fo/fo_secban_{n_default}.csv",
            
            # Client Position Limits (UPPERCASE month)
            f"oi_cli_limit_{d_upper}.lst":
                f"https://nsearchives.nseindia.com/content/nsccl/oi_cli_limit_{d_upper}.lst",
            
            # MWPL
            f"mwpl_cli_{p_default}.xls": 
                f"https://nsearchives.nseindia.com/archives/nsccl/mwpl/mwpl_cli_{p_default}.xls",
            
            # Settlement Prices
            f"FOSett_prce_{d_default}.csv":
                f"https://nsearchives.nseindia.com/content/fo/FOSett_prce_{d_default}.csv",
            
            # Bhavcopy (Market Activity)
            f"fo{d_default}.zip":
                f"https://nsearchives.nseindia.com/archives/fo/mkt/fo{d_default}.zip",
        }
        
        return files, target_date
    
    def download_all(self):
        print(f"\n{'='*70}")
        print(f"NSE Data Auto-Fetcher - {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
        print(f"{'='*70}\n")
        
        # Get fresh cookies
        if not self.get_cookies():
            print("⚠ Warning: Failed to get NSE cookies. Downloads might fail.")
        
        files, target_date = self.get_file_urls()
        
        print(f"Target Date: {target_date.strftime('%d-%b-%Y')}")
        print(f"Total Files: {len(files)}\n")
        
        results = {}
        for filename, url in files.items():
            results[filename] = self.download_file(url, filename)
            time.sleep(1.5)  # Rate limiting
        
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


if __name__ == "__main__":
    fetcher = NSEDataFetcher()
    fetcher.download_all()
    fetcher.extract_zips()
