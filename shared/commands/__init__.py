"""
Custom slash commands loader and management module.

This module provides functionality for discovering, loading, and executing
custom slash commands defined in markdown files. Similar to Claude Code's
custom commands feature.

Commands can be defined in:
- Per-project: .agentgsd/commands/ (in project root)
- Global: ~/.agentgsd/commands/

Command Format (markdown with YAML frontmatter):
    ---
    name: command-name
    description: Human-readable description of the command
    aliases: [alias1, alias2]
    ---

    # Command Instructions
    Your command instructions here...
    Use $ARGUMENTS to include user-provided arguments.
    Use $FILE or $SELECTED_FILES for file context.

Example:
    /test This is my test argument
    → Executes the command with "This is my test argument" as $ARGUMENTS
"""

import os
import re
from typing import List, Optional, Dict, Any


def _get_default_commands_path() -> str:
    """Get the default commands paths (global + package + per-project)."""
    paths = []

    # User's global commands directory
    global_commands = os.path.expanduser("~/.agentgsd/commands")
    paths.append(global_commands)

    # Package-installed commands (relative to this file's location)
    package_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    # Check for commands in the package
    package_commands_paths = [
        os.path.join(package_dir, "commands"),
        os.path.join(package_dir, "packages", "agentgsd", "commands"),
    ]

    for cp in package_commands_paths:
        if os.path.isdir(cp):
            paths.append(cp)

    # Per-project commands directory (current working directory)
    if os.path.isdir("./.agentgsd/commands"):
        paths.append("./.agentgsd/commands")

    return ":".join(paths)


COMMANDS_PATH = os.environ.get("COMMANDS_PATH", _get_default_commands_path())


