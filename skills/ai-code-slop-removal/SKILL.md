---
name: ai-code-slop-removal
description: Identify and remove AI-generated placeholder code, TODO comments, incomplete implementations, and code artifacts. Clean up AI-assisted code for production readiness.
license: MIT
metadata:
  author: agentgsd
  version: "1.0"
  tags: cleanup,refactoring,ai-generated,technical-debt,code-quality
  languages: python,javascript,typescript,java,go,rust
---

# AI Code Slop Removal Skill

## Overview
This skill specializes in identifying and removing AI-generated code artifacts including placeholder code, TODO comments, incomplete implementations, mock data, and other temporary constructs that should not exist in production code.

## What is AI Code Slop?

AI code slop refers to code artifacts left behind from AI-assisted development:
- TODO/FIXME/HACK comments meant as reminders
- Placeholder functions with `pass` or empty bodies
- Comment-only implementations
- Mock/stub data that should be real
- Incomplete error handling
- "Slot" code meant to be filled in later
- AI signature comments and explanations

## Detection Patterns

### 1. TODO/FIXME Comments
```python
# Patterns to detect
TODO_PATTERNS = [
    r'#\s*TODO[:\s]',           # Python TODO
    r'//\s*TODO[:\s]',          // JavaScript/Java TODO
    r'--\s*TODO[:\s]',          -- SQL/Lua TODO
    r'#\s*FIXME[:\s]',          # FIXME comments
    r'#\s*HACK[:\s]',           # HACK comments
    r'#\s*XXX[:\s]',            # XXX warning comments
    r'#\s*NOTE[:\s].*should',   # NOTE with action items
]
```

### 2. Placeholder Functions
```python
# Empty or minimal implementations
def process_data(data):
    # TODO: Implement this
    pass

def calculate_metrics():
    """Calculate metrics."""
    # Implementation goes here
    return None

def validate_input(value):
    # Placeholder implementation
    return True  # Always returns True - needs real validation
```

### 3. Comment-Only Implementations
```python
# Functions with only comments
def connect_to_database():
    # 1. Get database credentials from environment
    # 2. Establish connection using SQLAlchemy
    # 3. Handle connection errors
    # 4. Return connection object
    pass

def process_payment(amount, currency):
    # Validate amount is positive
    # Check currency is supported
    # Call payment gateway API
    # Handle response
    # Return transaction ID
    raise NotImplementedError("TODO: Implement payment processing")
```

### 4. Mock/Stub Data
```python
# Remove these patterns
users = [{"id": 1, "name": "John Doe"}]  # Mock data
response = {"status": "success"}  # Stub response
config = {}  # TODO: Load real config
API_KEY = "your_api_key_here"  # Replace with real key
SECRET = "changeme"  # Security risk!
```

### 5. Incomplete Error Handling
```python
# Bad error handling patterns
try:
    result = risky_operation()
except Exception as e:
    pass  # Silently ignore - bad practice

try:
    data = load_data()
except:
    # TODO: Handle this properly
    data = None

def divide(a, b):
    return a / b  # No zero division check!
```

### 6. AI Signature Comments
```python
# Comments that explain rather than implement
# This is a placeholder implementation
# The actual implementation would...
# Here we would typically...
# For demonstration purposes...
# In a real application, you would...
# Note: This is just an example
# Simplified for clarity
```

### 7. Example Code That Should Be Real
```python
# Remove example patterns
example_data = [...]  # Example data
sample_input = "test"  # Sample input
test_value = 42  # Test value
dummy_user = User("dummy", "dummy@example.com")  # Dummy object
```

## Removal Process

### Phase 1: Scan and Identify
```bash
# Find all TODO/FIXME patterns
grep -rn "TODO\|FIXME\|HACK\|XXX" src/

# Find pass-only functions
grep -rn "def.*:\s*$" src/ | grep -A1 "pass"

# Find empty implementations
grep -rn "return None\|return {}\|return \[\]\|raise NotImplementedError" src/

# Find placeholder strings
grep -rn "your_\|changeme\|placeholder\|example\|sample\|dummy" src/
```

### Phase 2: Categorize by Priority

| Priority | Type | Risk | Action Timeline |
|----------|------|------|-----------------|
| CRITICAL | Security placeholders, hardcoded secrets | High | Immediate |
| HIGH | Core functionality missing | High | Within 24h |
| MEDIUM | Error handling gaps | Medium | Within sprint |
| LOW | Documentation TODOs | Low | When convenient |

### Phase 3: Replace or Remove

#### Decision Matrix
```
For each placeholder:
1. Is the functionality needed?
   YES → Implement proper solution
   NO  → Remove entirely

2. Is this security-related?
   YES → Fix immediately, review thoroughly
   NO  → Prioritize based on impact

3. Is this core business logic?
   YES → Implement with tests
   NO  → Consider if needed at all
```

### Phase 4: Implement Proper Solutions

#### Example: Replace Placeholder with Real Implementation

**Before (AI Slop):**
```python
def validate_email(email: str) -> bool:
    # TODO: Implement email validation
    # Check if email contains @ symbol
    # Verify domain format
    # Return True if valid, False otherwise
    pass
```

