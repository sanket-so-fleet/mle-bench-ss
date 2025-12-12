# MLE BENCH REDUX

### See "writeup_MLE-Bench Redux.md" for detailed write up.

### See "MLE_BENCH_README.md" for original repo's readme.
---

## Quick Start

```bash
# 1. Add your OpenAI API key to .env
echo "OPENAI_API_KEY=sk-your-key" > .env

# 2. Set up environment
./setup.sh

# 3. Start the server separately (see the section below)
#    Start the server in a separate terminal after activating the environment:
#    python server.py

# 4. Open demo.ipynb in VS Code or Jupyter. KNOWN KAGGLE BUG: Sometimes the bulk data download at kaggle returns a error 500....so any runs will fail in that case.
```

---

## Start the server and run demo notebook!

Start the FastAPI demo server in a separate terminal after activating the environment. The `setup.sh` script does not start the server automatically.

- Activate your environment:
    - If using Conda: `conda activate mlebench-env`
    - If using venv: `source .venv/bin/activate`
- Start the server:

```
python server.py
```

Keep the server terminal running while you open and run `demo.ipynb`.



## Prerequisites

| Requirement | Notes |
|-------------|-------|
| **Python 3.11+** | Check with `python --version` |
| **Docker** | Docker Desktop or Colima |
| **Kaggle Credentials** | `~/.kaggle/kaggle.json` ([get it here](https://www.kaggle.com/settings)) |
| **OpenAI API Key** | For AIDE agent |

---

## Choose Competitions

Edit `experiments/splits/dev.txt` to select which competitions to run:

```
random-acts-of-pizza
spooky-author-identification
dogs-vs-cats-redux-kernels-edition
```

See all available competitions with `mlebench list`.

---

## Two Modes

### Option A: Competition Runs
Full Kaggle competitions - agent builds models, makes predictions, gets scored.

```python
run_id = client.run(
    agent_id="aide/dev",
    competition_set="experiments/splits/dev.txt",
    lite=True,
)
```

### Option B: Technique-Tasks
Focused ML skill assessments on the same data.

```python
run_id = client.run(
    agent_id="aide/dev",
    competition_set="experiments/splits/dev.txt",
    lite=True,
    technique_tasks=True,
    tasks=["imbalance", "missing", "encoding"],
)
```

**Available tasks:** `imbalance`, `missing`, `encoding`, `cv`, `scaling`, `leakage`

---
## AIDE Model Steps

- **Dev image (`aide/dev`)**: The demo uses `aide/dev`, which is configured to run with `agent.steps: 1` (fast, developer-friendly). This keeps runs quick for demos.

- **Change number of steps**: Edit `agents/aide/config.yaml` and adjust the `agent.steps` value under the agent `kwargs` you want to run (for example change `1` → `8` or `500`).
-
- **Rebuild the agent image**:

    ```bash
    cd agents/aide
    docker build -t aide/dev .
    ```

    **Warning:** building the agent image is slow — expect it to take many minutes and consume multiple gigabytes of disk and network bandwidth. If you want to avoid the long build, use the prebuilt `aide/dev` image (if available) or run the lightweight demo settings.

    Then re-tag and push the image if you use a registry, and restart the demo server.

- **Alternate model**: To try an older agent preconfigured with more internal search steps, set `agent_id="aide/gpt-4-turbo-dev"` in the notebook — that agent is typically configured to use 8 steps.

---

## SDK Reference

```python
from sdk import Client
client = Client()  # defaults to localhost:8000

# Start a run
run_id = client.run(agent_id="aide/dev", competition_set="experiments/splits/dev.txt", lite=True)

# Wait for completion
result = client.wait_for_completion(run_id)

# Get details
run = client.get_run(run_id)
summary = client.get_run_summary(run_id)
```

---

## Output Artifacts

All results are saved to `runs/<timestamp>_run-group_<agent>/`:

```
runs/2025-12-11T03-48-13-UTC_run-group_aide/
├── random-acts-of-pizza_<uuid>/
│   ├── submission/           # Agent's output files
│   ├── code/                 # Agent's code
│   └── logs/                 # Execution logs
├── technique_grades.json     # Technique-task scores (if applicable)
├── grading_report.json       # Competition scores (if applicable)
└── metadata.json
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Docker not found | Install Docker Desktop or run `colima start` |
| Server not responding | Check if `python server.py` is running |
| Grading fails | Check `runs/*/technique_grades.json` for error messages |
| Agent times out | Increase timeout or reduce competition size |