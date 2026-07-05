"""
ECC Loop — Skill Scanner / Hot-Reload (Phase B)

Periodically scans ~/.hermes/skills/ for new/changed skills and triggers reload.
Inspired by JiuwenSwarm's update_evolution_config() runtime hot-update mechanism.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Optional

SKILLS_DIR = "~/.hermes/skills"
MANIFEST_PATH = "~/.hermes/ecc-skill-scan-cache.json"


def scan_skills(skills_dir: Optional[str] = None) -> dict[str, str]:
    """Walk skills directory, return {skill_name: content_hash}."""
    root = Path(skills_dir or SKILLS_DIR).expanduser()
    if not root.exists():
        return {}

    result: dict[str, str] = {}
    for skill_md in root.rglob("SKILL.md"):
        rel = skill_md.relative_to(root)
        try:
            blob = skill_md.read_bytes()
            result[str(rel)] = hashlib.sha256(blob).hexdigest()[:12]
        except OSError:
            continue
    return result


def load_cache(path: Optional[str] = None) -> dict:
    """Load previous scan cache."""
    p = Path(path or MANIFEST_PATH).expanduser()
    if p.exists():
        try:
            return json.loads(p.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_cache(snapshot: dict, path: Optional[str] = None) -> None:
    """Persist scan cache."""
    p = Path(path or MANIFEST_PATH).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(snapshot, indent=2))


def detect_changes(skills_dir: Optional[str] = None) -> dict:
    """Return {'new': [...], 'modified': [...], 'removed': [...]}."""
    prev = load_cache()
    curr = scan_skills(skills_dir)

    new_skills = [k for k in curr if k not in prev]
    modified = [k for k in curr if k in prev and curr[k] != prev[k]]
    removed = [k for k in prev if k not in curr]

    save_cache(curr)

    return {
        "new": sorted(new_skills),
        "modified": sorted(modified),
        "removed": sorted(removed),
    }


def report_changes(skills_dir: Optional[str] = None) -> str:
    """Human-readable change report."""
    changes = detect_changes(skills_dir)
    parts: list[str] = []
    if changes["new"]:
        parts.append(f"🆕 New skills ({len(changes['new'])}): {', '.join(changes['new'][:10])}")
    if changes["modified"]:
        parts.append(f"✏️ Modified ({len(changes['modified'])}): {', '.join(changes['modified'][:10])}")
    if changes["removed"]:
        parts.append(f"🗑️ Removed ({len(changes['removed'])}): {', '.join(changes['removed'][:10])}")
    if not parts:
        return "✅ No skill changes detected."
    return "\n".join(parts)

# ECC self-evolution marker

# ECC self-evolution marker

# ECC self-evolution marker

# ECC self-evolution marker

# ECC self-evolution marker
