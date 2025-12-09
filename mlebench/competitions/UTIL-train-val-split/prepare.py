from pathlib import Path
import pandas as pd
import numpy as np

def prepare(raw: Path, public: Path, private: Path):
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

    # Expose raw to agent as /home/code/raw.csv
    (public / "raw.csv").write_text(raw_csv.read_text())

    # Crucial for dummy: sample_submission.csv in PUBLIC
    sample = df[["id"]].copy()
    sample["y"] = 0
    sample.to_csv(public / "sample_submission.csv", index=False)

    return public