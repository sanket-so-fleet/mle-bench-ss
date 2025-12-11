"""Local FastAPI server for MLE-Bench – runs directly on host, no container."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# Load .env file (for OPENAI_API_KEY, DOCKER_HOST, etc.)
load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent
RUNS_DIR = PROJECT_ROOT / "runs"

app = FastAPI(title="MLE-Bench Local Server", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# In-memory state (lost on restart, but fine for demo)
# ---------------------------------------------------------------------------
_STATE_LOCK = threading.Lock()
_RUN_STATE: Dict[str, "RunRecord"] = {}


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------
class RunRequest(BaseModel):
    competition_set: str = Field(
        "experiments/splits/low.txt",
        description="Path to a text file listing competition IDs (one per line).",
    )
    agent_id: str = Field("dummy", description="Agent ID from the agents registry.")
    lite: bool = Field(True, description="Use --lite flag during prepare/grade.")
    n_seeds: int = Field(1, ge=1)
    n_workers: int = Field(1, ge=1)
    retain: bool = Field(False, description="Keep agent containers after run.")
    data_dir: Optional[str] = Field(None, description="Override data directory.")
    gitlink: Optional[str] = Field(None, description="Git repo link (reserved for future use).")
    notes: Optional[str] = None
    tasks: Optional[List[str]] = Field(
        None, 
        description="Technique-tasks to run (e.g., ['imbalance', 'missing']). If provided, runs technique-task mode instead of competition mode."
    )


class RunRecord(BaseModel):
    run_id: str
    status: Literal["queued", "running", "completed", "failed"]
    created_at: float
    updated_at: float
    request: RunRequest
    message: Optional[str] = None
    run_group: Optional[str] = None
    run_dir: Optional[str] = None
    logs: List[Dict[str, Any]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _now() -> float:
    return time.time()


def _update(run_id: str, **kwargs: Any) -> None:
    with _STATE_LOCK:
        rec = _RUN_STATE.get(run_id)
        if rec is None:
            return
        data = rec.model_dump()
        data.update(kwargs)
        data["updated_at"] = _now()
        _RUN_STATE[run_id] = RunRecord(**data)


def _append_log(run_id: str, entry: Dict[str, Any]) -> None:
    with _STATE_LOCK:
        rec = _RUN_STATE.get(run_id)
        if rec is None:
            return
        data = rec.model_dump()
        data["logs"] = [*data["logs"], entry]
        data["updated_at"] = _now()
        _RUN_STATE[run_id] = RunRecord(**data)


def _run_cmd(cmd: List[str], run_id: str) -> None:
    result = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
    _append_log(run_id, {
        "cmd": cmd,
        "returncode": result.returncode,
        "stdout": result.stdout.strip()[-2000:],
        "stderr": result.stderr.strip()[-2000:],
    })
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "command failed")


def _discover_new_run_group(before: set[str]) -> Optional[str]:
    if not RUNS_DIR.exists():
        return None
    after = {p.name for p in RUNS_DIR.iterdir() if p.is_dir()}
    diff = sorted(after - before)
    return diff[-1] if diff else None


# ---------------------------------------------------------------------------
# Worker (background thread)
# ---------------------------------------------------------------------------
def _worker(run_id: str, req: RunRequest) -> None:
    _update(run_id, status="running")
    try:
        before = {p.name for p in RUNS_DIR.iterdir() if RUNS_DIR.exists() and p.is_dir()}

        # If tasks provided, run technique-task mode; otherwise regular competition mode
        if req.tasks:
            # Technique-tasks flow
            _run_technique_tasks(run_id, req, before)
        else:
            # Regular competition flow
            _run_regular_competition(run_id, req, before)

    except Exception as exc:
        _update(run_id, status="failed", message=str(exc))


def _run_regular_competition(run_id: str, req: RunRequest, before: set) -> None:
    """Run the regular competition flow."""
    # 1. prepare
    prepare_cmd = [sys.executable, "-m", "mlebench.cli", "prepare", "--list", req.competition_set]
    if req.lite:
        prepare_cmd.append("--lite")
    if req.data_dir:
        prepare_cmd.extend(["--data-dir", req.data_dir])
    _run_cmd(prepare_cmd, run_id)

    # 2. run_agent.py
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as tmp:
        # copy competition_set to temp so we have a clean path
        tmp.write((PROJECT_ROOT / req.competition_set).read_text())
        tmp.flush()
        agent_cmd = [
            sys.executable, "run_agent.py",
            "--agent-id", req.agent_id,
            "--competition-set", tmp.name,
            "--n-seeds", str(req.n_seeds),
            "--n-workers", str(req.n_workers),
        ]
        if req.retain:
            agent_cmd.append("--retain")
        if req.data_dir:
            agent_cmd.extend(["--data-dir", req.data_dir])
        _run_cmd(agent_cmd, run_id)

    run_group = _discover_new_run_group(before)
    if run_group is None:
        raise RuntimeError("Could not find new run group after agent run")

    run_group_dir = RUNS_DIR / run_group

    # 3. make_submission
    submission_path = run_group_dir / "submission.jsonl"
    make_sub_cmd = [
        sys.executable, "experiments/make_submission.py",
        "--metadata", str(run_group_dir / "metadata.json"),
        "--output", str(submission_path),
    ]
    _run_cmd(make_sub_cmd, run_id)

    # 4. grade
    grade_dir = run_group_dir / "grading"
    grade_cmd = [
        sys.executable, "-m", "mlebench.cli", "grade",
        "--submission", str(submission_path),
        "--output-dir", str(grade_dir),
    ]
    if req.lite:
        grade_cmd.append("--lite")
    if req.data_dir:
        grade_cmd.extend(["--data-dir", req.data_dir])
    _run_cmd(grade_cmd, run_id)

    _update(run_id, status="completed", run_group=run_group, run_dir=str(run_group_dir.relative_to(PROJECT_ROOT)))


def _run_technique_tasks(run_id: str, req: RunRequest, before: set) -> None:
    """Run technique-tasks flow: one container per (competition, task) pair."""
    from mlebench.tool_tasks.grader import grade_all_tasks
    
    # 1. prepare competitions
    prepare_cmd = [sys.executable, "-m", "mlebench.cli", "prepare", "--list", req.competition_set]
    if req.lite:
        prepare_cmd.append("--lite")
    if req.data_dir:
        prepare_cmd.extend(["--data-dir", req.data_dir])
    _run_cmd(prepare_cmd, run_id)
    
    tasks = req.tasks or ["imbalance", "missing", "encoding", "cv", "scaling", "leakage"]
    
    # Read competition IDs
    competition_ids = (PROJECT_ROOT / req.competition_set).read_text().strip().splitlines()
    competition_ids = [c.strip() for c in competition_ids if c.strip()]
    
    all_run_groups = []
    
    # 2. For each task, run agent on all competitions
    for task_name in tasks:
        _append_log(run_id, {"stage": f"Running technique-task: {task_name}"})
        
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as tmp:
            tmp.write((PROJECT_ROOT / req.competition_set).read_text())
            tmp.flush()
            
            agent_cmd = [
                sys.executable, "run_agent.py",
                "--agent-id", req.agent_id,
                "--competition-set", tmp.name,
                "--n-seeds", str(req.n_seeds),
                "--n-workers", str(req.n_workers),
                "--technique-task", task_name,
            ]
            if req.retain:
                agent_cmd.append("--retain")
            if req.data_dir:
                agent_cmd.extend(["--data-dir", req.data_dir])
            _run_cmd(agent_cmd, run_id)
        
        # Discover the run group created for this task
        run_group = _discover_new_run_group(before)
        if run_group:
            all_run_groups.append(run_group)
            before.add(run_group)  # So we don't rediscover it
    
    if not all_run_groups:
        raise RuntimeError("Could not find any run groups after technique-task runs")
    
    # Use the first run group as the main one (or we could create a summary dir)
    main_run_group = all_run_groups[0]
    run_group_dir = RUNS_DIR / main_run_group
    
    # 3. Grade technique-tasks for each competition
    all_grades = {}
    
    for rg in all_run_groups:
        rg_dir = RUNS_DIR / rg
        for comp_dir in rg_dir.iterdir():
            if not comp_dir.is_dir():
                continue
            submission_dir = comp_dir / "submission"
            if submission_dir.exists():
                grades = grade_all_tasks(submission_dir, tasks)
                comp_name = comp_dir.name.split("_")[0]  # Extract competition name
                if comp_name not in all_grades:
                    all_grades[comp_name] = {}
                all_grades[comp_name].update(grades)
    
    # Save technique-task grades
    grade_file = run_group_dir / "technique_grades.json"
    grade_file.write_text(json.dumps(all_grades, indent=2))
    
    _update(run_id, status="completed", run_group=main_run_group, run_dir=str(run_group_dir.relative_to(PROJECT_ROOT)))


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.post("/runs")
def create_run(req: RunRequest) -> Dict[str, Any]:
    run_id = str(uuid.uuid4())
    record = RunRecord(
        run_id=run_id,
        status="queued",
        created_at=_now(),
        updated_at=_now(),
        request=req,
    )
    with _STATE_LOCK:
        _RUN_STATE[run_id] = record

    threading.Thread(target=_worker, args=(run_id, req), daemon=True).start()
    return {"run_id": run_id, "status": "queued"}


@app.get("/runs")
def list_runs() -> List[Dict[str, Any]]:
    with _STATE_LOCK:
        return [r.model_dump() for r in sorted(_RUN_STATE.values(), key=lambda x: x.created_at, reverse=True)]


@app.get("/runs/{run_id}")
def get_run(run_id: str) -> Dict[str, Any]:
    with _STATE_LOCK:
        rec = _RUN_STATE.get(run_id)
    if rec is None:
        raise HTTPException(404, "run not found")
    return rec.model_dump()


@app.get("/runs/{run_id}/summary")
def get_summary(run_id: str) -> Dict[str, Any]:
    with _STATE_LOCK:
        rec = _RUN_STATE.get(run_id)
    if rec is None:
        raise HTTPException(404, "run not found")
    if rec.status != "completed":
        raise HTTPException(409, f"run not completed yet, status={rec.status}")
    run_group_dir = RUNS_DIR / rec.run_group
    grading_files = sorted(str(p.relative_to(PROJECT_ROOT)) for p in run_group_dir.glob("**/*grading*.json") if p.is_file())
    return {
        "run_id": run_id,
        "run_group": rec.run_group,
        "run_dir": rec.run_dir,
        "grading_reports": grading_files,
    }


@app.get("/runs/{run_id}/artifacts")
def get_artifacts(run_id: str) -> Dict[str, Any]:
    """Return paths to all artifacts (rollouts, logs, submissions, grading reports)."""
    with _STATE_LOCK:
        rec = _RUN_STATE.get(run_id)
    if rec is None:
        raise HTTPException(404, "run not found")
    if rec.status != "completed":
        raise HTTPException(409, f"run not completed yet, status={rec.status}")
    
    run_group_dir = RUNS_DIR / rec.run_group
    
    # Collect artifacts by type
    artifacts = {
        "run_id": run_id,
        "run_group": rec.run_group,
        "run_dir": rec.run_dir,
        "submissions": [],
        "grading_reports": [],
        "logs": [],
        "rollouts": [],       # agent decision traces / trajectories
        "code": [],           # agent-generated code
        "metadata": [],
    }
    
    for p in run_group_dir.rglob("*"):
        if not p.is_file():
            continue
        rel = str(p.relative_to(PROJECT_ROOT))
        name = p.name.lower()
        parent_name = p.parent.name.lower()
        
        if "submission" in name and p.suffix in (".csv", ".jsonl"):
            artifacts["submissions"].append(rel)
        elif "grading" in name and p.suffix == ".json":
            artifacts["grading_reports"].append(rel)
        elif p.suffix == ".log" or (name.endswith(".log") and parent_name != "logs"):
            artifacts["logs"].append(rel)
        elif "metadata" in name and p.suffix == ".json":
            artifacts["metadata"].append(rel)
        elif parent_name == "logs" or "rollout" in name or "trajectory" in name or "journal" in name:
            # AIDE writes rollouts/trajectories to logs/ directory
            artifacts["rollouts"].append(rel)
        elif parent_name in ("code", "best_solution", "workspaces"):
            # Agent-generated code artifacts
            artifacts["code"].append(rel)
    
    # Sort all lists
    for key in artifacts:
        if isinstance(artifacts[key], list):
            artifacts[key] = sorted(artifacts[key])
    
    return artifacts


@app.get("/competitions")
def list_competitions() -> List[str]:
    from mlebench.registry import registry
    return registry.list_competition_ids()


# ---------------------------------------------------------------------------
# Technique Tasks (Tool Tasks)
# ---------------------------------------------------------------------------
TECHNIQUE_TASKS = ["imbalance", "missing", "encoding", "cv", "scaling", "leakage"]


class TechniqueTaskRequest(BaseModel):
    """Request to run technique-tasks across competitions."""
    agent_id: str = Field("dummy", description="Agent ID")
    competitions: List[str] = Field(
        default_factory=list,
        description="Competition IDs to run technique-tasks on. Empty = use dev.txt"
    )
    tasks: List[str] = Field(
        default_factory=lambda: TECHNIQUE_TASKS,
        description="Which technique-tasks to run"
    )
    data_dir: Optional[str] = Field(None)


@app.get("/technique-tasks")
def list_technique_tasks() -> Dict[str, Any]:
    """List available technique-tasks."""
    return {
        "available": TECHNIQUE_TASKS,
        "descriptions": {
            "imbalance": "Detect class imbalance and choose handling strategy",
            "missing": "Analyze missing values and choose imputation strategy", 
            "encoding": "Analyze categorical features and choose encoding method",
        }
    }


@app.post("/runs/technique")
def create_technique_run(req: TechniqueTaskRequest) -> Dict[str, Any]:
    """
    Run technique-tasks across multiple competitions.
    
    This mounts ALL competition data at once, so the agent can iterate
    over competitions efficiently without separate container launches.
    """
    run_id = str(uuid.uuid4())
    
    # For now, return a stub - full implementation would:
    # 1. Create container with full data_dir mounted to /data/
    # 2. Pass COMPETITIONS env var with list of competition IDs
    # 3. Pass TECHNIQUE_TASKS env var with tasks to run
    # 4. Agent iterates, writes {task}_{competition}_analysis.json
    # 5. Grade each output
    
    return {
        "run_id": run_id,
        "status": "not_implemented",
        "message": "Technique-task runs coming soon. Use /runs for regular competition runs.",
        "request": req.model_dump(),
    }


@app.get("/files/{file_path:path}")
def download_file(file_path: str) -> FileResponse:
    """Download a file from the runs directory."""
    full_path = PROJECT_ROOT / file_path
    # Security: ensure path is within runs directory
    try:
        full_path.resolve().relative_to((PROJECT_ROOT / "runs").resolve())
    except ValueError:
        raise HTTPException(403, "access denied - path must be within runs/")
    if not full_path.is_file():
        raise HTTPException(404, "file not found")
    return FileResponse(full_path, filename=full_path.name)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)
