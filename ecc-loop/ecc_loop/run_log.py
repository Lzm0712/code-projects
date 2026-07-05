"""
ECC Loop — Structured run log (loop-engineering: operating-loops.md)

Records structured JSON entries per loop run for audit trail.
"""
import json
from pathlib import Path
from datetime import datetime

LOG_PATH = Path(__file__).parent.parent / ".ecc_logs" / "run-log.jsonl"


def record_run(goal: str, status: str, iterations: int = 0,
               tokens: int = 0, errors: list | None = None,
               duration_ms: int = 0):
    """Append a structured run entry to the JSONL log."""
    LOG_PATH.parent.mkdir(exist_ok=True)
    entry = {
        "ts": datetime.now().isoformat(),
        "goal": goal[:100],
        "status": status,  # PASS | FAIL | BREAKER
        "iterations": iterations,
        "tokens_est": tokens,
        "errors": errors or [],
        "duration_ms": duration_ms,
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def recent_runs(n: int = 10) -> list[dict]:
    """Return last N runs."""
    if not LOG_PATH.exists():
        return []
    runs = []
    with open(LOG_PATH) as f:
        for line in f:
            if line.strip():
                runs.append(json.loads(line))
    return runs[-n:]


def daily_stats() -> dict:
    """Today's run statistics."""
    today = datetime.now().strftime("%Y-%m-%d")
    runs = recent_runs(100)
    today_runs = [r for r in runs if r["ts"].startswith(today)]
    passes = [r for r in today_runs if r["status"] == "PASS"]
    return {
        "date": today,
        "total": len(today_runs),
        "passes": len(passes),
        "total_tokens": sum(r.get("tokens_est", 0) for r in today_runs),
    }
