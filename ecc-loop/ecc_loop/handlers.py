"""
ECC Loop — Task Handlers (Phase 2)

Handlers for the EXECUTE stage. Each handler takes a Task, runs it,
and raises on failure. The engine's execute() catches the exception
and maps it to TaskStatus.FAIL.

Following Karpathy principles:
- Surgical Changes: one handler per task type, no shared abstractions
- Simplicity First: minimal interface — just a callable that takes a Task
"""

import subprocess
import sys
from pathlib import Path

from ecc_loop.models import Task


class ShellHandler:
    """Execute a task via shell command."""

    def __call__(self, task: Task) -> str:
        if not task.description:
            raise ValueError("Shell task has no command")
        result = subprocess.run(
            task.description,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(Path.home()),
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Shell command failed (exit {result.returncode}): {result.stderr.strip()}"
            )
        return result.stdout.strip()


class SkillHandler:
    """Execute a task by invoking a Hermes skill."""

    def __call__(self, task: Task) -> str:
        # Phase 2 stub: Phase 3+ will implement real skill invocation
        skill_name = task.name.split("_", 1)[-1] if "_" in task.name else task.name
        return f"[skill] {skill_name}: {task.description}"


class CodeHandler:
    """Execute a task as Python code."""

    def __call__(self, task: Task) -> str:
        namespace: dict = {}
        exec(task.description, namespace)
        return namespace.get("__result__", "done")


# ── Handler dispatch ─────────────────────────────────────────────────

def handler_for(task: Task):
    """
    Pick the right handler based on task name convention:
    - task_shell_* → ShellHandler
    - task_skill_* → SkillHandler
    - task_code_*  → CodeHandler
    - default      → ShellHandler (simple commands)
    """
    name = task.name.lower()
    if "shell" in name:
        return ShellHandler()
    if "skill" in name:
        return SkillHandler()
    if "code" in name:
        return CodeHandler()
    return ShellHandler()  # Default: treat as shell command
