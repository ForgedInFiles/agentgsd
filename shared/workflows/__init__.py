"""
Workflows package for agentgsd.

Contains autonomous task execution, planning, and self-correction capabilities.
"""

from shared.workflows.engine import (
    TaskState,
    TaskType,
    WorkflowStep,
    Workflow,
    TaskContext,
    WorkflowEngine,
    create_workflow_engine,
)

from shared.workflows.corrector import (
    ErrorType,
    CodeError,
    CorrectionAttempt,
    ValidationResult,
    CodeValidator,
    FixPatterns,
    SelfCorrectingLoop,
    create_correction_loop,
)

from shared.workflows.planner import (
    PlanStatus,
    RiskLevel,
    PlanStep,
    Plan,
    PlanGenerator,
    PlanReviewer,
    format_plan_for_display,
    create_plan_generator,
    create_plan_reviewer,
)

from shared.workflows.thoughts import (
    ThoughtType,
    ThoughtLevel,
    Thought,
    ThoughtStream,
    ThoughtPrinter,
    create_thought_stream,
)

__all__ = [
    # Engine
    "TaskState",
    "TaskType",
    "WorkflowStep",
    "Workflow",
    "TaskContext",
    "WorkflowEngine",
    "create_workflow_engine",
    # Corrector
    "ErrorType",
    "CodeError",
    "CorrectionAttempt",
    "ValidationResult",
    "CodeValidator",
    "FixPatterns",
    "SelfCorrectingLoop",
    "create_correction_loop",
    # Planner
    "PlanStatus",
    "RiskLevel",
    "PlanStep",
    "Plan",
    "PlanGenerator",
    "PlanReviewer",
    "format_plan_for_display",
    "create_plan_generator",
    "create_plan_reviewer",
    # Thoughts
    "ThoughtType",
    "ThoughtLevel",
    "Thought",
    "ThoughtStream",
    "ThoughtPrinter",
    "create_thought_stream",
]
