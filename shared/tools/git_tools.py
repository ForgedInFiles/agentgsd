"""
Git operation tools for AI coding assistants.

This module provides tools for performing common Git operations.
Each tool inherits from the Tool base class and implements the execute method.

Tools included:
    - GitStatusTool: Show working tree status
    - GitDiffTool: Show changes
    - GitLogTool: Show commit logs
    - GitBranchTool: List/create/switch branches
    - GitCommitTool: Record changes to the repository
    - GitAddTool: Add file contents to the staging area
    - GitResetTool: Unstage changes
    - GitCheckoutTool: Switch branches or restore files

Example usage:
    from shared.tools.git_tools import GitStatusTool, GitDiffTool
    from shared.tools.base import ToolRegistry

    registry = ToolRegistry()
    registry.register(GitStatusTool())
    registry.register(GitDiffTool())
"""

import os
import subprocess
from typing import Any, Dict, List, Optional

from shared.tools.base import Tool
from shared.utils.colors import BLUE, CYAN, DIM, GREEN, RED, RESET, YELLOW


class GitTool(Tool):
    """Base class for Git tools with common functionality."""

    def __init__(self, name: str, description: str, parameters: Dict[str, str]):
        super().__init__(name, description, parameters)

    def _run_git(self, args: List[str], cwd: Optional[str] = None) -> subprocess.CompletedProcess:
        """Run a git command."""
        cmd = ["git"] + args
        return subprocess.run(
            cmd,
            cwd=cwd or os.getcwd(),
            capture_output=True,
            text=True,
            timeout=30,
        )


class GitStatusTool(GitTool):
    """
    Show the working tree status.

    Displays the current state of the repository including modified, staged,
    and untracked files.

    Parameters:
        repo_path (str, optional): Path to the git repository (default: current directory).

    Returns:
        str: Formatted status output.
    """

    def __init__(self):
        super().__init__(
            name="git_status",
            description="Show working tree status",
            parameters={"repo_path": "string?"},
        )

    def execute(self, args: Dict[str, Any]) -> str:
        repo_path = args.get("repo_path", ".")

        if not os.path.isdir(os.path.join(repo_path, ".git")):
            return f"{RED}✗{RESET} not a git repository: {repo_path}"

        result = self._run_git(["status", "--short"], cwd=repo_path)

        if result.returncode != 0:
            return f"{RED}✗{RESET} git error: {result.stderr}"

        if not result.stdout.strip():
            return f"{GREEN}✓{RESET} working tree clean"

        lines = result.stdout.strip().split("\n")
        output = [f"{CYAN}Git Status:{RESET}"]

        for line in lines:
            status = line[:2]
            filepath = line[3:]

            if "M" in status:
                prefix = f"{YELLOW}M{RESET}"
            elif "A" in status:
                prefix = f"{GREEN}A{RESET}"
            elif "D" in status:
                prefix = f"{RED}D{RESET}"
            elif "?" in status:
                prefix = f"{DIM}?{RESET}"
            else:
                prefix = f"{BLUE}{status}{RESET}"

            output.append(f"  {prefix} {filepath}")

        return "\n".join(output)


class GitDiffTool(GitTool):
    """
    Show changes between commits, working tree, etc.

    Parameters:
        repo_path (str, optional): Path to the git repository (default: current directory).
        staged (bool, optional): Show staged changes (default: False).
        staged_only (bool, optional): Show only staged changes (default: False).

    Returns:
        str: Formatted diff output.
    """

    def __init__(self):
        super().__init__(
            name="git_diff",
            description="Show changes",
            parameters={
                "repo_path": "string?",
                "staged": "boolean?",
                "staged_only": "boolean?",
            },
        )

    def execute(self, args: Dict[str, Any]) -> str:
        repo_path = args.get("repo_path", ".")

        if not os.path.isdir(os.path.join(repo_path, ".git")):
            return f"{RED}✗{RESET} not a git repository: {repo_path}"

        cmd = ["diff", "--color=always"]

        if args.get("staged"):
            cmd.append("--staged")
        elif args.get("staged_only"):
            cmd = ["diff", "--staged", "--color=always"]

        result = self._run_git(cmd, cwd=repo_path)

        if result.returncode != 0:
            return f"{RED}✗{RESET} git error: {result.stderr}"

        if not result.stdout.strip():
            return f"{DIM}No changes{RESET}"

        return result.stdout


