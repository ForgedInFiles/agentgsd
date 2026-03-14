"""
Interactive Planning & Review Mode for agentgsd.

A structured planning system that generates reviewable plans before
execution with user approval capabilities.
"""

import os
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pathlib import Path


class PlanStatus(Enum):
    """Status of a plan."""

    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RiskLevel(Enum):
    """Risk assessment levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PlanStep:
    """A single step in a plan."""

    step_id: str
    description: str
    files_affected: List[str] = field(default_factory=list)
    tool_needed: Optional[str] = None
    expected_outcome: str = ""
    risk_level: RiskLevel = RiskLevel.LOW
    status: str = "pending"  # pending, completed, skipped, failed
    result: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "description": self.description,
            "files_affected": self.files_affected,
            "tool_needed": self.tool_needed,
            "expected_outcome": self.expected_outcome,
            "risk_level": self.risk_level.value,
            "status": self.status,
            "result": self.result,
        }


@dataclass
class Plan:
    """A complete plan for a task."""

    plan_id: str
    title: str
    description: str
    goal: str
    steps: List[PlanStep] = field(default_factory=list)
    files_to_create: List[str] = field(default_factory=list)
    files_to_modify: List[str] = field(default_factory=list)
    files_to_delete: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    rollback_procedure: str = ""
    status: PlanStatus = PlanStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    approved_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    user_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "title": self.title,
            "description": self.description,
            "goal": self.goal,
            "steps": [s.to_dict() for s in self.steps],
            "files_to_create": self.files_to_create,
            "files_to_modify": self.files_to_modify,
            "files_to_delete": self.files_to_delete,
            "risks": self.risks,
            "rollback_procedure": self.rollback_procedure,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "user_notes": self.user_notes,
        }


class PlanGenerator:
    """Generate plans for tasks."""

    def __init__(self, indexer=None):
        self.indexer = indexer

    def generate_plan(self, task_description: str, task_type: str = "general") -> Plan:
        """Generate a plan for the given task."""
        plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        plan = Plan(
            plan_id=plan_id,
            title=self._generate_title(task_description),
            description=task_description,
            goal=task_description,
        )

        steps = self._generate_steps(task_description, task_type)
        plan.steps = steps

        plan.files_to_modify = self._identify_files(task_description)

        plan.risks = self._assess_risks(task_description, plan.files_to_modify)

        plan.rollback_procedure = self._generate_rollback(
            plan.files_to_modify, plan.files_to_create
        )

        plan.status = PlanStatus.PENDING_APPROVAL

        return plan

    def _generate_title(self, description: str) -> str:
        """Generate a title from the task description."""
        words = description.split()[:6]
        title = " ".join(words)
        if len(description.split()) > 6:
            title += "..."
        return title.title()

    def _generate_steps(self, description: str, task_type: str) -> List[PlanStep]:
        """Generate steps for the task."""
        steps = []

        if task_type == "bug_fix":
            steps = [
                PlanStep(
                    step_id="1",
                    description="Understand and analyze the bug",
                    tool_needed="grep",
                    expected_outcome="Identify root cause",
                ),
                PlanStep(
                    step_id="2",
                    description="Read affected source files",
                    tool_needed="read",
                    files_affected=[],
                    expected_outcome="Understand code context",
                ),
                PlanStep(
                    step_id="3",
                    description="Implement the fix",
                    tool_needed="edit",
                    expected_outcome="Code changes applied",
                ),
                PlanStep(
                    step_id="4",
                    description="Validate the fix",
                    tool_needed="bash",
                    expected_outcome="Tests pass",
                ),
            ]
        elif task_type == "feature_add":
            steps = [
                PlanStep(
                    step_id="1",
                    description="Explore existing codebase structure",
                    tool_needed="tree",
                    expected_outcome="Understand project layout",
                ),
                PlanStep(
                    step_id="2",
                    description="Design implementation approach",
                    expected_outcome="Clear design document",
                ),
                PlanStep(
                    step_id="3",
                    description="Implement feature code",
                    tool_needed="write",
                    expected_outcome="New code files created",
                ),
                PlanStep(
                    step_id="4",
                    description="Add tests for the feature",
                    tool_needed="write",
                    expected_outcome="Test coverage added",
                ),
                PlanStep(
                    step_id="5",
                    description="Validate implementation",
                    tool_needed="bash",
                    expected_outcome="All tests pass",
                ),
            ]
        elif task_type == "refactor":
            steps = [
                PlanStep(
                    step_id="1",
                    description="Analyze code to refactor",
                    tool_needed="read",
                    expected_outcome="Understand current implementation",
                ),
                PlanStep(
                    step_id="2",
                    description="Implement refactored code",
                    tool_needed="edit",
                    expected_outcome="Improved code structure",
                ),
                PlanStep(
                    step_id="3",
                    description="Verify refactoring didn't break functionality",
                    tool_needed="bash",
                    expected_outcome="All tests pass",
                ),
            ]
        else:
            steps = [
                PlanStep(
                    step_id="1",
                    description="Analyze the request",
                    expected_outcome="Clear understanding of goal",
                ),
                PlanStep(
                    step_id="2", description="Execute the task", expected_outcome="Task completed"
                ),
                PlanStep(
                    step_id="3", description="Validate results", expected_outcome="Results verified"
                ),
            ]

        return steps

    def _identify_files(self, description: str) -> List[str]:
        """Identify files that might be affected."""
        files = []

        if self.indexer:
            keywords = description.split()
            for keyword in keywords:
                if len(keyword) > 3:
                    results = self.indexer.search(keyword, top_k=3)
                    for r in results:
                        if r["file"] not in files:
                            files.append(r["file"])

        return files[:10]

    def _assess_risks(self, description: str, files: List[str]) -> List[str]:
        """Assess risks for the task."""
        risks = []

        dangerous_keywords = ["delete", "remove", "drop", "rm", "destroy"]
        if any(kw in description.lower() for kw in dangerous_keywords):
            risks.append("Potential data loss - requires careful review")

        if len(files) > 5:
            risks.append("Multiple files affected - higher chance of regression")

        critical_files = ["settings.py", "config.py", "main.py", "__init__.py"]
        for f in files:
            if any(cf in f for cf in critical_files):
                risks.append(f"Critical file affected: {f}")

        if not risks:
            risks.append("Low risk - straightforward task")

        return risks

    def _generate_rollback(self, files_to_modify: List[str], files_to_create: List[str]) -> str:
        """Generate rollback procedure."""
        lines = ["## Rollback Procedure", ""]

        if files_to_create:
            lines.append("1. Delete newly created files:")
            for f in files_to_create:
                lines.append(f"   - rm {f}")
            lines.append("")

        if files_to_modify:
            lines.append("2. Restore modified files from git:")
            lines.append("   - git checkout -- <files>")
            lines.append("")

        lines.append("3. Verify rollback:")
        lines.append("   - Run tests to ensure functionality is restored")

        return "\n".join(lines)


class PlanReviewer:
    """Review and manage plan approval."""

    def __init__(self):
        self.plans: Dict[str, Plan] = {}

    def add_plan(self, plan: Plan):
        """Add a plan to the reviewer."""
        self.plans[plan.plan_id] = plan

    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Get a plan by ID."""
        return self.plans.get(plan_id)

    def approve_plan(self, plan_id: str, notes: str = "") -> bool:
        """Approve a plan."""
        plan = self.plans.get(plan_id)
        if plan:
            plan.status = PlanStatus.APPROVED
            plan.approved_at = datetime.now()
            plan.user_notes = notes
            plan.updated_at = datetime.now()
            return True
        return False

    def reject_plan(self, plan_id: str, reason: str) -> bool:
        """Reject a plan."""
        plan = self.plans.get(plan_id)
        if plan:
            plan.status = PlanStatus.REJECTED
            plan.user_notes = reason
            plan.updated_at = datetime.now()
            return True
        return False

    def update_step_status(self, plan_id: str, step_id: str, status: str, result: str = "") -> bool:
        """Update the status of a step."""
        plan = self.plans.get(plan_id)
        if plan:
            for step in plan.steps:
                if step.step_id == step_id:
                    step.status = status
                    step.result = result
                    plan.updated_at = datetime.now()
                    return True
        return False

    def complete_plan(self, plan_id: str) -> bool:
        """Mark a plan as completed."""
        plan = self.plans.get(plan_id)
        if plan:
            plan.status = PlanStatus.COMPLETED
            plan.completed_at = datetime.now()
            plan.updated_at = datetime.now()
            return True
        return False


