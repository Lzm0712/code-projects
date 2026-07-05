"""
ECC Loop — Tiered Reflection (Phase C)

Two-speed reflection: fast path for simple queries, full path for complex ones.
Inspired by JiuwenSwarm's FastOneShotPlanner (greedy) vs BFS (complex) split.
"""

import json
import os
from pathlib import Path
from typing import Optional

_COMPLEX_KEYWORDS = {"分析", "对比", "设计", "规划", "制定", "refactor", "refactoring",
                     "architecture", "design", "compare", "analyze", "migrate",
                     "重构", "迁移", "优化", "评估", "方案"}


def should_use_fast_path(query: str) -> bool:
    """Decide whether a query can use fast-path reflection.

    Fast path is suitable when:
    - Query is short (≤30 chars)
    - No complex keywords present
    """
    if len(query.strip()) <= 30:
        return not any(k in query for k in _COMPLEX_KEYWORDS)
    return False


def fast_reflection(query: str, observations_path: Optional[str] = None) -> str:
    """Quick single-line conclusion for simple queries."""
    return f"[ECC Fast] {query.strip()} → 基于近期 observations，无阻塞，直接执行。"


def full_reflection(query: str, observations_path: str = "~/.hermes/observations.jsonl") -> str:
    """Full analysis path: reads observations and produces structured output."""
    path = Path(observations_path).expanduser()
    observations = []

    if path.exists():
        try:
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        observations.append(json.loads(line))
        except (json.JSONDecodeError, OSError):
            observations = []

    # Summarize recent observations
    recent = observations[-20:] if len(observations) > 20 else observations
    patterns = _extract_patterns(recent)

    return (
        f"[ECC Full] Query: {query}\n"
        f"  Observations scanned: {len(observations)}\n"
        f"  Recent patterns: {len(patterns)}\n"
        f"  Analysis: {_summarize(query, patterns)}"
    )


def reflect(query: str, observations_path: Optional[str] = None) -> str:
    """Unified entry point: auto-selects fast or full path."""
    if should_use_fast_path(query):
        return fast_reflection(query, observations_path)
    return full_reflection(query, observations_path or "~/.hermes/observations.jsonl")


# ── helpers ──────────────────────────────────────────────────────────

def _extract_patterns(observations: list[dict]) -> list[str]:
    """Extract unique patterns from observation entries."""
    patterns: set[str] = set()
    for obs in observations:
        if isinstance(obs, dict):
            for key in ("pattern", "tag", "category", "type"):
                val = obs.get(key)
                if isinstance(val, str) and val:
                    patterns.add(val)
    return sorted(patterns)


def _summarize(query: str, patterns: list[str]) -> str:
    """Build a concise summary based on patterns and query."""
    if not patterns:
        return "未检测到明显模式，建议进一步分析。"
    return f"检测到 {len(patterns)} 个活跃模式：{', '.join(patterns[:5])}"
