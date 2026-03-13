"""
UI layout and formatting utilities for prompt_toolkit integration.

This module contains functions for creating UI layouts, banners, popups,
and other visual elements for the terminal-based AI coding assistant.
"""

import os
from typing import Optional

from shared.utils.colors import (
    BOLD,
    CYAN,
    DIM,
    GREEN,
    RED,
    RESET,
    YELLOW,
)


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

        >>> # Custom banner
        >>> print_banner(current_dir="/home/user/project", model="claude-3")
    """
    if current_dir is None:
        current_dir = os.getcwd()

    banner = f"""
{BOLD}  _   _      _ _         __        __         _     _ _ _    {RESET}
{BOLD} | | | | ___| | | ___    \\ \\      / /__  ____| | __| | | |   {RESET}
{BOLD} | |_| |/ _ \\ | |/ _ \\    \\ \\ /\\ / / _ \\/ __| |/ _` | | |   {RESET}
{BOLD} |  _  |  __/ | | (_) |    \\ V  V /  __/ (__| | (_| | | |   {RESET}
{BOLD} |_| |_|\\___|_|_|\\___/      \\_/\\_/ \\___|\\___|_|\\__,_|_|_|   {RESET}
{BOLD}                                                                {RESET}
  {DIM}Elite Coding Assistant{RESET}
    """

    print(banner)

    # Current directory and model info
    dir_info = f"{CYAN}📁 {current_dir}{RESET}"
    if model:
        dir_info += f" {DIM}·{RESET} {YELLOW}🤖 {model}{RESET}"
    print(dir_info)

    # Skills status
    skills_status = (
        f"{GREEN}✓ Skills Available{RESET}"
        if skills_available
        else f"{RED}✗ Skills Not Available{RESET}"
    )
    print(f"  {skills_status}")

    # Quick reference
    print(
        f"  {YELLOW}/q{RESET} quit  {YELLOW}/c{RESET} clear  {YELLOW}/stats{RESET} tokens  {YELLOW}/h{RESET} help"
    )
    print()


def print_tool_call(tool_name: str, tool_args: dict) -> None:
    """
    Print formatted tool call information.

    Args:
        tool_name: Name of the tool being called
        tool_args: Arguments passed to the tool
    """
    from shared.utils.colors import CYAN

    args_str = ", ".join(f"{k}={v!r}" for k, v in tool_args.items())
    print(f"  {CYAN}⚡{RESET} {tool_name}({args_str})")


def print_tool_result(result: str) -> None:
    """
    Print formatted tool result.

    Args:
        result: Result string from tool execution
    """
    from shared.utils.colors import GREEN

    # Truncate long results for display
    if len(result) > 100:
        display_result = result[:97] + "..."
    else:
        display_result = result
    print(f"  {GREEN}✓{RESET} {display_result}")


def print_stats(token_stats: dict, context_window: int) -> None:
    """
    Print token statistics.

    Args:
        token_stats: Dictionary with input, output, and total token counts
        context_window: Context window size for percentage calculation
    """
    from shared.utils.colors import BOLD, DIM, RESET

    pct = (token_stats["total"] / context_window * 100) if context_window else 0
    bar_length = 20
    filled_length = (
        int(bar_length * token_stats["total"] // context_window) if context_window else 0
    )
    bar = "█" * filled_length + "░" * (bar_length - filled_length)

    stats = (
        f"  {DIM}│{RESET} 📊 {BOLD}In:{token_stats['input']}{RESET} {DIM}·{RESET} "
        f"{BOLD}Out:{token_stats['output']}{RESET} {DIM}·{RESET} {BOLD}Ctx:{pct:.1f}%{RESET} {bar}"
    )
    print(stats)


def separator(char: str = "─", color: str = CYAN) -> str:
    """
    Create a separator line.

    Args:
        char: Character to use for the separator
        color: Color name from shared.utils.colors

    Returns:
        Formatted separator string
    """
    from shared.utils.colors import RESET

    # Get color value
    colors = {
        "RED": RED,
        "GREEN": GREEN,
        "YELLOW": YELLOW,
        "BLUE": BLUE,
        "MAGENTA": MAGENTA,
        "CYAN": CYAN,
        "WHITE": WHITE,
        "DIM": DIM,
        "RESET": RESET,
    }
    color_code = colors.get(color.upper(), CYAN)

    # Try to get terminal width, fallback to 80
    try:
        width = min(os.get_terminal_size().columns, 100)
    except (AttributeError, OSError):
        width = 80

    return f"{color_code}{char * width}{RESET}"


def render_markdown(text: str) -> str:
    """
    Render markdown text (placeholder - in real implementation would use markdown library).

    Args:
        text: Markdown text to render

    Returns:
        Rendered text (plain text in this implementation)
    """
    # In a full implementation, this would use a markdown library
    # For now, just return the text as-is
    return text


# Re-export colors for backward compatibility
from shared.utils.colors import (
    BOLD,
    CYAN,
    DIM,
    GREEN,
    RED,
    RESET,
    WHITE,
    YELLOW,
    MAGENTA,
    BLUE,
)
