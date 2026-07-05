"""
ECC Loop — Learning Metrics (Best Practice #8: 保持学习)

Tracks loop performance metrics and uses them to improve.
"""
import json
from pathlib import Path
from datetime import datetime

METRICS_PATH = Path(__file__).parent.parent / ".ecc_logs" / "metrics.json"


def record(metric: str, value: float | int, tags: dict | None = None):
    """Record a metric data point."""
    METRICS_PATH.parent.mkdir(exist_ok=True)
    entry = {
        "ts": datetime.now().isoformat(),
        "metric": metric,
        "value": value,
        "tags": tags or {},
    }
    data = _load()
    data["history"].append(entry)
    # Keep last 1000 entries
    if len(data["history"]) > 1000:
        data["history"] = data["history"][-1000:]
    _save(data)


def summary() -> dict:
    """Return summary metrics for self-improvement."""
    data = _load()
    history = data["history"]
    if not history:
        return {"total_runs": 0}

    passes = sum(1 for h in history if h["metric"] == "cycle" and h["value"] == 1)
    fails = sum(1 for h in history if h["metric"] == "cycle" and h["value"] == 0)
    total = passes + fails

    return {
        "total_runs": total,
        "passes": passes,
        "fails": fails,
        "pass_rate": f"{int(passes/total*100)}%" if total else "N/A",
        "last_run": history[-1]["ts"] if history else None,
        "trend": _trend(history),
    }


def _trend(history: list) -> str:
    """Simple trend analysis."""
    if len(history) < 5:
        return "insufficient data"
    recent = [h for h in history[-10:] if h["metric"] == "cycle"]
    if not recent:
        return "no cycle data"
    recent_passes = sum(1 for h in recent if h["value"] == 1)
    recent_rate = recent_passes / len(recent)
    if recent_rate >= 0.9:
        return "improving"
    if recent_rate <= 0.5:
        return "degrading"
    return "stable"


def _load() -> dict:
    if METRICS_PATH.exists():
        try:
            return json.loads(METRICS_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"history": []}


def _save(data: dict):
    METRICS_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))