class GitLogTool(GitTool):
    """
    Show commit logs.

    Parameters:
        repo_path (str, optional): Path to the git repository (default: current directory).
        max_count (int, optional): Maximum number of commits to show (default: 10).

    Returns:
        str: Formatted commit log.
    """

    def __init__(self):
        super().__init__(
            name="git_log",
            description="Show commit logs",
            parameters={
                "repo_path": "string?",
                "max_count": "number?",
            },
        )

    def execute(self, args: Dict[str, Any]) -> str:
        repo_path = args.get("repo_path", ".")
        max_count = args.get("max_count", 10)

        if not os.path.isdir(os.path.join(repo_path, ".git")):
            return f"{RED}✗{RESET} not a git repository: {repo_path}"

        result = self._run_git(
            ["log", f"--max-count={max_count}", "--oneline", "--decorate"], cwd=repo_path
        )

        if result.returncode != 0:
            return f"{RED}✗{RESET} git error: {result.stderr}"

        if not result.stdout.strip():
            return f"{DIM}No commits yet{RESET}"

        lines = result.stdout.strip().split("\n")
        output = [f"{CYAN}Git Log:{RESET}"]

        for line in lines:
            output.append(f"  {line}")

        return "\n".join(output)


class GitBranchTool(GitTool):
    """
    List, create, or delete branches.

    Parameters:
        repo_path (str, optional): Path to the git repository (default: current directory).
        branch_name (str, optional): Name of branch to create or switch to.
        create (bool, optional): Create a new branch (default: False).
        delete (bool, optional): Delete a branch (default: False).

    Returns:
        str: Branch listing or operation result.
    """

    def __init__(self):
        super().__init__(
            name="git_branch",
            description="List/create/delete branches",
            parameters={
                "repo_path": "string?",
                "branch_name": "string?",
                "create": "boolean?",
                "delete": "boolean?",
            },
        )

    def execute(self, args: Dict[str, Any]) -> str:
        repo_path = args.get("repo_path", ".")
        branch_name = args.get("branch_name")

        if not os.path.isdir(os.path.join(repo_path, ".git")):
            return f"{RED}✗{RESET} not a git repository: {repo_path}"

        # Create branch
        if args.get("create") and branch_name:
            result = self._run_git(["branch", branch_name], cwd=repo_path)
            if result.returncode != 0:
                return f"{RED}✗{RESET} git error: {result.stderr}"
            return f"{GREEN}✓{RESET} created branch: {branch_name}"

        # Delete branch
        if args.get("delete") and branch_name:
            result = self._run_git(["branch", "-d", branch_name], cwd=repo_path)
            if result.returncode != 0:
                return f"{RED}✗{RESET} git error: {result.stderr}"
            return f"{GREEN}✓{RESET} deleted branch: {branch_name}"

        # List branches
        result = self._run_git(
            ["branch", "-a", "--format=%(refname:short) %(upstream:short)"], cwd=repo_path
        )

        if result.returncode != 0:
            return f"{RED}✗{RESET} git error: {result.stderr}"

        lines = result.stdout.strip().split("\n")
        output = [f"{CYAN}Branches:{RESET}"]

        # Get current branch
        current_result = self._run_git(["branch", "--show-current"], cwd=repo_path)
        current_branch = current_result.stdout.strip()

        for line in lines:
            if not line:
                continue
            parts = line.split()
            name = parts[0]

            if name == current_branch:
                prefix = f"{GREEN}*{RESET}"
            else:
                prefix = "  "

            output.append(f"  {prefix} {name}")

        return "\n".join(output)


