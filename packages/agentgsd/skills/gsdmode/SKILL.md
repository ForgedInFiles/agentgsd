---
name: gsdmode
description: Superpowers-inspired workflow for agentgsd that provides automated, structured software development cycles including brainstorming, planning, implementation with quality gates, and finishing.
license: MIT
metadata:
  author: agentgsd team
  version: "1.0"
  tags: workflow,superpowers,automation,development-cycle
---

# GSDMode (AgentGSD Superpowers Mode)

## Overview
GSDMode is an agentgsd skill that implements a structured, automated workflow inspired by the Obra/Superpowers framework. When activated, it guides the agent through a complete software development cycle:

1. **Brainstorming** - Refines rough ideas through Socratic questioning
2. **Git Worktrees** - Sets up isolated implementation environments  
3. **Writing Plans** - Breaks designs into actionable tasks (2-5 min each)
4. **Subagent-Driven Development** - Implements tasks with quality gates
5. **Test-Driven Development** - Ensures correctness during implementation
6. **Code Review** - Maintains quality between tasks
7. **Finishing Branch** - Completes the work cycle with merge/PR options

This skill is a "meta-skill" that coordinates the activation of other specialized skills in the correct sequence based on workflow state.

## When to Activate
Activate gsdmode when:
- Starting a new feature or significant code change
- You want structured guidance through the development process
- You'd benefit from automated workflow progression
- You want to ensure best practices are followed throughout

Do NOT activate gsdmode for:
- Small, isolated changes (like fixing a typo)
- Simple questions or explanations
- When you prefer free-form, unstructured interaction
- Debugging existing issues (use systematic-debugging skill instead)

## How to Use
There are two ways to engage gsdmode:

### 1. Command-Line Activation (Recommended)
Start agentgsd with the `--gsdmode` flag:
```bash
python3 -m packages.agentgsd.main --gsdmode
```
This automatically activates gsdmode at startup in the brainstorming phase.

### 2. Interactive Activation
While agentgsd is running, use the `/gsdmode` command:
```
/gsdmode
```
This toggles gsdmode on/off and shows current status when already active.

## Workflow State Management
GSDMode maintains internal state to track progress through the workflow:
- **INACTIVE**: GSDMode not enabled or not activated
- **BRAINSTORMING**: Refining ideas and requirements
- **GIT_WORKTREES**: Setting up clean implementation environment
- **WRITING_PLANS**: Creating detailed implementation tasks
- **SUBAGENT_DEVELOPMENT**: Implementing with quality gates
- **TEST_DRIVEN_DEVELOPMENT**: Writing tests first, then code
- **REQUESTING_CODE_REVIEW**: Seeking feedback on completed work
- **RECEIVING_CODE_REVIEW**: Responding to code review feedback
- **FINISHING_BRANCH**: Preparing to merge or share work

The agent automatically progresses through states based on:
- User commands and validation
- Completion of skill objectives
- Verification of work products

## Subskills
GSDMode coordinates these specialized skills:
- `brainstorming` - Idea refinement and design documentation
- `using-git-worktrees` - Environment setup and isolation
- `writing-plans` - Task breakdown and specification
- `subagent-driven-development` - Quality-gated implementation
- `test-driven-development` - RED-GREEN-REFACTOR cycle
- `requesting-code-review` - Pre-commit quality checks
- `receiving-code-review` - Feedback processing
- `finishing-a-development-branch` - Work completion and cleanup

## Tool Integration
GSDMode works with all agentgsd tools:
- File operations (read, write, edit, grep, etc.)
- Web search and fetch for research
- Bash commands for scripting and automation
- Skill activation for workflow progression

## Best Practices

### Do ✅
- Start with `/gsdmode` or `--gsdmode` for new features
- Let the agent guide you through each phase
- Validate work products before progressing
- Keep the conversation focused on the current phase
- Use the workflow to ensure completeness

### Don't ❌
- Skip phases without validation
- Ignore the agent's questions about requirements
- Rush through planning to start coding
- Forget to verify tests pass before moving on
- Mix unrelated work in the same gsdmode session

## Example Session
```
$ python3 -m packages.agentgsd.main --gsdmode
[agentgsd banner appears]

> I want to add user authentication to my web app
[Agent activates brainstorming skill, asks clarifying questions]

> Yes, that design looks good. Let's move to planning.
[Agent activates writing-plans skill, creates task breakdown]

> The plan looks good. Let's start implementing.
[Agent activates subagent-driven-development skill, begins implementation]

> All tasks done. Let's run tests and finish up.
[Agent runs verification, then activates finishing skill]

> Ready to merge to main branch.
[Agent cleans up worktree and exits gsdmode]

> Thanks for using agentgsd!
```

## Customization
You can customize gsdmode behavior by:
- Modifying the subskills in `/skills/gsdmode/`
- Adjusting workflow transitions in the skill logic
- Adding domain-specific validation steps
- Changing task time estimates or complexity thresholds

## Related Skills
- `brainstorming` - For idea refinement without full workflow
- `writing-plans` - For task breakdown only
- `using-git-worktrees` - For environment setup only
- `test-driven-development` - For TDD-focused work
- `code-review` - For manual code review processes

## References
- Inspired by Obra/Superpowers: https://github.com/obra/superpowers
- Agent Skills Open Standard: https://agentskills.io
- Test-Driven Development: Kent Beck
- Git Worktrees: Git SCM Documentation

---
*GSDMode brings structured, automated workflows to agentgsd while maintaining flexibility for expert users to override or customize the process as needed.*
