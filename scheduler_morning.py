"""
Morning Routine Scheduler
Runs global indices fetch at 8:30 AM daily
"""

import schedule
import time
from datetime import datetime
from global_indices_fetcher import GlobalIndicesFetcher

def morning_job():
    """Job to run at 8:30 AM"""
    print(f"\n{'#'*80}")
    print(f"# Scheduled Job Triggered: {datetime.now().strftime('%d-%b-%Y %I:%M:%S %p IST')}")
    print(f"{'#'*80}\n")
    
    fetcher = GlobalIndicesFetcher()
    fetcher.run_morning_routine()

def main():
    """Schedule and run"""
    print(f"\n{'='*80}")
    print(f"⏰ MORNING ROUTINE SCHEDULER STARTED")
    print(f"{'='*80}")
    print(f"  Time: {datetime.now().strftime('%d-%b-%Y %I:%M:%S %p IST')}")
    print(f"  Schedule: Daily at 8:30 AM IST")
    print(f"  Press Ctrl+C to stop")
    print(f"{'='*80}\n")
    
    # Schedule at 8:30 AM
    schedule.every().day.at("08:30").do(morning_job)
    
    # Optional: Test run immediately (comment out in production)
    # print("Running test execution now...\n")
    # morning_job()
    
    print("⏰ Waiting for 8:30 AM...\n")
    
    while True:
        schedule.run_pending()
        time.sleep(30)  # Check every 30 seconds

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Scheduler stopped by user")
        print("Goodbye! 👋\n")
