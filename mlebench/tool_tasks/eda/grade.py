"""Grader for eda (Exploratory Data Analysis Notebook) technique-task."""

import json
from pathlib import Path


def grade(submission_dir: Path, competition_data: dict) -> dict:
    result = {"score": 0.0, "passed": False, "checks": {}, "feedback": []}
    
    # Check notebook exists
    notebook = submission_dir / "eda.ipynb"
    if not notebook.exists():
        result["feedback"].append("eda.ipynb not found")
        return result
    result["checks"]["notebook_exists"] = True
    result["score"] = 0.2
    
    # Check analysis file exists
    analysis_file = submission_dir / "eda_analysis.json"
    if not analysis_file.exists():
        result["feedback"].append("eda_analysis.json not found")
        result["score"] = 0.3
        return result
    result["checks"]["analysis_exists"] = True
    result["score"] = 0.4
    
    try:
        analysis = json.loads(analysis_file.read_text())
    except json.JSONDecodeError as e:
        result["feedback"].append(f"Invalid JSON: {e}")
        return result
    result["checks"]["valid_json"] = True
    
    # Check required fields
    required = ["num_rows", "num_cols", "target_column", "issues"]
    missing = [f for f in required if f not in analysis]
    if missing:
        result["feedback"].append(f"Missing fields: {missing}")
        result["score"] = 0.5
        return result
    result["checks"]["required_fields"] = True
    result["score"] = 0.6
    
    # Check issues were identified
    issues = analysis.get("issues", [])
    if not issues or len(issues) == 0:
        result["feedback"].append("No issues identified - every dataset has something!")
        result["score"] = 0.6
        return result
    result["checks"]["issues_found"] = True
    result["score"] = 0.7
    
    # Check for plots
    plots_dir = submission_dir / "plots"
    plots_saved = analysis.get("plots_saved", [])
    
    if plots_dir.exists():
        actual_plots = list(plots_dir.glob("*.png")) + list(plots_dir.glob("*.jpg"))
        if len(actual_plots) >= 2:
            result["checks"]["plots_saved"] = True
            result["score"] = 0.9
        else:
            result["feedback"].append(f"Only {len(actual_plots)} plots found, expected at least 3")
            result["score"] = 0.8
    elif plots_saved:
        result["checks"]["plots_listed"] = True
        result["score"] = 0.85
    else:
        result["feedback"].append("No plots directory or plots_saved in analysis")
        result["score"] = 0.75
    
    result["passed"] = True
    return result
