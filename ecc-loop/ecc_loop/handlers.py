"""
ECC Loop — Task Handlers + Auto-detection

Handlers for the EXECUTE stage. Each handler takes a Task and returns output.
Raises on failure; engine's execute() catches -> TaskStatus.FAIL.
"""

import json
import subprocess
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
    """Execute a task as Python code."""
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
    """Execute a task that writes a file from JSON spec."""
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


# ── Shell command keywords for auto-detection ────────────────────────

_SHELL_PREFIXES = (
    "echo ", "ls ", "cat ", "rm ", "cp ", "mv ", "mkdir ", "cd ",
    "git ", "npm ", "npx ", "pip ", "python ", "python3 ",
    "curl ", "wget ", "grep ", "find ", "which ", "ps ", "kill ",
    "brew ", "docker ", "kubectl ", "ssh ", "scp ",
)


# ── Dispatch with auto-detection ─────────────────────────────────────

def handler_for(task):
    """
    Auto-detect handler based on task description content:

    1. If name contains 'shell'/'file'/'code' -> explicit choice
    2. If description starts with known shell prefix -> ShellHandler
    3. If description is valid JSON with 'path'+'content' -> FileHandler
    4. Default -> CodeHandler
    """
    name = task.name.lower()
    desc = task.description.strip()

    # Explicit naming overrides auto-detection
    if "shell" in name:
        return ShellHandler()
    if "file" in name:
        return FileHandler()
    if "code" in name:
        return CodeHandler()

    # Auto-detect: shell prefix
    if desc.startswith(_SHELL_PREFIXES):
        return ShellHandler()

    # Auto-detect: JSON file spec
    if desc.startswith("{"):
        try:
            spec = json.loads(desc)
            if "path" in spec and "content" in spec:
                return FileHandler()
        except json.JSONDecodeError:
            pass

    # Default: Python code
    return CodeHandler()
