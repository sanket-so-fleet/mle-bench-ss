# mlebench/runner.py
"""
Runner for technique-tasks (tool-tasks).

These tasks run against existing competition datasets to test
specific ML primitive skills like CV strategy, leakage detection, etc.
"""

import json
from pathlib import Path
from typing import Optional
from mlebench.registry import Competition, Registry
from mlebench.utils import get_logger

logger = get_logger(__name__)

# Path to tool_tasks directory
TOOL_TASKS_DIR = Path(__file__).parent / "tool_tasks"


def list_tool_tasks() -> list[str]:
    """List all available tool task IDs."""
    if not TOOL_TASKS_DIR.exists():
        return []
    tasks = []
    for p in TOOL_TASKS_DIR.iterdir():
        if p.is_dir() and (p / "config.yaml").exists():
            tasks.append(p.name)
    return sorted(tasks)


def get_tool_task_config(task_id: str) -> dict:
    """Load config for a tool task."""
    import yaml
    config_path = TOOL_TASKS_DIR / task_id / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Tool task '{task_id}' not found")
    with open(config_path) as f:
        return yaml.safe_load(f)


def run_tools_on_prepare(competition: Competition) -> None:
    """
    Prepare hook for technique-tasks.
    
    Called after a competition is prepared. Can be used to:
    - Generate synthetic inputs for the tool task
    - Set up ground truth for grading
    """
    logger.info(f"[TOOLS] (prepare) Processing competition `{competition.id}` for tool-tasks")
    
    # For now, tool-tasks use the existing competition data directly
    # Future: could generate tool-task specific data here
    available_tasks = list_tool_tasks()
    if available_tasks:
        logger.info(f"[TOOLS] Available tool-tasks: {available_tasks}")
    else:
        logger.warning("[TOOLS] No tool-tasks found in mlebench/tool_tasks/")


def run_tools_on_grade(
    competition_id: str,
    submission_entry: dict,
    registry: Registry,
    output_dir: Path,
) -> dict:
    """
    Grade technique-task submissions for a competition.
    
    Args:
        competition_id: The competition being graded
        submission_entry: The submission data (path to submission dir, etc.)
        registry: The registry with competition metadata
        output_dir: Where to save grading results
        
    Returns:
        dict with tool-task grades
    """
    logger.info(f"[TOOLS] (grade) Grading tool-tasks for competition `{competition_id}`")
    
    results = {
        "competition_id": competition_id,
        "tool_task_grades": {}
    }
    
    # Get submission directory (where agent wrote outputs)
    submission_dir = Path(submission_entry.get("submission_path", "")).parent
    if not submission_dir.exists():
        logger.warning(f"[TOOLS] Submission directory not found: {submission_dir}")
        return results
    
    # Get competition for context
    try:
        competition = registry.get_competition(competition_id)
        competition_data = {
            "id": competition.id,
            "name": competition.name,
            "public_dir": str(competition.public_dir),
        }
    except Exception as e:
        logger.warning(f"[TOOLS] Could not load competition {competition_id}: {e}")
        competition_data = {}
    
    # Grade each tool task
    for task_id in list_tool_tasks():
        try:
            grade_result = grade_tool_task(task_id, submission_dir, competition_data)
            results["tool_task_grades"][task_id] = grade_result
            
            status = "PASS" if grade_result.get("passed") else "FAIL"
            score = grade_result.get("score", 0)
            logger.info(f"[TOOLS] {task_id}: {status} (score={score:.2f})")
            
        except Exception as e:
            logger.error(f"[TOOLS] Error grading {task_id}: {e}")
            results["tool_task_grades"][task_id] = {
                "score": 0,
                "passed": False,
                "error": str(e)
            }
    
    # Save results
    tools_output = output_dir / f"tool_tasks_{competition_id}.json"
    with open(tools_output, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"[TOOLS] Results saved to {tools_output}")
    
    return results


def grade_tool_task(task_id: str, submission_dir: Path, competition_data: dict) -> dict:
    """
    Grade a specific tool task.
    
    Args:
        task_id: The tool task ID (e.g., 'cv', 'leakage')
        submission_dir: Path to agent's submission directory
        competition_data: Metadata about the competition
        
    Returns:
        dict with score, passed, checks, feedback
    """
    import importlib.util
    
    grader_path = TOOL_TASKS_DIR / task_id / "grade.py"
    if not grader_path.exists():
        return {
            "score": 0,
            "passed": False,
            "error": f"No grader found for {task_id}"
        }
    
    # Load the grader module
    spec = importlib.util.spec_from_file_location(f"{task_id}_grader", grader_path)
    grader_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(grader_module)
    
    # Call the grade function
    if hasattr(grader_module, "grade"):
        return grader_module.grade(submission_dir, competition_data)
    else:
        return {
            "score": 0,
            "passed": False,
            "error": f"Grader for {task_id} missing 'grade' function"
        }