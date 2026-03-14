---
name: commit
description: Create a git commit with proper conventions
aliases: [git-commit]
---

Create a git commit for the staged changes with a properly formatted commit message.

Steps:
1. Run git status to see what files are staged
2. Run git diff --staged to review the changes
3. Generate a commit message following conventional commits format:
   - feat: for new features
   - fix: for bug fixes
   - docs: for documentation changes
   - style: for formatting changes
   - refactor: for code refactoring
   - test: for test changes
   - chore: for maintenance tasks

4. Execute: git commit -m "your message"

Provide the commit message and confirm after executing.
