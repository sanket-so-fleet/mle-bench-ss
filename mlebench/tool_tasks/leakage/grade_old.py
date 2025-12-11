"""
Grader for leakage (Data Leakage Detection) technique-task.
"""

import json
from pathlib import Path


def grade(submission_dir: Path, competition_data: dict) -> dict:
    """Grade the data leakage detection task."""
    analysis_file = submission_dir / "leakage_analysis.json"
    
    result = {
        "score": 0.0,
        "passed": False,
        "checks": {},
        "feedback": []
    }
    
    if not analysis_file.exists():
        result["feedback"].append("leakage_analysis.json not found")
        return result
    result["checks"]["file_exists"] = True
    
    try:
        analysis = json.loads(analysis_file.read_text())
    except json.JSONDecodeError as e:
        result["feedback"].append(f"Invalid JSON: {e}")
        return result
    result["checks"]["valid_json"] = True
    
    # Check required fields
    required = ["features_analyzed", "leaky_features", "recommended_action"]
    missing = [f for f in required if f not in analysis]
    if missing:
        result["feedback"].append(f"Missing fields: {missing}")
        result["score"] = 0.2
        return result
    result["checks"]["required_fields"] = True
    result["score"] = 0.4
    
    # Check features were analyzed
    if not analysis.get("features_analyzed"):
        result["feedback"].append("No features analyzed")
        return result
    result["checks"]["features_analyzed"] = True
    result["score"] = 0.6
    
    # Check leaky features have proper structure
    leaky = analysis.get("leaky_features", [])
    if leaky:
        for feat in leaky:
            if not isinstance(feat, dict) or "feature" not in feat:
                result["feedback"].append("leaky_features must be list of dicts with 'feature' key")
                return result
    result["checks"]["proper_structure"] = True
    result["score"] = 0.8
    
    # Validate against ground truth if available
    ground_truth = competition_data.get("leakage_ground_truth", {})
    if ground_truth:
        expected_leaky = set(ground_truth.get("leaky_features", []))
        found_leaky = set(f["feature"] for f in leaky if isinstance(f, dict))
        
        if expected_leaky:
            recall = len(found_leaky & expected_leaky) / len(expected_leaky)
            result["score"] = 0.8 + (0.2 * recall)
            if recall >= 0.8:
                result["passed"] = True
            else:
                result["feedback"].append(f"Missed leaky features: {expected_leaky - found_leaky}")
        else:
            # No leaky features in ground truth
            if not leaky:
                result["score"] = 1.0
                result["passed"] = True
            else:
                result["feedback"].append("False positives - flagged features that aren't leaky")
                result["score"] = 0.7
    else:
        result["passed"] = True
        result["score"] = 0.9
        result["feedback"].append("No ground truth - graded on completeness")
    
    return result
