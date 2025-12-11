#!/usr/bin/env bash
# demo_run.sh – spin up the local server, run a quick SDK test, then shut down.
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Use conda env with Python 3.11+ (adjust CONDA_ENV if needed)
CONDA_ENV="${CONDA_ENV:-fleet}"
LOG_FILE="$PROJECT_ROOT/demo_uvicorn.log"

echo "==> Activating conda env: $CONDA_ENV"
eval "$(conda shell.bash hook)"
conda activate "$CONDA_ENV"

echo "==> Installing dependencies..."
pip install --upgrade pip
pip install -e "$PROJECT_ROOT"
pip install fastapi uvicorn requests

echo "==> Starting uvicorn server in background..."
uvicorn server:app --host 127.0.0.1 --port 8000 > "$LOG_FILE" 2>&1 &
SERVER_PID=$!
sleep 3

cleanup() {
    echo "==> Stopping server (pid $SERVER_PID)..."
    kill "$SERVER_PID" 2>/dev/null || true
}
trap cleanup EXIT

echo "==> Running SDK demo..."
python <<'PYCODE'
import time
from pprint import pprint
from sdk.client import Client

client = Client("http://127.0.0.1:8000")

# Health check
print("Health:", client.health())

# List competitions (optional introspection)
comps = client.list_competitions()
print(f"Available competitions: {len(comps)} total")

# Trigger a run with dummy agent on dev.txt competitions
print("\nStarting run with dummy agent on dev.txt...")
run_id = client.run(competition_set="experiments/splits/dev.txt", agent_id="dummy", lite=False)
print(f"Run ID: {run_id}")

# Poll for completion
print("Waiting for completion...")
rec = client.wait_for_completion(run_id, poll_interval=5, timeout=600)
print(f"Final status: {rec['status']}")

if rec["status"] == "completed":
    summary = client.get_run_summary(run_id)
    print("\nRun summary:")
    pprint(summary)
else:
    print("Run failed:")
    pprint(rec.get("message"))
PYCODE

echo ""
echo "==> Demo complete. Logs saved to $LOG_FILE"
