"""Tests for ecc_loop.logger"""

import tempfile
from pathlib import Path
from ecc_loop.logger import log


def test_log_writes_file():
    with tempfile.TemporaryDirectory() as tmp:
        # Override LOG_DIR
        import ecc_loop.logger as logger_mod
        original_dir = logger_mod.LOG_DIR
        logger_mod.LOG_DIR = Path(tmp)
        try:
            log("TEST", "goal1", "details here", 1)
            files = list(Path(tmp).glob("*.log"))
            assert len(files) == 1
            content = files[0].read_text()
            assert "TEST" in content
            assert "goal1" in content
            assert "iter=01" in content
        finally:
            logger_mod.LOG_DIR = original_dir


def test_log_multiple_entries_same_file():
    with tempfile.TemporaryDirectory() as tmp:
        import ecc_loop.logger as logger_mod
        original_dir = logger_mod.LOG_DIR
        logger_mod.LOG_DIR = Path(tmp)
        try:
            log("EXECUTE", "task A", "start", 1)
            log("PASS", "task A", "done", 1)
            log("EXECUTE", "task B", "start", 2)
            files = list(Path(tmp).glob("*.log"))
            assert len(files) == 1  # Same day, same file
            lines = files[0].read_text().strip().splitlines()
            assert len(lines) == 3
        finally:
            logger_mod.LOG_DIR = original_dir
