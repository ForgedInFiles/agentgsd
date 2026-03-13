"""
File manipulation tools for AI coding assistants.

This module provides tools for reading, writing, editing, and browsing files
and directories. Each tool inherits from the Tool base class and implements
the execute method.

Tools included:
    - ReadTool: Read file with line numbers
    - WriteTool: Write content to file
    - EditTool: Replace old with new in file
    - MkdirTool: Create directory
    - LsTool: List directory contents
    - TreeTool: Show directory tree
    - HeadTool: Show first N lines
    - TailTool: Show last N lines
    - WcTool: Count lines/words/chars
    - PwdTool: Get current directory

Example usage:
    from shared.tools.file_tools import ReadTool, WriteTool
    from shared.tools.base import ToolRegistry

    registry = ToolRegistry()
    registry.register(ReadTool())
    registry.register(WriteTool())

    result = registry.get("read").execute({"path": "example.txt"})
"""

import os
from datetime import datetime
from typing import Any, Dict, List

from shared.tools.base import Tool
from shared.utils.colors import BLUE, CYAN, DIM, GREEN, RED, RESET, YELLOW


class ReadTool(Tool):
    """
    Read file content with line numbers.

    Reads a file and returns its contents with line numbers. Supports optional
    offset and limit parameters for reading specific portions of the file.

    Parameters:
        path (str): Path to the file to read (required).
        offset (int, optional): Line number to start reading from (0-indexed, default: 0).
        limit (int, optional): Maximum number of lines to read (default: all lines).

    Returns:
        str: File contents with line numbers in format "{line_num}│ {content}".

    Example:
        >>> tool = ReadTool()
        >>> result = tool.execute({"path": "example.txt"})
        >>> result = tool.execute({"path": "example.txt", "offset": 10, "limit": 20})
    """

    def __init__(self):
        super().__init__(
            name="read",
            description="Read file with line numbers",
            parameters={"path": "string", "offset": "number?", "limit": "number?"},
        )

    def execute(self, args: Dict[str, Any]) -> str:
        path = args["path"]
        if not os.path.isfile(path):
            return f"{RED}✗{RESET} file not found: {path}"

        try:
            with open(path) as f:
                lines = f.readlines()
        except (IOError, PermissionError) as e:
            return f"{RED}✗{RESET} cannot read {path}: {e}"

        offset = args.get("offset", 0)
        limit = args.get("limit", len(lines))
        selected = lines[offset : offset + limit]

        return "".join(
            f"{DIM}{offset + idx + 1:5}{RESET}│ {line}" for idx, line in enumerate(selected)
        )


class WriteTool(Tool):
    """
    Write content to a file.

    Creates a new file or overwrites an existing file with the given content.
    Automatically creates parent directories if they don't exist.

    Parameters:
        path (str): Path to the file to write (required).
        content (str): Content to write to the file (required).

    Returns:
        str: Success message with the file path.

    Example:
        >>> tool = WriteTool()
        >>> result = tool.execute({"path": "new_file.txt", "content": "Hello World"})
    """

    def __init__(self):
        super().__init__(
            name="write",
            description="Write content to file",
            parameters={"path": "string", "content": "string"},
        )

    def execute(self, args: Dict[str, Any]) -> str:
        """Write content to a file.
        
        Args:
            args: Dictionary containing:
                - path (str): Path to the file to write (required)
                - content (str): Content to write to the file (required)
                
        Returns:
            str: Success message or error message
        """
        path = args["path"]
        content = args["content"]

        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
        except (IOError, PermissionError) as e:
            return f"{RED}✗{RESET} cannot write {path}: {e}"

        return f"{GREEN}✓{RESET} written: {DIM}{path}{RESET}"


