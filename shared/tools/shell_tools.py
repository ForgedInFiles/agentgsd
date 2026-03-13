"""
Shell operation tools for AI coding assistants.

This module provides tools for executing shell commands and environment
variable operations. Each tool inherits from the Tool base class and
implements the execute method.

Tools included:
    - BashTool: Run shell command
    - EnvTool: Get environment variable

Example usage:
    from shared.tools.shell_tools import BashTool, EnvTool
    from shared.tools.base import ToolRegistry

    registry = ToolRegistry()
    registry.register(BashTool())
    registry.register(EnvTool())

    result = registry.get("bash").execute({"cmd": "ls -la"})
    result = registry.get("env").execute({"key": "PATH"})
"""

import os
import subprocess
from typing import Any, Dict

from shared.tools.base import Tool
from shared.utils.colors import DIM, GREEN, RED, RESET, YELLOW


class BashTool(Tool):
    """
    Run a shell command.

    Executes a shell command and returns its output. The command is run using
    subprocess with a 60-second timeout. Output is streamed to stdout and
    captured for return.

    Parameters:
        cmd (str): Shell command to execute (required).

    Returns:
        str: Command output, or error message if command fails/times out.

    Example:
        >>> tool = BashTool()
        >>> result = tool.execute({"cmd": "ls -la /tmp"})
        >>> result = tool.execute({"cmd": "git status"})
    """

    def __init__(self):
        super().__init__(
            name="bash",
            description="Run shell command",
            parameters={"cmd": "string"},
        )
        # SECURITY: This tool uses shell=True. Do not pass unsanitized user input
        # to the cmd parameter as it may lead to command injection.

    def execute(self, args: Dict[str, Any]) -> str:
        """Run a shell command.
        
        Args:
            args: Dictionary containing:
                - cmd (str): Shell command to execute (required)
                
        Returns:
            str: Command output, or error message if command fails/times out
            
        Note:
            This tool uses shell=True. Do not pass unsanitized user input
            to the cmd parameter as it may lead to command injection.
        """
        cmd = args["cmd"]
        timeout = 60

        proc = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        if proc.stdout is None:
            proc.kill()
            return f"{RED}✗{RESET} failed to capture stdout"

        output_lines = []
        try:
            while True:
                line = proc.stdout.readline()
                if not line and proc.poll() is not None:
                    break
                if line:
                    print(f"  {DIM}│ {line.rstrip()}{RESET}", flush=True)
                    output_lines.append(line)
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            output_lines.append(f"\n{RED}(timed out after {timeout}s){RESET}")
            return "".join(output_lines).strip() or f"{DIM}(empty output){RESET}"

        output = "".join(output_lines).strip()
        return output if output else f"{DIM}(empty output){RESET}"


class EnvTool(Tool):
    """
    Get environment variable value.

    Retrieves the value of an environment variable. If no key is provided,
    returns all environment variables.

    Parameters:
        key (str, optional): Name of the environment variable to retrieve.
                             If empty, returns all variables.

    Returns:
        str: Value of the environment variable, or error if not set.
             If key is empty, returns all environment variables.

    Example:
        >>> tool = EnvTool()
        >>> result = tool.execute({"key": "PATH"})
        >>> result = tool.execute({"key": "HOME"})
        >>> result = tool.execute({})
    """

    def __init__(self):
        super().__init__(
            name="env",
            description="Get environment variable",
            parameters={"key": "string?"},
        )

    def execute(self, args: Dict[str, Any]) -> str:
        key = args.get("key", "")

        if not key:
            env_vars = []
            for k, v in sorted(os.environ.items()):
                env_vars.append(f"{DIM}{k}{RESET}={v}")
            return "\n".join(env_vars) or f"{DIM}(no variables){RESET}"

        value = os.environ.get(key)
        if value is None:
            return f"{RED}✗{RESET} not set: {key}"

        return value
