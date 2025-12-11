"""Grader for cv technique-task. Simple: did agent write content?"""

from pathlib import Path


def grade(submission_dir: Path, competition_data: dict = None) -> dict:
    """Grade = file exists + has content. Returns word count."""
    analysis_file = submission_dir / "cv_analysis.json"
    
    if not analysis_file.exists():
        return {
            "score": 0,
            "passed": False,
            "word_count": 0,
            "message": "cv_analysis.json not found"
        }
    
    try:
        content = analysis_file.read_text()
        word_count = len(content.split())
        
        return {
            "score": 1.0 if word_count > 0 else 0,
            "passed": word_count > 0,
            "word_count": word_count,
            "message": f"Agent wrote {word_count} words"
        }
    except Exception as e:
        return {
            "score": 0,
            "passed": False,
            "word_count": 0,
            "message": f"Error: {e}"
        }
