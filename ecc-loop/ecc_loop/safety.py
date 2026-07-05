"""
ECC Loop — Safety Guard (loop-engineering docs: safety.md)

Enforces denylist and human gates before task execution.
"""
from pathlib import Path

DENYLIST_GLOBS = [
    ".env", ".env.*", "**/secrets/**", "**/credentials/**",
    "**/*_key*", "**/*_secret*", "**/migrations/**",
    "auth/**", "payments/**",
]


def check_path(path_str: str) -> tuple[bool, str]:
    """Check if a path is safe to modify. Returns (safe, reason)."""
    import fnmatch
    for pattern in DENYLIST_GLOBS:
        if fnmatch.fnmatch(path_str, pattern):
            return False, f"DENYLIST: {path_str} matches {pattern}"
    return True, ""


def check_denylist(code: str) -> tuple[bool, str]:
    """Scan code for references to denylist paths."""
    for line in code.splitlines():
        for pattern in DENYLIST_GLOBS:
            if pattern.replace("*", "") in line:
                if any(kw in line.lower() for kw in ["open(", "write", "path(", "mkdir"]):
                    return False, f"Possible denylist access: {line.strip()[:80]}"
    return True, ""


def safety_check(task_description: str) -> tuple[bool, str]:
    """Pre-flight safety check. Returns (safe, reason_if_unsafe)."""
    # Check file count
    path_count = task_description.count("Path(") + task_description.count("open(")
    if path_count > 10:
        return False, f"Touches >10 files ({path_count}) — human gate required"

    # Check denylist
    ok, reason = check_denylist(task_description)
    return ok, reason
