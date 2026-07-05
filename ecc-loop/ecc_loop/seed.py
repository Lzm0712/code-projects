"""
ECC Loop — Evolution State Serialization (Phase A)

Transforms STATE.md into a structured seed.json for cross-process state tracking.
Inspired by JiuwenSwarm's to_seed() / from_seed() mechanism.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

SEED_SCHEMA_VERSION = "1.0"

DEFAULT_SEED = {
    "version": SEED_SCHEMA_VERSION,
    "created_at": None,
    "last_modified": None,
    "current_phase": "",
    "execution_state": {
        "active_tasks": [],
        "completed_tasks": [],
        "blocked_tasks": [],
    },
    "metrics": {
        "observations_count": 0,
        "skills_generated": 0,
        "patterns_tracked": 0,
    },
    "skills": {},
}


def load_seed(path: str | Path) -> dict:
    """Load seed.json, return default if missing or corrupt."""
    path = Path(path).expanduser()
    if not path.exists():
        return dict(DEFAULT_SEED)

    try:
        with open(path) as f:
            data = json.load(f)
        # Ensure all keys exist (forward-compatible defaults)
        for key, val in DEFAULT_SEED.items():
            data.setdefault(key, val)
        return data
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_SEED)


def save_seed(state: dict, path: str | Path) -> None:
    """Serialize state to seed.json with timestamp."""
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)

    now = datetime.now().isoformat()
    if state.get("created_at") is None:
        state["created_at"] = now
    state["last_modified"] = now

    with open(path, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    return


def mark_complete(state: dict, task_name: str) -> dict:
    """Mark a task as completed (moves from active to completed)."""
    state.setdefault("execution_state", {})
    exec_state = state["execution_state"]
    exec_state.setdefault("active_tasks", [])
    exec_state.setdefault("completed_tasks", [])

    if task_name in exec_state["active_tasks"]:
        exec_state["active_tasks"].remove(task_name)
    if task_name not in exec_state["completed_tasks"]:
        exec_state["completed_tasks"].append(task_name)

    return state


def update_metrics(state: dict, **kwargs) -> dict:
    """Update metric counters."""
    state.setdefault("metrics", {})
    for key, val in kwargs.items():
        state["metrics"][key] = val
    return state


def track_skill(state: dict, skill_name: str, version: str = "1.0.0") -> dict:
    """Register a skill in the seed's skill version tracker."""
    state.setdefault("skills", {})
    now = datetime.now().isoformat()
    state["skills"][skill_name] = {
        "version": version,
        "last_used": now,
    }
    return state
