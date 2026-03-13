"""
UI components for terminal interactions and prompt_toolkit integration.

This module provides the core UI functionality for building terminal-based
AI coding assistants. It includes:
- CommandCompleter: Custom completer for commands, tools, skills, and file paths
- Key binding creation and management
- Help and command popup displays
- Tool call and result formatting utilities
- Token statistics display

Example:
    >>> from shared.ui.prompts import CommandCompleter, get_prompt_config
    >>>
    >>> # Create prompt configuration with completion
    >>> config = get_prompt_config()
    >>> print(config)
    {'completer': ..., 'complete_style': ..., ...}

    >>> # Use the completer directly
    >>> completer = CommandCompleter()
    >>> for completion in completer.get_completions(document, event):
    ...     print(completion.text)
"""

import os
from typing import List, Optional

from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion, FuzzyCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

from shared.skills import load_skills
from shared.tools import ToolRegistry
from shared.ui.keybindings import create_keybindings
from shared.utils.colors import (
    BOLD,
    CYAN,
    DIM,
    GREEN,
    MAGENTA,
    RED,
    RESET,
    YELLOW,
)

# Token tracking - can be passed in or use module-level default
_token_stats = {"input": 0, "output": 0, "total": 0}

# Default model context (can be overridden)
MODEL_CONTEXT = 200000

# Custom style for prompt_toolkit
style = Style.from_dict(
    {
        "completion-menu.completion": "bg:#008888 #ffffff",
        "completion-menu.completion.current": "bg:#00aaaa #000000",
        "completion-menu.meta.completion": "bg:#008888 #ffffff",
        "completion-menu.meta.completion.current": "bg:#00aaaa #000000",
        "toolbar": "bg:#222222 #ffffff",
        "status": "bg:#333333 #ffffff",
    }
)


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


