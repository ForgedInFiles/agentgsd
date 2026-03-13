---
name: subagent-driven-development
description: Executes implementation plans by dispatching fresh subagents per task with two-stage review (spec compliance, then code quality), or executes in batches with human checkpoints. This is the fourth step in the gsdmode workflow.
license: MIT
metadata:
  author: adapted from obra/superpowers
  version: "1.0"
  tags: development,subagent,implementation,workflow
---

# Subagent-Driven Development Skill (gsdmode)

## Overview
This skill activates after plans have been written and validated. It implements the approved plan by breaking it down into individual tasks and executing each task with quality assurance. For each task, it either:
1. Dispatches a fresh subagent with the task specification (spec compliance review → code quality review), OR
2. Executes the task in the current context with human checkpoints between batches

The subagent-driven-development skill follows the gsdmode philosophy of "test-driven development" and "systematic over ad-hoc" - it ensures each piece of work is correct before moving on, maintaining high quality throughout implementation.

## When to Activate
This skill should automatically activate when:
- The user has validated an implementation plan (from writing-plans)
- The agent is ready to begin implementation work
- The user indicates they want to start coding based on an approved plan
- The agent needs to implement a series of tasks with quality gates

It should NOT activate when:
- The user is still planning or designing (brainstorming or writing-plans phase)
- The user wants to make a small, isolated change that doesn't follow the plan
- The agent is already in the middle of implementing a task and needs to continue
- The user is asking for explanations or reviewing existing code

## Core Process

### 1. Task Preparation
For each task in the plan:
- Read the complete task specification (files, code, verification, dependencies)
- Verify all dependencies are completed before starting
- Prepare the task description for the subagent or current context
- Set up any necessary environment or state for the task

### 2. Two-Stage Review Process (Preferred)
When using subagents:
**Stage 1: Spec Compliance Review**
- Dispatch a fresh subagent with ONLY the task specification
- Ask: "Does this implementation fully and correctly satisfy the task requirements?"
- Subagent should respond with: "Yes, it meets all requirements" or list specific gaps
- If gaps exist, have subagent revise until spec compliance is achieved

**Stage 2: Code Quality Review**
- Dispatch another fresh subagent (or the same one) with the implemented code
- Ask: "Review this code for quality, clarity, maintainability, and best practices"
- Subagent should provide feedback on: naming, structure, error handling, edge cases, etc.
- Implement suggested improvements that align with project standards

### 3. Batch Execution with Checkpoints (Alternative)
When not using subagents or for simpler tasks:
- Implement a batch of 2-3 related tasks in the current context
- After each batch, pause for human checkpoint:
  - Review what was implemented
  - Run verification steps for completed tasks
  - Confirm everything is correct before proceeding
- Continue with next batch after approval

### 4. Verification & Completion
For each task:
- Run the specified verification steps (tests, checks, etc.)
- Confirm the task is complete before marking it as done
- If verification fails, debug and fix until it passes
- Only after successful verification should the task be marked complete

### 5. Progress Tracking
- Maintain a record of completed tasks
- Update the plan document to show progress
- Provide regular summaries of what's been accomplished
- Notify the user of any blockers or issues encountered

## Output Format
The subagent-driven-development skill should produce progress updates and a completion record:

### 📊 Task Execution Log
A chronological record of task execution:
- Task ID and description
- Start time
- Approach used (subagent/direct)
- Any issues encountered and how they were resolved
- Verification results
- Completion time

### 🐞 Issues & Resolutions
Any problems that arose during implementation:
- What the issue was
- Root cause analysis
- How it was fixed
- Preventive measures taken

### ✅ Completed Tasks
List of tasks that have been successfully implemented and verified:
- Task ID
- Description
- Files modified
- Verification status

### 📋 Remaining Work
Tasks that still need to be completed:
- Task ID
- Description
- Dependencies (if any)
- Estimated time

## Tool Usage Patterns