def format_plan_for_display(plan: Plan) -> str:
    """Format a plan for display to the user."""
    lines = [
        f"# 📋 {plan.title}",
        "",
        f"**Goal:** {plan.goal}",
        f"**Status:** {plan.status.value.upper()}",
        "",
        "## 📝 Description",
        plan.description,
        "",
    ]

    if plan.risks:
        lines.append("## ⚠️ Risks")
        for risk in plan.risks:
            lines.append(f"- {risk}")
        lines.append("")

    lines.append("## 📄 Files Affected")
    if plan.files_to_create:
        lines.append("**Create:**")
        for f in plan.files_to_create:
            lines.append(f"  + {f}")
    if plan.files_to_modify:
        lines.append("**Modify:**")
        for f in plan.files_to_modify:
            lines.append(f"  ~ {f}")
    if plan.files_to_delete:
        lines.append("**Delete:**")
        for f in plan.files_to_delete:
            lines.append(f"  - {f}")
    lines.append("")

    lines.append("## 🔧 Steps")
    for step in plan.steps:
        status_icon = {"pending": "○", "completed": "✓", "skipped": "⊘", "failed": "✗"}.get(
            step.status, "○"
        )

        risk_indicator = {
            RiskLevel.LOW: "",
            RiskLevel.MEDIUM: " 🟡",
            RiskLevel.HIGH: " 🟠",
            RiskLevel.CRITICAL: " 🔴",
        }.get(step.risk_level, "")

        lines.append(f"{status_icon} **{step.step_id}.** {step.description}{risk_indicator}")
        if step.files_affected:
            lines.append(f"   Files: {', '.join(step.files_affected)}")
    lines.append("")

    lines.append("## ↩️ Rollback")
    lines.append(plan.rollback_procedure)

    return "\n".join(lines)


def create_plan_generator(indexer=None) -> PlanGenerator:
    """Create a new plan generator."""
    return PlanGenerator(indexer)


def create_plan_reviewer() -> PlanReviewer:
    """Create a new plan reviewer."""
    return PlanReviewer()


__all__ = [
    "PlanStatus",
    "RiskLevel",
    "PlanStep",
    "Plan",
    "PlanGenerator",
    "PlanReviewer",
    "format_plan_for_display",
    "create_plan_generator",
    "create_plan_reviewer",
]