class EditTool(Tool):
    """
    Replace old text with new text in a file.

    Replaces occurrences of old with new in the file. By default, replaces only
    the first occurrence. Use all=true to replace all occurrences.

    Parameters:
        path (str): Path to the file to edit (required).
        old (str): Text to find and replace (required).
        new (str): Replacement text (required).
        all (bool, optional): Replace all occurrences (default: False).

    Returns:
        str: Success message or error if old text not found or appears multiple times.

    Example:
        >>> tool = EditTool()
        >>> result = tool.execute({"path": "file.txt", "old": "foo", "new": "bar"})
        >>> result = tool.execute({"path": "file.txt", "old": "foo", "new": "bar", "all": True})
    """

    def __init__(self):
        super().__init__(
            name="edit",
            description="Replace old with new in file",
            parameters={
                "path": "string",
                "old": "string",
                "new": "string",
                "all": "boolean?",
            },
        )

    def execute(self, args: Dict[str, Any]) -> str:
        """Replace old text with new text in a file.
        
        Args:
            args: Dictionary containing:
                - path (str): Path to the file to edit (required)
                - old (str): Text to find and replace (required)
                - new (str): Replacement text (required)
                - all (bool, optional): Replace all occurrences (default: False)
                
        Returns:
            str: Success message indicating replacements made or error message
        """
        path = args["path"]
        if not os.path.isfile(path):
            return f"{RED}✗{RESET} file not found: {path}"

        try:
            with open(path) as f:
                text = f.read()
        except (IOError, PermissionError) as e:
            return f"{RED}✗{RESET} cannot read {path}: {e}"

        old = args["old"]
        new = args["new"]

        if old not in text:
            return f"{RED}✗{RESET} old_string not found"

        count = text.count(old)
        if not args.get("all") and count > 1:
            return f"{RED}✗{RESET} old_string appears {count} times, use all=true to replace all occurrences"

        replacement = text.replace(old, new, 1) if not args.get("all") else text.replace(old, new)

        try:
            with open(path, "w") as f:
                f.write(replacement)
        except (IOError, PermissionError) as e:
            return f"{RED}✗{RESET} cannot write {path}: {e}"

        return f"{GREEN}✓{RESET} edited: {DIM}{path}{RESET}"


class MkdirTool(Tool):
    """
    Create a directory.

    Creates a new directory at the specified path. Creates parent directories
    as needed (like mkdir -p).

    Parameters:
        path (str): Path to the directory to create (required).

    Returns:
        str: Success message with the created directory path.

    Example:
        >>> tool = MkdirTool()
        >>> result = tool.execute({"path": "new_directory/subdir"})
    """

    def __init__(self):
        super().__init__(
            name="mkdir",
            description="Create directory",
            parameters={"path": "string"},
        )

    def execute(self, args: Dict[str, Any]) -> str:
        """Create a directory.
        
        Args:
            args: Dictionary containing:
                - path (str): Path to the directory to create (required)
                
        Returns:
            str: Success message with the created directory path or error message
        """
        path = args["path"]

        try:
            os.makedirs(path, exist_ok=True)
        except (IOError, PermissionError) as e:
            return f"{RED}✗{RESET} cannot create {path}: {e}"

        return f"{GREEN}✓{RESET} created: {DIM}{path}{RESET}"


class LsTool(Tool):
    """
    List directory contents.

    Lists files and directories in the specified path with size and modification
    time information.

    Parameters:
        path (str, optional): Path to list (default: current directory).

    Returns:
        str: Directory contents with file/directory indicators, sizes, and mtimes.

    Example:
        >>> tool = LsTool()
        >>> result = tool.execute({"path": "/some/directory"})
        >>> result = tool.execute({})
    """

    def __init__(self):
        super().__init__(
            name="ls",
            description="List directory contents",
            parameters={"path": "string?"},
        )

    def execute(self, args: Dict[str, Any]) -> str:
        path = args.get("path", ".")
        if not os.path.isdir(path):
            return f"{RED}✗{RESET} not a directory: {path}"

        entries = []
        try:
            for name in sorted(os.listdir(path)):
                full = os.path.join(path, name)
                # Determine prefix based on whether it's a directory or file
                prefix = f"{CYAN}📁{RESET} " if os.path.isdir(full) else f"{BLUE}📄{RESET} "
                try:
                    stat = os.stat(full)
                    size = stat.st_size
                    mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                    entries.append(f"{prefix}{name} {DIM}({size:,} bytes · {mtime}){RESET}")
                except (OSError, PermissionError):
                    entries.append(f"{prefix}{name} {DIM}(?){RESET}")
        except PermissionError:
            return f"{RED}✗{RESET} permission denied: {path}"

        return "\n".join(entries) or f"{DIM}(empty){RESET}"


class TreeTool(Tool):
    """
    Show directory tree structure.

    Displays a hierarchical tree view of directories and files starting from
    the specified path.

    Parameters:
        path (str, optional): Root directory to display (default: current directory).
        depth (int, optional): Maximum depth to traverse (not implemented, shown files limited to 20 per dir).

    Returns:
        str: Tree representation of the directory structure.

    Example:
        >>> tool = TreeTool()
        >>> result = tool.execute({"path": "/project"})
        >>> result = tool.execute({})
    """

    def __init__(self):
        super().__init__(
            name="tree",
            description="Show directory tree",
            parameters={"path": "string?", "depth": "number?"},
        )

    def execute(self, args: Dict[str, Any]) -> str:
        path = args.get("path", ".")
        if not os.path.isdir(path):
            return f"{RED}✗{RESET} not a directory: {path}"

        def _tree(p: str, prefix: str = "", depth: int = 0) -> List[str]:
            try:
                entries = sorted(os.listdir(p))
                dirs = [e for e in entries if os.path.isdir(os.path.join(p, e))]
                files = [e for e in entries if os.path.isfile(os.path.join(p, e))]
            except PermissionError:
                return [f"{prefix}{RED}permission denied{RESET}"]

            result = []
            for i, f in enumerate(files[:20]):
                is_last = i == len(files) - 1 and not dirs
                connector = "└── " if is_last else "├── "
                result.append(f"{prefix}{connector}{BLUE}📄{RESET} {f}")

            for i, d in enumerate(dirs[:20]):
                is_last = i == len(dirs) - 1
                connector = "└── " if is_last else "├── "
                result.append(f"{prefix}{connector}{CYAN}📁{RESET}{d}/")
                extension = "    " if is_last else "│   "
                result.extend(_tree(os.path.join(p, d), prefix + extension, depth + 1))

            return result

        tree_lines = _tree(path)
        return "\n".join(tree_lines) or f"{DIM}(empty){RESET}"


