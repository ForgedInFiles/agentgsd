"""
Tools package for AI coding assistants.

This package provides a shared tool system for AI coding assistants in the monorepo.
It includes base classes for defining tools and a registry system for managing them.

Available submodules:
    - base: Tool base class, ToolRegistry, and run_tool function
    - file_tools: File manipulation tools (read, write, edit, mkdir, ls, tree, etc.)
    - search_tools: Search tools (grep, glob, find)
    - shell_tools: Shell operation tools (bash, env)

Example usage:
    from shared.tools.base import Tool, ToolRegistry, run_tool
    from shared.tools.file_tools import ReadTool, WriteTool
    from shared.tools.search_tools import GrepTool
    from shared.tools.shell_tools import BashTool

    # Define a tool
    class ReadTool(Tool):
        def __init__(self):
            super().__init__(
                name="read",
                description="Read file with line numbers",
                parameters={"path": "string", "offset": "number?", "limit": "number?"}
            )

        def execute(self, args):
            with open(args["path"]) as f:
                lines = f.readlines()
            offset = args.get("offset", 0)
            limit = args.get("limit", len(lines))
            return "".join(f"{i+1:4}| {line}" for i, line in enumerate(lines[offset:offset+limit]))

    # Create registry and register tool
    registry = ToolRegistry()
    registry.register(ReadTool())

    # Execute tool
    result = run_tool(registry, "read", {"path": "/path/to/file"})
"""

from shared.tools.base import Tool, ToolRegistry, run_tool

from shared.tools.file_tools import (
    EditTool,
    HeadTool,
    LsTool,
    MkdirTool,
    PwdTool,
    ReadTool,
    TailTool,
    TreeTool,
    WcTool,
    WriteTool,
)
from shared.tools.git_tools import (
    GitAddTool,
    GitBranchTool,
    GitCheckoutTool,
    GitCommitTool,
    GitDiffTool,
    GitLogTool,
    GitPullTool,
    GitPushTool,
    GitResetTool,
    GitStatusTool,
)
from shared.tools.indexer_tools import (
    IndexBuildTool,
    IndexSearchTool,
    IndexStatsTool,
)
from shared.tools.search_tools import FindTool, GlobTool, GrepTool
from shared.tools.shell_tools import BashTool, EnvTool

__all__ = [
    "Tool",
    "ToolRegistry",
    "run_tool",
    "ReadTool",
    "WriteTool",
    "EditTool",
    "MkdirTool",
    "LsTool",
    "TreeTool",
    "HeadTool",
    "TailTool",
    "WcTool",
    "PwdTool",
    "GrepTool",
    "GlobTool",
    "FindTool",
    "BashTool",
    "EnvTool",
    "GitStatusTool",
    "GitDiffTool",
    "GitLogTool",
    "GitBranchTool",
    "GitCommitTool",
    "GitAddTool",
    "GitResetTool",
    "GitCheckoutTool",
    "GitPushTool",
    "GitPullTool",
    "IndexBuildTool",
    "IndexSearchTool",
    "IndexStatsTool",
]
