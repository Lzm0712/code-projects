"""
ECC Loop — Worktree Isolation (Best Practice #6: 工作树隔离)

Never let multiple agents work on the same files simultaneously.
Creates an isolated temp copy, runs the task, copies back on success.
"""
import shutil
import tempfile
from pathlib import Path


class WorktreeHandler:
    """
    File-level sandbox: copies project to temp, runs task,
    copies changes back only on success.
    """

    def __init__(self, project_root: str = ""):
        self.root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.tmp_dir: Path | None = None

    def __call__(self, task) -> str:
        from ecc_loop.handlers import CodeHandler

        # Create isolated copy
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="ecc-wt-"))
        tmp_project = self.tmp_dir / "project"
        shutil.copytree(
            self.root, tmp_project,
            ignore=shutil.ignore_patterns(
                "__pycache__", ".venv", ".pytest_cache", ".git",
                ".ecc_logs", ".hermes", "node_modules"
            )
        )

        # Run task in isolation
        try:
            handler = CodeHandler()
            import os
            original_cwd = os.getcwd()
            os.chdir(tmp_project)
            try:
                result = handler(task)
            finally:
                os.chdir(original_cwd)

            # On success, copy changes back
            self._copy_back(tmp_project)
            return f"[worktree] {result}"

        except Exception as e:
            # On failure: discard everything
            raise RuntimeError(f"Worktree task failed: {e}")

        finally:
            # Cleanup temp dir
            if self.tmp_dir and self.tmp_dir.exists():
                shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _copy_back(self, tmp_project: Path):
        """Copy modified/new files from temp back to project root."""
        import filecmp
        for src_file in tmp_project.rglob("*"):
            if src_file.is_dir():
                continue
            if any(p in src_file.parts for p in ["__pycache__", ".pytest_cache"]):
                continue

            rel = src_file.relative_to(tmp_project)
            dest = self.root / rel

            if not dest.exists() or not filecmp.cmp(str(src_file), str(dest), shallow=False):
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dest)


def isolate(task, project_root: str = "") -> str:
    """Quick worktree isolation for a single task."""
    return WorktreeHandler(project_root)(task)
