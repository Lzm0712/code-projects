"""
ECC Loop — Reader (Codersarts minimal control ring)

Reads diffs, test output, logs, and progress files to build context
for the next iteration. Replaces blind re-entry into DISCOVER.
"""
import subprocess
from pathlib import Path


def read_context(project_root: str = "") -> dict:
    """Read all available context: git diff, last logs, progress, state."""
    root = Path(project_root) if project_root else Path(__file__).parent.parent
    ctx = {}

    # 1. Git diff (what changed last)
    try:
        diff = subprocess.run(
            ["git", "diff", "HEAD~1", "--stat", "--", "ecc_loop/", "tests/"],
            cwd=root, capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        if diff:
            ctx["last_diff"] = diff[:500]
    except Exception:
        pass

    # 2. Last test output
    try:
        tests = subprocess.run(
            ["python3", "-m", "pytest", "-q", "--tb=short"],
            cwd=root, capture_output=True, text=True, timeout=30,
        ).stdout.strip()
        ctx["test_output"] = tests[-300:] if len(tests) > 300 else tests
    except Exception:
        pass

    # 3. Last run log entries
    log_path = root / ".ecc_logs" / "run-log.jsonl"
    if log_path.exists():
        import json
        entries = []
        with open(log_path) as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
        ctx["last_runs"] = entries[-3:] if entries else []

    # 4. Progress checkpoint
    progress_path = root / "progress.md"
    if progress_path.exists():
        ctx["progress"] = progress_path.read_text()[:500]

    # 5. Discovery gaps
    from ecc_loop.engine import _discover_gaps
    ctx["gaps"] = _discover_gaps({}, {})

    return ctx


def summarize_context(ctx: dict) -> str:
    """Produce a human-readable summary from reader context."""
    lines = ["## ECC Context Summary\n"]

    if "last_diff" in ctx:
        lines.append(f"### Recent Changes\n```\n{ctx['last_diff']}\n```\n")

    if "test_output" in ctx:
        lines.append(f"### Test Output\n```\n{ctx['test_output']}\n```\n")

    if "gaps" in ctx:
        gaps = ctx["gaps"]
        if gaps:
            lines.append(f"### Gaps ({len(gaps)})\n")
            for g in gaps:
                lines.append(f"- {g}")
        else:
            lines.append("### Gaps: 0 (healthy)\n")

    if "last_runs" in ctx:
        lines.append(f"### Last Runs ({len(ctx['last_runs'])})\n")
        for r in ctx["last_runs"][-3:]:
            lines.append(f"- {r.get('ts','?')[:19]} {r.get('status','?')} {r.get('goal','')[:40]}")

    return "\n".join(lines)