### Using with Agent Tools
```yaml
# Typical workflow with subagents
1. User: "Let's start implementing the authentication plan"
2. Agent activates subagent-driven-development skill
3. For each task in the plan:
   a. Verify dependencies are complete
   b. Dispatch subagent #1: "Here is the task spec... Does this implementation fully satisfy the requirements?"
   c. If needed, have subagent revise until spec compliant
   d. Dispatch subagent #2: "Review this code for quality and best practices..."
   e. Implement quality improvements as needed
   f. Run verification steps from task spec
   g. If verification fails, debug and fix
   h. Mark task as complete
4. Update plan document with progress
5. Continue until all tasks are complete
```

### Direct Implementation Approach
```yaml
# Typical workflow without subagents
1. User: "Let's implement these two tasks directly"
2. Agent activates subagent-driven-development skill
3. For each task (or small batch):
   a. Implement the specification in current context
   b. Run verification steps
   c. If verification fails, debug and fix
   d. Mark task as complete
   e. Pause for human checkpoint after every 2-3 tasks
   f. Review completed work with user before continuing
```

## Integration with gsdmode Workflow
This skill is the fourth in the gsdmode sequence:
1. **Brainstorming** → Refines the idea
2. **Using Git Worktrees** → Sets up clean implementation environment
3. **Writing Plans** → Creates detailed implementation tasks
4. **Subagent-Driven Development** (this skill) → Executes the plan with quality gates
5. **TDD** → Ensures correctness during implementation (overlaps with this skill)
6. **Code Review** → Maintains quality between tasks (overlaps with this skill)
7. **Finishing Branch** → Completes the work cycle

The agent should automatically progress to the next skill when:
- All tasks in the plan have been completed and verified
- The user has confirmed the implementation meets their needs
- There is a clean verification state (tests passing, etc.)
- The user indicates readiness to move to finishing the development branch

## Best Practices

### Do ✅
- Always verify dependencies before starting a task
- Use fresh subagents when possible for unbiased review
- Keep subagent prompts focused and specific
- Verify everything - don't assume correctness
- Keep the user informed of progress and any blockers
- Celebrate small wins and completed tasks
- Learn from issues and improve the process

### Don't ❌
- Skip verification steps to "move faster"
- Implement without checking dependencies first
- Ignore subagent feedback or quality suggestions
- Let tasks pile up without verification
- Work in silence without updating the user
- Assume something is correct because "it looks right"
- Forget to update the plan document with progress

## Example Session

**User**: "Let's start implementing the blog authentication feature using our plan."

**Agent (Subagent-Driven Development)**:
1. Reads the plan document from writing-plans phase
2. Starts with Task T1: Create User model
3. Verifies no dependencies (T1 has none)
4. Dispatches subagent #1: 
   ```
   Here is the task spec for T1:
   Files: src/models/user.py
   Code: [complete User model code as specified in plan]
   Verification: 
     - Run: python -c "from src.models.user import User; u=User(); u.set_password('test'); assert u.check_password('test')"
     - Check: File exists and contains the complete class definition
   
   Does this implementation fully and correctly satisfy the task requirements?
   ```
5. Subagent reviews and either approves or suggests revisions
6. If revisions needed, has subagent implement them
7. Dispatches subagent #2:
   ```
   Please review this code for quality, clarity, maintainability, and best practices:
   [the User model code]
   
   Provide feedback on naming, structure, error handling, edge cases, etc.
   ```
8. Implements agreed-upon quality improvements
9. Runs verification steps:
   - Runs the test command
   - Confirms file exists and contains correct code
10. Marks T1 as complete, updates plan document
11. Continues with T2, T3, etc., following the same process
12. After each batch of tasks, pauses for human checkpoint if using direct implementation
13. When all tasks are complete, asks: "All tasks in the plan have been completed and verified. Should we run a final comprehensive test or move to code review?"

**User**: "Let's run the full test suite to make sure everything works together."

**Agent**: Runs comprehensive tests, then if passing, deactivates subagent-driven-development skill and activates requesting-code-review skill.

---
*Adapted from obra/superpowers subagent-driven-development skill for agentgsd gsdmode*
