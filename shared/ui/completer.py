"""
Command completion for prompt_toolkit integration.

This module contains the CommandCompleter class for intelligent tab-completion
of commands, tools, skills, and file paths in the terminal interface.
"""

import os
from typing import List, Optional

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import HTML

from shared.skills import load_skills
from shared.tools import ToolRegistry


class CommandCompleter(Completer):
    """
    Custom completer for commands, tools, skills, and file paths.

    This completer provides intelligent tab-completion for:
    - Slash commands (/q, /quit, /exit, /c, /clear, /h, /help, /s, /skills, /stats)
    - Tool names (from the provided ToolRegistry)
    - Skill names (loaded via load_skills())
    - File paths (for commands that take path arguments)

    Attributes:
        commands: List of available slash commands
        tools: List of available tool names from registry
        skills: List of available skill names
        registry: Optional ToolRegistry for tool completion

    Example:
        >>> completer = CommandCompleter()
        >>> # Commands complete with /
        >>> document = Document("/q")
        >>> completions = list(completer.get_completions(document, CompleteEvent()))
        >>> completions[0].text
        '/q'

        >>> # Tool names complete after "tool:" or "!"
        >>> document = Document("!read")
        >>> completions = list(completer.get_completions(document, CompleteEvent()))

        >>> # File paths complete for path arguments
        >>> document = Document("read path/to/")
    """

    def __init__(
        self,
        registry: Optional[ToolRegistry] = None,
        commands: Optional[List[str]] = None,
    ):
        """
        Initialize CommandCompleter.

        Args:
            registry: Optional ToolRegistry for tool name completion.
                     If not provided, tools list will be empty.
            commands: Optional custom list of commands.
                     Defaults to standard command list if not provided.
        """
        self.commands = commands or [
            "/q",
            "/quit",
            "/exit",
            "/c",
            "/clear",
            "/h",
            "/help",
            "/s",
            "/skills",
            "/stats",
        ]
        self.registry = registry
        self.tools: List[str] = []
        self.skills: List[str] = []

        if registry:
            self.tools = [tool.name for tool in registry.list_tools()]

        try:
            skills = load_skills()
            self.skills = [skill.name for skill in skills]
        except Exception:
            self.skills = []

    def get_completions(self, document, complete_event):
        """
        Generate completions based on current input context.

        Args:
            document: Document object containing text before cursor
            complete_event: Event that triggered completion

        Yields:
            Completion objects for matching items

        Example:

            >>> completer = CommandCompleter()
            >>> doc = Document("/h")
            >>> event = CompleteEvent()
            >>> for comp in completer.get_completions(doc, event):
            ...     print(comp.text)
            /h
            /help
        """
        text = document.text_before_cursor
        words = text.split()

        # Command completion (starts with /)
        if text.startswith("/"):
            for cmd in self.commands:
                if cmd.startswith(text):
                    yield Completion(
                        cmd,
                        start_position=-len(text),
                        display=HTML(f"<b>{cmd}</b>"),
                        display_meta=self._get_command_meta(cmd),
                    )
            return

        # Tool name completion (after tool: or in tool calls)
        tool_trigger = False
        if text.startswith("!"):
            tool_trigger = True
        elif "tool:" in text.lower():
            tool_trigger = True

        if tool_trigger and self.tools:
            last_word = words[-1] if words else ""
            for tool_name in self.tools:
                if tool_name.startswith(last_word):
                    tool_desc = ""
                    if self.registry and tool_name in self.registry:
                        tool_desc = self.registry.get(tool_name).description
                    yield Completion(
                        tool_name,
                        start_position=-len(last_word),
                        display=HTML(f"<b>{tool_name}</b>"),
                        display_meta=f"Tool: {tool_desc}" if tool_desc else "Tool",
                    )
            return

        # Skill name completion
        if "skill:" in text.lower() or "activate" in text.lower():
            if self.skills:
                last_word = words[-1] if words else ""
                for skill in self.skills:
                    if skill.startswith(last_word):
                        yield Completion(
                            skill,
                            start_position=-len(last_word),
                            display=HTML(f"<b>{skill}</b>"),
                            display_meta="Agent Skill",
                        )
            return

        # File path completion
        if any(kw in text.lower() for kw in ["path:", "read ", "write ", "edit ", "mkdir "]):
            try:
                last_word = words[-1] if words else ""
                if "/" in last_word or last_word.startswith("."):
                    path_prefix = last_word
                    base = os.path.dirname(path_prefix) or "."
                    prefix = os.path.basename(path_prefix)

                    if os.path.isdir(base):
                        for entry in os.listdir(base):
                            if entry.startswith(prefix):
                                full_path = os.path.join(base, entry)
                                if os.path.isdir(full_path):
                                    yield Completion(
                                        full_path + "/",
                                        start_position=-len(path_prefix),
                                        display=HTML(f"<b>{entry}/</b>"),
                                        display_meta="Directory",
                                    )
                                else:
                                    yield Completion(
                                        full_path,
                                        start_position=-len(path_prefix),
                                        display=HTML(f"<b>{entry}</b>"),
                                        display_meta="File",
                                    )
            except (PermissionError, FileNotFoundError, OSError):
                pass

    def _get_command_meta(self, cmd: str) -> str:
        """
        Get metadata description for a command.

        Args:
            cmd: The command to get metadata for

        Returns:
            Description string for the command

        Example:

            >>> completer = CommandCompleter()
            >>> completer._get_command_meta("/q")
            'Quit the application'
        """
        meta = {
            "/q": "Quit the application",
            "/quit": "Quit the application",
            "/exit": "Exit the application",
            "/c": "Clear conversation history",
            "/clear": "Clear conversation history",
            "/h": "Show help",
            "/help": "Show help",
            "/s": "List available skills",
            "/skills": "List available skills",
            "/stats": "Show token statistics",
        }
        return meta.get(cmd, "Command")
