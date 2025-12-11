"""
Test suite for the MLE-Bench SDK client.

Run with:
    pytest sdk/test_client.py -v

For integration tests (requires running server):
    pytest sdk/test_client.py -v -m integration
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

# Allow running as script or via pytest
try:
    from sdk.client import Client
except ModuleNotFoundError:
    # When running directly as a script
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from sdk.client import Client


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def client() -> Client:
    """Return a Client instance pointing to default localhost."""
    return Client("http://127.0.0.1:8000")


@pytest.fixture
def mock_response() -> MagicMock:
    """Create a mock response object."""
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    return mock


# =============================================================================
# Unit Tests (mocked, no server required)
# =============================================================================


class TestClientInit:
    """Test client initialization."""

    def test_default_url(self) -> None:
        client = Client()
        assert client.base_url == "http://127.0.0.1:8000"

    def test_custom_url(self) -> None:
        client = Client("http://example.com:9000")
        assert client.base_url == "http://example.com:9000"

    def test_strips_trailing_slash(self) -> None:
        client = Client("http://example.com:9000/")
        assert client.base_url == "http://example.com:9000"


class TestRunMethod:
    """Test the run() method."""

    @patch("sdk.client.requests.post")
    def test_run_default_params(self, mock_post: MagicMock, mock_response: MagicMock) -> None:
        mock_response.json.return_value = {"run_id": "test-run-123"}
        mock_post.return_value = mock_response

        client = Client()
        run_id = client.run()

        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "http://127.0.0.1:8000/runs"
        payload = call_args[1]["json"]
        assert payload["competition_set"] == "experiments/splits/low.txt"
        assert payload["agent_id"] == "dummy"
        assert payload["lite"] is True
        assert run_id == "test-run-123"

    @patch("sdk.client.requests.post")
    def test_run_custom_params(self, mock_post: MagicMock, mock_response: MagicMock) -> None:
        mock_response.json.return_value = {"run_id": "custom-run-456"}
        mock_post.return_value = mock_response

        client = Client()
        run_id = client.run(
            competition_set="experiments/splits/dev.txt",
            agent_id="aide",
            lite=False,
            n_seeds=3,
            n_workers=2,
            data_dir="/data/custom",
            notes="test notes",
        )

        payload = mock_post.call_args[1]["json"]
        assert payload["competition_set"] == "experiments/splits/dev.txt"
        assert payload["agent_id"] == "aide"
        assert payload["lite"] is False
        assert payload["n_seeds"] == 3
        assert payload["n_workers"] == 2
        assert payload["data_dir"] == "/data/custom"
        assert payload["notes"] == "test notes"
        assert run_id == "custom-run-456"


class TestGetRun:
    """Test get_run() method."""

    @patch("sdk.client.requests.get")
    def test_get_run(self, mock_get: MagicMock, mock_response: MagicMock) -> None:
        expected = {
            "run_id": "abc123",
            "status": "running",
            "request": {"agent_id": "dummy"},
        }
        mock_response.json.return_value = expected
        mock_get.return_value = mock_response

        client = Client()
        result = client.get_run("abc123")

        mock_get.assert_called_once_with(
            "http://127.0.0.1:8000/runs/abc123", timeout=60
        )
        assert result == expected


class TestGetRunSummary:
    """Test get_run_summary() method."""

    @patch("sdk.client.requests.get")
    def test_get_run_summary(self, mock_get: MagicMock, mock_response: MagicMock) -> None:
        expected = {
            "run_id": "abc123",
            "run_group": "2025-01-01_run-group_dummy",
            "grading_reports": ["report.json"],
        }
        mock_response.json.return_value = expected
        mock_get.return_value = mock_response

        client = Client()
        result = client.get_run_summary("abc123")

        mock_get.assert_called_once_with(
            "http://127.0.0.1:8000/runs/abc123/summary", timeout=60
        )
        assert result == expected


class TestListRuns:
    """Test list_runs() method."""

    @patch("sdk.client.requests.get")
    def test_list_runs(self, mock_get: MagicMock, mock_response: MagicMock) -> None:
        expected = [
            {"run_id": "run1", "status": "completed"},
            {"run_id": "run2", "status": "running"},
        ]
        mock_response.json.return_value = expected
        mock_get.return_value = mock_response

        client = Client()
        result = client.list_runs()

        mock_get.assert_called_once_with("http://127.0.0.1:8000/runs", timeout=60)
        assert result == expected


class TestListCompetitions:
    """Test list_competitions() method."""

    @patch("sdk.client.requests.get")
    def test_list_competitions(self, mock_get: MagicMock, mock_response: MagicMock) -> None:
        expected = ["titanic", "house-prices", "dogs-vs-cats"]
        mock_response.json.return_value = expected
        mock_get.return_value = mock_response

        client = Client()
        result = client.list_competitions()

        mock_get.assert_called_once_with(
            "http://127.0.0.1:8000/competitions", timeout=60
        )
        assert result == expected


class TestHealth:
    """Test health() method."""

    @patch("sdk.client.requests.get")
    def test_health(self, mock_get: MagicMock, mock_response: MagicMock) -> None:
        expected = {"status": "ok"}
        mock_response.json.return_value = expected
        mock_get.return_value = mock_response

        client = Client()
        result = client.health()

        mock_get.assert_called_once_with("http://127.0.0.1:8000/health", timeout=10)
        assert result == expected


class TestWaitForCompletion:
    """Test wait_for_completion() method."""

    @patch("sdk.client.requests.get")
    def test_wait_for_completion_immediate(
        self, mock_get: MagicMock, mock_response: MagicMock
    ) -> None:
        mock_response.json.return_value = {"run_id": "abc", "status": "completed"}
        mock_get.return_value = mock_response

        client = Client()
        result = client.wait_for_completion("abc", poll_interval=0.1)

        assert result["status"] == "completed"

    @patch("sdk.client.requests.get")
    def test_wait_for_completion_polls(
        self, mock_get: MagicMock, mock_response: MagicMock
    ) -> None:
        # First call: running, second call: completed
        responses = [
            {"run_id": "abc", "status": "running"},
            {"run_id": "abc", "status": "completed"},
        ]
        mock_response.json.side_effect = responses
        mock_get.return_value = mock_response

        client = Client()
        result = client.wait_for_completion("abc", poll_interval=0.1)

        assert result["status"] == "completed"
        assert mock_get.call_count == 2

    @patch("sdk.client.requests.get")
    def test_wait_for_completion_failed(
        self, mock_get: MagicMock, mock_response: MagicMock
    ) -> None:
        mock_response.json.return_value = {"run_id": "abc", "status": "failed"}
        mock_get.return_value = mock_response

        client = Client()
        result = client.wait_for_completion("abc", poll_interval=0.1)

        assert result["status"] == "failed"

    @patch("sdk.client.requests.get")
    def test_wait_for_completion_timeout(
        self, mock_get: MagicMock, mock_response: MagicMock
    ) -> None:
        mock_response.json.return_value = {"run_id": "abc", "status": "running"}
        mock_get.return_value = mock_response

        client = Client()
        with pytest.raises(TimeoutError):
            client.wait_for_completion("abc", poll_interval=0.1, timeout=0.3)


class TestRunLiteExistingTasks:
    """Test run_lite_existing_tasks() convenience method."""

    @patch("sdk.client.requests.post")
    def test_run_lite_existing_tasks(
        self, mock_post: MagicMock, mock_response: MagicMock
    ) -> None:
        mock_response.json.return_value = {"run_id": "lite-run"}
        mock_post.return_value = mock_response

        client = Client()
        run_id = client.run_lite_existing_tasks()

        payload = mock_post.call_args[1]["json"]
        assert payload["lite"] is True
        assert run_id == "lite-run"


# =============================================================================
# Integration Tests (require running server)
# =============================================================================


@pytest.fixture
def live_client() -> Generator[Client, None, None]:
    """
    Provide a client for integration tests.
    Skip if server is not running.
    """
    client = Client("http://127.0.0.1:8000")
    try:
        client.health()
    except Exception:
        pytest.skip("Server not running at http://127.0.0.1:8000")
    yield client


@pytest.mark.integration
class TestIntegration:
    """Integration tests requiring a live server."""

    def test_health_check(self, live_client: Client) -> None:
        """Verify server is healthy."""
        result = live_client.health()
        assert result["status"] == "ok"

    def test_list_competitions(self, live_client: Client) -> None:
        """Verify competitions endpoint returns data."""
        comps = live_client.list_competitions()
        assert isinstance(comps, list)
        assert len(comps) > 0

    def test_list_runs(self, live_client: Client) -> None:
        """Verify runs endpoint works."""
        runs = live_client.list_runs()
        assert isinstance(runs, list)

    def test_full_run_workflow(self, live_client: Client) -> None:
        """
        End-to-end test: trigger a run, wait for completion, get summary.

        This test runs the dummy agent on dev.txt competitions.
        It may take several minutes to complete.
        """
        # Trigger a run
        run_id = live_client.run(
            competition_set="experiments/splits/dev.txt",
            agent_id="dummy",
            lite=False,
        )
        assert run_id is not None
        print(f"Started run: {run_id}")

        # Wait for completion (up to 30 minutes for full run)
        result = live_client.wait_for_completion(
            run_id, poll_interval=10.0, timeout=1800.0
        )
        assert result["status"] == "completed", f"Run failed: {result}"
        print(f"Run completed with status: {result['status']}")

        # Get summary
        summary = live_client.get_run_summary(run_id)
        assert "run_group" in summary
        assert "grading_reports" in summary
        print(f"Summary: {summary}")


# =============================================================================
# Run as script for quick manual testing
# =============================================================================


def main() -> None:
    """Quick manual test against a running server."""
    print("Testing SDK client against http://127.0.0.1:8000")
    print("=" * 60)

    client = Client()

    # Health check
    print("\n1. Health check...")
    try:
        health = client.health()
        print(f"   ✓ Server healthy: {health}")
    except Exception as e:
        print(f"   ✗ Server not reachable: {e}")
        return

    # List competitions
    print("\n2. Listing competitions...")
    try:
        comps = client.list_competitions()
        print(f"   ✓ Found {len(comps)} competitions")
        print(f"   First 5: {comps[:5]}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")

    # List runs
    print("\n3. Listing existing runs...")
    try:
        runs = client.list_runs()
        print(f"   ✓ Found {len(runs)} runs")
    except Exception as e:
        print(f"   ✗ Failed: {e}")

    # Trigger a new run
    print("\n4. Triggering a new run (dummy agent, dev.txt)...")
    try:
        run_id = client.run(
            competition_set="experiments/splits/dev.txt",
            agent_id="dummy",
            lite=False,
        )
        print(f"   ✓ Started run: {run_id}")

        # Poll for status
        print("\n5. Waiting for completion (this may take a while)...")
        while True:
            rec = client.get_run(run_id)
            status = rec["status"]
            print(f"   ... status: {status}")
            if status in ("completed", "failed"):
                break
            time.sleep(10)

        if status == "completed":
            print("\n6. Fetching summary...")
            summary = client.get_run_summary(run_id)
            print(f"   ✓ Summary: {summary}")
        else:
            print(f"\n   ✗ Run failed!")

    except Exception as e:
        print(f"   ✗ Failed: {e}")

    print("\n" + "=" * 60)
    print("Done!")


if __name__ == "__main__":
    main()
