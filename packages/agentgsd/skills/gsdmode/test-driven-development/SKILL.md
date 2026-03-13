---
name: test-driven-development
description: Enforces RED-GREEN-REFACTOR cycle: write failing test, watch it fail, write minimal code, watch it pass, commit. Deletes code written before tests. This overlaps with subagent-driven-development in gsdmode.
license: MIT
metadata:
  author: adapted from obra/superpowers
  version: "1.0"
  tags: testing,tdd,red-green-refactor,workflow
---

# Test-Driven Development Skill (gsdmode)

## Overview
This skill enforces the Test-Driven Development (TDD) methodology throughout the implementation process. It follows the strict RED-GREEN-REFACTOR cycle:
1. **RED**: Write a failing test that defines the desired behavior
2. **GREEN**: Write the minimum code necessary to make the test pass
3. **REFACTOR**: Improve the code structure while keeping tests passing

The test-driven-development skill works in conjunction with subagent-driven-development to ensure that all implementation follows TDD principles, resulting in well-tested, maintainable code.

## When to Activate
This skill should automatically activate when:
- Implementation work begins (after planning)
- The agent is about to write code for a task
- The user indicates they want to follow TDD practices
- The agent needs to ensure code quality through testing

It should NOT activate when:
- The user is still in planning or design phases
- The user wants to write code without tests (prototyping/spiking)
- The agent is doing pure research or investigation
- The user is asking for explanations about existing code

## Core Process

### 1. RED Phase: Write Failing Test
Before writing any implementation code:
- Read the task specification to understand what needs to be implemented
- Write a test that defines the exact expected behavior
- Ensure the test fails initially (confirms we're testing the right thing)
- The test should be specific, atomic, and focused on one behavior

### 2. GREEN Phase: Make Test Pass
After writing a failing test:
- Write the minimum implementation code necessary to make the test pass
- Do not write more code than needed to satisfy the test
- Focus on correctness over elegance or performance
- Run the test to confirm it passes

### 3. REFACTOR Phase: Improve Structure
After the test passes:
- Examine the implementation code for improvements
- Refactor for clarity, maintainability, and best practices
- Ensure all tests still pass after refactoring
- Do not change behavior, only improve structure

### 4. Commit Cycle
After successful RED-GREEN-REFACTOR:
- Commit the changes with a clear, descriptive message
- Include both test and implementation code in the commit
- Move to the next task or continue with related work

## Output Format
The test-driven-development skill should produce test implementation records:

### 🔴 RED Phase Records
- Test files created
- Test descriptions and expected behaviors
- Initial failure output/error messages

### 🟢 GREEN Phase Records
- Implementation code written
- Changes made to satisfy the test
- Final test pass output

### 🔵 REFACTOR Phase Records
- Refactoring actions taken
- Code improvements made
- Test status after refactoring (should still pass)

### 📝 Commit Information
- Commit messages for each RED-GREEN-REFACTOR cycle
- Files included in each commit

## Tool Usage Patterns

### Using with Agent Tools
```yaml
# Typical TDD workflow for a task
1. User: "Implement user email validation"
2. Agent activates test-driven-development skill
3. RED: Write test for email validation function
   - Use `write` to create test file
   - Use `bash` to run test and confirm failure
4. GREEN: Write minimal implementation to pass test
   - Use `edit` or `write` to implement function
   - Use `bash` to run test and confirm pass
5. REFACTOR: Improve implementation while keeping test passing
   - Use `edit` to refine code
   - Use `bash` to run test and confirm still passing
6. Commit: Save the changes
   - Use `bash` to git add and commit
```

### Test Creation Patterns
```python
# Good test structure
def test_validate_email_valid():
    """Test that valid emails return True"""
    assert validate_email("test@example.com") == True
    assert validate_email("user.name@domain.co.uk") == True

def test_validate_email_invalid():
    """Test that invalid emails return False"""
    assert validate_email("invalid-email") == False
    assert validate_email("@missing-local.com") == False
    assert validate_email("missing-domain@") == False
```

## Integration with gsdmode Workflow
This skill overlaps with subagent-driven-development in the gsdmode sequence:
1. **Brainstorming** → Refines the idea
2. **Using Git Worktrees** → Sets up clean implementation environment
3. **Writing Plans** → Creates detailed implementation tasks
4. **Subagent-Driven Development** → Executes the plan with quality gates
5. **Test-Driven Development** (this skill) → Ensures correctness during implementation (overlaps)
6. **Code Review** → Maintains quality between tasks (overlaps with this skill)
7. **Finishing Branch** → Completes the work cycle

The agent should apply TDD principles to each task in the implementation plan, cycling through RED-GREEN-REFACTOR for every piece of functionality.

## Best Practices

### Do ✅
- Always start with a failing test (RED)
- Write tests that specify behavior, not implementation
- Keep tests focused on single responsibilities
- Make the smallest possible change to pass tests (GREEN)
- Refactor only after tests are passing
- Run tests frequently (ideally after every change)
- Commit after each successful RED-GREEN-REFACTOR cycle
- Test edge cases and error conditions

### Don't ❌
- Write implementation code before tests
- Skip the RED phase (don't write tests first)
- Write more code than necessary to pass tests
- Refactor without failing tests as safety net
- Commit untested code
- Ignore failing tests
- Over-refactor and introduce bugs

## Example Session

**Task**: "Create function to validate email addresses"

**Agent (Test-Driven Development)**:
1. **RED Phase**:
   - Creates test file `tests/test_email_validation.py`
   - Writes test: `assert validate_email("test@example.com") == True`
   - Runs test: `pytest tests/test_email_validation.py -v`
   - Confirms test fails (function doesn't exist yet)

2. **GREEN Phase**:
   - Creates implementation in `src/utils/email.py`
   - Writes minimal function: 
     ```python
     def validate_email(email):
         return "@" in email
     ```
   - Runs test: `pytest tests/test_email_validation.py -v`
   - Confirms test passes

3. **REFACTOR Phase**:
   - Improves implementation with proper regex validation
   - Adds edge case handling (empty string, None, etc.)
   - Runs test suite to confirm all tests still pass
   - Refactors test to be more comprehensive if needed

4. **Commit**:
   - Commits both test and implementation files
   - Message: "Add email validation with basic format checking"

**User**: "Great, let's move to the next task."

**Agent**: Continues with next task, applying the same TDD process.

---
*Adapted from obra/superpowers test-driven-development skill for agentgsd gsdmode*
