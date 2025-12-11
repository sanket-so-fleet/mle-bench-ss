"""Grader for baseline (Baseline Model Implementation) technique-task."""

import json
from pathlib import Path


def grade(submission_dir: Path, competition_data: dict) -> dict:
    result = {"score": 0.0, "passed": False, "checks": {}, "feedback": []}
    
    # Check baseline.py exists
    baseline_py = submission_dir / "baseline.py"
    if not baseline_py.exists():
        result["feedback"].append("baseline.py not found")
        return result
    result["checks"]["baseline_exists"] = True
    result["score"] = 0.3
    
    # Check baseline.py content
    code = baseline_py.read_text()
    
    # Must use cross-validation
    cv_patterns = ["cross_val_score", "cross_validate", "KFold", "StratifiedKFold", "cv="]
    has_cv = any(p in code for p in cv_patterns)
    if not has_cv:
        result["feedback"].append("No cross-validation found - use cross_val_score or KFold")
        result["score"] = 0.4
        return result
    result["checks"]["has_cv"] = True
    result["score"] = 0.5
    
    # Must print something
    if "print" not in code:
        result["feedback"].append("No print statements - must output metrics")
        result["score"] = 0.5
        return result
    result["checks"]["prints_metrics"] = True
    result["score"] = 0.6
    
    # Check README exists
    readme = submission_dir / "README.md"
    if not readme.exists():
        result["feedback"].append("README.md not found")
        result["score"] = 0.7
    else:
        readme_content = readme.read_text().lower()
        if "run" in readme_content or "python" in readme_content:
            result["checks"]["readme_has_instructions"] = True
            result["score"] = 0.8
        else:
            result["feedback"].append("README missing run instructions")
            result["score"] = 0.75
    
    # Check results JSON
    results_file = submission_dir / "baseline_results.json"
    if results_file.exists():
        try:
            results = json.loads(results_file.read_text())
            if "metrics" in results:
                result["checks"]["results_saved"] = True
                result["score"] = 0.95
        except json.JSONDecodeError:
            result["feedback"].append("baseline_results.json is not valid JSON")
    
    result["passed"] = result["score"] >= 0.6
    return result
