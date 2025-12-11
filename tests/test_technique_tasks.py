"""
Test technique-tasks with dummy agent.

Tests:
1. Mounting all competitions at once works
2. Agent can iterate over competitions
3. Graders return word counts
"""

import json
import tempfile
from pathlib import Path
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from mlebench.tool_tasks.grader import grade_all_tasks, grade_technique_task


def test_grader_missing_file():
    """Test grader returns 0 when file doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = grade_technique_task("imbalance", Path(tmpdir))
        
        assert result["score"] == 0
        assert result["passed"] == False
        assert result["word_count"] == 0
        print("✓ test_grader_missing_file passed")


def test_grader_with_content():
    """Test grader returns word count when file has content."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create a dummy analysis file
        analysis = {
            "class_distribution": {"0": 0.7, "1": 0.3},
            "imbalance_ratio": 2.3,
            "is_imbalanced": False,
            "reasoning": "The classes are not severely imbalanced."
        }
        (tmpdir / "imbalance_analysis.json").write_text(json.dumps(analysis, indent=2))
        
        result = grade_technique_task("imbalance", tmpdir)
        
        assert result["score"] == 1.0
        assert result["passed"] == True
        assert result["word_count"] > 0
        print(f"✓ test_grader_with_content passed (word_count={result['word_count']})")


def test_grader_empty_file():
    """Test grader handles empty file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        (tmpdir / "missing_analysis.json").write_text("")
        
        result = grade_technique_task("missing", tmpdir)
        
        assert result["score"] == 0
        assert result["passed"] == False
        assert result["word_count"] == 0
        print("✓ test_grader_empty_file passed")


def test_grade_all_tasks():
    """Test grading all tasks at once."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create some analysis files
        (tmpdir / "imbalance_analysis.json").write_text('{"ratio": 1.5, "note": "balanced"}')
        (tmpdir / "missing_analysis.json").write_text('{"cols_with_missing": ["age", "cabin"]}')
        # Don't create encoding_analysis.json - should fail
        
        results = grade_all_tasks(tmpdir, tasks=["imbalance", "missing", "encoding"])
        
        assert results["tasks"]["imbalance"]["passed"] == True
        assert results["tasks"]["missing"]["passed"] == True
        assert results["tasks"]["encoding"]["passed"] == False
        assert results["summary"]["passed"] == 2
        assert results["summary"]["total"] == 3
        print(f"✓ test_grade_all_tasks passed (pass_rate={results['summary']['pass_rate']:.1%})")


def test_individual_graders():
    """Test each individual grader module works."""
    from mlebench.tool_tasks.imbalance.grade import grade as grade_imbalance
    from mlebench.tool_tasks.missing.grade import grade as grade_missing
    from mlebench.tool_tasks.encoding.grade import grade as grade_encoding
    from mlebench.tool_tasks.cv.grade import grade as grade_cv
    from mlebench.tool_tasks.scaling.grade import grade as grade_scaling
    from mlebench.tool_tasks.leakage.grade import grade as grade_leakage
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Test each grader returns expected structure
        for name, grader, filename in [
            ("imbalance", grade_imbalance, "imbalance_analysis.json"),
            ("missing", grade_missing, "missing_analysis.json"),
            ("encoding", grade_encoding, "encoding_analysis.json"),
            ("cv", grade_cv, "cv_analysis.json"),
            ("scaling", grade_scaling, "scaling_analysis.json"),
            ("leakage", grade_leakage, "leakage_analysis.json"),
        ]:
            # Test missing file
            result = grader(tmpdir)
            assert "score" in result
            assert "passed" in result
            assert "word_count" in result
            assert result["passed"] == False
            
            # Test with file
            (tmpdir / filename).write_text(f'{{"task": "{name}", "analysis": "test content here"}}')
            result = grader(tmpdir)
            assert result["passed"] == True
            assert result["word_count"] > 0
            
            # Clean up for next iteration
            (tmpdir / filename).unlink()
            
        print("✓ test_individual_graders passed (all 6 graders work)")


def test_data_dir_structure():
    """Test that we can access competition data directories."""
    try:
        from mlebench.registry import registry
    except ImportError as e:
        print(f"⚠ Skipping test_data_dir_structure: {e}")
        return
    
    # Check we can list competitions
    comp_ids = registry.list_competition_ids()
    assert len(comp_ids) > 0, "No competitions found in registry"
    print(f"✓ Found {len(comp_ids)} competitions in registry")
    
    # Check data_dir exists
    data_dir = registry.get_data_dir()
    print(f"  Data dir: {data_dir}")
    
    # Check if any competitions are prepared
    prepared = []
    for comp_id in comp_ids[:5]:  # Check first 5
        comp = registry.get_competition(comp_id)
        if comp.public_dir.exists():
            prepared.append(comp_id)
    
    if prepared:
        print(f"✓ Found {len(prepared)} prepared competitions: {prepared}")
    else:
        print("⚠ No competitions prepared yet (run: mlebench prepare --lite)")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Technique-Tasks Graders")
    print("=" * 60)
    
    test_grader_missing_file()
    test_grader_with_content()
    test_grader_empty_file()
    test_grade_all_tasks()
    test_individual_graders()
    test_data_dir_structure()
    
    print("=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
