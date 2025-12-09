# mlebench/tools/runner.py
from pathlib import Path
from mlebench.registry import Competition
from mlebench.utils import get_logger

logger = get_logger(__name__)

# mlebench/tools/runner.py
from mlebench.utils import get_logger

logger = get_logger(__name__)

def run_tools_on_prepare(competition):
    logger.info(f"[TOOLS] (prepare) would run tools for competition `{competition.id}`")

def run_tools_on_grade(competition_id, submission_entry, registry, output_dir):
    logger.info(f"[TOOLS] (grade) would run tools for competition `{competition_id}`")