def show_commands_popup(app) -> None:
    """
    Show a popup with all available commands, tools, and skills.

    Displays a quick reference panel with:
    - Available slash commands
    - Available tools from registry
    - Available skills (if any are loaded)

    Args:
        app: The prompt_toolkit Application instance (can be None)

    Example:
        >>> # Show commands popup
        >>> show_commands_popup(app)

        >>> # Can also be called with None
        >>> show_commands_popup(None)

        Quick Reference:
        /q quit  /c clear  /stats tokens  /h help
        Tab autocomplete  Ctrl+P commands popup  F1 help
    """
    skills = load_skills()

    # Try to get tools from registry if available
    tools_info = []
    try:
        from shared.tools import ToolRegistry

        registry = ToolRegistry()
        # Register default tools
        from shared.tools import (
            BashTool,
            EditTool,
            FindTool,
            GlobTool,
            GrepTool,
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

        for tool_cls in [
            ReadTool,
            WriteTool,
            EditTool,
            MkdirTool,
            LsTool,
            TreeTool,
            HeadTool,
            TailTool,
            WcTool,
            GrepTool,
            GlobTool,
            FindTool,
            BashTool,
            PwdTool,
        ]:
            try:
                registry.register(tool_cls())
            except ValueError:
                pass

        tools_info = [(t.name, t.description) for t in registry.list_tools()]
    except Exception:
        # Fallback to empty list
        tools_info = []

    commands_text = [
        ("class:toolbar", " Available Commands "),
        ("", "\n"),
        ("class:command", "  /q, /quit, /exit  "),
        ("", "    Quit the application\n"),
        ("class:command", "  /c, /clear        "),
        ("", "    Clear conversation & reset tokens\n"),
        ("class:command", "  /h, /help         "),
        ("", "    Show this help message\n"),
        ("class:command", "  /s, /skills       "),
        ("", "    List available skills\n"),
        ("class:command", "  /stats            "),
        ("", "    Show token statistics\n"),
        ("", "\n"),
        ("class:toolbar", " Available Tools "),
        ("", "\n"),
    ]

    for tool_name, desc in sorted(tools_info):
        commands_text.append(("class:tool", f"  {tool_name:15} "))
        commands_text.append(("", f"{desc[:50]}\n"))

    if skills:
        commands_text.extend(
            [
                ("", "\n"),
                ("class:toolbar", " Available Skills "),
                ("", "\n"),
            ]
        )
        for skill in skills:
            commands_text.append(("class:skill", f"  {skill.name:20} "))
            commands_text.append(("", f"{skill.description[:40]}\n"))

    commands_text.append(("", "\n Press F1 for detailed help • Ctrl+P to show this popup"))

    # Print simple text version
    separator_line = "─" * min(os.get_terminal_size().columns, 120)
    print("\n" + f"{CYAN}{separator_line}{RESET}")
    print(f"{BOLD}Quick Reference:{RESET}")
    print(
        f"  {YELLOW}/q{RESET} quit  {YELLOW}/c{RESET} clear  {YELLOW}/stats{RESET} tokens  {YELLOW}/h{RESET} help"
    )
    print(
        f"  {CYAN}Tab{RESET} autocomplete  {CYAN}Ctrl+P{RESET} commands popup  {CYAN}F1{RESET} help"
    )
    print(f"{CYAN}{separator_line}{RESET}")


def show_help_popup(app) -> None:
    """
    Show detailed help information.

    Displays comprehensive help including:
    - All available commands with descriptions
    - Key binding reference
    - Available tools
    - Loaded skills (if any)

    Args:
        app: The prompt_toolkit Application instance (can be None)

    Example:
        >>> # Show detailed help
        >>> show_help_popup(app)

        ═════════════════════════════════════════════════════
        agentgsd - Help & Documentation
        ═════════════════════════════════════════════════════

        Commands:
          /q, /quit, /exit  - Quit the application
          ...
    """
    separator_line = "═" * min(os.get_terminal_size().columns, 120)

    # Try to get tools
    tools_info = []
    try:
        from shared.tools import ToolRegistry

        registry = ToolRegistry()
        from shared.tools import (
            BashTool,
            EditTool,
            FindTool,
            GlobTool,
            GrepTool,
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

        for tool_cls in [
            ReadTool,
            WriteTool,
            EditTool,
            MkdirTool,
            LsTool,
            TreeTool,
            HeadTool,
            TailTool,
            WcTool,
            GrepTool,
            GlobTool,
            FindTool,
            BashTool,
            PwdTool,
        ]:
            try:
                registry.register(tool_cls())
            except ValueError:
                pass

        tools_info = [(t.name, t.description) for t in registry.list_tools()]
    except Exception:
        tools_info = []

    help_text = f"""
{separator_line}
{BOLD}Help & Documentation{RESET}
{separator_line}

{BOLD}Commands:{RESET}
  {YELLOW}/q, /quit, /exit{RESET}  - Quit the application
  {YELLOW}/c, /clear{RESET}        - Clear conversation history & reset tokens
  {YELLOW}/h, /help{RESET}         - Show this help message
  {YELLOW}/s, /skills{RESET}       - List available skills
  {YELLOW}/stats{RESET}            - Show token statistics

{BOLD}Key Bindings:{RESET}
  {CYAN}Tab{RESET}                 - Trigger autocomplete
  {CYAN}Ctrl+P{RESET}              - Show commands popup
  {CYAN}F1{RESET}                  - Show this help
  {CYAN}Ctrl+C{RESET}              - Cancel current input
  {CYAN}Ctrl+D{RESET}              - Quit

{BOLD}Available Tools:{RESET}
"""
    for tool_name, desc in sorted(tools_info):
        help_text += f"  {CYAN}{tool_name:15}{RESET} {desc}\n"

    skills = load_skills()
    if skills:
        help_text += f"\n{BOLD}Loaded Skills:{RESET}\n"
        for skill in skills:
            help_text += f"  {GREEN}{skill.name:20}{RESET} {skill.description}\n"

    help_text += f"\n{separator_line}"

    print(help_text)


def get_prompt_config(
    registry: Optional[ToolRegistry] = None,
    history_path: Optional[str] = None,
) -> dict:
    """
    Get prompt_toolkit configuration with completion support.

    Creates a complete configuration dictionary for use with prompt_toolkit's
    prompt() function. Includes:
    - Fuzzy command completer
    - Auto-suggest from history
    - File-based history
    - Custom key bindings
    - Styled completion menu

    Args:
        registry: Optional ToolRegistry for tool completion.
                 If not provided, uses default tools.
        history_path: Optional path to history file.
                     Defaults to ~/.agentgsd_history

    Returns:
        Dictionary with prompt_toolkit configuration options:
        - completer: FuzzyCompleter wrapping CommandCompleter
        - complete_style: Style for completion menu
        - auto_suggest: AutoSuggestFromHistory instance
        - history: FileHistory instance
        - key_bindings: KeyBindings from create_keybindings()
        - style: Custom prompt_toolkit Style
        - multiline: Boolean (False)

    Example:
        >>> # Basic usage
        >>> config = get_prompt_config()
        >>> user_input = prompt(">>> ", **config)

        >>> # With custom registry
        >>> registry = ToolRegistry()
        >>> registry.register(MyTool())
        >>> config = get_prompt_config(registry=registry)
        >>> user_input = prompt(">>> ", **config)

        >>> # With custom history
        >>> config = get_prompt_config(history_path="/tmp/my_history")
    """
    kb = create_keybindings()
    completer = FuzzyCompleter(CommandCompleter(registry=registry))

    if history_path is None:
        history_path = os.path.expanduser("~/.agentgsd_history")

    os.makedirs(os.path.dirname(history_path), exist_ok=True)

    return {
        "completer": completer,
        "complete_style": style,
        "auto_suggest": AutoSuggestFromHistory(),
        "history": FileHistory(history_path),
        "key_bindings": kb,
        "style": style,
        "multiline": False,
    }


def print_banner(
    current_dir: Optional[str] = None,
    skills_available: bool = True,
    model: Optional[str] = None,
) -> None:
    """
    Print the application banner.

    Displays an ASCII art banner with:
    - Application name/logo
    - Current working directory
    - Powered by information
    - Available commands quick reference

    Args:
        current_dir: Optional current directory to display.
                    Defaults to os.getcwd()
        skills_available: Whether skills are available.
                         Shows "Skills Available" in green if True.
        model: Optional model name to display in the banner.

    Example:
        >>> # Default banner
        >>> print_banner()

          ░░      ▓▓▓▓      ▓▓▓        ░░   ▓▓▓  ░░
          ...

        >>> # Custom directory
        >>> print_banner("/home/user/project")

        >>> # No skills
        >>> print_banner(skills_available=False)

        >>> # With model
        >>> print_banner(model="nvidia/nemotron-3-super-120b-a12b:free")
    """
    if current_dir is None:
        current_dir = os.getcwd()

    try:
        width = os.get_terminal_size().columns
    except:
        width = 80

    separator = "─" * min(width, 120)
    bg_dim = "\033[100m"

    skills_status = (
        f"{GREEN}Skills Available{RESET}{DIM}" if skills_available else f"{DIM}No Skills{RESET}"
    )
    model_status = f"{YELLOW}{model}{RESET}{DIM}" if model else f"{DIM}No Model{RESET}"

    print(f"""
{BOLD}{CYAN}
 (`-')  _            (`-')  _<-. (`-')_ (`-')                (`-').->_(`-')    
 (OO ).-/     .->    ( OO).-/   \( OO) )( OO).->      .->    ( OO)_ ( (OO ).-> 
 / ,---.   ,---(`-')(,------.,--./ ,--/ /    '._   ,---(`-')(_)--\_) \    .'_  
 | \ /`.\ '  .-(OO ) |  .---'|   \ |  | |'--...__)'  .-(OO )/    _ / '`'-..__) 
 '-'|_.' ||  | .-, \(|  '--. |  . '|  |)`--.  .--'|  | .-, \\_..`--. |  |  ' | 
(|  .-.  ||  | '.(_/ |  .--' |  |\    |    |  |   |  | '.(_/.-._)   \|  |  / : 
 |  | |  ||  '-'  |  |  `---.|  | \   |    |  |   |  '-'  | \       /|  '-'  / 
 `--' `--' `-----'   `------'`--'  `--'    `--'    `-----'   `-----' `------'  
   {DIM}  Coding Assistant
   {separator}
   {DIM}  📂 {current_dir}
     🧠 Powered by OpenRouter · {model_status} · {skills_status}{DIM}
     {YELLOW}/q{RESET}{DIM} quit · {YELLOW}/c{RESET}{DIM} clear · {YELLOW}/s{RESET}{DIM} skills · {YELLOW}/stats{RESET}{DIM} tokens{RESET}
   {separator}
 """)


def print_tool_call(name: str, args: dict) -> None:
    """
    Print a tool call with styled icon and preview.

    Displays a formatted tool invocation with:
    - Icon based on tool name (e.g., 📖 for read, ✍️ for write)
    - Tool name in uppercase
    - Preview of first argument (truncated to 50 chars)

    Args:
        name: Name of the tool being called
        args: Dictionary of arguments passed to the tool

    Example:
        >>> print_tool_call("read", {"path": "/home/user/file.txt"})

        📖 READ(path=/home/user/file.txt)

        >>> print_tool_call("bash", {"cmd": "ls -la"})

        💻 BASH(cmd=ls -la)
    """
    arg_preview = str(list(args.values())[0])[:50] if args else ""

    icons = {
        "read": "📖",
        "write": "✍️",
        "edit": "✏️",
        "append": "➕",
        "prepend": "⏪",
        "delete": "🗑️",
        "mkdir": "📁",
        "ls": "📋",
        "tree": "🌳",
        "glob": "🔍",
        "grep": "🔎",
        "find": "🔎",
        "head": "📰",
        "tail": "📯",
        "wc": "📊",
        "bash": "💻",
        "pwd": "📍",
        "env": "🔧",
        "skill": "🎯",
        "skills_list": "📚",
    }

    icon = icons.get(name, "🔧")
    print(f"\n{GREEN}{icon} {name.upper()}{RESET}({DIM}{arg_preview}{RESET})")


def print_tool_result(result: str) -> None:
    """
    Print a tool result with preview.

    Displays the tool's return value with:
    - First line truncated to 70 characters
    - Line count indicator if more than 1 line
    - Truncation indicator if first line exceeds 70 chars

    Args:
        result: The result string from tool execution

    Example:
        >>> print_tool_result("File content line 1")

          └─  File content line 1

        >>> print_tool_result("Line 1\\nLine 2\\nLine 3")

          └─  Line 1 ... +2 lines
    """
    result_lines = result.split("\n")
    preview = result_lines[0][:70]

    if len(result_lines) > 1:
        preview += f" {DIM}... +{len(result_lines) - 1} lines{RESET}"
    elif len(result_lines[0]) > 70:
        preview += "..."

    print(f"  {DIM}└─{RESET}  {preview}")


def format_tokens(n: int) -> str:
    """
    Format token count with K suffix.

    Args:
        n: Number of tokens

    Returns:
        String representation with K suffix for thousands

    Example:
        >>> format_tokens(500)
        '500'
        >>> format_tokens(1500)
        '1.5K'
        >>> format_tokens(10000)
        '10.0K'
    """
    if n >= 1000:
        return f"{n / 1000:.1f}K"
    return str(n)


def context_bar(current: int, max_val: int, width: int = 30) -> str:
    """
    Draw a context usage bar.

    Creates a visual progress bar showing token usage:
    - Green when < 50% full
    - Yellow when 50-80% full
    - Red when > 80% full

    Args:
        current: Current token count
        max_val: Maximum token context
        width: Width of the bar in characters (default 30)

    Returns:
        Formatted string with the bar visualization

    Example:
        >>> context_bar(50000, 200000)
        '████████████████░░░░░░░░░░░░░░░░░'
        >>> context_bar(150000, 200000)
        '███████████████████████████████░░░'
    """
    pct = min(current / max_val, 1.0)
    filled = int(width * pct)
    empty = width - filled
    color = GREEN if pct < 0.5 else YELLOW if pct < 0.8 else RED
    return f"{color}{'█' * filled}{DIM}{'░' * empty}{RESET}"


def print_stats(
    stats: Optional[dict] = None,
    model_context: int = MODEL_CONTEXT,
) -> None:
    """
    Print token statistics.

    Displays token usage statistics including:
    - Input tokens
    - Output tokens
    - Total tokens with percentage of context used
    - Visual context bar

    Args:
        stats: Optional dictionary with token stats.
              Defaults to module-level _token_stats.
              Expected keys: 'input', 'output', 'total'
        model_context: The model's context window size.
                     Defaults to 200000.

    Example:
        >>> print_stats()

          │ 📊 In:1.5K · Out:0.5K · Ctx:1.0% ████░░░░░░░░░░░░░░░░░░░░░░░░

        >>> print_stats({"input": 1000, "output": 500, "total": 1500}, 100000)

          │ 📊 In:1.0K · Out:0.5K · Ctx:1.5% █████░░░░░░░░░░░░░░░░░░░░░░░
    """
    if stats is None:
        stats = _token_stats

    pct = (stats["total"] / model_context * 100) if model_context else 0
    bar = context_bar(stats["total"], model_context)

    stats_str = f"  {DIM}│{RESET} 📊 {BOLD}In:{format_tokens(stats['input'])}{RESET} {DIM}·{RESET} {BOLD}Out:{format_tokens(stats['output'])}{RESET} {DIM}·{RESET} {BOLD}Ctx:{pct:.1f}%{RESET} {bar}"
    print(stats_str)


def update_token_stats(input_tokens: int, output_tokens: int) -> None:
    """
    Update the module-level token statistics.

    Args:
        input_tokens: Number of input tokens to add
        output_tokens: Number of output tokens to add

    Example:
        >>> update_token_stats(1000, 500)
        >>> # Module stats now reflect the increase
        >>> print_stats()
    """
    global _token_stats
    _token_stats["input"] += input_tokens
    _token_stats["output"] += output_tokens
    _token_stats["total"] = _token_stats["input"] + _token_stats["output"]


def reset_token_stats() -> None:
    """
    Reset token statistics to zero.

    Example:
        >>> reset_token_stats()
        >>> print_stats()
          │ 📊 In:0 · Out:0 · Ctx:0.0% ░░░░░░░░░░░░░░░░░░░░░░░░░░
    """
    global _token_stats
    _token_stats = {"input": 0, "output": 0, "total": 0}


# Import FileHistory at module level for get_prompt_config
from prompt_toolkit.history import FileHistory
