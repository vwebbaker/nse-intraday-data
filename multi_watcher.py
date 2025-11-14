import pandas as pd
import os
import time
import json
import subprocess

REPO_DIR = r'C:\Users\Vivek\nse-intraday-data'

FILES = {
    "tick": "all_ticks_FUTURES.csv",
    "preopen": os.path.join("preopen", "preopen_2025-11-14.csv"),
    "global": os.path.join("global", "global_market_2025-11-14.csv"),
    "fii_dii": os.path.join("fii_dii", "fii_dii_2025-11-13.csv"),
    "participant": os.path.join("participant", "fao_participant_oi_13112025.csv"),
    # add EOD files key/values if needed
}

def tick_snapshot():
    path = os.path.join(REPO_DIR, FILES["tick"])
    try:
        df = pd.read_csv(path)
    except Exception:
        return {}
    out = {}
    for sym, g in df.groupby('Symbol'):
        g = g.tail(800)
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
    return out

def preopen_snapshot():
    path = os.path.join(REPO_DIR, FILES["preopen"])
    try:
        df = pd.read_csv(path)
        return df.to_dict(orient="list")
    except Exception:
        return {}

def global_snapshot():
    path = os.path.join(REPO_DIR, FILES["global"])
    try:
        df = pd.read_csv(path)
        return df.to_dict(orient="list")
    except Exception:
        return {}

def fiidii_participant_snapshot():
    out = {}
    for key in ["fii_dii", "participant"]:
        path = os.path.join(REPO_DIR, FILES[key])
        try:
            df = pd.read_csv(path)
            out[key] = df.to_dict(orient="list")
        except Exception:
            out[key] = {}
    return out

def write_json():
    snap = {
        "tick": tick_snapshot(),
        "preopen": preopen_snapshot(),
        "global": global_snapshot(),
        "fiidii_participant": fiidii_participant_snapshot(),
        # add more sections if needed
    }
    with open(os.path.join(REPO_DIR, "full_snapshot.json"), "w") as f:
        json.dump(snap, f, indent=2)
    print("Full snapshot written.")

def git_push():
    try:
        subprocess.run(["git", "add", "."], cwd=REPO_DIR)
        subprocess.run(["git", "commit", "-m", "auto multi-snapshot update"], cwd=REPO_DIR)
        subprocess.run(["git", "push"], cwd=REPO_DIR)
        print("Git push complete.")
    except Exception as e:
        print("Git push error:", e)

if __name__ == "__main__":
    while True:
        try:
            write_json()
            git_push()
        except Exception as ex:
            print("Error:", ex)
        time.sleep(60)
