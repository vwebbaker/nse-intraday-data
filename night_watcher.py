# watcher_night.py (repo folder ke andar hi rakhein)
import pandas as pd, os, json, subprocess

REPO = r'C:\Users\Vivek\nse-intraday-data'
OUT = os.path.join(REPO, "night_selection.json")

def safe_load(path):
    try: return pd.read_csv(path).to_dict(orient="list")
    except: return {}

def main():
    snapshot = {}
    snapshot["eod"] = {name[:-4]: safe_load(os.path.join(REPO, "eod", name))
                       for name in os.listdir(os.path.join(REPO, "eod")) if name.endswith('.csv')}
    snapshot["oi_movers"] = safe_load(os.path.join(REPO, "oi_movers", "ttfut13112025.csv"))
    snapshot["fii_dii"] = safe_load(os.path.join(REPO, "fii_dii", "fii_dii_2025-11-13.csv"))
    snapshot["participant"] = safe_load(os.path.join(REPO, "participant", "fao_participant_oi_13112025.csv"))
    with open(OUT, "w") as f: json.dump(snapshot, f, indent=2)
    subprocess.run(["git", "add", "."], cwd=REPO)
    subprocess.run(["git", "commit", "-m", "night snapshot"], cwd=REPO)
    subprocess.run(["git", "push"], cwd=REPO)
    print("night_selection.json updated.")

if __name__ == "__main__":
    main()
