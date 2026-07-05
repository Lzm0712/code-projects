"""
ECC Loop — Data Models (Phase 1)

Data structures for the five-stage engine.
Following Karpathy principles: minimal, surgical, goal-driven.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASS = "pass"
    FAIL = "fail"


class VerifyStatus(Enum):
    PASS = "pass"
    FAIL = "fail"


@dataclass
class Task:
    """A single executable task within a plan."""
    name: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    output: str = ""
    error: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
        }


@dataclass
class DiscoveryResult:
    """Stage 1 output: what we found and what problem we're solving."""
    issue: str           # The core problem/goal
    context: dict         # Relevant context (skills, recent observations)
    goals: list[str]     # Specific sub-goals
    assumptions: list[str] = field(default_factory=list)  # Stated assumptions

    def to_dict(self) -> dict:
        return {
            "issue": self.issue,
            "context": self.context,
            "goals": self.goals,
            "assumptions": self.assumptions,
        }


@dataclass
class Plan:
    """Stage 2 output: ordered task sequence with success criteria."""
    tasks: list[Task]
    summary: str = ""

    def to_dict(self) -> dict:
        return {
            "tasks": [t.to_dict() for t in self.tasks],
            "summary": self.summary,
        }


@dataclass
class ExecutionResult:
    """Stage 3 output: execution outcomes for all tasks."""
    results: list[Task]  # Updated tasks with status/output/error

    def to_dict(self) -> dict:
        return {"results": [r.to_dict() for r in self.results]}


@dataclass
class VerifyResult:
    """Stage 4 output: verification against success criteria."""
    status: VerifyStatus
    passed_tasks: list[str]
    failed_tasks: list[str]
    summary: str
    feedback: str = ""  # What went wrong (fed into ITERATE)

    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "passed_tasks": self.passed_tasks,
            "failed_tasks": self.failed_tasks,
            "summary": self.summary,
            "feedback": self.feedback,
        }


@dataclass
class ECCState:
    """Full ECC Loop state — lives in seed.json."""
    version: str = "1.0"
    current_goal: str = ""
    stage: str = "idle"  # idle | discover | plan | execute | verify | iterate
    iteration: int = 0
    discovery: Optional[DiscoveryResult] = None
    plan: Optional[Plan] = None
    execution: Optional[ExecutionResult] = None
    verify: Optional[VerifyResult] = None
