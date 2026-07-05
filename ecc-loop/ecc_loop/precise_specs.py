"""
ECC Loop — Precise Specs (Best Practice #5: 编写精确规格)

Binary success criteria for tasks. No vague "works" or "looks good".
Each spec is a concrete, verifiable condition.
"""
import subprocess
from pathlib import Path


class Spec:
    """A precise, binary success criterion for a task."""

    def __init__(self, description: str, condition: str):
        self.description = description
        self.condition = condition  # Shell command; exit 0 = pass

    def verify(self, cwd: str = "") -> tuple[bool, str]:
        """Run the condition. Returns (passed, output)."""
        try:
            proc = subprocess.run(
                self.condition, shell=True, capture_output=True,
                text=True, timeout=30, cwd=cwd or str(Path.home()),
            )
            if proc.returncode == 0:
                return True, f"✅ {self.description}"
            return False, f"❌ {self.description}: {proc.stderr.strip()[:100]}"
        except Exception as e:
            return False, f"❌ {self.description}: {e}"


# ── Pre-built specs ──────────────────────────────────────────────────

class Specs:
    """Common precise specs for ECC tasks."""

    TESTS_PASS = Spec("所有测试通过", "python3 -m pytest -q")
    NO_LINT_ERRORS = Spec("无 lint 错误", "python3 -m flake8 ecc_loop/ --max-line-length=120 2>&1 || true")
    FILE_EXISTS = lambda path: Spec(f"文件存在: {path}", f"test -f {path}")
    FILE_CONTAINS = lambda path, text: Spec(f"文件包含: {text}", f"grep -q '{text}' {path}")
    IMPORT_OK = lambda module: Spec(f"模块可导入: {module}", f"python3 -c 'import {module}'")


def verify_specs(specs: list[Spec], cwd: str = "") -> tuple[bool, list[str]]:
    """Run multiple specs. Returns (all_passed, results)."""
    results = []
    all_pass = True
    for spec in specs:
        ok, msg = spec.verify(cwd)
        results.append(msg)
        if not ok:
            all_pass = False
    return all_pass, results
