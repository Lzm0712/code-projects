"""
ECC Loop — Checkpoint (opencode-loop article)

Human-readable progress tracking. Updated at each loop iteration.
Replaces blind seed.json as the single source of loop truth.
"""
from pathlib import Path
from datetime import datetime


def save_checkpoint(goal: str, status: str, iteration: int = 0,
                    details: str = "", project_root: str = ""):
    """Update progress.md with latest iteration results."""
    root = Path(project_root) if project_root else Path(__file__).parent.parent
    progress_path = root / "progress.md"

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"""## Iteration {iteration} — {status}
**Time**: {ts}
**Goal**: {goal[:80]}
**Status**: {status}
{details}

---
"""

    if progress_path.exists():
        existing = progress_path.read_text()
        # Keep last 20 entries max
        entries = existing.split("---")
        entries = [e.strip() for e in entries if e.strip()]
        entries = entries[-19:]  # Keep 19 + add 1 new = 20
        all_entries = "\n---\n".join(entries) + "\n---\n" + entry
        progress_path.write_text(all_entries)
    else:
        progress_path.write_text(f"# ECC Loop Progress\n\n{entry}")


def read_progress(project_root: str = "") -> str:
    """Read the latest progress checkpoint."""
    root = Path(project_root) if project_root else Path(__file__).parent.parent
    progress_path = root / "progress.md"
    if progress_path.exists():
        content = progress_path.read_text()
        # Return last 1000 chars for the latest context
        return content[-1000:] if len(content) > 1000 else content
    return "(no progress recorded)"


def latest_status(project_root: str = "") -> dict:
    """Parse the latest iteration status from progress.md."""
    root = Path(project_root) if project_root else Path(__file__).parent.parent
    progress_path = root / "progress.md"
    if not progress_path.exists():
        return {"status": "no_progress", "iteration": 0}

    content = progress_path.read_text()
    # Find the last "## Iteration" heading
    entries = content.split("## Iteration")
    if len(entries) < 2:
        return {"status": "unparsed", "iteration": 0}

    last = entries[-1]
    lines = last.strip().split("\n")
    result = {"iteration": 0, "status": "unknown"}
    for line in lines:
        line = line.strip()
        if line.startswith("**Status**:"):
            result["status"] = line.split(":", 1)[1].strip()
        elif line.startswith("**Goal**:"):
            result["goal"] = line.split(":", 1)[1].strip()
    # Try to parse iteration number from heading
    try:
        result["iteration"] = int(lines[0].split("—")[0].strip())
    except (ValueError, IndexError):
        pass

    return result
