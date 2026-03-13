---
name: receiving-code-review
description: Processes and responds to code review feedback, implementing necessary changes and updating documentation. This is the seventh step in the gsdmode workflow.
license: MIT
metadata:
  author: adapted from obra/superpowers
  version: "1.0"
  tags: review,feedback,implementation,workflow
---

# Receiving Code Review Skill (gsdmode)

## Overview
This skill activates after a code review has been conducted (by the requesting-code-review skill or manually) and feedback has been provided. It processes the feedback, implements necessary changes, updates documentation, and prepares the work for finalization.

The receiving-code-review skill follows the gsdmode philosophy of "systematic over ad-hoc" - it ensures that feedback is addressed in an organized, thorough manner, preventing the accumulation of unresolved issues.

## When to Activate
This skill should automatically activate when:
- Code review feedback has been provided (by requesting-code-review skill or user)
- The user indicates they want to address the feedback
- The agent has received a code review from an external source
- The user asks to "fix the issues found in the review"

It should NOT activate when:
- No code review has been conducted yet
- The user wants to proceed without addressing feedback
- The agent is in the middle of implementing new features
- The user is asking for explanations about existing code

## Core Process

### 1. Feedback Processing
Read and understand the feedback:
- Categorize feedback by type (bug, enhancement, question, etc.)
- Prioritize based on severity and impact
- Clarify any ambiguous feedback through questioning if needed
- Group related feedback for efficient processing

### 2. Change Implementation
For each piece of feedback requiring changes:
- Locate the relevant code or documentation
- Implement the necessary changes
- Ensure changes are consistent with the rest of the codebase
- Update any related tests or specifications

### 3. Verification
After implementing changes:
- Run the verification steps for affected tasks
- Ensure existing functionality still works
- Confirm that the changes resolve the feedback points
- Run any relevant tests to prevent regressions

### 4. Documentation Updates
Update any affected documentation:
- Design documents if assumptions changed
- Plan documents if task definitions changed
- User-facing documentation
- Code comments and inline documentation

### 5. Feedback Closure
For each feedback item:
- Confirm the change addresses the concern
- Note any alternative solutions considered and rejected
- Document the resolution for future reference
- Mark the feedback as resolved

## Output Format
The receiving-code-review skill should produce a feedback resolution document with these sections:

### 📋 Feedback Summary
- **Total Feedback Items**: Number of items received
- **By Source**: Breakdown of where feedback came from
- **By Severity**: Distribution of critical/high/medium/low
- **By Type**: Categories (bug, enhancement, question, etc.)

### ✅ Resolved Items
Feedback that has been addressed:
- **Feedback ID/Reference**: Original feedback identifier
- **Description**: What the feedback was about
- **Resolution**: How it was addressed
- **Files Changed**: What was modified to resolve it
- **Verification**: How the fix was confirmed

### 🔄 Deferred Items
Feedback that was not implemented immediately:
- **Feedback ID/Reference**: Original feedback identifier
- **Description**: What the feedback was about
- **Reason**: Why it was deferred (scope, priority, etc.)
- **Planned For**: When/where it will be addressed
- **Impact**: Effect of deferring

### 📝 Documentation Changes
Documentation updated as a result of feedback:
- **Document**: Name of document updated
- **Section**: Part of document that was changed
- **Change Summary**: What was updated and why

### 🧪 Verification Results
Tests and checks performed to confirm fixes:
- **Test Suite**: Overall test status after changes
- **Specific Tests**: Tests related to changed code
- **Manual Checks**: Any manual verification performed

## Tool Usage Patterns

### Using with Agent Tools
```yaml
# Typical workflow
1. User: "Let's address the code review feedback on the authentication feature"
2. Agent activates receiving-code-review skill
3. Agent uses `read` to examine the feedback document
4. Agent uses `grep` and `read` to locate relevant code
5. Agent uses `edit` or `write` to implement changes
6. Agent uses `bash` to run tests and verification steps
7. Agent uses `write` to update documentation
8. Agent uses `write` to create feedback resolution document
9. Agent presents the resolution in chunks for user validation
```

### Feedback Processing Commands
```bash
# Extract action items from feedback
grep -i "should\|need\|must\|fix\|address" feedback.md

# Locate specific code mentioned in feedback
grep -rn "function_name" src/
grep -rn "variable_name" src/

# Check for patterns mentioned in feedback
grep -rn "TODO\|FIXME" src/  # If feedback mentioned placeholders
```

## Integration with gsdmode Workflow
This skill is the seventh in the gsdmode sequence:
1. **Brainstorming** → Refines the idea
2. **Using Git Worktrees** → Sets up clean implementation environment
3. **Writing Plans** → Creates detailed implementation tasks
4. **Subagent-Driven Development** → Executes the plan with quality gates
5. **Test-Driven Development** → Ensures correctness during implementation
6. **Requesting Code Review** → Validates completed work
7. **Receiving Code Review** (this skill) → Processes and implements feedback
8. **Finishing Branch** → Completes the work cycle

The agent should automatically progress to the next skill when:
- All critical and high feedback items have been resolved
- The user has approved the resolution of medium/low items (or accepted deferral)
- Documentation has been updated as needed
- The user indicates readiness to move to finishing the development branch

## Best Practices

### Do ✅
- Address all critical and high priority feedback
- Keep changes focused and minimal
- Verify that fixes actually resolve the feedback
- Update documentation to reflect changes
- Provide clear feedback on what was done and why

### Don't ❌
- Ignore feedback without explanation
- Make changes that introduce new issues
- Forget to update related tests
- Over-engineer solutions beyond what's needed
- Leave feedback items unresolved without tracking

## Example Session

**User**: "Here's the code review feedback for the authentication feature. Let's address it."

**Agent (Receiving Code Review)**:
1. Reads the feedback document from requesting-code-review
2. Identifies 3 feedback items:
   - [Critical] Hardcoded secret key in config file
   - [High] Missing validation for email format in login
   - [Medium] Add logout button to navigation menu
3. Processes each item:
   - Critical: 
     * Locates `src/config.py` 
     * Changes `SECRET_KEY = "hardcoded-key"` to `SECRET_KEY = os.environ.get("SECRET_KEY")`
     * Adds error handling for missing key
     * Runs verification: config loads correctly with env var
   - High:
     * Locates `src/routes/auth.py` login function
     * Adds email format validation before processing
     * Updates unit test to cover valid/invalid email cases
     * Runs verification: login route now rejects invalid emails
   - Medium:
     * Locates `src/components/navigation.js`
     * Adds logout button item
     * Updates import for logout function
     * Runs verification: button appears and triggers logout
4. Updates documentation:
   - Updates config documentation to mention required env var
   - Adds note about email validation in API documentation
   - Updates user guide with logout instructions
5. Creates feedback resolution document and presents in chunks
6. Asks: "All feedback items have been addressed and verified. Should we run a final comprehensive test or move to finishing the branch?"

**User**: "Let's run the full test suite to make sure everything still works."

**Agent**: Runs comprehensive tests, then if passing, deactivates receiving-code-review skill and activates finishing-a-development-branch skill.

---
*Adapted from obra/superpowers receiving-code-review skill for agentgsd gsdmode*
