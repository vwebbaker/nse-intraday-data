# global_preopen.py
import pandas as pd, os, json, subprocess

REPO = r'C:\Users\Vivek\nse-intraday-data'
GLOBAL_CSV = os.path.join(REPO, "global", "global_market_2025-11-14.csv")
PREOPEN_CSV = os.path.join(REPO, "preopen", "preopen_2025-11-14.csv")
OUT = os.path.join(REPO, "global_preopen.json")

def safe_load(path):
    try: return pd.read_csv(path).to_dict(orient="list")
    except: return {}

def main():
    snapshot = {}
    snapshot["global"] = safe_load(GLOBAL_CSV)
    snapshot["preopen"] = safe_load(PREOPEN_CSV)
    with open(OUT, "w") as f: json.dump(snapshot, f, indent=2)
    subprocess.run(["git", "add", "."], cwd=REPO)
    subprocess.run(["git", "commit", "-m", "morning global+preopen snapshot"], cwd=REPO)
    subprocess.run(["git", "push"], cwd=REPO)
    print("global_preopen.json updated.")

if __name__ == "__main__":
    main()
