# mlebench/competitions/train_val_split/grade.py
from pathlib import Path
import pandas as pd
from typing import Dict

def grade(submission: str, answers: str) -> Dict[str, float]:
    """
    Dummy grading logic:
    - If the agent produced train.csv and val.csv → evaluate simple split correctness.
    - Otherwise, return score 0.0.

    This tests the MLE-bench pipeline end-to-end without requiring real agent behavior.
    """
    submission_dir = Path(submission)
    answers_path = Path(answers)

    raw_df = pd.read_csv(answers_path)

    train_path = submission_dir / "train.csv"
    val_path = submission_dir / "val.csv"

    if not train_path.exists() or not val_path.exists():
        # dummy agent will hit this path; this is fine.
        return {
            "score": 0.0,
            "covered_ok": 0.0,
            "no_overlap": 0.0,
            "ratio_ok": 0.0,
        }

    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)

    raw_ids = set(raw_df["id"])
    train_ids = set(train_df["id"])
    val_ids = set(val_df["id"])

    covered_ok = float((train_ids | val_ids) == raw_ids)
    no_overlap = float(len(train_ids & val_ids) == 0)
    ratio = len(train_ids) / len(raw_ids)
    ratio_ok = float(0.7 <= ratio <= 0.9)

    score = (covered_ok + no_overlap + ratio_ok) / 3

    return {
        "score": float(score),
        "covered_ok": covered_ok,
        "no_overlap": no_overlap,
        "ratio_ok": ratio_ok,
    }