"""
Autonomous Task Execution Engine for agentgsd.

A state machine-based workflow engine that can chain multiple tool
invocations based on task type without requiring external APIs.
"""

import os
import json
import re
from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set
from datetime import datetime


class TaskState(Enum):
    """States in the task execution state machine."""

    IDLE = "idle"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    EXECUTING = "executing"
    VALIDATING = "validating"
    CORRECTING = "correcting"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING_USER = "waiting_user"


class TaskType(Enum):
    """Types of tasks the engine can handle."""

    BUG_FIX = "bug_fix"
    FEATURE_ADD = "feature_add"
    REFACTOR = "refactor"
    TEST_WRITE = "test_write"
    CODE_REVIEW = "code_review"
    DOCUMENT = "document"
    GENERAL = "general"


@dataclass
class WorkflowStep:
    """A single step in a workflow."""

    name: str
    description: str
    action: str
    tool: Optional[str] = None
    condition: Optional[str] = None
    on_success: Optional[str] = None
    on_failure: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class Workflow:
    """A workflow definition for a task type."""

    task_type: TaskType
    name: str
    description: str
    steps: List[WorkflowStep]
    requires_approval: bool = False
    auto_rollback: bool = True


@dataclass
class TaskContext:
    """Context for a task being executed."""

    task_id: str
    task_type: TaskType
    description: str
    state: TaskState = TaskState.IDLE
    current_step: int = 0
    steps_completed: List[str] = field(default_factory=list)
    tool_results: Dict[str, str] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    user_approved: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowEngine:
    """State machine engine for autonomous task execution."""

    def __init__(self, registry=None):
        self.registry = registry
        self.workflows: Dict[TaskType, Workflow] = {}
        self.current_task: Optional[TaskContext] = None
        self.task_history: List[TaskContext] = []

        self._register_default_workflows()

    def _register_default_workflows(self):
        """Register default workflow templates."""

        bug_fix_workflow = Workflow(
            task_type=TaskType.BUG_FIX,
            name="Bug Fix Workflow",
            description="Automated bug fixing workflow",
            requires_approval=True,
            steps=[
                WorkflowStep(
                    name="analyze_bug",
                    description="Understand the bug by analyzing error messages and code",
                    action="analyze",
                ),
                WorkflowStep(
                    name="locate_code",
                    description="Find the relevant code files",
                    action="search",
                    tool="grep",
                ),
                WorkflowStep(
                    name="understand_code",
                    description="Read and understand the affected code",
                    action="read_files",
                    tool="read",
                ),
                WorkflowStep(
                    name="plan_fix",
                    description="Plan the fix approach",
                    action="plan",
                ),
                WorkflowStep(
                    name="implement_fix",
                    description="Implement the fix",
                    action="implement",
                    tool="edit",
                    on_success="validate_fix",
                    on_failure="retry_implement",
                    max_retries=3,
                ),
                WorkflowStep(
                    name="validate_fix",
                    description="Validate the fix by running tests or linters",
                    action="validate",
                    tool="bash",
                ),
                WorkflowStep(
                    name="verify_solution",
                    description="Verify the solution works",
                    action="verify",
                ),
            ],
        )

        feature_add_workflow = Workflow(
            task_type=TaskType.FEATURE_ADD,
            name="Feature Addition Workflow",
            description="Automated feature implementation workflow",
            requires_approval=True,
            steps=[
                WorkflowStep(
                    name="understand_requirement",
                    description="Understand the feature requirement",
                    action="analyze",
                ),
                WorkflowStep(
                    name="explore_codebase",
                    description="Explore existing code structure",
                    action="explore",
                    tool="tree",
                ),
                WorkflowStep(
                    name="design_implementation",
                    description="Design the implementation approach",
                    action="design",
                ),
                WorkflowStep(
                    name="implement_feature",
                    description="Implement the feature",
                    action="implement",
                    max_retries=3,
                ),
                WorkflowStep(
                    name="add_tests",
                    description="Add tests for the feature",
                    action="test",
                    max_retries=2,
                ),
                WorkflowStep(
                    name="validate_implementation",
                    description="Validate the implementation",
                    action="validate",
                ),
            ],
        )

        refactor_workflow = Workflow(
            task_type=TaskType.REFACTOR,
            name="Refactoring Workflow",
            description="Code refactoring workflow",
            requires_approval=True,
            steps=[
                WorkflowStep(
                    name="analyze_code",
                    description="Analyze code to be refactored",
                    action="analyze",
                ),
                WorkflowStep(
                    name="plan_refactor",
                    description="Plan refactoring approach",
                    action="plan",
                ),
                WorkflowStep(
                    name="execute_refactor",
                    description="Execute refactoring",
                    action="implement",
                    max_retries=3,
                ),
                WorkflowStep(
                    name="validate_refactor",
                    description="Validate refactored code",
                    action="validate",
                ),
            ],
        )

        test_write_workflow = Workflow(
            task_type=TaskType.TEST_WRITE,
            name="Test Writing Workflow",
            description="Automated test writing workflow",
            requires_approval=False,
            steps=[
                WorkflowStep(
                    name="analyze_target",
                    description="Analyze code to test",
                    action="analyze",
                ),
                WorkflowStep(
                    name="identify_cases",
                    description="Identify test cases",
                    action="identify",
                ),
                WorkflowStep(
                    name="write_tests",
                    description="Write test code",
                    action="implement",
                    max_retries=2,
                ),
                WorkflowStep(
                    name="run_tests",
                    description="Run tests to verify",
                    action="validate",
                    tool="bash",
                ),
            ],
        )

        general_workflow = Workflow(
            task_type=TaskType.GENERAL,
            name="General Task Workflow",
            description="General purpose task workflow",
            requires_approval=False,
            steps=[
                WorkflowStep(
                    name="analyze",
                    description="Understand the task",
                    action="analyze",
                ),
                WorkflowStep(
                    name="execute",
                    description="Execute the task",
                    action="execute",
                    max_retries=2,
                ),
                WorkflowStep(
                    name="validate",
                    description="Validate the result",
                    action="validate",
                ),
            ],
        )

        self.workflows[TaskType.BUG_FIX] = bug_fix_workflow
        self.workflows[TaskType.FEATURE_ADD] = feature_add_workflow
        self.workflows[TaskType.REFACTOR] = refactor_workflow
        self.workflows[TaskType.TEST_WRITE] = test_write_workflow
        self.workflows[TaskType.GENERAL] = general_workflow

    def classify_task(self, description: str) -> TaskType:
        """Classify a task based on its description using local heuristics."""
        desc_lower = description.lower()

        bug_keywords = ["bug", "fix", "error", "crash", "fail", "broken", "wrong", "issue"]
        feature_keywords = ["add", "new", "implement", "create", "feature", "support"]
        refactor_keywords = ["refactor", "rename", "restructure", "improve", "clean"]
        test_keywords = ["test", "spec", "verify", "coverage"]

        bug_score = sum(1 for kw in bug_keywords if kw in desc_lower)
        feature_score = sum(1 for kw in feature_keywords if kw in desc_lower)
        refactor_score = sum(1 for kw in refactor_keywords if kw in desc_lower)
        test_score = sum(1 for kw in test_keywords if kw in desc_lower)

        scores = {
            TaskType.BUG_FIX: bug_score,
            TaskType.FEATURE_ADD: feature_score,
            TaskType.REFACTOR: refactor_score,
            TaskType.TEST_WRITE: test_score,
        }

        max_score = max(scores.values())

        if max_score > 0:
            for task_type, score in scores.items():
                if score == max_score:
                    return task_type

        return TaskType.GENERAL

    def start_task(self, description: str, task_type: Optional[TaskType] = None) -> TaskContext:
        """Start a new task."""
        if task_type is None:
            task_type = self.classify_task(description)

        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        context = TaskContext(
            task_id=task_id,
            task_type=task_type,
            description=description,
            state=TaskState.ANALYZING,
        )

        self.current_task = context
        self.task_history.append(context)

        return context

    def get_current_workflow(self) -> Optional[Workflow]:
        """Get the workflow for the current task."""
        if self.current_task:
            return self.workflows.get(self.current_task.task_type)
        return None

    def get_next_step(self) -> Optional[WorkflowStep]:
        """Get the next step to execute."""
        if not self.current_task:
            return None

        workflow = self.get_current_workflow()
        if not workflow:
            return None

        if self.current_task.current_step < len(workflow.steps):
            return workflow.steps[self.current_task.current_step]

        return None

    def advance_state(self, new_state: TaskState):
        """Advance the task state."""
        if self.current_task:
            self.current_task.state = new_state
            self.current_task.updated_at = datetime.now()

    def complete_step(self, step_name: str, result: str = "success"):
        """Mark a step as completed."""
        if self.current_task:
            self.current_task.steps_completed.append(step_name)
            self.current_task.tool_results[step_name] = result
            self.current_task.current_step += 1
            self.current_task.updated_at = datetime.now()

    def add_error(self, error: str):
        """Add an error to the current task."""
        if self.current_task:
            self.current_task.errors.append(error)

    def approve(self):
        """Approve the current task for execution."""
        if self.current_task:
            self.current_task.user_approved = True

    def reject(self, reason: str = "Rejected by user"):
        """Reject the current task."""
        if self.current_task:
            self.current_task.state = TaskState.FAILED
            self.current_task.errors.append(reason)

    def get_status(self) -> Dict[str, Any]:
        """Get current task status."""
        if not self.current_task:
            return {"status": "no_active_task"}

        workflow = self.get_current_workflow()
        next_step = self.get_next_step()

        return {
            "task_id": self.current_task.task_id,
            "task_type": self.current_task.task_type.value,
            "description": self.current_task.description,
            "state": self.current_task.state.value,
            "progress": f"{self.current_task.current_step}/{len(workflow.steps) if workflow else 0}",
            "next_step": next_step.name if next_step else None,
            "requires_approval": workflow.requires_approval if workflow else False,
            "approved": self.current_task.user_approved,
            "errors": self.current_task.errors,
        }

    def generate_plan(self) -> str:
        """Generate a text-based plan for the current task."""
        if not self.current_task:
            return "No active task"

        workflow = self.get_current_workflow()
        if not workflow:
            return "No workflow available"

        lines = [
            f"# {workflow.name}",
            f"**Task:** {self.current_task.description}",
            f"**Type:** {workflow.task_type.value}",
            "",
            "## Steps:",
        ]

        for i, step in enumerate(workflow.steps, 1):
            status = "✓" if step.name in self.current_task.steps_completed else "○"
            lines.append(f"{i}. {status} {step.name} - {step.description}")

        if workflow.requires_approval:
            lines.append("")
            lines.append("⚠️ **This workflow requires user approval before execution**")

        if self.current_task.errors:
            lines.append("")
            lines.append("## Errors:")
            for error in self.current_task.errors:
                lines.append(f"- {error}")

        return "\n".join(lines)

    def reset(self):
        """Reset the current task."""
        self.current_task = None


def create_workflow_engine(registry=None) -> WorkflowEngine:
    """Create a new workflow engine instance."""
    return WorkflowEngine(registry)


__all__ = [
    "TaskState",
    "TaskType",
    "WorkflowStep",
    "Workflow",
    "TaskContext",
    "WorkflowEngine",
    "create_workflow_engine",
]
