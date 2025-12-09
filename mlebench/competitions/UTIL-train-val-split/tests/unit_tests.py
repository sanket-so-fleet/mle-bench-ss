from pathlib import Path
import pandas as pd

from mlebench.competitions.UTIL-train-val-split.prepare import prepare

def test_prepare_creates_raw_and_sample(tmp_path):
    raw = tmp_path / "raw"
    public = tmp_path / "public"
    private = tmp_path / "private"

    prepare(raw, public, private)

    assert (raw / "raw.csv").exists()
    assert (public / "raw.csv").exists()
    assert (public / "sample_submission.csv").exists()

    df = pd.read_csv(raw / "raw.csv")
    assert {"id", "y"}.issubset(df.columns)
    assert len(df) == 20