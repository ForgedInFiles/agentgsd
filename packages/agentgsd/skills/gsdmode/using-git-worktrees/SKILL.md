---
name: using-git-worktrees
description: Sets up isolated workspaces using git worktrees for clean implementation, runs project setup, and verifies a clean test baseline. This is the second step in the gsdmode workflow.
license: MIT
metadata:
  author: adapted from obra/superpowers
  version: "1.0"
  tags: git,worktree,setup,environment,workflow
---

# Using Git Worktrees Skill (gsdmode)

## Overview
This skill activates after the design has been validated (by brainstorming or writing-plans) and before implementation begins. It creates an isolated workspace using git worktrees on a new branch, runs any necessary project setup commands, and verifies that the test suite passes in a clean state.

The using-git-worktrees skill follows the gsdmode philosophy of "systematic over ad-hoc" - it ensures that implementation starts from a known, clean state, reducing environment-related issues and making it easy to abandon work if needed.

## When to Activate
This skill should automatically activate when:
- The user has validated a design document (from brainstorming) or approved a plan (from writing-plans)
- The agent is about to begin implementation work
- The user indicates readiness to start coding
- The agent needs a clean environment to work in

It should NOT activate when:
- The user is still discussing or refining ideas (brainstorming phase)
- The user wants to make a small, isolated change that doesn't require a clean workspace
- The agent is already in an implementation workflow and needs to continue in the same environment
- The user is asking for explanations or reviewing existing code

## Core Process

### 1. Workspace Creation
Create an isolated worktree:
- Generate a descriptive branch name based on the feature or task
- Create a new git worktree linked to this branch
- Ensure the worktree is clean (no uncommitted changes)
- Verify we're on the correct branch and commit

### 2. Environment Setup
Run any necessary setup commands:
- Install dependencies if needed (npm install, pip install -r requirements.txt, etc.)
- Set up environment variables or configuration files
- Prepare any required services (databases, caches, etc.)
- Verify the development environment is ready

### 3. Baseline Verification
Ensure we start from a known good state:
- Run the test suite to confirm it passes in the current state
- If tests fail, investigate and fix before proceeding (or reset to a known good commit)
- Record the baseline state for later comparison
- Ensure linting and other code quality checks pass

### 4. Workspace Preparation
Prepare the workspace for implementation:
- Clear any temporary or cache files that might interfere
- Ensure editor/IDE configurations are loaded if needed
- Verify all tools are accessible and functioning
- Set up any necessary debugging or monitoring tools

## Output Format
The using-git-worktrees skill should produce a workspace setup document with these sections:

### 🌳 Workspace Information
- **Branch Name**: The git branch created for this work
- **Worktree Path**: Filesystem path to the isolated worktree
- **Base Commit**: The commit this worktree was created from
- **Setup Commands**: List of commands run to prepare the environment

### 🔧 Setup Steps
A detailed list of what was done to prepare the environment:
- Dependency installation
- Configuration steps
- Service initialization
- Any manual steps taken

### ✅ Baseline Verification
Results from verifying a clean starting state:
- Test suite status (pass/fail, coverage if relevant)
- Linting results
- Build status (if applicable)
- Any issues found and how they were resolved

### 📝 Notes
Any important information about the workspace:
- Known issues or limitations
- Special considerations for this environment
- Instructions for returning to this workspace later

## Tool Usage Patterns

### Using with Agent Tools
```yaml
# Typical workflow
1. User: "Let's start implementing the user authentication feature"
2. Agent activates using-git-worktrees skill
3. Agent uses `bash` to run git commands (rev-parse, worktree add, etc.)
4. Agent uses `bash` to run setup commands (npm install, etc.)
5. Agent uses `bash` to run tests and verify baseline
6. Agent uses `write` to create a workspace document
7. Agent proceeds to implementation (activating writing-plans or subagent-driven-development)
```

### Git Worktree Commands
```bash
# Main commands used
git rev-parse --show-toplevel          # Get project root
git worktree add ../feature-branch feature-description  # Create worktree
cd ../feature-branch
git checkout -b feature-description    # Or just checkout if worktree creates branch
# Run setup commands
npm install                            # or pip install, etc.
# Verify baseline
npm test                               # or pytest, etc.
```

## Integration with gsdmode Workflow
This skill is the second in the gsdmode sequence:
1. **Brainstorming** → Refines the idea
2. **Using Git Worktrees** (this skill) → Sets up clean implementation environment
3. **Writing Plans** → Creates detailed implementation tasks
4. **Subagent-Driven Development** → Executes the plan with quality gates
5. **TDD** → Ensures correctness during implementation
6. **Code Review** → Maintains quality between tasks
7. **Finishing Branch** → Completes the work cycle

The agent should automatically progress to the next skill when:
- The worktree has been successfully created and checked out
- Environment setup commands have completed successfully
- The test suite passes (or any pre-existing failures have been documented and accepted as baseline)
- The user indicates readiness to move to planning or implementation

## Best Practices

### Do ✅
- Use descriptive branch names that indicate the feature or purpose
- Always verify a clean baseline before starting work
- Document any pre-existing test failures as known issues
- Keep the worktree isolated and avoid committing unrelated changes
- Clean up worktrees when they're no longer needed (or let the finishing skill handle it)

### Don't ❌
- Start implementation without verifying the environment is ready
- Assume dependencies are installed without checking
- Ignore failing tests in the baseline (investigate or document them)
- Commit large generated files or dependencies to the worktree
- Forget which worktree you're working in when managing multiple

## Example Session

**User**: "Let's start implementing the blog authentication feature based on our plan."

**Agent (Using Git Worktrees)**:
1. Determines project root using git rev-parse
2. Creates a new worktree: `git worktree add ../gsdmode-blog-auth feature-blog-auth`
3. Changes to the worktree directory
4. Runs setup: `npm install` (if a Node.js project) or `pip install -r requirements.txt`
5. Verifies baseline: runs `npm test` or `pytest` and records the result
6. Creates a workspace document summarizing:
   - Branch: feature-blog-auth
   - Worktree: /path/to/project/../gsdmode-blog-auth
   - Setup: Installed dependencies, ran setup script
   - Baseline: All tests passing
7. Asks: "Workspace is ready. Should we proceed to creating implementation plans or start coding directly?"

**User**: "Let's create the implementation plans first."

**Agent**: Deactivates using-git-worktrees skill, activates writing-plans skill.

---
*Adapted from obra/superpowers using-git-worktrees skill for agentgsd gsdmode*
