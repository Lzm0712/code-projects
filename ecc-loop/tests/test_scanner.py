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
        changes = scanner.detect_changes(tmp)
        assert changes["new"] == []
        assert changes["modified"] == []
        assert changes["removed"] == []


def test_report_no_changes():
    with tempfile.TemporaryDirectory() as tmp:
        report = scanner.report_changes(tmp)
        assert "No skill changes" in report
