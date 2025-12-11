"""
Test technique-task Docker mounting.

Verifies that we can mount multiple competitions into a single container.
"""

import docker
import tempfile
import json
from pathlib import Path


def test_multi_mount_structure():
    """
    Test that we can create a volume config that mounts
    multiple competition directories under /data/{comp_id}/
    """
    # Simulate what the technique-task runner would do
    data_dir = Path("/Users/sanketshah/.mlebench")  # Typical data dir
    competitions = ["random-acts-of-pizza", "spaceship-titanic", "dogs-vs-cats-redux-kernels-edition"]
    
    # Option 1: Mount entire data_dir at once
    volumes_single = {
        str(data_dir): {
            "bind": "/data",
            "mode": "ro"
        }
    }
    
    # This would give container:
    # /data/random-acts-of-pizza/prepared/public/train.csv
    # /data/spaceship-titanic/prepared/public/train.csv
    # etc.
    
    print("Option 1: Single mount of data_dir")
    print(f"  Host: {data_dir}")
    print(f"  Container: /data")
    print(f"  Agent accesses: /data/{{comp_id}}/prepared/public/train.csv")
    print()
    
    # Option 2: Mount each competition separately (more isolation)
    volumes_multi = {}
    for comp_id in competitions:
        host_path = data_dir / comp_id / "prepared" / "public"
        volumes_multi[str(host_path)] = {
            "bind": f"/data/{comp_id}",
            "mode": "ro"
        }
    
    print("Option 2: Separate mount per competition")
    for host, mount in volumes_multi.items():
        print(f"  {host} -> {mount['bind']}")
    print()
    
    print("✓ Volume configs generated successfully")
    return volumes_single, volumes_multi


def test_docker_available():
    """Test Docker client can connect."""
    try:
        client = docker.from_env()
        client.ping()
        print("✓ Docker is available")
        
        # List images
        images = client.images.list()
        image_names = [img.tags[0] if img.tags else img.id[:12] for img in images]
        
        # Check for relevant images
        mlebench_images = [n for n in image_names if 'mlebench' in n.lower() or 'aide' in n.lower() or 'dummy' in n.lower()]
        if mlebench_images:
            print(f"✓ Found relevant images: {mlebench_images}")
        else:
            print("⚠ No mlebench/aide images found")
            
        return True
    except docker.errors.DockerException as e:
        print(f"⚠ Docker not available: {e}")
        return False


def test_technique_task_env_vars():
    """Test the environment variables we'd pass to container."""
    env_vars = {
        "TECHNIQUE_MODE": "true",
        "COMPETITIONS": "random-acts-of-pizza,spaceship-titanic",
        "TASKS": "imbalance,missing,encoding",
        "DATA_ROOT": "/data",  # Where competitions are mounted
    }
    
    print("Environment variables for technique-task container:")
    for k, v in env_vars.items():
        print(f"  {k}={v}")
    
    # What agent would do:
    print()
    print("Agent pseudo-code:")
    print("""
    if os.environ.get("TECHNIQUE_MODE"):
        competitions = os.environ["COMPETITIONS"].split(",")
        tasks = os.environ["TASKS"].split(",")
        data_root = os.environ["DATA_ROOT"]
        
        for comp_id in competitions:
            train_path = f"{data_root}/{comp_id}/prepared/public/train.csv"
            df = pd.read_csv(train_path)
            
            for task in tasks:
                analyze(df, task, comp_id)
    """)
    print("✓ Environment variable structure defined")


def test_create_dummy_technique_output():
    """Create dummy output that agent would produce."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Simulate agent output for technique-tasks
        competitions = ["random-acts-of-pizza", "spaceship-titanic"]
        tasks = ["imbalance", "missing", "encoding"]
        
        for comp_id in competitions:
            comp_dir = tmpdir / comp_id
            comp_dir.mkdir()
            
            for task in tasks:
                analysis = {
                    "competition": comp_id,
                    "task": task,
                    "analysis": f"Dummy analysis for {task} on {comp_id}",
                    "word_count_target": 50
                }
                (comp_dir / f"{task}_analysis.json").write_text(
                    json.dumps(analysis, indent=2)
                )
        
        # Verify structure
        print("Simulated agent output structure:")
        for f in sorted(tmpdir.rglob("*.json")):
            rel = f.relative_to(tmpdir)
            size = len(f.read_text().split())
            print(f"  {rel} ({size} words)")
        
        print("✓ Dummy output structure created")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Technique-Task Docker Mounting")
    print("=" * 60)
    print()
    
    test_multi_mount_structure()
    print()
    
    test_docker_available()
    print()
    
    test_technique_task_env_vars()
    print()
    
    test_create_dummy_technique_output()
    print()
    
    print("=" * 60)
    print("Docker mounting tests complete!")
    print("=" * 60)
