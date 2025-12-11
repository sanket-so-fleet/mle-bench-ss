"""Simple HTTP client SDK for the local MLE-Bench server."""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import requests


class Client:
    """Wrapper around the local MLE-Bench server endpoints."""

    def __init__(self, base_url: str = "http://127.0.0.1:8000") -> None:
        self.base_url = base_url.rstrip("/")

    # -------------------------------------------------------------------------
    # Core methods
    # -------------------------------------------------------------------------
    def run(
        self,
        *,
        competition_set: str = "experiments/splits/low.txt",
        agent_id: str = "dummy",
        lite: bool = True,
        n_seeds: int = 1,
        n_workers: int = 1,
        retain: bool = False,
        data_dir: Optional[str] = None,
        notes: Optional[str] = None,
        technique_tasks: bool = False,
        tasks: Optional[List[str]] = None,
    ) -> str:
        """Trigger a new run and return the run_id.
        
        Args:
            technique_tasks: If True, run technique-tasks instead of regular competition.
            tasks: Which technique-tasks to run (default: all). Only used if technique_tasks=True.
        """
        payload: Dict[str, Any] = {
            "competition_set": competition_set,
            "agent_id": agent_id,
            "lite": lite,
            "n_seeds": n_seeds,
            "n_workers": n_workers,
            "retain": retain,
            "technique_tasks": technique_tasks,
        }
        if data_dir:
            payload["data_dir"] = data_dir
        if notes:
            payload["notes"] = notes
        if tasks:
            payload["tasks"] = tasks

        resp = requests.post(f"{self.base_url}/runs", json=payload, timeout=300)
        resp.raise_for_status()
        return resp.json()["run_id"]

    def get_run(self, run_id: str) -> Dict[str, Any]:
        """Fetch full run record (including status and logs)."""
        resp = requests.get(f"{self.base_url}/runs/{run_id}", timeout=60)
        resp.raise_for_status()
        return resp.json()

    def get_run_summary(self, run_id: str) -> Dict[str, Any]:
        """Get summary for a completed run (grading reports, paths, etc.)."""
        resp = requests.get(f"{self.base_url}/runs/{run_id}/summary", timeout=60)
        resp.raise_for_status()
        return resp.json()

    def list_runs(self) -> List[Dict[str, Any]]:
        """List all known runs."""
        resp = requests.get(f"{self.base_url}/runs", timeout=60)
        resp.raise_for_status()
        return resp.json()

    def list_competitions(self) -> List[str]:
        """Return available competition IDs from the registry."""
        resp = requests.get(f"{self.base_url}/competitions", timeout=60)
        resp.raise_for_status()
        return resp.json()

    def list_technique_tasks(self) -> List[str]:
        """Return available technique-task IDs."""
        resp = requests.get(f"{self.base_url}/technique-tasks", timeout=60)
        resp.raise_for_status()
        return resp.json()

    def health(self) -> Dict[str, str]:
        """Check server health."""
        resp = requests.get(f"{self.base_url}/health", timeout=10)
        resp.raise_for_status()
        return resp.json()

    # -------------------------------------------------------------------------
    # Convenience helpers
    # -------------------------------------------------------------------------
    def run_lite_existing_tasks(
        self,
        competition_set: str = "experiments/splits/low.txt",
        agent_id: str = "dummy",
    ) -> str:
        """Shortcut matching the fleet.txt example."""
        return self.run(competition_set=competition_set, agent_id=agent_id, lite=True)

    def wait_for_completion(self, run_id: str, poll_interval: float = 5.0, timeout: float = 3600.0) -> Dict[str, Any]:
        """Poll until run completes or fails, then return the run record."""
        start = time.time()
        poll_count = 0
        while True:
            poll_count += 1
            rec = self.get_run(run_id)
            elapsed = time.time() - start
            print(f"[Poll {poll_count}] Run {run_id[:8]}... status: {rec['status']} (elapsed: {elapsed:.1f}s)")
            if rec["status"] in ("completed", "failed"):
                print(f"✓ Run finished with status: {rec['status']}")
                return rec
            if elapsed > timeout:
                raise TimeoutError(f"Run {run_id} did not complete within {timeout}s")
            time.sleep(poll_interval)
