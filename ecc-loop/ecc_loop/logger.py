"""
ECC Loop — Cycle Logger (Best Practice #4: 记录一切)

Appends structured log entries for every loop iteration.
"""
from pathlib import Path
from datetime import datetime

LOG_DIR = Path(__file__).parent.parent / ".ecc_logs"
LOG_DIR.mkdir(exist_ok=True)


def log(stage: str, goal: str = "", detail: str = "", iteration: int = 0):
    """Append one line to today's cycle log."""
    ts = datetime.now().isoformat()
    line = f"{ts} | iter={iteration:02d} | {stage:10s} | {goal[:60]:60s} | {detail[:200]}\n"
    log_file = LOG_DIR / f"ecc-{datetime.now().strftime('%Y%m%d')}.log"
    with open(log_file, "a") as f:
        f.write(line)
