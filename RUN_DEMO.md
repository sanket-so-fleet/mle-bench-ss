# Local Demo Guide

This document explains how to run the local MLE-Bench server + SDK workflow **without containerizing the benchmark itself**. Agent containers still run on your host Docker daemon.

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| **Python 3.11+** | Project requires `>=3.11` per `pyproject.toml`. |
| **Docker Desktop** | Needed only when you trigger *real* runs (agent containers). |
| **Prepared Datasets** | For any competition you want to run, first execute `mlebench prepare -c <competition-id>`. |
| **Kaggle Credentials** | `~/.kaggle/kaggle.json` must be present for dataset downloads. |

---

## Quick Start (one-liner)

```bash
./demo_run.sh
```

This script will:

1. Create a `.venv` and install the project + FastAPI/Uvicorn/requests.
2. Start the server at `http://127.0.0.1:8000`.
3. Use the SDK to trigger a run with the `dummy` agent on `experiments/splits/low.txt`.
4. Poll until completion and print the summary.
5. Shut down the server automatically.

Logs are written to `demo_uvicorn.log`.

---

## Manual Usage

### 1. Start the server

```bash
# activate your venv or install deps globally
pip install -e . && pip install fastapi uvicorn requests

# run locally
uvicorn server:app --host 127.0.0.1 --port 8000
```

### 2. Use the SDK

```python
from sdk.client import Client

client = Client("http://127.0.0.1:8000")

# ===== Option A: Competition Run (Original MLE-Bench) =====
run_id = client.run(
    agent_id="aide/dev",
    competition_set="experiments/splits/dev.txt",
    lite=True,
    technique_tasks=False,  # Regular competition run
)
print("Competition run started:", run_id)

# ===== Option B: Technique-Tasks (ML Skill Assessment) =====
run_id = client.run(
    agent_id="aide/dev",
    competition_set="experiments/splits/dev.txt",
    lite=True,
    technique_tasks=True,
    tasks=["imbalance", "missing", "encoding"],
)
print("Technique-tasks run started:", run_id)

# Wait and get results
rec = client.wait_for_completion(run_id)
print("Status:", rec["status"])

if rec["status"] == "completed":
    summary = client.get_run_summary(run_id)
    print(summary)
```

---

## SDK Methods

| Method | Description |
|--------|-------------|
| `run(...)` | POST `/runs` – triggers prepare → run_agent → grade. Returns `run_id`. |
| `get_run(run_id)` | GET `/runs/{run_id}` – fetch full run record including logs. |
| `get_run_summary(run_id)` | GET `/runs/{run_id}/summary` – returns grading reports once complete. |
| `list_runs()` | GET `/runs` – list all runs tracked by the server session. |
| `list_competitions()` | GET `/competitions` – returns available competition IDs from registry. |
| `wait_for_completion(run_id)` | Helper that polls until run finishes (completed/failed). |

### Run Parameters

| Parameter | Description |
|-----------|-------------|
| `agent_id` | Agent to use (e.g., `aide/dev`, `dummy`) |
| `competition_set` | Path to competition list (e.g., `experiments/splits/dev.txt`) |
| `lite` | Use lite mode for faster runs |
| `technique_tasks` | Enable technique-task mode (default: False) |
| `tasks` | List of technique tasks: `imbalance`, `missing`, `encoding`, `cv`, `scaling`, `leakage` |

---

## Server Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/runs` | POST | Create a new run. Body mirrors `RunRequest`. |
| `/runs` | GET | List all runs. |
| `/runs/{run_id}` | GET | Get status + logs for one run. |
| `/runs/{run_id}/summary` | GET | Get grading results (only once completed). |
| `/competitions` | GET | List competition IDs. |
| `/health` | GET | Simple health-check. |

---

## Notes

* **No container wraps the server.** It runs natively so it can shell out to `run_agent.py`, which in turn spawns agent containers on your host Docker daemon.
* All artefacts land in `runs/<run_group>/` – submissions, metadata, grading reports.
* State is held in-memory; restarting the server loses run history (fine for a demo).




Would the grade server interfere with the bench server....