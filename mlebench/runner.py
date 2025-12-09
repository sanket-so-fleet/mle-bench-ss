# mlebench/tools/runner.py
from pathlib import Path
from mlebench.registry import Competition
from mlebench.utils import get_logger

logger = get_logger(__name__)

def run_tools_for_competition(competition: Competition) -> None:
    """
    Dummy hook for tool-tasks.

    For now, this just logs that tools *could* run for this competition.
    Later, this is where you'd invoke split-checking, metrics tools, etc.
    """
    logger.info(f"[TOOLS] Running tool-tasks for competition `{competition.id}`...")
    # Example of what you'd do later:
    # from mlebench.tools.split_checker import run_split_analysis
    # run_split_analysis(competition.public_dir, competition.private_dir)
    #
    # For now, it's a no-op beyond logging.
    return None