class GitCommitTool(GitTool):
    """
    Record changes to the repository.

    Parameters:
        repo_path (str, optional): Path to the git repository (default: current directory).
        message (str, optional): Commit message.
        amend (bool, optional): Amend the previous commit (default: False).
        all (bool, optional): Stage all modified files (default: False).

    Returns:
        str: Commit result.
    """

    def __init__(self):
        super().__init__(
            name="git_commit",
            description="Record changes",
            parameters={
                "repo_path": "string?",
                "message": "string?",
                "amend": "boolean?",
                "all": "boolean?",
            },
        )

    def execute(self, args: Dict[str, Any]) -> str:
        repo_path = args.get("repo_path", ".")

        if not os.path.isdir(os.path.join(repo_path, ".git")):
            return f"{RED}✗{RESET} not a git repository: {repo_path}"

        message = args.get("message")
        if not message:
            return f"{RED}✗{RESET} commit message is required"

        # Stage all if requested
        if args.get("all"):
            result = self._run_git(["add", "-A"], cwd=repo_path)
            if result.returncode != 0:
                return f"{RED}✗{RESET} git error: {result.stderr}"

        # Build commit command
        cmd = ["commit", "-m", message]

        if args.get("amend"):
            cmd.append("--amend")

        result = self._run_git(cmd, cwd=repo_path)

        if result.returncode != 0:
            return f"{RED}✗{RESET} git error: {result.stderr}"

        return f"{GREEN}✓{RESET} committed: {message[:50]}"


class GitAddTool(GitTool):
    """
    Add file contents to the staging area.

    Parameters:
        repo_path (str, optional): Path to the git repository (default: current directory).
        files (str, optional): Files to stage (default: all - ".").
        all_files (bool, optional): Stage all modified files (default: False).

    Returns:
        str: Operation result.
    """

    def __init__(self):
        super().__init__(
            name="git_add",
            description="Stage file changes",
            parameters={
                "repo_path": "string?",
                "files": "string?",
                "all_files": "boolean?",
            },
        )

    def execute(self, args: Dict[str, Any]) -> str:
        repo_path = args.get("repo_path", ".")

        if not os.path.isdir(os.path.join(repo_path, ".git")):
            return f"{RED}✗{RESET} not a git repository: {repo_path}"

        cmd = ["add"]

        if args.get("all_files"):
            cmd.append("-A")
        else:
            files = args.get("files", ".")
            cmd.extend(files.split())

        result = self._run_git(cmd, cwd=repo_path)

        if result.returncode != 0:
            return f"{RED}✗{RESET} git error: {result.stderr}"

        return f"{GREEN}✓{RESET} staged changes"


class GitResetTool(GitTool):
    """
    Unstage changes or reset HEAD.

    Parameters:
        repo_path (str, optional): Path to the git repository (default: current directory).
        mode (str, optional): Reset mode - "soft", "mixed", "hard" (default: "mixed").
        target (str, optional): Commit to reset to (default: HEAD).
        unstage (bool, optional): Only unstage files (default: False).

    Returns:
        str: Operation result.
    """

    def __init__(self):
        super().__init__(
            name="git_reset",
            description="Unstage or reset changes",
            parameters={
                "repo_path": "string?",
                "mode": "string?",
                "target": "string?",
                "unstage": "boolean?",
            },
        )

    def execute(self, args: Dict[str, Any]) -> str:
        repo_path = args.get("repo_path", ".")

        if not os.path.isdir(os.path.join(repo_path, ".git")):
            return f"{RED}✗{RESET} not a git repository: {repo_path}"

        # Unstage only
        if args.get("unstage"):
            result = self._run_git(["reset", "HEAD"], cwd=repo_path)
        else:
            cmd = ["reset"]
            mode = args.get("mode", "mixed")
            cmd.append(f"--{mode}")

            target = args.get("target", "HEAD")
            cmd.append(target)

            result = self._run_git(cmd, cwd=repo_path)

        if result.returncode != 0:
            return f"{RED}✗{RESET} git error: {result.stderr}"

        return f"{GREEN}✓{RESET} reset completed"