class Command:
    """
    Represents a custom slash command.

    Commands are defined as markdown files with YAML frontmatter containing
    metadata and instructions for the command execution.

    Attributes:
        name: Unique identifier for the command (without leading slash)
        description: Human-readable description
        aliases: Alternative names for the command
        content: The command instructions (body of the markdown)
        location: File path where the command is defined
        metadata: Additional metadata from frontmatter
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        aliases: Optional[List[str]] = None,
        content: str = "",
        location: str = "",
        metadata: Optional[dict] = None,
    ) -> None:
        """Initialize a Command instance."""
        self.name = name
        self.description = description
        self.aliases = aliases or []
        self.content = content
        self.location = location
        self.metadata = metadata or {}

    @classmethod
    def from_file(cls, filepath: str) -> Optional["Command"]:
        """
        Load a command from a markdown file.

        Args:
            filepath: Path to the command .md file

        Returns:
            Command instance if successfully loaded, None otherwise
        """
        if not os.path.isfile(filepath):
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except (IOError, OSError):
            return None

        # Check for YAML frontmatter
        if not content.startswith("---"):
            # No frontmatter - use filename as name, content as-is
            name = os.path.splitext(os.path.basename(filepath))[0]
            return cls(
                name=name,
                description="",
                content=content.strip(),
                location=filepath,
            )

        parts = content.split("---", 2)
        if len(parts) < 3:
            name = os.path.splitext(os.path.basename(filepath))[0]
            return cls(
                name=name,
                description="",
                content=content.strip(),
                location=filepath,
            )

        yaml_content = parts[1].strip()
        body = parts[2].strip()

        metadata = cls._parse_yaml_frontmatter(yaml_content)

        name = metadata.pop("name", os.path.splitext(os.path.basename(filepath))[0])
        description = metadata.pop("description", "")
        aliases_str = metadata.pop("aliases", "")

        if isinstance(aliases_str, str) and aliases_str.startswith("["):
            aliases = [a.strip().strip("\"'") for a in aliases_str[1:-1].split(",")]
        elif isinstance(aliases_str, list):
            aliases = aliases_str
        else:
            aliases = []

        return cls(
            name=name,
            description=description,
            aliases=aliases,
            content=body,
            location=filepath,
            metadata=metadata,
        )

    @staticmethod
    def _parse_yaml_frontmatter(yaml_content: str) -> dict:
        """Parse simple YAML frontmatter into a dictionary."""
        metadata = {}
        for line in yaml_content.split("\n"):
            line = line.strip()
            if ":" in line and not line.startswith("#"):
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip().strip("\"'")

                if val.startswith("[") and val.endswith("]"):
                    val = [v.strip().strip("\"'") for v in val[1:-1].split(",")]

                metadata[key] = val

        return metadata

    def execute(self, arguments: str = "", selected_files: List[str] = None) -> str:
        """
        Execute the command with given arguments.

        Replaces placeholders in the command content:
        - $ARGUMENTS: User-provided arguments
        - $FILE: First selected file
        - $SELECTED_FILES: All selected files (comma-separated)
        - $FILE_COUNT: Number of selected files

        Args:
            arguments: User-provided arguments after command name
            selected_files: List of currently selected files

        Returns:
            Processed command content with placeholders replaced
        """
        if selected_files is None:
            selected_files = []

        result = self.content

        # Replace placeholders
        result = result.replace("$ARGUMENTS", arguments)
        result = result.replace("$FILE", selected_files[0] if selected_files else "")
        result = result.replace("$SELECTED_FILES", ", ".join(selected_files))
        result = result.replace("$FILE_COUNT", str(len(selected_files)))

        # Add context header
        context_parts = []
        if arguments:
            context_parts.append(f"Arguments: {arguments}")
        if selected_files:
            context_parts.append(f"Selected Files: {', '.join(selected_files)}")

        if context_parts:
            header = "\n".join(context_parts)
            result = f"{header}\n\n{result}"

        return result

    def matches(self, command_input: str) -> bool:
        """
        Check if this command matches the input.

        Args:
            command_input: The command name (with or without leading slash)

        Returns:
            True if matches name or any alias
        """
        cmd = command_input.lstrip("/")
        return cmd == self.name or cmd in self.aliases

    def __repr__(self) -> str:
        return f"Command(name={self.name!r}, description={self.description!r})"

    def __str__(self) -> str:
        return f"/{self.name}: {self.description}"


def load_commands(paths: Optional[List[str]] = None) -> List[Command]:
    """
    Discover and load all commands from the specified paths.

    Searches each path in COMMANDS_PATH (colon-separated) for .md files
    containing valid command definitions.

    Args:
        paths: Optional list of paths to load commands from. If None, uses
               the COMMANDS_PATH environment variable.

    Returns:
        List of loaded Command instances
    """
    commands = []
    seen_commands = set()

    if paths is None:
        path_str = os.environ.get("COMMANDS_PATH", COMMANDS_PATH)
        paths = path_str.split(":") if path_str else []
    elif isinstance(paths, str):
        paths = paths.split(":")

    for base_path in paths:
        base_path = base_path.strip()
        if not base_path or not os.path.isdir(base_path):
            continue

        for entry in os.listdir(base_path):
            if not entry.endswith(".md"):
                continue

            filepath = os.path.join(base_path, entry)
            command = Command.from_file(filepath)

            if command is not None:
                # Skip if we've already loaded a command with this name
                if command.name in seen_commands:
                    continue
                commands.append(command)
                seen_commands.add(command.name)

                # Also track aliases
                for alias in command.aliases:
                    if alias not in seen_commands:
                        seen_commands.add(alias)

    return commands


def get_command(name: str, paths: Optional[List[str]] = None) -> Optional[Command]:
    """
    Get a command by name or alias.

    Args:
        name: Command name (with or without leading slash)
        paths: Optional list of paths to search

    Returns:
        Command instance if found, None otherwise
    """
    commands = load_commands(paths)

    for cmd in commands:
        if cmd.matches(name):
            return cmd

    return None


def execute_command(
    name: str,
    arguments: str = "",
    selected_files: List[str] = None,
    paths: Optional[List[str]] = None,
) -> str:
    """
    Execute a command by name with given arguments.

    Args:
        name: Command name (with or without leading slash)
        arguments: Arguments provided after command name
        selected_files: List of selected files
        paths: Optional list of paths to search

    Returns:
        Processed command content, or error message if not found
    """
    command = get_command(name, paths)

    if command is None:
        return f"error: command '/{name.lstrip('/')}' not found"

    return command.execute(arguments, selected_files)


def commands_list(paths: Optional[List[str]] = None) -> str:
    """
    Generate a formatted list of available commands.

    Args:
        paths: Optional list of paths to search

    Returns:
        Formatted string listing available commands
    """
    commands = load_commands(paths)

    if not commands:
        return (
            "No custom commands found. Add .md files to ~/.agentgsd/commands or .agentgsd/commands/"
        )

    lines = ["Available Commands:"]
    for cmd in commands:
        alias_info = f" (aliases: {', '.join(cmd.aliases)})" if cmd.aliases else ""
        lines.append(f"  /{cmd.name}{alias_info} - {cmd.description}")

    return "\n".join(lines)


__all__ = [
    "Command",
    "load_commands",
    "get_command",
    "execute_command",
    "commands_list",
    "COMMANDS_PATH",
]
