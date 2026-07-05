"""ECC Loop — L4 Proactive Workflow (Claude Code 官方分级)

Autonomous decision-making: discovers work, decides priority,
executes multi-agent tasks, verifies, and reports — unattended.
"""
import time
from pathlib import Path


def run_proactive(project_root: str = "", max_cycles: int = 3) -> dict:
    """L4 Proactive: fully autonomous decision-making workflow."""
    from ecc_loop.engine import loop, discover_work, _discover_gaps
    from ecc_loop.models import CircuitBreakerConfig, VerifyStatus
    from ecc_loop.reader import read_context, summarize_context
    from ecc_loop.checkpoint import save_checkpoint
    from ecc_loop.learning import record

    root = Path(project_root) if project_root else Path(__file__).parent.parent
    t_start = time.time()
    results = {"cycles": 0, "fixed": 0, "failed": 0, "tokens_est": 0}

    for cycle in range(1, max_cycles + 1):
        ctx = read_context(str(root))
        summary = summarize_context(ctx)
        save_checkpoint(f"Proactive cycle {cycle}", "RUNNING", cycle, summary, str(root))

        work = discover_work(str(root))
        gaps = _discover_gaps({}, {})

        if not gaps and not work:
            save_checkpoint(f"Proactive cycle {cycle}", "IDLE", cycle,
                            "No work discovered — system healthy", str(root))
            record("proactive", 0, {"cycle": cycle, "reason": "idle"})
            continue

        priority = (gaps or [])[:3]
        if work and len(priority) < 3:
            priority.extend(work[:3 - len(priority)])

        for item in priority:
            goal = f"[Proactive] {item}"
            save_checkpoint(goal, "EXECUTING", cycle, f"Priority: {item}", str(root))
            config = CircuitBreakerConfig(max_iterations=5, max_consecutive_failures=3)
            result = loop(goal, config=config, run_verifier_on_pass=False)

            if result.status == VerifyStatus.PASS:
                results["fixed"] += 1
                record("proactive", 1, {"cycle": cycle, "item": item[:50]})
            else:
                results["failed"] += 1
                record("proactive", 0, {"cycle": cycle, "item": item[:50]})
            results["tokens_est"] += 2000

        results["cycles"] = cycle
        gaps = _discover_gaps({}, {})
        if not gaps:
            save_checkpoint(f"Proactive — all gaps fixed", "COMPLETE", cycle,
                            f"Fixed {results['fixed']} issues", str(root))
            break

    elapsed = int((time.time() - t_start) * 1000)
    save_checkpoint("Proactive done", "DONE", results["cycles"],
                    f"Fixed: {results['fixed']}, Failed: {results['failed']}, "
                    f"Tokens: ~{results['tokens_est']}, Time: {elapsed}ms", str(root))
    results["elapsed_ms"] = elapsed
    return results


def token_usage(project_root: str = "") -> dict:
    """Estimate token usage from run log."""
    import json
    root = Path(project_root) if project_root else Path(__file__).parent.parent
    log_path = root / ".ecc_logs" / "run-log.jsonl"
    if not log_path.exists():
        return {"total_est": 0, "runs": 0, "avg_per_run": 0}
    total = 0
    runs = 0
    with open(log_path) as f:
        for line in f:
            if line.strip():
                entry = json.loads(line)
                total += entry.get("tokens_est", 2000)
                runs += 1
    return {"total_est": total, "runs": runs, "avg_per_run": total // runs if runs else 0}
