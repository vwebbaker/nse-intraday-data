import pandas as pd
import os
import time
import subprocess

# CONFIG
CSV_FILE = r'C:\Users\Vivek\nse-intraday-data\all_ticks_FUTURES.csv'
REPO_DIR = r'C:\Users\Vivek\nse-intraday-data'
SNAPSHOT_FILE = os.path.join(REPO_DIR, "snapshot.json")
SNAPSHOT_ROWS = 800 # last N ticks per symbol

def create_snapshot():
    df = pd.read_csv(CSV_FILE)
    out = {}
    for sym, g in df.groupby('Symbol'):
        g = g.tail(SNAPSHOT_ROWS).copy()
        g['vwap'] = (g['last_price']*g['last_traded_quantity']).cumsum()/g['last_traded_quantity'].replace(0, pd.NA).cumsum()
        g['oi_delta'] = g['open_interest'].diff().fillna(0)
        g['qty_spike'] = (g['last_traded_quantity'] > g['last_traded_quantity'].shift(1).fillna(0)*2).astype(int)
        out[sym] = {
            "last_ts": str(g['exchange_timestamp'].iloc[-1]),
            "last_price": float(g['last_price'].iloc[-1]),
            "vwap": float(g['vwap'].iloc[-1]),
            "oi_delta_last": int(g['oi_delta'].iloc[-1]),
            "orh": float(g['last_price'].max()),
            "orl": float(g['last_price'].min()),
            "qty_spike_count": int(g['qty_spike'].tail(50).sum())
        }
    import json
    with open(SNAPSHOT_FILE, "w") as f:
        json.dump(out, f, indent=2)
    print("Snapshot saved.")

def git_push():
    try:
        subprocess.run(["git", "add", "."], cwd=REPO_DIR)
        subprocess.run(["git", "commit", "-m", "auto snapshot update"], cwd=REPO_DIR)
        subprocess.run(["git", "push"], cwd=REPO_DIR)
        print("Git push complete.")
    except Exception as e:
        print("Git push error:", e)

if __name__ == "__main__":
    while True:
        try:
            create_snapshot()
            git_push()
        except Exception as ex:
            print("Error:", ex)
        time.sleep(60) # run every 1 min
