---
name: code-review
description: Comprehensive code review for Python, JavaScript, and web applications. Analyzes code quality, security vulnerabilities, performance issues, and best practices adherence.
license: MIT
metadata:
  author: agentgsd
  version: "1.0"
  languages: python,javascript,typescript,html,css
  tags: code-quality,security,review,best-practices
  compatibility: Universal
---

# Code Review Skill

## Overview
This skill provides comprehensive code review capabilities following industry best practices. It analyzes code for quality, security, performance, and maintainability across multiple programming languages.

## Capabilities

### 1. Security Analysis
- SQL injection vulnerabilities
- XSS (Cross-Site Scripting) risks
- Hardcoded secrets and API keys
- Insecure file operations
- Missing input validation
- Weak authentication patterns
- CSRF vulnerabilities
- Insecure dependencies

### 2. Code Quality Assessment
- Naming conventions (variables, functions, classes)
- Function length and cyclomatic complexity
- Code duplication (DRY violations)
- Error handling completeness
- Type hints and documentation
- Test coverage gaps
- Code organization and structure

### 3. Performance Review
- Inefficient loops and algorithms (Big O analysis)
- N+1 query problems
- Memory leaks and inefficient data structures
- Missing caching opportunities
- Blocking I/O operations
- Unnecessary computations

### 4. Best Practices Verification
- Single Responsibility Principle
- Separation of concerns
- Consistent code style
- Appropriate design patterns
- SOLID principles
- Clean code principles

## Usage

### Activation
```
/skill code-review
```

### Example Requests
- "Review the authentication code in src/auth.py"
- "Analyze src/api/ for security vulnerabilities"
- "Check tests/ for coverage gaps"
- "Review this pull request for code quality"

## Review Process

### Phase 1: Initial Analysis
1. Read target file(s) using `read` tool
2. Identify programming language and framework
3. Understand code purpose and context
4. Map dependencies and imports

### Phase 2: Security Scan
```python
# Security patterns to detect
patterns = {
    "sql_injection": r"execute\(.*%.*\)|query\(.*\+.*\)",
    "hardcoded_secrets": r"(password|api_key|secret)\s*=\s*['\"][^'\"]+['\"]",
    "eval_usage": r"\beval\b|\bexec\b",
    "path_traversal": r"open\(.*\+.*\)",
    "weak_crypto": r"\bmd5\b|\bsha1\b(?!_hash)",
}
```

### Phase 3: Quality Metrics
- Function length (>50 lines flagged)
- Cyclomatic complexity (>10 flagged)
- Nesting depth (>4 levels flagged)
- Parameter count (>5 params flagged)

### Phase 4: Output Report

## Output Format

```markdown
## 🔍 Code Review: [filename]

### ✅ Strengths
- [List positive aspects with specific examples]

### ⚠️ Issues Found

| Severity | Location | Issue | Recommendation |
|----------|----------|-------|----------------|
| 🔴 High  | Line 42  | SQL injection risk in user query | Use parameterized queries: `cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))` |
| 🟡 Medium| Line 15  | Missing type hints on public function | Add type annotations: `def process_data(data: dict) -> list:` |
| 🟢 Low   | Line 89  | Inconsistent naming (camelCase vs snake_case) | Rename to follow PEP 8: `userName` → `user_name` |

### 📊 Metrics
- **Security**: ⭐⭐⭐☆☆ (3/5)
- **Quality**: ⭐⭐⭐⭐☆ (4/5)
- **Performance**: ⭐⭐⭐☆☆ (3/5)
- **Maintainability**: ⭐⭐⭐⭐☆ (4/5)

### 🎯 Priority Actions
1. **CRITICAL**: Fix SQL injection vulnerability (Line 42)
2. **HIGH**: Add input validation for user parameters
3. **MEDIUM**: Implement proper error handling
4. **LOW**: Add docstrings to public functions

### 📝 Suggested Fixes

#### Fix 1: SQL Injection (Line 42)
**Before:**
```python
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

**After:**
```python
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```
```

## Tool Integration

### Using with Agent Tools
```yaml
# Example agent workflow
1. User: "Review src/auth.py for security issues"
2. Agent activates code-review skill
3. Agent uses `read` tool to fetch file
4. Agent analyzes using skill guidelines
5. Agent uses `edit` tool to fix critical issues
6. Agent provides summary report
```

### Grep Patterns for Security Scan
```bash
# Find hardcoded secrets
grep -rn "(password|api_key|secret)\s*=\s*['\"]" src/

# Find SQL injection risks
grep -rn "execute(.*%|execute(.*+" src/

# Find eval/exec usage
grep -rn "\beval\b\|\bexec\b" src/

# Find TODO/FIXME security items
grep -rn "TODO.*security\|FIXME.*auth\|HACK.*validation" src/
```

## Severity Levels

| Level | Icon | Description | Action Required |
|-------|------|-------------|-----------------|
| Critical | 🔴 | Immediate security risk or data loss | Fix before merge |
| High | 🟠 | Significant bug or vulnerability | Fix within 24h |
| Medium | 🟡 | Code quality issue or minor vulnerability | Fix within sprint |
| Low | 🟢 | Style inconsistency or minor improvement | Fix when convenient |
| Info | 🔵 | Suggestion or observation | Optional |

## Language-Specific Guidelines

### Python
- Follow PEP 8 style guide
- Use type hints (PEP 484)
- Prefer list comprehensions
- Use context managers (`with` statement)
- Avoid mutable default arguments

### JavaScript/TypeScript
- Use strict mode (`'use strict'`)
- Prefer `const`/`let` over `var`
- Use async/await over callbacks
- Add TypeScript types for public APIs
- Handle Promise rejections

### HTML/CSS
- Use semantic HTML5 elements
- Ensure accessibility (ARIA labels)
- Avoid inline styles
- Use CSS custom properties
- Optimize selector specificity

## Checklist

### Security Checklist
- [ ] No hardcoded credentials
- [ ] Input validation on all user inputs
- [ ] Parameterized queries for database
- [ ] Output encoding for XSS prevention
- [ ] CSRF tokens on state-changing operations
- [ ] Proper authentication/authorization
- [ ] Secure session management
- [ ] No sensitive data in logs

### Quality Checklist
- [ ] Functions < 50 lines
- [ ] Cyclomatic complexity < 10
- [ ] Meaningful variable/function names
- [ ] Error handling implemented
- [ ] Unit tests for critical paths
- [ ] Documentation for public APIs
- [ ] No code duplication
- [ ] Consistent code style

## References
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- PEP 8 - Style Guide: https://peps.python.org/pep-0008/
- Clean Code by Robert C. Martin
- Secure Coding Practices: https://wiki.sei.cmu.edu/confluence/
