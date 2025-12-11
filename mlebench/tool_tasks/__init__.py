"""
Technique Tasks (Tool Tasks) for MLE-Bench

These are primitive ML skills that agents must demonstrate.
Each task runs against existing competition datasets and grades
the agent's diagnostic reasoning + implementation.

Categories:
- Data Quality & Validation: cv, leakage, missing, imbalance, scaling, encoding
- Workflow & Process: eda, baseline, evaluation
"""

from pathlib import Path

TOOL_TASKS_DIR = Path(__file__).parent


def list_tool_tasks() -> list[str]:
    """List all available tool task IDs."""
    tasks = []
    for p in TOOL_TASKS_DIR.iterdir():
        if p.is_dir() and (p / "config.yaml").exists():
            tasks.append(p.name)
    return sorted(tasks)
