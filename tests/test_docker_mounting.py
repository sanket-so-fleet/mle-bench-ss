#!/usr/bin/env python3
"""
Test Docker mounting for technique-tasks.

This test:
1. Creates a container with all competition data mounted to /data/
2. Runs a script inside that lists what's available
3. Verifies the mount structure works
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def get_data_dir():
    """Get the mlebench data directory."""
    try:
        from mlebench.registry import registry
        return registry.get_data_dir()
    except Exception as e:
        # Fallback to common location
        return Path.home() / ".cache" / "mlebench"


def test_docker_available():
    """Check Docker is available."""
    result = subprocess.run(["docker", "info"], capture_output=True)
    if result.returncode != 0:
        print("✗ Docker not available or not running")
        return False
    print("✓ Docker is available")
    return True


def test_base_image_exists():
    """Check mlebench-env image exists."""
    result = subprocess.run(
        ["docker", "images", "-q", "mlebench-env"],
        capture_output=True, text=True
    )
    if not result.stdout.strip():
        print("✗ mlebench-env image not found. Build it first:")
        print("  cd environment && docker build -t mlebench-env .")
        return False
    print("✓ mlebench-env image exists")
    return True


def test_single_competition_mount():
    """Test mounting a single competition (traditional way)."""
    data_dir = get_data_dir()
    
    # Find a prepared competition
    prepared = None
    if data_dir.exists():
        for comp_dir in data_dir.iterdir():
            public_dir = comp_dir / "prepared" / "public"
            if public_dir.exists() and (public_dir / "train.csv").exists():
                prepared = comp_dir.name
                break
    
    if not prepared:
        print("⚠ No prepared competitions found. Run: mlebench prepare --lite")
        return True  # Not a failure, just skip
    
    public_dir = data_dir / prepared / "prepared" / "public"
    print(f"  Testing with competition: {prepared}")
    
    # Mount single competition to /home/data (traditional)
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{public_dir}:/home/data:ro",
        "mlebench-env",
        "ls", "-la", "/home/data"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"✗ Single mount failed: {result.stderr}")
        return False
    
    print("✓ Single competition mount works:")
    for line in result.stdout.strip().split("\n")[:5]:
        print(f"    {line}")
    return True


def test_all_competitions_mount():
    """Test mounting all competitions at once (technique-tasks way)."""
    data_dir = get_data_dir()
    
    if not data_dir.exists():
        print(f"⚠ Data dir not found: {data_dir}")
        return True  # Skip
    
    # Mount entire data_dir to /data/
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{data_dir}:/data:ro",
        "mlebench-env",
        "sh", "-c", "ls /data | head -10"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"✗ All-data mount failed: {result.stderr}")
        return False
    
    competitions = result.stdout.strip().split("\n")
    print(f"✓ All competitions mount works ({len(competitions)} visible):")
    for comp in competitions[:5]:
        print(f"    /data/{comp}/")
    return True


def test_technique_task_access():
    """Test that technique-task can access multiple competitions."""
    data_dir = get_data_dir()
    
    if not data_dir.exists():
        print(f"⚠ Data dir not found: {data_dir}")
        return True
    
    # Script to run inside container
    script = '''
import os
import json

data_dir = "/data"
results = {"competitions": [], "errors": []}

for comp_id in os.listdir(data_dir)[:3]:  # Check first 3
    comp_path = os.path.join(data_dir, comp_id, "prepared", "public")
    if os.path.isdir(comp_path):
        files = os.listdir(comp_path)
        has_train = "train.csv" in files
        results["competitions"].append({
            "id": comp_id,
            "path": comp_path,
            "files": files[:5],
            "has_train": has_train
        })
    else:
        results["errors"].append(f"{comp_id}: no prepared/public dir")

print(json.dumps(results, indent=2))
'''
    
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{data_dir}:/data:ro",
        "mlebench-env",
        "python", "-c", script
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"✗ Technique-task access failed: {result.stderr}")
        return False
    
    try:
        data = json.loads(result.stdout)
        print(f"✓ Technique-task can access {len(data['competitions'])} competitions:")
        for comp in data["competitions"]:
            status = "✓" if comp["has_train"] else "✗"
            print(f"    {status} {comp['id']}: {comp['files']}")
        if data["errors"]:
            print(f"  Errors: {data['errors']}")
        return True
    except json.JSONDecodeError:
        print(f"✗ Failed to parse output: {result.stdout}")
        return False


def test_env_var_passing():
    """Test passing competition list via env var."""
    data_dir = get_data_dir()
    
    if not data_dir.exists():
        return True
    
    # Find 2 prepared competitions
    prepared = []
    for comp_dir in data_dir.iterdir():
        if (comp_dir / "prepared" / "public").exists():
            prepared.append(comp_dir.name)
            if len(prepared) >= 2:
                break
    
    if len(prepared) < 2:
        print("⚠ Need at least 2 prepared competitions")
        return True
    
    competitions_str = ",".join(prepared)
    
    script = '''
import os
comps = os.environ.get("COMPETITIONS", "").split(",")
print(f"Received {len(comps)} competitions: {comps}")
for c in comps:
    path = f"/data/{c}/prepared/public"
    exists = os.path.isdir(path)
    print(f"  {c}: {'exists' if exists else 'NOT FOUND'}")
'''
    
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{data_dir}:/data:ro",
        "-e", f"COMPETITIONS={competitions_str}",
        "mlebench-env",
        "python", "-c", script
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"✗ Env var passing failed: {result.stderr}")
        return False
    
    print("✓ Env var passing works:")
    for line in result.stdout.strip().split("\n"):
        print(f"    {line}")
    return True


import json

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Docker Mounting for Technique-Tasks")
    print("=" * 60)
    
    tests = [
        ("Docker available", test_docker_available),
        ("Base image exists", test_base_image_exists),
        ("Single competition mount", test_single_competition_mount),
        ("All competitions mount", test_all_competitions_mount),
        ("Technique-task access", test_technique_task_access),
        ("Env var passing", test_env_var_passing),
    ]
    
    results = []
    for name, test_fn in tests:
        print(f"\n--- {name} ---")
        try:
            passed = test_fn()
            results.append((name, passed))
        except Exception as e:
            print(f"✗ Exception: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Summary:")
    for name, passed in results:
        status = "✓" if passed else "✗"
        print(f"  {status} {name}")
    
    all_passed = all(r[1] for r in results)
    print("=" * 60)
    if all_passed:
        print("All tests passed! ✓")
    else:
        print("Some tests failed ✗")
        sys.exit(1)
