"""
Enhanced UI module for terminal interactions.

This module provides a professional, polished CLI experience similar to
top-tier AI coding assistants like Claude Code, OpenCode, and Pi Agent.

Features:
- Semantic color palette for different message types
- Professional tool call formatting with icons
- Beautiful assistant message blocks with proper framing
- Thought process visualization with streaming
- Rich status indicators and notifications
- Enhanced prompt styling

Example usage:
    from shared.ui.enhanced import (
        print_banner,
        print_tool_call,
        print_assistant_message,
        print_thinking,
        Notification,
    )
"""

import os
import sys
import threading
import time
from typing import Optional, List, Dict, Any

from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

from shared.skills import load_skills
from shared.tools import ToolRegistry


class Colors:
    """Enhanced semantic color palette for professional terminal UI."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    BG_BRIGHT_BLACK = "\033[100m"
    BG_BRIGHT_RED = "\033[101m"
    BG_BRIGHT_GREEN = "\033[102m"
    BG_BRIGHT_YELLOW = "\033[103m"
    BG_BRIGHT_BLUE = "\033[104m"
    BG_BRIGHT_MAGENTA = "\033[105m"
    BG_BRIGHT_CYAN = "\033[106m"
    BG_BRIGHT_WHITE = "\033[107m"

    @classmethod
    def gradient(cls, text: str, colors: List[str]) -> str:
        """Apply gradient coloring to text.

        Args:
            text: Text to gradient
            colors: List of color codes to cycle through

        Returns:
            Gradient-colored text
        """
        if not text:
            return ""
        result = ""
        for i, char in enumerate(text):
            if char.strip():
                result += colors[i % len(colors)] + char
            else:
                result += char
        return result + cls.RESET


class Theme:
    """Professional color theme for the CLI."""

    PRIMARY = Colors.CYAN
    SECONDARY = Colors.BLUE
    ACCENT = Colors.MAGENTA
    SUCCESS = Colors.GREEN
    WARNING = Colors.YELLOW
    ERROR = Colors.RED
    INFO = Colors.BRIGHT_BLUE

    USER_INPUT = Colors.BRIGHT_WHITE
    ASSISTANT = Colors.BRIGHT_CYAN
    TOOL_CALL = Colors.BRIGHT_YELLOW
    TOOL_RESULT = Colors.BRIGHT_BLACK
    THINKING = Colors.MAGENTA

    BORDER = Colors.DIM
    SEPARATOR = Colors.BRIGHT_BLACK

    PROMPT_SYMBOL = Colors.BRIGHT_GREEN + "❯" + Colors.RESET
    PROMPT_SYMBOL_IDLE = Colors.DIM + "❯" + Colors.RESET


class Icons:
    """Professional icon set for different operations."""

    FILE = "📄"
    FOLDER = "📁"
    CODE = "💻"
    GEAR = "⚙️"
    GLOBE = "🌐"
    SEARCH = "🔍"
    PENCIL = "✏️"
    PLUS = "➕"
    TRASH = "🗑️"
    CHECK = "✓"
    CROSS = "✗"
    ARROW_RIGHT = "→"
    ARROW_DOWN = "↓"
    ARROW_UP = "↑"
    STAR = "★"
    SPARKLE = "✨"
    ROCKET = "🚀"
    BRAIN = "🧠"
    LIGHT = "💡"
    WARNING = "⚠️"
    INFO = "ℹ️"
    QUESTION = "❓"

    TOOL_ICONS = {
        "read": "📖",
        "write": "📝",
        "edit": "✏️",
        "mkdir": "📁",
        "ls": "📋",
        "tree": "🌳",
        "glob": "🔎",
        "grep": "🔍",
        "find": "🔎",
        "head": "📰",
        "tail": "📯",
        "wc": "📊",
        "bash": "💻",
        "pwd": "📍",
        "env": "🔧",
        "skill": "🎯",
        "git": "🔀",
        "git_status": "📊",
        "git_diff": "📑",
        "git_log": "📜",
        "git_branch": "🌿",
        "git_commit": "💾",
        "git_push": "⬆️",
        "git_pull": "⬇️",
        "index_build": "🏗️",
        "index_search": "🔎",
        "index_stats": "📈",
        "web_search": "🌐",
        "web_fetch": "📥",
    }

    @classmethod
    def get(cls, name: str, default: str = "⚡") -> str:
        return cls.TOOL_ICONS.get(name.lower(), default)


def get_terminal_width() -> int:
    """Get current terminal width."""
    try:
        return os.get_terminal_size().columns
    except:
        return 80


def separator(char: str = "─", color: str = Colors.DIM, width: int = None) -> str:
    """Create a separator line."""
    if width is None:
        width = get_terminal_width()
    return f"{color}{char * min(width, get_terminal_width())}{Colors.RESET}"


def box(
    text: str,
    title: str = None,
    border_color: str = Colors.DIM,
    width: int = None,
    padding: int = 1,
) -> str:
    """Create a boxed text display.

    Args:
        text: Text to display in the box
        title: Optional title for the box
        border_color: Color for the border
        width: Width of the box
        padding: Padding inside the box

    Returns:
        Formatted boxed text
    """
    if width is None:
        width = min(get_terminal_width() - 4, 80)

    lines = text.split("\n")
    max_len = max(len(line) for line in lines) if lines else 0
    box_width = max(max_len, len(title) if title else 0) + padding * 2 + 2

    border_horiz = border_color + "─" * box_width + Colors.RESET
    border_vert = border_color + "│" + Colors.RESET
    border_corner_tl = border_color + "┌" + Colors.RESET
    border_corner_tr = border_color + "┐" + Colors.RESET
    border_corner_bl = border_color + "└" + Colors.RESET
    border_corner_br = border_color + "┘" + Colors.RESET

    result = []
    result.append(f" {border_corner_tl}{border_horiz[:-1]}{border_corner_tr}")

    if title:
        title_line = f" {border_vert} {Colors.BOLD}{Colors.CYAN}{title.center(box_width - 4)}{Colors.RESET} {border_vert}"
        result.append(title_line)
        result.append(f" {border_vert}{border_horiz}{border_vert}")

    for line in lines:
        padded = line + " " * (box_width - len(line) - padding - 2)
        result.append(f" {border_vert}{' ' * padding}{padded}{' ' * padding}{border_vert}")

    result.append(f" {border_corner_bl}{border_horiz[:-1]}{border_corner_br}")

    return "\n".join(result)


class Notification:
    """Professional notification display."""

    @staticmethod
    def success(message: str, icon: str = Icons.CHECK) -> None:
        print(
            f"\n{Colors.BRIGHT_GREEN}{icon}{Colors.RESET} {Colors.BRIGHT_GREEN}{message}{Colors.RESET}\n"
        )

    @staticmethod
    def error(message: str, icon: str = Icons.CROSS) -> None:
        print(
            f"\n{Colors.BRIGHT_RED}{icon}{Colors.RESET} {Colors.BRIGHT_RED}{message}{Colors.RESET}\n"
        )

    @staticmethod
    def warning(message: str, icon: str = Icons.WARNING) -> None:
        print(
            f"\n{Colors.BRIGHT_YELLOW}{icon}{Colors.RESET} {Colors.BRIGHT_YELLOW}{message}{Colors.RESET}\n"
        )

    @staticmethod
    def info(message: str, icon: str = Icons.INFO) -> None:
        print(
            f"\n{Colors.BRIGHT_CYAN}{icon}{Colors.RESET} {Colors.BRIGHT_CYAN}{message}{Colors.RESET}\n"
        )

    @staticmethod
    def dim(message: str) -> None:
        print(f"\n{Colors.DIM}{message}{Colors.RESET}\n")


class ProgressBar:
    """Professional progress bar for terminal."""

    def __init__(
        self,
        total: int = 100,
        width: int = 40,
        filled_char: str = "█",
        empty_char: str = "░",
        color_filled: str = Colors.CYAN,
        color_empty: str = Colors.DIM,
    ):
        self.total = total
        self.width = width
        self.filled_char = filled_char
        self.empty_char = empty_char
        self.color_filled = color_filled
        self.color_empty = color_empty

    def render(self, current: int, show_pct: bool = True) -> str:
        pct = min(current / self.total, 1.0) if self.total > 0 else 0
        filled = int(self.width * pct)
        empty = self.width - filled

        bar = (
            self.color_filled
            + self.filled_char * filled
            + self.color_empty
            + self.empty_char * empty
            + Colors.RESET
        )

        if show_pct:
            return f"{bar} {Colors.BOLD}{pct * 100:.1f}%{Colors.RESET}"
        return bar


def print_banner(model: str = None, provider: str = None, skills_count: int = None) -> None:
    """Print a professional application banner.

    Args:
        model: Model name to display
        provider: Provider name to display
        skills_count: Number of available skills
    """
    width = get_terminal_width()

    gradient_colors = [Colors.CYAN, Colors.BLUE, Colors.MAGENTA]

    banner_lines = [
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}╭{'─' * min(width - 4, 60)}{Colors.RESET}",
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}│{Colors.RESET} {Colors.BOLD}{Colors.BRIGHT_WHITE}agentgsd{Colors.RESET} {Colors.DIM}•{Colors.RESET} {Colors.BRIGHT_MAGENTA}Elite Coding Assistant{Colors.RESET}",
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}│{Colors.RESET} {Colors.DIM}Local-first, privacy-focused AI developer{Colors.RESET}",
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}├{'─' * min(width - 4, 60)}{Colors.RESET}",
    ]

    info_items = []
    if model:
        model_display = model[:40] + "..." if len(model) > 40 else model
        info_items.append(
            (
                Colors.BRIGHT_YELLOW + "◉" + Colors.RESET,
                f"Model: {Colors.BRIGHT_WHITE}{model_display}{Colors.RESET}",
            )
        )
    if provider:
        info_items.append(
            (
                Colors.BRIGHT_BLUE + "◉" + Colors.RESET,
                f"Provider: {Colors.BRIGHT_WHITE}{provider}{Colors.RESET}",
            )
        )
    if skills_count is not None:
        info_items.append(
            (
                Colors.BRIGHT_GREEN + "◉" + Colors.RESET,
                f"Skills: {Colors.BRIGHT_WHITE}{skills_count}{Colors.RESET}",
            )
        )

    for i, (icon, text) in enumerate(info_items):
        banner_lines.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}│{Colors.RESET} {icon} {text}")

    banner_lines.append(
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}├{'─' * min(width - 4, 60)}{Colors.RESET}"
    )

    commands = [
        (Colors.YELLOW + "/q" + Colors.RESET, "quit"),
        (Colors.YELLOW + "/c" + Colors.RESET, "clear"),
        (Colors.YELLOW + "/s" + Colors.RESET, "skills"),
        (Colors.YELLOW + "/stats" + Colors.RESET, "tokens"),
        (Colors.YELLOW + "/h" + Colors.RESET, "help"),
    ]

    cmd_str = "  ".join([f"{cmd} {Colors.DIM}{desc}{Colors.RESET}" for cmd, desc in commands])
    banner_lines.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}│{Colors.RESET} {cmd_str}")
    banner_lines.append(
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}╰{'─' * min(width - 4, 60)}{Colors.RESET}"
    )

    print("\n" + "\n".join(banner_lines) + "\n")


def print_assistant_message(content: str, show_avatar: bool = True) -> None:
    """Print assistant message with beautiful framing.

    Args:
        content: Message content to display
        show_avatar: Whether to show assistant avatar
    """
    avatar = f"{Colors.BRIGHT_CYAN} assistant{Colors.RESET} "
    lines = content.split("\n")

    width = min(get_terminal_width() - 4, 80)

    header = f"{Colors.BRIGHT_CYAN}┌─{Colors.DIM} assistant{Colors.RESET}"
    print(f"\n{header}")

    for line in lines[:50]:
        print(f"{Colors.BRIGHT_CYAN}│{Colors.RESET} {line}")

    if len(lines) > 50:
        print(
            f"{Colors.BRIGHT_CYAN}│{Colors.RESET} {Colors.DIM}... ({len(lines) - 50} more lines){Colors.RESET}"
        )

    print(f"{Colors.BRIGHT_CYAN}└{'─' * (width - 1)}{Colors.RESET}")


def print_tool_call(name: str, args: dict = None) -> None:
    """Print tool call with color-coded formatting.

    Args:
        name: Tool name
        args: Tool arguments
    """
    if args is None:
        args = {}

    icon = Icons.get(name)
    args_str = ""

    if args:
        arg_items = []
        for k, v in list(args.items())[:3]:
            v_str = str(v)[:40]
            arg_items.append(
                f"{Colors.DIM}{k}{Colors.RESET}={Colors.BRIGHT_YELLOW}{v_str}{Colors.RESET}"
            )
        args_str = f"({', '.join(arg_items)})"
        if len(args) > 3:
            args_str += f" {Colors.DIM}+{len(args) - 3} more{Colors.RESET}"

    print(f"\n{Colors.BRIGHT_YELLOW}{icon} {Colors.BOLD}{name.upper()}{Colors.RESET}{args_str}")


def print_tool_result(result: str, max_lines: int = 30, max_width: int = 80) -> None:
    """Print tool result with formatted display.

    Args:
        result: Tool result string
        max_lines: Maximum lines to display
        max_width: Maximum line width
    """
    lines = result.split("\n")
    display_lines = lines[:max_lines]

    for line in display_lines:
        if len(line) > max_width:
            line = line[: max_width - 3] + "..."
        print(f"  {Colors.DIM}│{Colors.RESET} {Colors.BRIGHT_BLACK}{line}{Colors.RESET}")

    if len(lines) > max_lines:
        print(
            f"  {Colors.DIM}│{Colors.RESET} {Colors.DIM}... ({len(lines) - max_lines} more lines){Colors.RESET}"
        )


class ThinkingSpinner:
    """Animated thinking spinner with multiple frames."""

    FRAMES = [
        "   ",
        "·  ",
        "·· ",
        "···",
        " ··",
        "  ·",
    ]

    THOUGHT_FRAMES = [
        "💭 ",
        "💭·",
        "💭··",
        "💭···",
        "💭··",
        "💭·",
    ]

    def __init__(self, message: str = "Thinking", color: str = Colors.MAGENTA):
        self.message = message
        self.color = color
        self.running = False
        self.thread = None

    def _spin(self):
        i = 0
        while self.running:
            frame = self.THOUGHT_FRAMES[i % len(self.THOUGHT_FRAMES)]
            sys.stdout.write(f"\r{self.color}{frame}{Colors.RESET} {self.message}")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
        sys.stdout.flush()

    def start(self, message: str = None):
        if message:
            self.message = message
        self.running = True
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()
        return self

    def stop(self, final: str = ""):
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.5)
        if final:
            print(f"{final}")


class StreamingText:
    """Stream text character by character for effect."""

    def __init__(self, text: str, delay: float = 0.01, color: str = Colors.RESET):
        self.text = text
        self.delay = delay
        self.color = color

    def render(self):
        for char in self.text:
            sys.stdout.write(f"{self.color}{char}{Colors.RESET}")
            sys.stdout.flush()
            time.sleep(self.delay)
        print()


def format_tokens(n: int) -> str:
    """Format token count with K suffix."""
    if n >= 1000000:
        return f"{n / 1000000:.1f}M"
    elif n >= 1000:
        return f"{n / 1000:.1f}K"
    return str(n)


def context_bar(current: int, max_val: int, width: int = 20) -> str:
    """Draw a context usage bar with color coding."""
    if max_val == 0:
        return ""
    pct = min(current / max_val, 1.0)
    filled = int(width * pct)
    empty = width - filled

    if pct < 0.5:
        color = Colors.BRIGHT_GREEN
    elif pct < 0.8:
        Colors.BRIGHT_YELLOW
    else:
        color = Colors.BRIGHT_RED

    return f"{color}{'█' * filled}{Colors.DIM}{'░' * empty}{Colors.RESET}"


def print_stats(stats: dict, context_window: int = 200000) -> None:
    """Print token statistics with visual bar.

    Args:
        stats: Dictionary with 'input', 'output', 'total' token counts
        context_window: Maximum context window size
    """
    if not stats:
        return

    pct = (stats["total"] / context_window * 100) if context_window else 0
    bar = context_bar(stats["total"], context_window, width=15)

    stats_str = (
        f"{Colors.DIM}│{Colors.RESET} "
        f"{Colors.BRIGHT_BLUE}token usage{Colors.RESET} "
        f"in:{Colors.BRIGHT_WHITE}{format_tokens(stats.get('input', 0))}{Colors.RESET} "
        f"out:{Colors.BRIGHT_WHITE}{format_tokens(stats.get('output', 0))}{Colors.RESET} "
        f"total:{Colors.BRIGHT_WHITE}{format_tokens(stats.get('total', 0))}{Colors.RESET} "
        f"ctx:{Colors.BRIGHT_YELLOW}{pct:.0f}%{Colors.RESET} "
        f"{bar}"
    )
    print(stats_str)


def print_separator(style: str = "light", color: str = None) -> None:
    """Print a styled separator.

    Args:
        style: 'light', 'heavy', 'double', 'dotted'
        color: Optional color override
    """
    width = get_terminal_width()

    chars = {
        "light": "─",
        "heavy": "━",
        "double": "═",
        "dotted": "┅",
        "corner": "┌┐└┘├┤┬┴┼",
    }

    char = chars.get(style, "─")
    if color is None:
        color = Colors.DIM

    print(f"{color}{char * min(width, 80)}{Colors.RESET}")


class EnhancedPrompt:
    """Enhanced prompt configuration."""

    @staticmethod
    def get_style() -> Style:
        """Get the enhanced prompt_toolkit style."""
        return Style.from_dict(
            {
                "prompt": "fg:#50fa7b bold",
                "prompt.arg": "fg:#f1fa8c",
                "prompt.tool": "fg:#ff79c6",
                "prompt.skill": "fg:#8be9fd",
                "completion-menu.completion": "bg:#282a36 fg:#f8f8f2",
                "completion-menu.completion.current": "bg:#44475a fg:#f8f8f2",
                "completion-menu.meta.completion": "bg:#44475a fg:#6272a4",
                "completion-menu.meta.completion.current": "bg:#6272a4 fg:#f8f8f2",
                "toolbar": "bg:#282a36 fg:#f8f8f2",
                "status": "bg:#44475a fg:#f8f8f2",
            }
        )

    @staticmethod
    def get_prompt_tokens():
        """Get prompt tokens for prompt_toolkit."""
        return [
            ("class:prompt", Theme.PROMPT_SYMBOL),
            ("class:prompt", " "),
        ]


def create_keybindings() -> KeyBindings:
    """Create key bindings for the prompt."""
    kb = KeyBindings()

    @kb.add("c-c")
    def _(event):
        event.app.exit(exception=KeyboardInterrupt)

    @kb.add("c-d")
    def _(event):
        event.app.exit()

    return kb


def print_welcome_message(model: str = None) -> None:
    """Print welcome message with helpful tips."""
    width = get_terminal_width()

    print(f"\n{Colors.BRIGHT_CYAN}{'═' * min(width, 60)}{Colors.RESET}")
    print(
        f"{Colors.BRIGHT_CYAN}  Welcome to {Colors.BRIGHT_WHITE}agentgsd{Colors.RESET}{Colors.BRIGHT_CYAN}!{Colors.RESET}"
    )
    print(f"{Colors.BRIGHT_CYAN}{'═' * min(width, 60)}{Colors.RESET}")

    print(f"\n{Colors.DIM}Quick start:{Colors.RESET}")
    tips = [
        ("Describe your task", "I'll help you write, edit, or understand code"),
        ("Use /help", "See all available commands"),
        ("Use Tab", "Autocomplete commands and file paths"),
    ]

    for tip, desc in tips:
        print(f"  {Colors.BRIGHT_YELLOW}•{Colors.RESET} {Colors.BOLD}{tip}{Colors.RESET}")
        print(f"    {Colors.DIM}{desc}{Colors.RESET}")

    print(f"\n{Colors.BRIGHT_CYAN}{'─' * min(width, 60)}{Colors.RESET}\n")


def print_help_detailed(commands: List[Any] = None) -> None:
    """Print detailed help information."""
    width = get_terminal_width()

    print(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}agentgsd Help{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}{'═' * min(width - 10, 50)}{Colors.RESET}\n")

    sections = [
        (
            "Commands",
            [
                ("/q, /quit, /exit", "Exit the application"),
                ("/c, /clear", "Clear conversation history"),
                ("/h, /help", "Show this help message"),
                ("/s, /skills", "List available skills"),
                ("/cmds, /commands", "List custom commands"),
                ("/stats", "Show token usage statistics"),
                ("/compact", "Compact conversation to save context"),
            ],
        ),
        (
            "Key Bindings",
            [
                ("Tab", "Trigger autocomplete"),
                ("Ctrl+C", "Cancel current input"),
                ("Ctrl+D", "Quit application"),
            ],
        ),
    ]

    for section_name, items in sections:
        print(f"{Colors.BOLD}{Colors.BRIGHT_YELLOW}{section_name}:{Colors.RESET}")
        for cmd, desc in items:
            print(f"  {Colors.BRIGHT_CYAN}{cmd:20}{Colors.RESET} {desc}")
        print()

    # Show custom commands if any exist
    if commands:
        print(f"{Colors.BOLD}{Colors.BRIGHT_YELLOW}Custom Commands:{Colors.RESET}")
        for cmd in commands:
            alias_info = f" ({', '.join(['/' + a for a in cmd.aliases])})" if cmd.aliases else ""
            print(
                f"  {Colors.BRIGHT_CYAN}/{cmd.name}{alias_info:25}{Colors.RESET} {cmd.description}"
            )
        print()

    print(f"{Colors.BRIGHT_CYAN}{'─' * min(width - 10, 50)}{Colors.RESET}\n")


def print_skills_list(skills: List[Any]) -> None:
    """Print available skills in a formatted list."""
    if not skills:
        print(
            f"\n{Colors.DIM}No skills loaded. Set SKILLS_PATH environment variable.{Colors.RESET}\n"
        )
        return

    print(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}Available Skills{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}{'─' * 40}{Colors.RESET}\n")

    for skill in skills:
        name = f"{Colors.BRIGHT_GREEN}{skill.name}{Colors.RESET}"
        desc = f"{Colors.DIM}{skill.description}{Colors.RESET}"
        print(f"  {Icons.SPARKLE} {name:20} {desc}")

    print()


__all__ = [
    "Colors",
    "Theme",
    "Icons",
    "Notification",
    "ProgressBar",
    "box",
    "separator",
    "print_banner",
    "print_assistant_message",
    "print_tool_call",
    "print_tool_result",
    "ThinkingSpinner",
    "StreamingText",
    "print_stats",
    "print_separator",
    "print_welcome_message",
    "print_help_detailed",
    "print_skills_list",
    "format_tokens",
    "context_bar",
    "create_keybindings",
    "EnhancedPrompt",
]
