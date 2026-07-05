# ECC Loop — LOOP.md

Loop configuration for the Evolutionary Consciousness Code Loop.
Following [loop-engineering](https://github.com/cobusgreyling/loop-engineering) conventions.

## Identity

| Field | Value |
|-------|-------|
| **Loop name** | ECC Self-Improvement Loop |
| **Pattern** | `ecc-loop` |
| **Cadence** | Task-driven (runs on task completion, not on a schedule) |
| **Readiness** | L1 (report + detect) → L2 (assisted fixes with verifier) |
| **Goal** | Monitor Hermes agent state, detect improvement opportunities, execute self-improvements |

## State

| File | Purpose |
|------|---------|
| `STATE.md` | Human-readable project state |
| `~/.hermes/ecc-loop-seed.json` | Machine-readable loop state (iteration count, circuit breaker) |
| `~/.hermes/observations.jsonl` | Agent interaction log (DISCOVER context) |
| `~/.hermes/ecc-skill-scan-cache.json` | Skill change detection cache |

## Allowed Operations

| Phase | Allowed | Denied |
|-------|---------|--------|
| **DISCOVER** | Read state, scan skills, analyze observations | Modify files |
| **PLAN** | Create task lists, set success criteria | Execute anything |
| **EXECUTE** | Shell commands, code patches, skill invocations via handlers | Unrestricted writes |
| **VERIFY** | Check task status, run tests | Modify state |

## Circuit Breaker

| Threshold | Default | Behavior |
|-----------|---------|----------|
| `max_iterations` | 5 | Max total loop iterations per goal |
| `max_consecutive_failures` | 3 | Consecutive same-error → trip (tracked in `loop()`) |
| Trip action | Return FAIL with reason | Escalate to human |

## Commands

```bash
ecc run  <goal>    # Single pass: D→P→E→V (no iteration)
ecc loop <goal>    # Full closed loop: iterate on FAIL until PASS or breaker trips
ecc scan           # Detect skill changes
ecc seed           # Dump current seed state
ecc status         # Show loop health + iteration count
```

## Lifecycle

```
L1 (current) — Report + detect
  ├─ Scan skills for changes
  ├─ Analyze observations for patterns
  ├─ Detect drift between state and reality
  └─ Report findings (no auto-fix)

L2 (planned) — Assisted fixes with verifier
  ├─ Apply small code patches via handlers
  ├─ Run verifier (tests) after each patch
  ├─ Auto-revert on failure
  └─ Escalate anything complex

L3 (future) — Autonomous
  ├─ Full auto-fix loop
  ├─ Self-scheduling
  └─ Human approval gates for risky changes
```
