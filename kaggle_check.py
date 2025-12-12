"""Simple Kaggle API health check."""
import os
import json
import time
import sys
from pathlib import Path

def check(loops=10):
    """Check Kaggle API repeatedly."""
    print("--- Kaggle API Check ---")
    
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    if kaggle_json.exists():
        creds = json.loads(kaggle_json.read_text())
        os.environ['KAGGLE_USERNAME'] = creds['username']
        os.environ['KAGGLE_KEY'] = creds['key']
    
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    
    failures = 0
    for i in range(loops):
        try:
            api.competition_list_files("titanic")
            print(f"[{i+1}/{loops}] ✅ working")
        except Exception as e:
            print(f"[{i+1}/{loops}] ❌ error: {e}")
            failures += 1
        time.sleep(1)
    
    if failures > 0:
        print(f"\n⚠️  WARNING: {failures}/{loops} Kaggle API calls failed!")
        print("   Kaggle API may be unstable. You can still proceed, but data downloads may fail.")
        sys.exit(1)
    else:
        print("✅ Kaggle API stable")

if __name__ == "__main__":
    check()
