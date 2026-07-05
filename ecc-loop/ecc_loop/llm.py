"""
ECC Loop — LLM-powered code generator.

Uses the existing DeepSeek API to generate fix code for
gaps discovered by the DISCOVER stage.
"""

import os
import json
import urllib.request
import urllib.error


def _get_api_key() -> str:
    """Load DeepSeek API key from Hermes config."""
    # Try env file first
    env_path = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env_path):
        for line in open(env_path):
            if line.startswith("DEEPSEEK_API_KEY=") and not line.startswith("#"):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
                if key:
                    return key
    # Fallback to env var
    return os.environ.get("DEEPSEEK_API_KEY", "")


def _llm_call(messages: list[dict], max_tokens: int = 2000) -> str:
    """Call DeepSeek API and return the response text."""
    api_key = _get_api_key()
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY not found in ~/.hermes/.env")

    body = json.dumps({
        "model": "deepseek-chat",
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.3,  # Low temp for code generation
    }).encode()

    req = urllib.request.Request(
        "https://api.deepseek.com/v1/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"API error {e.code}: {e.read().decode()[:200]}")
    except Exception as e:
        raise RuntimeError(f"LLM call failed: {e}")


def generate_fix(gap_description: str, context: dict | None = None) -> str:
    """
    Ask LLM to generate a Python code fix for a gap.

    Returns executable Python code (with __result__ set).
    """
    system_prompt = """You are an expert Python developer fixing issues in the ECC Loop project.
The ECC Loop is a self-improving agent loop at ~/projects/ecc-loop/.
Project structure and real module APIs:

  ecc_loop/engine.py — Five-stage loop:
    discover(goal, feedback=None) -> DiscoveryResult
    plan(discovery) -> Plan
    execute(plan) -> ExecutionResult
    verify(plan, execution) -> VerifyResult
    loop(goal) — full closed D->P->E->V->I cycle
    goal(task, condition_cmd) — run until condition met
    run_verifier() — external pytest check

  ecc_loop/models.py — Data classes:
    Task(name, description, status, output, error)
    Plan(tasks, summary)
    VerifyResult(status, passed_tasks, failed_tasks, summary, feedback)
    DiscoveryResult(issue, context, goals, assumptions)
    CircuitBreakerConfig(max_iterations=5, max_consecutive_failures=3)
    TaskStatus.PENDING/RUNNING/PASS/FAIL, VerifyStatus.PASS/FAIL

  ecc_loop/handlers.py:
    ShellHandler, CodeHandler, FileHandler
    handler_for(task) — auto-detects handler type

  ecc_loop/llm.py:
    generate_fix(gap_description) — calls LLM, returns Python code
    LLMHandler — generates fix code via LLM then executes it

  ecc_loop/seed.py: load_seed(path), save_seed(state, path), mark_complete(state, task)
  ecc_loop/scanner.py: detect_changes(), report_changes()
  ecc_loop/reflection.py: analyze_observations(), reflect(query)

Generate executable Python code that directly fixes the issue.
- Use from ecc_loop.xxx import exact names listed above
- Set __result__ to describe what was done
- Use pathlib.Path for file operations
- Know that tests go in tests/ directory at project root
- Return ONLY valid Python code, no markdown fences, no explanations"""

    user_prompt = f"Fix this gap in the ECC Loop project:\n{gap_description}\n\nGenerate executable Python code that fixes this issue. Set __result__ to describe what was done."

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    return _llm_call(messages)


class LLMHandler:
    """Handler that generates fix code via LLM, then executes it."""
    def __call__(self, task) -> str:
        from ecc_loop.handlers import CodeHandler
        desc = task.description.strip()
        if not desc:
            raise ValueError("No task description for LLM")

        # Generate fix code
        code = generate_fix(desc)
        if not code:
            raise RuntimeError("LLM returned empty code")

        # Clean up code (remove markdown fences if present)
        code = code.strip()
        for fence in ("```python", "```"):
            if code.startswith(fence):
                code = code[len(fence):].strip()
        if code.endswith("```"):
            code = code[:-3].strip()
        if not code:
            raise RuntimeError("LLM code is empty after cleanup")

        # Execute the generated code
        return CodeHandler()(type(task)(name=task.name, description=code))
