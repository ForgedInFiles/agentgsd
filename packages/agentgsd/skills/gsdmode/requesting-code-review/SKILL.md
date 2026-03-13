---
name: requesting-code-review
description: Reviews completed work against plan, reports issues by severity. Critical issues block progress. This is the sixth step in the gsdmode workflow.
license: MIT
metadata:
  author: adapted from obra/superpowers
  version: "1.0"
  tags: review,code-quality,validation,workflow
---

# Requesting Code Review Skill (gsdmode)

## Overview
This skill activates after implementation tasks are completed. It systematically reviews the implemented code against the original plan and design, identifying issues by severity and determining whether progress can continue or if rework is needed.

The requesting-code-review skill follows the gsdmode philosophy of "evidence over claims" - it ensures that work is thoroughly validated before considering it complete, preventing the accumulation of technical debt.

## When to Activate
This skill should automatically activate when:
- All tasks in the current implementation plan have been marked as complete
- The user has finished a batch of work and wants validation
- The agent has completed a significant milestone or feature
- The user requests a code review of recent work

It should NOT activate when:
- Work is still in progress (tasks remain incomplete)
- The user wants to continue implementation without review
- The agent is in the middle of a TDD cycle
- The user is asking for explanations about existing code

## Core Process

### 1. Plan Compliance Check
Review each completed task against its specification:
- Verify all required files were modified correctly
- Confirm implemented code matches the specification exactly
- Check that all verification steps pass
- Ensure dependencies were properly handled

### 2. Quality Assessment
Evaluate the code for maintainability and best practices:
- Naming conventions and clarity
- Error handling completeness
- Edge case consideration
- Code duplication and refactoring opportunities
- Documentation and comments

### 3. Issue Classification
Categorize any issues found by severity:
- **CRITICAL**: Blocks functionality, security risks, data loss
- **HIGH**: Major functionality missing or broken
- **MEDIUM**: Usability issues, performance concerns
- **LOW**: Style issues, minor improvements, documentation

### 4. Progress Determination
Based on issue severity, determine next steps:
- **CRITICAL/HIGH**: Block progress, require immediate fixes
- **MEDIUM**: Allow progress but schedule fixes for next iteration
- **LOW**: Allow progress, track for future refinement

### 5. Feedback Preparation
Prepare clear, actionable feedback for the user:
- Summarize what was reviewed
- List issues by severity with examples
- Provide specific recommendations for fixes
- Indicate whether work can proceed or needs revision

## Output Format
The requesting-code-review skill should produce a review document with these sections:

### 📋 Review Summary
- **Tasks Reviewed**: Number and IDs of tasks examined
- **Files Changed**: List of all modified files
- **Lines Changed**: Approximate count of additions/modifications
- **Review Date/Time**: When the review was conducted

### ✅ What's Working Well
Areas where the implementation meets or exceeds expectations:
- Correctly implemented features
- Good code quality practices
- Proper error handling
- Clean, maintainable code

### 🚨 Issues Found
Issues categorized by severity:

#### 🔴 Critical Issues
- Must be fixed before proceeding
- Examples: security vulnerabilities, data loss, broken core functionality

#### 🟠 High Issues
- Should be fixed soon, may block depending on context
- Examples: major features not working, significant performance issues

#### 🟡 Medium Issues
- Good to fix, but don't block immediate progress
- Examples: usability improvements, minor bugs, performance optimization

#### 🟢 Low Issues
- Nice to have, track for future refinement
- Examples: style preferences, documentation improvements, minor refactoring

### 📝 Recommendations
Specific, actionable advice for addressing issues:
- Exact changes needed for each issue
- Priority order for fixes
- Estimated effort for resolution

### 📊 Progress Decision
Clear indication of whether work can continue:
- ✅ **PROCEED**: No blocking issues, safe to move to next phase
- ⚠️ **PROCEED WITH TRACKING**: Medium/low issues only, track for fixes
- 🛑 **BLOCK AND FIX**: Critical/high issues require immediate attention
- 🔄 **REVISE AND RETRY**: Fundamental issues require design revisit

## Tool Usage Patterns

### Using with Agent Tools
```yaml
# Typical workflow
1. User: "Let's review the authentication implementation"
2. Agent activates requesting-code-review skill
3. Agent uses `read` to examine the original plan and design documents
4. Agent uses `ls` and `tree` to see what files were changed
5. Agent uses `grep` and `read` to examine specific implementations
6. Agent uses `bash` to run tests and verification steps
7. Agent categorizes any issues found
8. Agent uses `write` to create the review document
9. Agent presents the review in chunks for user validation
```

### Review Commands
```bash
# Check against plan
diff -u plan-original.md plan-current.md || echo "No plan diff tool available"

# Run tests
npm test || pytest tests/ || ./run-tests.sh

# Check for common issues
grep -rn "TODO\|FIXME\|XXX\|HACK" src/
grep -rn "console.log\|print\|debug" src/  # Remove debug statements
grep -rn "password\|secret\|key" src/ | grep -v "#"  # Potential hardcoded secrets
```

## Integration with gsdmode Workflow
This skill is the sixth in the gsdmode sequence:
1. **Brainstorming** → Refines the idea
2. **Using Git Worktrees** → Sets up clean implementation environment
3. **Writing Plans** → Creates detailed implementation tasks
4. **Subagent-Driven Development** → Executes the plan with quality gates
5. **Test-Driven Development** → Ensures correctness during implementation
6. **Requesting Code Review** (this skill) → Validates completed work
7. **Finishing Branch** → Completes the work cycle

The agent should automatically progress to the next skill when:
- No critical or high issues are found (or user accepts the risk)
- The user has reviewed the feedback and agreed on next steps
- Any agreed-upon fixes have been scheduled or completed
- The user indicates readiness to move to finishing the development branch

## Best Practices

### Do ✅
- Review everything that was supposed to be done
- Be specific and objective in feedback
- Focus on blocking issues first
- Provide clear paths to resolution
- Respect the user's time and priorities
- Celebrate what was done well

### Don't ❌
- Skip verification steps to "move faster"
- Ignore failing tests or verification errors
- Be vague about what needs fixing
- Make subjective judgments without basis
- Overwhelm with minor issues when critical ones exist
- Forget to check that dependencies still work

## Example Session

**User**: "Let's review the blog authentication implementation."

**Agent (Requesting Code Review)**:
1. Reads the original design and plan documents
2. Checks that all 8 tasks from the plan are marked complete
3. Examines each implemented file:
   - src/models/user.py: Complete User model with password hashing ✓
   - src/routes/auth.py: Registration and login routes ✓
   - src/middleware/session.js: Session middleware implementation ✓
   - etc.
4. Runs verification steps for each task:
   - All task-specific tests pass
   - Full test suite: 92% pass, 3 failing tests
5. Categorizes issues:
   - **Critical**: None
   - **High**: 3 failing tests related to edge case validation
   - **Medium**: Missing logout functionality in navigation
   - **Low**: Several TODO comments for future enhancements
6. Creates review document and presents in chunks
7. Asks: "The implementation is mostly complete with 3 high-priority test failures. Should we fix these now or proceed and track them for the next iteration?"

**User**: "Let's fix the failing tests now, then we can finish up."

**Agent**: Deactivates requesting-code-review skill, returns to subagent-driven-development skill to fix the failing tests.

---
*Adapted from obra/superpowers requesting-code-review skill for agentgsd gsdmode*
