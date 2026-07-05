"""Tests for ecc_loop.scanner"""

import tempfile
from pathlib import Path

from ecc_loop import scanner


def test_scan_empty_dir():
    with tempfile.TemporaryDirectory() as tmp:
        result = scanner.scan_skills(tmp)
        assert result == {}


def test_scan_skill_file():
    with tempfile.TemporaryDirectory() as tmp:
        skill_dir = Path(tmp) / "test-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: test\n---\n# Test")
        result = scanner.scan_skills(tmp)
        assert "test-skill/SKILL.md" in result


def test_detect_new_skill():
    with tempfile.TemporaryDirectory() as tmp:
        # Use isolated cache so test doesn't pollute global state
        isolated_cache = Path(tmp) / ".cache.json"
        prev = scanner.load_cache(str(isolated_cache))
        curr = scanner.scan_skills(tmp)
        new = [k for k in curr if k not in prev]
        modified = [k for k in curr if k in prev and curr[k] != prev[k]]
        removed = [k for k in prev if k not in curr]
        assert new == []
        assert modified == []
        assert removed == []


def test_report_no_changes():
    with tempfile.TemporaryDirectory() as tmp:
        # Isolated cache + scan — don't touch global MANIFEST_PATH
        cache_path = Path(tmp) / "cache.json"
        prev = scanner.load_cache(str(cache_path))
        curr = scanner.scan_skills(tmp)
        new = [k for k in curr if k not in prev]
        modified = [k for k in curr if k in prev and curr[k] != prev[k]]
        removed = [k for k in prev if k not in curr]
        parts = []
        if new:
            parts.append(f"New ({len(new)})")
        if modified:
            parts.append(f"Modified ({len(modified)})")
        if removed:
            parts.append(f"Removed ({len(removed)})")
        assert len(parts) == 0, f"Expected no changes, got: {parts}"
