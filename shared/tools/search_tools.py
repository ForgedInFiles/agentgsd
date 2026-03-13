"""
Search tools for AI coding assistants.

This module provides tools for searching and finding files based on patterns.
Each tool inherits from the Tool base class and implements the execute method.

Tools included:
    - GrepTool: Search files for regex pattern
    - GlobTool: Find files by pattern
    - FindTool: Find files by name pattern

Example usage:
    from shared.tools.search_tools import GrepTool, GlobTool
    from shared.tools.base import ToolRegistry

    registry = ToolRegistry()
    registry.register(GrepTool())
    registry.register(GlobTool())

    result = registry.get("grep").execute({"pat": "def.*main", "path": "."})
"""

import os
import re
from typing import Any, Dict

from shared.tools.base import Tool
from shared.utils.colors import BLUE, CYAN, DIM, GREEN, RED, RESET, YELLOW


class GrepTool(Tool):
    """
    Search files for a regex pattern.

    Recursively searches through files in the specified path for lines matching
    a regular expression pattern. Returns up to 100 matches.

    Parameters:
        pat (str): Regular expression pattern to search for (required).
        path (str, optional): Directory to search in (default: current directory).

    Returns:
        str: Matching lines in format "{filepath}:{line_num}:{content}".

    Example:
        >>> tool = GrepTool()
        >>> result = tool.execute({"pat": "def.*hello", "path": "/project"})
        >>> result = tool.execute({"pat": "TODO"})
    """

    def __init__(self):
        super().__init__(
            name="grep",
            description="Search files for regex pattern",
            parameters={"pat": "string", "path": "string?"},
        )

    def execute(self, args: Dict[str, Any]) -> str:
        """Search files for a regex pattern.
        
        Args:
            args: Dictionary containing:
                - pat (str): Regular expression pattern to search for (required)
                - path (str, optional): Directory to search in (default: current directory)
                
        Returns:
            str: Matching lines in format "{filepath}:{line_num}:{content}" or error message
        """
        try:
            pattern = re.compile(args["pat"])
        except re.error as e:
            return f"{RED}✗{RESET} invalid regex: {e}"

        search_path = args.get("path", ".")
        hits = []
        max_results = 100

        for root, dirs, files in os.walk(search_path):
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath) as f:
                        for line_num, line in enumerate(f, 1):
                            if pattern.search(line):
                                rel_path = os.path.relpath(filepath, search_path)
                                hits.append(
                                    f"{DIM}{rel_path}:{line_num}{RESET}:{line.rstrip()}"
                                )
                                if len(hits) >= max_results:
                                    break
                except (IOError, PermissionError, UnicodeDecodeError):
                    continue

            if len(hits) >= max_results:
                break

        if not hits:
            return f"{DIM}(no matches){RESET}"

        return "\n".join(hits[:max_results])


class GlobTool(Tool):
    """
    Find files by glob pattern.

    Searches for files matching a glob pattern (e.g., *.py, **/*.js).
    Results are sorted by modification time (newest first).

    Parameters:
        pat (str): Glob pattern to match (e.g., "*.py", "**/*.txt") (required).
        path (str, optional): Base directory to search from (default: current directory).

    Returns:
        str: List of matching file paths, one per line.

    Example:
        >>> tool = GlobTool()
        >>> result = tool.execute({"pat": "*.py"})
        >>> result = tool.execute({"pat": "**/*.js", "path": "/project"})
    """

    def __init__(self):
        super().__init__(
            name="glob",
            description="Find files by pattern",
            parameters={"pat": "string", "path": "string?"},
        )

    def execute(self, args: Dict[str, Any]) -> str:
        """Find files by glob pattern.
        
        Args:
            args: Dictionary containing:
                - pat (str): Glob pattern to match (e.g., "*.py", "**/*.txt") (required)
                - path (str, optional): Base directory to search from (default: current directory)
                
        Returns:
            str: List of matching file paths, one per line, or message if none found
        """
        base_path = args.get("path", ".")
        pattern = args["pat"]

        full_pattern = os.path.join(base_path, pattern)
        full_pattern = full_pattern.replace("//", "/")

        try:
            files = glob.glob(full_pattern, recursive=True)
        except (OSError, re.error) as e:
            return f"{RED}✗{RESET} glob error: {e}"

        files = sorted(
            files,
            key=lambda f: os.path.getmtime(f) if os.path.isfile(f) else 0,
            reverse=True,
        )

        if not files:
            return f"{DIM}(none found){RESET}"

        return "\n".join(files)


class FindTool(Tool):
    """
    Find files by name pattern.

    Recursively searches for files whose names match a given pattern.
    The pattern is treated as a case-insensitive regex.

    Parameters:
        name (str): Pattern to match against file names (required).
        path (str, optional): Directory to search in (default: current directory).

    Returns:
        str: List of matching file paths, one per line.

    Example:
        >>> tool = FindTool()
        >>> result = tool.execute({"name": "test", "path": "/project"})
        >>> result = tool.execute({"name": ".*\\.py$"})
    """

    def __init__(self):
        super().__init__(
            name="find",
            description="Find files by name",
            parameters={"name": "string", "path": "string?"},
        )

    def execute(self, args: Dict[str, Any]) -> str:
        """Find files by name pattern.
        
        Args:
            args: Dictionary containing:
                - name (str): Pattern to match against file names (required)
                - path (str, optional): Directory to search in (default: current directory)
                
        Returns:
            str: List of matching file paths, one per line, or message if none found
        """
        try:
            pattern = re.compile(args.get("name", ".*"), re.IGNORECASE)
        except re.error as e:
            return f"{RED}✗{RESET} invalid regex: {e}"

        search_path = args.get("path", ".")
        hits = []
        max_results = 50

        for root, dirs, files in os.walk(search_path):
            for filename in files:
                if pattern.search(filename):
                    full_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(full_path, search_path)
                    hits.append(rel_path)
                    if len(hits) >= max_results:
                        break

            if len(hits) >= max_results:
                break

        if not hits:
            return f"{DIM}(none found){RESET}"

        return "\n".join(hits[:max_results])


import glob as globlib
