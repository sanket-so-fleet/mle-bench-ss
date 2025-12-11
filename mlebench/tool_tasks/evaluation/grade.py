"""Grader for evaluation (Evaluation Metrics & Plots) technique-task."""

import json
from pathlib import Path


def grade(submission_dir: Path, competition_data: dict) -> dict:
    result = {"score": 0.0, "passed": False, "checks": {}, "feedback": []}
    
    # Check evaluate.py exists
    evaluate_py = submission_dir / "evaluate.py"
    if not evaluate_py.exists():
        result["feedback"].append("evaluate.py not found")
        return result
    result["checks"]["evaluate_exists"] = True
    result["score"] = 0.2
    
    # Check evaluate.py has metric computations
    code = evaluate_py.read_text()
    metric_patterns = ["accuracy", "precision", "recall", "f1", "auc", "confusion_matrix"]
    metrics_found = [p for p in metric_patterns if p in code.lower()]
    
    if len(metrics_found) < 2:
        result["feedback"].append(f"Only found metrics: {metrics_found}. Need multiple metrics.")
        result["score"] = 0.3
        return result
    result["checks"]["multiple_metrics"] = True
    result["score"] = 0.4
    
    # Check for plotting
    plot_patterns = ["plt.savefig", "matplotlib", "seaborn", "figure"]
    has_plotting = any(p in code for p in plot_patterns)
    if not has_plotting:
        result["feedback"].append("No plotting code found")
        result["score"] = 0.5
    else:
        result["checks"]["has_plotting"] = True
        result["score"] = 0.6
    
    # Check plots directory
    plots_dir = submission_dir / "plots"
    if plots_dir.exists():
        plots = list(plots_dir.glob("*.png")) + list(plots_dir.glob("*.jpg"))
        if plots:
            result["checks"]["plots_saved"] = True
            result["score"] = 0.7
    
    # Check report.md
    report = submission_dir / "report.md"
    if not report.exists():
        result["feedback"].append("report.md not found")
    else:
        report_content = report.read_text().lower()
        has_metrics = any(m in report_content for m in ["accuracy", "precision", "f1"])
        if has_metrics:
            result["checks"]["report_has_metrics"] = True
            result["score"] = 0.85
        else:
            result["feedback"].append("report.md missing metric summary")
            result["score"] = 0.75
    
    # Check results JSON
    results_file = submission_dir / "evaluation_results.json"
    if results_file.exists():
        try:
            json.loads(results_file.read_text())
            result["checks"]["results_json"] = True
            result["score"] = 0.95
        except json.JSONDecodeError:
            result["feedback"].append("evaluation_results.json is invalid")
    
    result["passed"] = result["score"] >= 0.6
    return result
