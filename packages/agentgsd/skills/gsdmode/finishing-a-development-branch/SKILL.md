---
name: finishing-a-development-branch
description: Verifies tests, presents options (merge/PR/keep/discard), and cleans up worktree. This is the eighth and final step in the gsdmode workflow.
license: MIT
metadata:
  author: adapted from obra/superpowers
  version: "1.0"
  tags: git,finishing,merge,cleanup,workflow
---

# Finishing a Development Branch Skill (gsdmode)

## Overview
This skill activates after implementation and review are complete. It performs final verification, presents options for how to proceed with the work, and cleans up resources. This brings the gsdmode workflow to a clean conclusion.

The finishing-a-development-branch skill follows the gsdmode philosophy of "complexity reduction" - it ensures that work is properly completed or disposed of, leaving no loose ends or forgotten workspaces.

## When to Activate
This skill should automatically activate when:
- All implementation tasks are complete and verified
- Code review feedback has been addressed (if applicable)
- The user indicates they want to finish the current work
- The agent has completed a significant milestone or feature

It should NOT activate when:
- Work is still in progress (tasks remain incomplete)
- The user wants to continue implementing or reviewing
- The agent is in the middle of addressing feedback
- The user is asking for explanations about existing code

## Core Process

### 1. Final Verification
Run comprehensive checks to ensure the work is ready:
- Run the full test suite
- Verify all planned features are implemented
- Check for any leftover debugging or temporary code
- Ensure documentation is up to date
- Confirm no unintended changes were made

### 2. Workspace Assessment
Evaluate the current state of the worktree:
- What changes have been made compared to the base branch?
- Are there any uncommitted changes that need to be committed?
- Have all intended commits been made?
- Is the workspace in a clean, understandable state?

### 3. Option Presentation
Present clear options for how to proceed with the work:
- **Merge to main**: Integrate the work into the main development branch
- **Create Pull Request**: Prepare for collaborative review before merging
- **Keep Branch**: Preserve the work for future continuation
- **Discard Work**: Abandon the work and clean up resources

### 4. User Guidance
Help the user make an informed decision by:
- Summarizing what was accomplished
- Highlighting any known issues or limitations
- Explaining the implications of each option
- Recommending the best course based on the work done

### 5. Cleanup Execution
Based on the user's choice:
- **Merge**: Perform the merge, delete the worktree, update local tracking
- **Push PR**: Push the branch to remote and create/pull request URL
- **Keep**: Preserve the worktree and branch for future use
- **Discard**: Remove the worktree and delete the local branch

### 6. Session Conclusion
Wrap up the gsdmode session:
- Provide a final summary of what was accomplished
- Offer to save any relevant notes or documents
- Return the agent to normal, non-workflow operation

## Output Format
The finishing-a-development-branch skill should produce a completion document with these sections:

### 📋 Work Summary
- **Original Goal**: What we set out to accomplish
- **Work Completed**: High-level summary of what was done
- **Tasks Completed**: Number and list of finished tasks
- **Files Changed**: Summary of modifications made
- **Tests Status**: Final test suite results

### 🌳 Workspace Information
- **Branch Name**: The git branch used for this work
- **Worktree Path**: Filesystem path to the isolated worktree
- **Base Commit**: The commit this work was based on
- **Changes Made**: Summary of differences from base

### 🚦 Available Options
Clear presentation of choices for proceeding:

#### 🔀 Merge to Main
- **Pros**: Immediate integration, single source of truth
- **Cons**: Requires confidence in stability, affects main branch
- **Process**: Fast-forward or merge commit, then cleanup

#### 📤 Create Pull Request
- **Pros**: Collaborative review, safety net before merging
- **Cons**: Requires remote access, extra step
- **Process**: Push to remote, create PR, review, then merge

#### 📎 Keep Branch
- **Pros**: Preserves work for future continuation
- **Cons**: Uses disk space, potential for conflicts
- **Process**: Leave worktree and branch intact

#### 🗑️ Discard Work
- **Pros**: Clean slate, no lingering work
- **Cons**: Work is lost unless preserved elsewhere
- **Process**: Remove worktree, delete local branch

### 📝 Recommended Action
Based on the work completed and current state:
- Clear recommendation with reasoning
- Any caveats or considerations
- Next steps if applicable

### 🧹 Cleanup Performed
What was done based on the user's choice:
- Commands executed
- Resources removed or preserved
- Final state of the system

## Tool Usage Patterns

