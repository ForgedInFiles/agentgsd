---
name: writing-plans
description: Breaks approved designs into bite-sized implementation tasks (2-5 minutes each) with exact file paths, complete code, and verification steps. This is the third step in the gsdmode workflow.
license: MIT
metadata:
  author: adapted from obra/superpowers
  version: "1.0"
  tags: planning,tasks,implementation,workflow
---

# Writing Plans Skill (gsdmode)

## Overview
This skill activates after the brainstorming skill has produced a validated design document. It takes the high-level design and breaks it down into concrete, actionable implementation tasks that are small enough to be completed quickly (typically 2-5 minutes each).

Each task includes:
- Exact file paths to be modified
- Complete code to be written (not just stubs)
- Clear verification steps to confirm the task is done correctly
- Dependencies on other tasks (if any)

The writing plans skill follows the gsdmode philosophy of "evidence over claims" - it produces plans that are so specific that implementation becomes a matter of following instructions, reducing the chance of misinterpretation or drift from the design.

## When to Activate
This skill should automatically activate when:
- The brainstorming skill has completed and produced a validated design document
- The user has confirmed the design is correct and ready for implementation planning
- The agent is asked to create an implementation plan based on discussed requirements
- The user says something like "Let's move to planning" or "How should we break this down?"

It should NOT activate when:
- The user is still exploring alternatives (brainstorming phase)
- The user wants to make a small, isolated change
- Implementation work is already in progress
- The user is asking for explanations about existing code

## Core Process

### 1. Task Granularity
Break work into tasks that are:
- Small enough to complete in 2-5 minutes of focused work
- Large enough to provide meaningful progress and value
- Independent enough to be worked on in any order (when possible)
- Specific enough that completion is unambiguous

### 2. Task Specification
For each task, specify:
- **File(s) to modify**: Exact paths relative to project root
- **Code to write**: Complete, copy-pasteable implementation (not pseudocode)
- **Verification steps**: How to confirm the task is done correctly (tests, checks, etc.)
- **Dependencies**: Which other tasks must be completed first (if any)
- **Estimated time**: Realistic time estimate for completion

### 3. Interface Definition
When tasks involve interactions between components:
- Clearly define the interface (function signatures, data structures, etc.)
- Specify expected behavior and error conditions
- Note any contracts that must be upheld

### 4. Error Handling & Edge Cases
Ensure each task includes:
- Proper error handling for expected error conditions
- Validation of inputs where appropriate
- Consideration of edge cases (empty inputs, boundary values, etc.)

### 5. Testability
Design tasks to be testable:
- Where possible, write tests first (TDD approach)
- Ensure verification steps include running relevant tests
- Make sure new code is observable and measurable

### 6. Sequence Optimization
Order tasks to:
- Minimize blocking dependencies
- Allow for parallel work where possible
- Build foundational elements first
- Deliver user-facing value early when appropriate

## Output Format
The writing plans skill should produce a plan document with these sections:

### 📋 Implementation Plan
A high-level summary of the approach and any important notes about the implementation strategy.

### 🧩 Task List
A numbered list of tasks, each containing:
- **Task ID**: Unique identifier (e.g., T1, T2, T3)
- **Description**: What the task accomplishes in plain language
- **Files**: Exact file paths to be modified (comma-separated if multiple)
- **Code**: Complete code to be written (or edit instructions for existing files)
- **Verification**: How to verify the task is complete (test commands, checks, etc.)
- **Dependencies**: Task IDs that must be completed first (if any)
- **Est. Time**: Realistic time estimate (e.g., "3 min")

### 🔗 Dependency Graph
A visual or textual representation of task dependencies to help understand execution order.

### 🛠️ Setup Notes
Any special setup required before beginning implementation (environment variables, configuration, etc.).

### ✅ Definition of Done
Criteria that must be met for the entire plan to be considered complete.

## Tool Usage Patterns

### Using with Agent Tools
```yaml
# Typical workflow
1. User: "Let's create an implementation plan for the user authentication feature"
2. Agent activates writing-plans skill
3. Agent uses `read` to examine the design document from brainstorming
4. Agent uses `ls` and `tree` to understand project structure
5. Agent breaks down design into specific tasks
6. Agent uses `write` to create the plan document
7. Agent presents the plan in chunks for user validation
```

### Task Specification Examples
Good task specification:
```
T1: Create User model
Files: src/models/user.py
Code: 
  class User(Base):
      __tablename__ = 'users'
      
      id = Column(Integer, primary_key=True)
      email = Column(String(255), unique=True, nullable=False, index=True)
      password_hash = Column(String(255), nullable=False)
      created_at = Column(DateTime, server_default=func.now())
      
      def set_password(self, password):
          self.password_hash = generate_password_hash(password)
          
      def check_password(self, password):
          return check_password_hash(self.password_hash, password)
      
      def __repr__(self):
          return f'<User {self.email}>'
Verification: 
  - Run: python -c "from src.models.user import User; u=User(); u.set_password('test'); assert u.check_password('test')"
  - Check: File exists and contains the complete class definition
Dependencies: None
Est. Time: 4 min
```

## Integration with gsdmode Workflow
This skill is the third in the gsdmode sequence:
1. **Brainstorming** → Refines the idea
2. **Git Worktrees** → Sets up clean implementation environment
3. **Writing Plans** (this skill) → Creates detailed implementation tasks
4. **Subagent-Driven Development** → Executes the plan with quality gates
5. **TDD** → Ensures correctness during implementation
6. **Code Review** → Maintains quality between tasks
7. **Finishing Branch** → Completes the work cycle

The agent should automatically progress to the next skill when:
- The user has validated the plan document
- All tasks are clearly specified with code and verification steps
- Dependencies are identified and ordered
- The user indicates readiness to move to execution

## Best Practices

### Do ✅
- Be specific: include exact code to copy-paste
- Keep tasks small: if a task estimates >5 minutes, break it down further
- Verify everything: each task should have clear completion criteria
- Think in interfaces: specify how components interact
- Plan for tests: where possible, include test writing as part of tasks
- Consider order: identify what must come first

### Don't ❌
- Write vague instructions like "implement authentication"
- Leave implementation details to chance ("add error handling as needed")
- Create tasks that are too large or ambiguous
- Forget to specify exact file paths
- Over-specify irrelevant details (exact variable names that don't matter)
- Ignore dependencies between tasks

## Example Session

**User**: "Let's create an implementation plan for the blog authentication feature based on our design."

**Agent (Writing Plans)**:
1. Reads the design document from brainstorming phase
2. Identifies components: User model, registration form, login form, session middleware, protected routes
3. Breaks down into tasks:
   - T1: Create User model with email and password hash
   - T2: Create registration route and form
   - T3: Create login route and form
   - T4: Implement session middleware
   - T5: Create route protector decorator
   - T6: Update existing routes to use protection
   - T7: Add login/logout links to template
   - T8: Write tests for authentication flow
4. For each task, specifies exact files, complete code, and verification steps
5. Writes plan document and presents in chunks for user validation
6. Asks: "Does this plan look correct? Should we adjust any task breakdown or details?"

**User**: "Yes, this looks good. Let's move to execution."

**Agent**: Deactivates writing-plans skill, activates git worktrees skill (to set up clean environment) then subagent-driven-development skill.

---
*Adapted from obra/superpowers writing-plans skill for agentgsd gsdmode*
