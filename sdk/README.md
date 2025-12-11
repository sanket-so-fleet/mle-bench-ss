# MLE-Bench SDK

Python SDK for interacting with the MLE-Bench server.

## Installation

```bash
# From the sdk/ directory
pip install -e .

# Or install directly
pip install /path/to/mle-bench-ss/sdk
```

## Quick Start

```python
from mlebench_sdk import Client

# Connect to local server
client = Client("http://127.0.0.1:8000")

# Check server health
print(client.health())

# List available competitions
competitions = client.list_competitions()
print(f"Available: {len(competitions)} competitions")

# List technique-tasks
tasks = client.list_technique_tasks()
print(f"Available: {len(tasks)} technique-tasks")

# Start a run
run_id = client.run(
    agent_id="aide",
    competition_set="experiments/splits/dev.txt",
    lite=True,
)
print(f"Started run: {run_id}")

# Poll until completion (prints status every 5 seconds)
result = client.wait_for_completion(run_id, poll_interval=5.0)
print(f"Final status: {result['status']}")

# Get run summary
summary = client.get_run_summary(run_id)
print(summary)
```

## Running Technique-Tasks

```python
# Run all technique-tasks
run_id = client.run(
    agent_id="aide",
    technique_tasks=True,
)

# Run specific technique-tasks
run_id = client.run(
    agent_id="aide",
    technique_tasks=True,
    tasks=["missing-values", "feature-scaling"],
)

result = client.wait_for_completion(run_id)
```

## API Reference

### `Client(base_url: str = "http://127.0.0.1:8000")`

Create a client connected to the MLE-Bench server.

### Methods

| Method | Description |
|--------|-------------|
| `run(...)` | Start a new benchmark run |
| `get_run(run_id)` | Get full run record |
| `get_run_summary(run_id)` | Get summary for completed run |
| `list_runs()` | List all runs |
| `list_competitions()` | List available competitions |
| `list_technique_tasks()` | List available technique-tasks |
| `health()` | Check server health |
| `wait_for_completion(run_id, poll_interval, timeout)` | Poll until run finishes |

### `run()` Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `agent_id` | str | "dummy" | Agent to use |
| `competition_set` | str | "experiments/splits/low.txt" | Path to competition list |
| `lite` | bool | True | Use lite mode |
| `n_seeds` | int | 1 | Number of seeds |
| `n_workers` | int | 1 | Parallel workers |
| `retain` | bool | False | Keep containers after run |
| `technique_tasks` | bool | False | Run technique-tasks instead |
| `tasks` | List[str] | None | Specific tasks (if technique_tasks=True) |
