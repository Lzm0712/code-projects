"""
ECC Loop — Continuous Learning (inspired by everything-claude-code)

Auto-extracts patterns from loop runs into reusable improvements.
"""
import json
from pathlib import Path
from datetime import datetime

LEARNING_PATH = Path(__file__).parent.parent / ".ecc_logs" / "learned-patterns.json"


def extract_patterns(run_log_path: str = "") -> list[str]:
    """Analyze run log for recurring patterns that suggest improvements."""
    log_path = Path(run_log_path) if run_log_path else \
        Path(__file__).parent.parent / ".ecc_logs" / "run-log.jsonl"
    if not log_path.exists():
        return []

    errors = []
    with open(log_path) as f:
        for line in f:
            if line.strip():
                entry = json.loads(line)
                for err in entry.get("errors", []):
                    errors.append(err)

    # Find repeating errors
    from collections import Counter
    error_freq = Counter(errors)
    suggestions = []
    for err, count in error_freq.most_common(5):
        if count >= 2:
            suggestions.append(f"Recurring error ({count}x): {err[:80]}")

    # Check pass rate trend
    passes = 0
    fails = 0
    with open(log_path) as f:
        for line in f:
            if line.strip():
                entry = json.loads(line)
                if entry.get("status") == "PASS":
                    passes += 1
                else:
                    fails += 1

    if fails > passes and passes + fails > 10:
        suggestions.append(f"Pass rate <50% ({passes}/{passes+fails}) — review verifier")

    return suggestions


def save_learned(pattern: str):
    """Save an extracted pattern for future reference."""
    LEARNING_PATH.parent.mkdir(exist_ok=True)
    data = _load_learned()
    data["patterns"].append({
        "ts": datetime.now().isoformat(),
        "pattern": pattern,
    })
    with open(LEARNING_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _load_learned() -> dict:
    if LEARNING_PATH.exists():
        try:
            return json.loads(LEARNING_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"patterns": []}


def show_learned() -> list[str]:
    """Return all learned patterns."""
    return [p["pattern"] for p in _load_learned().get("patterns", [])]
