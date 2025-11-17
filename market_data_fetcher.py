import requests
import time
from pathlib import Path

def download_nse_preopen_csv(output_dir="data"):
    """
    Download Pre-Open Market CSV from NSE India website
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # NSE headers to mimic browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.nseindia.com/',
        'Connection': 'keep-alive',
    }
    
    # Create session
    session = requests.Session()
    session.headers.update(headers)
    
    # First, visit the main page to get cookies
    print("Visiting NSE website to establish session...")
    main_url = "https://www.nseindia.com/market-data/pre-open-market-cm-and-emerge-market"
    response = session.get(main_url, timeout=10)
    
    if response.status_code != 200:
        print(f"Failed to access main page: {response.status_code}")
        return None
    
    print("Session established. Downloading CSV...")
    time.sleep(1)  # Brief pause
    
    # CSV download URL
    csv_url = "https://www.nseindia.com/api/market-data-pre-open?key=ALL"
    
    try:
        csv_response = session.get(csv_url, timeout=10)
        
        if csv_response.status_code == 200:
            # Generate filename with timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/nse_preopen_{timestamp}.csv"
            
            # Save the CSV data
            with open(filename, 'wb') as f:
                f.write(csv_response.content)
            
            print(f"✓ CSV downloaded successfully: {filename}")
            print(f"  File size: {len(csv_response.content)} bytes")
            return filename
        else:
            print(f"Failed to download CSV: {csv_response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error downloading CSV: {e}")
        return None

if __name__ == "__main__":
    print("NSE Pre-Open Market CSV Downloader")
    print("=" * 50)
    
    # Download the CSV
    result = download_nse_preopen_csv()
    
    if result:
        print(f"\n✓ Download complete: {result}")
    else:
        print("\n✗ Download failed")
