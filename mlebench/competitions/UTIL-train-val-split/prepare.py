# mlebench/competitions/train-val-split/prepare.py
from pathlib import Path
import pandas as pd
import numpy as np

def prepare(raw: Path, public: Path, private: Path):
    """
    Create a tiny synthetic dataset for the split task.

    raw/      → contains raw.csv
    public/   → exposed to /home/code (and used by dummy agent)
    private/  → metadata if needed
    """
    raw.mkdir(parents=True, exist_ok=True)
    public.mkdir(parents=True, exist_ok=True)
    private.mkdir(parents=True, exist_ok=True)

    n = 20
    df = pd.DataFrame({
        "id": range(n),
        "y": np.random.randint(0, 2, size=n),
    })

    raw_csv = raw / "raw.csv"
    df.to_csv(raw_csv, index=False)

    # Expose raw.csv to the agent
    (public / "raw.csv").write_text(raw_csv.read_text())

    # Dummy sample submission so the dummy agent has something to copy
    # Schema doesn't matter much; the dummy just copies the file.
    sample = df[["id"]].copy()
    sample["y"] = 0  # arbitrary placeholder
    sample.to_csv(public / "sample_submission.csv", index=False)

    return public