class HeadTool(Tool):
    """
    Show the first N lines of a file.

    Displays the beginning of a file with line numbers.

    Parameters:
        path (str): Path to the file (required).
        n (int, optional): Number of lines to show (default: 20).

    Returns:
        str: First N lines of the file with line numbers.

    Example:
        >>> tool = HeadTool()
        >>> result = tool.execute({"path": "large_file.txt", "n": 10})
    """

    def __init__(self):
        super().__init__(
            name="head",
            description="Show first N lines",
            parameters={"path": "string", "n": "number?"},
        )

    def execute(self, args: Dict[str, Any]) -> str:
        path = args["path"]
        n = args.get("n", 20)

        if not os.path.isfile(path):
            return f"{RED}✗{RESET} file not found: {path}"

        try:
            with open(path) as f:
                lines = []
                for _ in range(n):
                    line = f.readline()
                    if not line:
                        break
                    lines.append(line)
        except (IOError, PermissionError) as e:
            return f"{RED}✗{RESET} cannot read {path}: {e}"

        return "".join(f"{DIM}{i + 1:5}{RESET}│ {l}" for i, l in enumerate(lines))


class TailTool(Tool):
    """
    Show the last N lines of a file.

    Displays the end of a file with line numbers.

    Parameters:
        path (str): Path to the file (required).
        n (int, optional): Number of lines to show (default: 20).

    Returns:
        str: Last N lines of the file with line numbers.

    Example:
        >>> tool = TailTool()
        >>> result = tool.execute({"path": "large_file.txt", "n": 10})
    """

    def __init__(self):
        super().__init__(
            name="tail",
            description="Show last N lines",
            parameters={"path": "string", "n": "number?"},
        )

    def execute(self, args: Dict[str, Any]) -> str:
        path = args["path"]
        n = args.get("n", 20)

        if not os.path.isfile(path):
            return f"{RED}✗{RESET} file not found: {path}"

        try:
            from collections import deque

            lines = deque(maxlen=n)
            with open(path) as f:
                for i, line in enumerate(f, 1):
                    lines.append((i, line))
        except (IOError, PermissionError) as e:
            return f"{RED}✗{RESET} cannot read {path}: {e}"

        return "".join(f"{DIM}{line_num:5}{RESET}│ {line}" for line_num, line in lines)


class WcTool(Tool):
    """
    Count lines, words, and characters in a file.

    Displays statistics about a file's content.

    Parameters:
        path (str): Path to the file (required).

    Returns:
        str: Statistics showing line, word, and character counts.

    Example:
        >>> tool = WcTool()
        >>> result = tool.execute({"path": "document.txt"})
    """

    def __init__(self):
        super().__init__(
            name="wc",
            description="Count lines/words/chars",
            parameters={"path": "string"},
        )

    def execute(self, args: Dict[str, Any]) -> str:
        path = args["path"]
        if not os.path.isfile(path):
            return f"{RED}✗{RESET} file not found: {path}"

        try:
            with open(path) as f:
                content = f.read()
        except (IOError, PermissionError) as e:
            return f"{RED}✗{RESET} cannot read {path}: {e}"

        lines = content.count("\n") + 1
        words = len(content.split())
        chars = len(content)

        return f"{DIM}lines: {lines:,} · words: {words:,} · chars: {chars:,}{RESET}"


class PwdTool(Tool):
    """
    Get the current working directory.

    Returns the absolute path of the current working directory.

    Parameters:
        None - this tool takes no parameters.

    Returns:
        str: Current working directory path.

    Example:
        >>> tool = PwdTool()
        >>> result = tool.execute({})
    """

    def __init__(self):
        super().__init__(
            name="pwd",
            description="Get current directory",
            parameters={},
        )

    def execute(self, args: Dict[str, Any]) -> str:
        return os.getcwd()
