"""
ECC Loop — Task Handlers

Handlers for the EXECUTE stage. Each handler takes a Task and returns output.
Raises on failure; engine's execute() catches → TaskStatus.FAIL.
"""

import json
import subprocess
import sys
from pathlib import Path


class ShellHandler:
    """Execute a task as a shell command."""
    def __call__(self, task) -> str:
        cmd = task.description.strip()
        if not cmd:
            raise ValueError("Shell task has no command")
        result = subprocess.run(cmd, shell=True, capture_output=True,
                                text=True, timeout=60, cwd=str(Path.home()))
        if result.returncode != 0:
            raise RuntimeError(f"exit {result.returncode}: {result.stderr.strip()}")
        return result.stdout.strip()


class CodeHandler:
    """Execute a task as Python code with file operations."""
    def __call__(self, task) -> str:
        code = task.description.strip()
        if not code:
            raise ValueError("Code task has no code")

        namespace = {"__builtins__": __builtins__}
        try:
            exec(code, namespace)
        except Exception as e:
            raise RuntimeError(f"Python error: {e}") from e

        return namespace.get("__result__", "done")


class FileHandler:
    """Execute a task that writes a file."""
    def __call__(self, task) -> str:
        code = task.description.strip()
        try:
            spec = json.loads(code)
            path = Path(spec["path"]).expanduser()
            content = spec.get("content", "")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            return f"wrote {path}"
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid file spec: {e}")
        except OSError as e:
            raise RuntimeError(f"File error: {e}")


# ── Dispatch ─────────────────────────────────────────────────────────

def handler_for(task):
    """
    Pick handler by task name:
    - task_shell_* → ShellHandler
    - task_file_*  → FileHandler
    - default      → CodeHandler (Python code)
    """
    name = task.name.lower()
    if "shell" in name:
        return ShellHandler()
    if "file" in name:
        return FileHandler()
    return CodeHandler()
