# ECC Loop — Budget & Kill Switch

## Loop Budget

| Item | Budget |
|------|--------|
| Max iterations per run | 5 (circuit breaker) |
| Max consecutive failures | 3 (circuit breaker) |
| LLM calls per fix | 1 (generate) + 1 (reviewer) |
| LLM cost per run | ~$0.01 USD (DeepSeek) |
| Pytest runtime | ~1s |
| Total per loop run | ~5-10s + $0.01 |

## Kill Switch

To pause ECC: `ecc status` → check circuit state → address gaps.
To stop auto-evolution: set `CIRCUIT_BREAKER_DISABLED=1` env var.

### Pause Criteria
- 3 consecutive same-error → circuit breaker trips
- 5 total iterations → circuit breaker trips
- Human intervention needed → review `.ecc_logs/`

### Resume
- Clear `~/.hermes/ecc-loop-seed.json` to reset state
- Run `ecc improve` to verify health
