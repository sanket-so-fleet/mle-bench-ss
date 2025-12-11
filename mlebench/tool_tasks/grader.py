"""
Simple grader for technique-tasks.

Grading = Did the agent produce output with content?
Returns word count for each task. Developer judges quality.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Union


def grade_technique_task(task_id: str, submission_dir: Union[Path, str]) -> dict:
    """
    Grade a technique-task submission.
    
    Args:
        task_id: The task (e.g., 'imbalance', 'missing', 'encoding')
        submission_dir: Path to agent's output directory
        
    Returns:
        dict with score, passed, word_count
    """
    submission_dir = Path(submission_dir)
    analysis_file = submission_dir / f"{task_id}_analysis.json"
    
    if not analysis_file.exists():
        return {
            "task": task_id,
            "score": 0,
            "passed": False,
            "word_count": 0,
            "message": f"{task_id}_analysis.json not found"
        }
    
    try:
        content = analysis_file.read_text()
        word_count = len(content.split())
        
        return {
            "task": task_id,
            "score": 1.0 if word_count > 0 else 0,
            "passed": word_count > 0,
            "word_count": word_count,
            "message": f"Agent wrote {word_count} words"
        }
    except Exception as e:
        return {
            "task": task_id,
            "score": 0,
            "passed": False,
            "word_count": 0,
            "message": f"Error reading file: {e}"
        }


def grade_all_tasks(submission_dir: Union[Path, str], tasks: list = None) -> dict:
    """
    Grade all technique-tasks for a submission.
    
    Args:
        submission_dir: Path to agent's output directory
        tasks: List of task IDs to grade (default: all)
        
    Returns:
        dict with per-task results and summary
    """
    submission_dir = Path(submission_dir)
    if tasks is None:
        tasks = ["imbalance", "missing", "encoding", "cv", "scaling", "leakage"]
    
    results = {
        "tasks": {},
        "summary": {
            "total": len(tasks),
            "passed": 0,
            "total_words": 0
        }
    }
    
    for task_id in tasks:
        task_result = grade_technique_task(task_id, submission_dir)
        results["tasks"][task_id] = task_result
        
        if task_result["passed"]:
            results["summary"]["passed"] += 1
        results["summary"]["total_words"] += task_result["word_count"]
    
    results["summary"]["pass_rate"] = results["summary"]["passed"] / len(tasks)
    
    return results