class GitCheckoutTool(GitTool):
    """
    Switch branches or restore working tree files.

    Parameters:
        repo_path (str, optional): Path to the git repository (default: current directory).
        branch_name (str, optional): Branch to switch to.
        create_branch (bool, optional): Create and switch to new branch (default: False).
        file_path (str, optional): File to restore.

    Returns:
        str: Operation result.
    """

    def __init__(self):
        super().__init__(
            name="git_checkout",
            description="Switch branches or restore files",
            parameters={
                "repo_path": "string?",
                "branch_name": "string?",
                "create_branch": "boolean?",
                "file_path": "string?",
            },
        )

    def execute(self, args: Dict[str, Any]) -> str:
        repo_path = args.get("repo_path", ".")

        if not os.path.isdir(os.path.join(repo_path, ".git")):
            return f"{RED}✗{RESET} not a git repository: {repo_path}"

        cmd = ["checkout"]

        if args.get("create_branch") and args.get("branch_name"):
            cmd.extend(["-b", args["branch_name"]])
        elif args.get("branch_name"):
            cmd.append(args["branch_name"])
        elif args.get("file_path"):
            cmd.extend(["--", args["file_path"]])
        else:
            return f"{RED}✗{RESET} branch_name or file_path required"

        result = self._run_git(cmd, cwd=repo_path)

        if result.returncode != 0:
            return f"{RED}✗{RESET} git error: {result.stderr}"

        target = args.get("branch_name") or args.get("file_path")
        return f"{GREEN}✓{RESET} checked out: {target}"


class GitPushTool(GitTool):
    """
    Push changes to a remote repository.

    Parameters:
        repo_path (str, optional): Path to the git repository (default: current directory).
        remote (str, optional): Remote name (default: "origin").
        branch (str, optional): Branch to push (default: current branch).
        set_upstream (bool, optional): Set upstream for branch (default: False).

    Returns:
        str: Operation result.
    """

    def __init__(self):
        super().__init__(
            name="git_push",
            description="Push to remote",
            parameters={
                "repo_path": "string?",
                "remote": "string?",
                "branch": "string?",
                "set_upstream": "boolean?",
            },
        )

    def execute(self, args: Dict[str, Any]) -> str:
        repo_path = args.get("repo_path", ".")

        if not os.path.isdir(os.path.join(repo_path, ".git")):
            return f"{RED}✗{RESET} not a git repository: {repo_path}"

        cmd = ["push"]

        if args.get("set_upstream"):
            cmd.append("-u")

        remote = args.get("remote", "origin")
        branch = args.get("branch")

        if branch:
            cmd.extend([remote, branch])
        else:
            cmd.append(remote)

        result = self._run_git(cmd, cwd=repo_path)

        if result.returncode != 0:
            return f"{RED}✗{RESET} git error: {result.stderr}"

        return f"{GREEN}✓{RESET} pushed to {remote}"


class GitPullTool(GitTool):
    """
    Fetch and integrate with another repository or branch.

    Parameters:
        repo_path (str, optional): Path to the git repository (default: current directory).
        remote (str, optional): Remote name (default: "origin").
        branch (str, optional): Branch to pull (default: current branch).

    Returns:
        str: Operation result.
    """

    def __init__(self):
        super().__init__(
            name="git_pull",
            description="Pull from remote",
            parameters={
                "repo_path": "string?",
                "remote": "string?",
                "branch": "string?",
            },
        )

    def execute(self, args: Dict[str, Any]) -> str:
        repo_path = args.get("repo_path", ".")

        if not os.path.isdir(os.path.join(repo_path, ".git")):
            return f"{RED}✗{RESET} not a git repository: {repo_path}"

        cmd = ["pull"]

        remote = args.get("remote", "origin")
        branch = args.get("branch")

        if branch:
            cmd.extend([remote, branch])
        else:
            cmd.append(remote)

        result = self._run_git(cmd, cwd=repo_path)

        if result.returncode != 0:
            return f"{RED}✗{RESET} git error: {result.stderr}"

        return f"{GREEN}✓{RESET} pulled from {remote}"