### Using with Agent Tools
```yaml
# Typical workflow
1. User: "Let's finish up the authentication feature work"
2. Agent activates finishing-a-development-branch skill
3. Agent uses `bash` to run final test suite
4. Agent uses `git status`, `git diff` to assess workspace
5. Agent uses `read` to review work summary documents
6. Agent presents options and asks for user choice
7. Based on choice:
   - If merge: `git merge`, `git worktree remove`, `git branch -d`
   - If PR: `git push`, create PR URL
   - If keep: Leave worktree, inform user how to return
   - If discard: `git worktree remove`, `git branch -D`
8. Agent uses `write` to create final summary document
9. Agent provides closing message and returns to normal operation
```

### Git Worktree Commands
```bash
# Assess current state
git status
git diff --stat base-branch...HEAD
git log --oneline base-branch..HEAD

# Merge option
git checkout main
git merge --no-ff feature-branch
git worktree remove ../feature-worktree
git branch -d feature-branch

# PR option
git push -u origin feature-branch
# Then create PR via GitHub UI or CLI

# Keep option
# Worktree and branch remain available
# Return later with: git worktree list

# Discard option
git worktree remove ../feature-worktree
git branch -D feature-branch
```

## Integration with gsdmode Workflow
This skill is the eighth and final step in the gsdmode sequence:
1. **Brainstorming** → Refines the idea
2. **Using Git Worktrees** → Sets up clean implementation environment
3. **Writing Plans** → Creates detailed implementation tasks
4. **Subagent-Driven Development** → Executes the plan with quality gates
5. **Test-Driven Development** → Ensures correctness during implementation
6. **Requesting Code Review** → Validates completed work
7. **Receiving Code Review** → Processes and implements feedback
8. **Finishing a Development Branch** (this skill) → Completes the work cycle

The agent should automatically progress to this skill when:
- All implementation tasks are complete and verified
- All code review feedback has been addressed (or user accepts remaining issues)
- The user indicates they want to conclude the work
- There is a clean verification state (tests passing, etc.)

After this skill completes, the gsdmode workflow ends and the agent returns to normal operation unless gsdmode is reactivated.

## Best Practices

### Do ✅
- Always run final verification before presenting options
- Be clear about what each option entails
- Make cleanup thorough to avoid leaving residues
- Provide a summary of what was accomplished
- Respect the user's autonomy in deciding what to do with their work

### Don't ❌
- Skip verification to "move faster"
- Leave ambiguous or incomplete options
- Forget to clean up worktrees (can cause confusion later)
- Pressure the user into a particular choice
- Leave unresolved issues or confusion about the state

## Example Session

**User**: "Let's finish up the blog authentication feature work."

**Agent (Finishing a Development Branch)**:
1. Runs final verification: `pytest` shows 98% pass, 2 skipped (expected)
2. Assesses workspace: 
   - Branch: feature-blog-auth
   - Changes: 12 files modified, 245 additions, 32 deletions
   - Commits: 8 logical commits representing completed tasks
3. Presents options:
   ```
   📋 Work Summary:
   - Original Goal: Add user authentication to blog
   - Work Completed: User model, registration/login routes, session middleware, protection
   - Tasks Completed: 8/8
   - Tests Status: 98% pass (2 skipped as expected)
   
   🌳 Workspace Information:
   - Branch: feature-blog-auth
   - Worktree: /path/to/project/../gsdmode-blog-auth
   - Base Commit: abc123 (Initial project setup)
   
   🚦 Available Options:
   
   🔀 Merge to Main
   Pros: Immediate integration, single source of truth
   Cons: Requires confidence in stability, affects main branch
   Process: Merge to main, then cleanup
   
   📤 Create Pull Request
   Pros: Collaborative review, safety net before merging
   Cons: Requires remote access, extra step
   Process: Push to remote, create PR
   
   📎 Keep Branch
   Pros: Preserves work for future continuation
   Cons: Uses disk space, potential for conflicts
   Process: Leave worktree intact
   
   🗑️ Discard Work
   Pros: Clean slate, no lingering work
   Cons: Work is lost unless preserved elsewhere
   Process: Remove worktree and branch
   
   📝 Recommended Action: Create Pull Request
   Reasoning: The feature is complete and well-tested. Getting a second pair of eyes 
   via PR will help catch any edge cases before merging to main.
   ```
4. Asks: "Does this look correct? Which option would you prefer?"
5. User: "Let's create a pull request."
6. Agent:
   - Pushes branch to remote: `git push -u origin feature-blog-auth`
   - Provides PR URL: https://github.com/user/repo/compare/main...feature-blog-auth
   - Informs user how to return to this work: `git worktree list`
   - Creates final summary document
   - Deactivates gsdmode, returns to normal operation
7. Agent: "The work has been pushed to your remote repository. You can create the pull request at the URL above. To return to this work later, use `git worktree list`. Thanks for using agentgsd!"

**User**: "Great, thanks for the help!"

**Agent**: Session concludes normally.

---
*Adapted from obra/superpowers finishing-a-development-branch skill for agentgsd gsdmode*