**After (Production Ready):**
```python
import re

def validate_email(email: str) -> bool:
    """Validate email format using RFC 5322 pattern."""
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False
    
    # Additional checks
    if len(email) > 254:
        return False
    
    local, domain = email.rsplit('@', 1)
    if not local or len(local) > 64:
        return False
    
    if '..' in email or email.startswith('.') or email.endswith('.'):
        return False
    
    return True
```

### Phase 5: Verify

```bash
# Run tests to ensure functionality works
pytest tests/ -v

# Check for broken imports/references
python -m py_compile src/*.py

# Verify error handling is complete
grep -rn "except.*:" src/ | grep -v "Exception as"

# Confirm no orphaned code remains
git diff --name-only
```

## Tool Usage Patterns

### Using with Agent Tools
```yaml
# Example workflow
1. User: "Clean up the AI-generated code in src/"
2. Agent activates ai-code-slop-removal skill
3. Agent uses `grep` to find placeholder patterns
4. Agent uses `read` to examine each file
5. Agent categorizes issues by priority
6. Agent uses `edit` to fix/remove placeholders
7. Agent runs tests to verify
8. Agent provides summary report
```

### Grep Commands for Detection
```bash
# Find all TODO comments
grep -rn "TODO" src/ --include="*.py"

# Find FIXME comments
grep -rn "FIXME" src/ --include="*.py"

# Find pass statements
grep -rn "^\s*pass\s*$" src/ --include="*.py"

# Find NotImplementedError
grep -rn "NotImplementedError" src/ --include="*.py"

# Find placeholder strings
grep -rn "TODO\|FIXME\|XXX\|HACK\|placeholder\|stub\|mock" src/ --include="*.py"

# Find empty except blocks
grep -rn "except.*:\s*$" src/ --include="*.py" | grep -A1 "pass"
```

## Output Format

```markdown
## 🧹 AI Code Cleanup Report

### Summary
- **Files Scanned**: 24
- **Issues Found**: 47
- **Issues Fixed**: 42
- **Remaining**: 5 (deferred)

### Issues by Category

| Category | Count | Fixed | Pending |
|----------|-------|-------|---------|
| TODO Comments | 18 | 15 | 3 |
| Placeholder Functions | 8 | 6 | 2 |
| Mock Data | 12 | 12 | 0 |
| Error Handling | 6 | 6 | 0 |
| AI Comments | 3 | 3 | 0 |

### Files Modified

| File | Changes | Status |
|------|---------|--------|
| src/auth.py | 12 | ✅ Complete |
| src/api.py | 8 | ✅ Complete |
| src/utils.py | 15 | ✅ Complete |
| src/models.py | 7 | ⏳ Pending review |
| src/config.py | 5 | ⏳ Needs real values |

### Critical Fixes Applied

1. **Security**: Replaced hardcoded API key with environment variable
   - File: `src/config.py:23`
   - Before: `API_KEY = "your_api_key_here"`
   - After: `API_KEY = os.environ.get("API_KEY")`

2. **Validation**: Implemented proper email validation
   - File: `src/utils.py:45`
   - Replaced `pass` with regex-based validation

3. **Error Handling**: Added proper exception handling
   - File: `src/api.py:89`
   - Added specific exception types and logging

### Remaining Work

- [ ] Implement OAuth integration (src/auth.py:156)
- [ ] Add rate limiting (src/api.py:23)
- [ ] Configure production database (src/config.py:45)

### Commands Run
```bash
grep -rn "TODO" src/
pytest tests/ -v
python -m py_compile src/*.py
```
```

## Best Practices

### Do ✅
- Replace placeholders with real implementations immediately
- Add proper error handling for all edge cases
- Use meaningful default values
- Write tests for newly implemented code
- Update documentation after implementation
- Use environment variables for configuration
- Implement proper logging

### Don't ❌
- Leave TODO comments in production code
- Use `pass` as a real implementation
- Ignore error handling "for now"
- Leave mock data in live code
- Add more placeholders while removing old ones
- Commit hardcoded secrets
- Use `except: pass` patterns

## Prevention Strategies

### 1. Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: no-todo
        name: Check for TODO comments
        entry: grep -rn "TODO\|FIXME\|XXX" 
        language: system
        stages: [commit]
```

### 2. CI/CD Integration
```yaml
# .github/workflows/lint.yml
- name: Check for placeholders
  run: |
    ! grep -rn "TODO\|FIXME\|pass  #" src/ || echo "Found placeholders"
```

### 3. Linting Rules
```python
# .flake8 or setup.cfg
[flake8]
extend-ignore = 
    # Uncomment to fail on TODOs
    # T100,T101,T102,T103
```

### 4. Code Review Checklist
- [ ] No TODO/FIXME comments
- [ ] No `pass` statements in business logic
- [ ] No mock data in production paths
- [ ] All error handling implemented
- [ ] No hardcoded values
- [ ] All functions have real implementations

## Related Patterns

### Good Implementation ✅
```python
def validate_email(email: str) -> bool:
    """Validate email format using regex."""
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
```

### Bad Placeholder ❌
```python
def validate_email(email: str) -> bool:
    # TODO: Implement email validation
    # Check if email contains @ symbol
    # Verify domain format
    # Return True if valid, False otherwise
    pass
```

## References
- Clean Code by Robert C. Martin
- Refactoring Guru: https://refactoring.guru/
- OWASP Secure Coding Practices
- Python Best Practices: https://docs.python-guide.org/
