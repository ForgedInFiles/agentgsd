"""
Formatting utilities for terminal output.

This module provides functions for:
- Formatting token counts with K suffix
- Drawing context usage bars with color coding
- Creating separator lines
- Rendering simple markdown for terminal display

Example usage:
    from shared.utils.formatters import format_tokens, context_bar, separator

    # Format tokens
    print(f"Tokens used: {format_tokens(1500)}")  # Output: Tokens used: 1.5K

    # Context bar
    bar = context_bar(50000, 100000, width=20)
    print(f"Context: {bar}")

    # Separator
    print(separator())
"""

import os
import re

from shared.utils.colors import BOLD, BLUE, CYAN, DIM, GREEN, ITALIC, RED, YELLOW, RESET


def format_tokens(n):
    """
    Format a token count with K suffix for human-readable display.

    Converts large numbers to a more compact format using the K suffix
    (thousands). Numbers below 1000 are returned as-is.

    Args:
        n: The token count to format (integer or float).

    Returns:
        A string representation of the token count:
        - Numbers >= 1000 are formatted with one decimal place and K suffix (e.g., "1.5K")
        - Numbers < 1000 are returned as strings (e.g., "500")

    Example:
        >>> format_tokens(500)
        '500'
        >>> format_tokens(1500)
        '1.5K'
        >>> format_tokens(100000)
        '100.0K'
    """
    if n >= 1000:
        return f"{n / 1000:.1f}K"
    return str(n)


def context_bar(current, max_val, width=30):
    """
    Draw a context usage bar with color coding based on usage percentage.

    Creates a visual representation of context window usage with color coding:
    - Green: usage below 50%
    - Yellow: usage between 50% and 80%
    - Red: usage at 80% or above

    Args:
        current: Current context usage value (e.g., tokens used).
        max_val: Maximum context value (e.g., total context window size).
        width: Width of the bar in characters. Defaults to 30.

    Returns:
        A string containing the colored progress bar with filled (█) and
        empty (░) segments, bounded by color codes.

    Example:
        >>> # 40% usage - green
        >>> context_bar(40000, 100000)
        '\\x1b[32m████████████████░░░░░░░░░░░░░░░░░░\\x1b[0m'

        >>> # 65% usage - yellow
        >>> context_bar(65000, 100000)
        '\\x1b[33m█████████████████████████░░░░░░░░\\x1b[0m'

        >>> # 90% usage - red
        >>> context_bar(90000, 100000)
        '\\x1b[31m███████████████████████████████░░\\x1b[0m'

        >>> # Print with print() to see colored output
        >>> print(f"Context: {context_bar(50000, 100000, width=20)}")
    """
    pct = min(current / max_val, 1.0)
    filled = int(width * pct)
    empty = width - filled
    color = GREEN if pct < 0.5 else YELLOW if pct < 0.8 else RED
    return f"{color}{'█' * filled}{DIM}{'░' * empty}{RESET}"


def separator(char="─", color=DIM, width=None):
    """
    Draw a separator line spanning the terminal width.

    Creates a horizontal separator line using a specified character,
    colored with the provided ANSI color code. The line width defaults
    to the terminal width (capped at 120 characters) but can be overridden.

    Args:
        char: Character to use for the separator. Defaults to "─" (horizontal line).
        color: ANSI color code for the separator. Defaults to DIM.
        width: Optional width override. If None, uses terminal width (max 120).

    Returns:
        A string containing the colored separator line.

    Example:
        >>> print(separator())
        ─────────────────────────────────────────────────

        >>> print(separator("═", CYAN))
        ═══════════════════════════════════════════════

        >>> print(separator("-", GREEN, width=40))
        ─────────────────────────────────────────
    """
    if width is None:
        try:
            width = os.get_terminal_size().columns
        except:
            width = 80
    return f"{color}{char * min(width, 120)}{RESET}"


def render_markdown(text):
    """
    Render simple markdown formatting for terminal display.

    Converts common markdown syntax to ANSI-colored terminal output:
    - **bold** → BOLD text
    - *italic* → ITALIC text
    - `inline code` → CYAN colored code
    - ``` code blocks ``` → Colored code block markers
    - # Headers → Colored header lines (h1=BLUE, h2=CYAN, h3=GREEN)
    - > Quotes → ITALIC/DIM quoted lines
    - - List items → Yellow bullet points

    Args:
        text: The markdown text to render.

    Returns:
        The text with markdown syntax converted to ANSI escape codes.

    Example:
        >>> md = "This is **bold** and *italic* with `code`"
        >>> print(render_markdown(md))
        This is \x1b[1mbold\x1b[0m and \x1b[3mitalic\x1b[0m with \x1b[36m`code`\x1b[0m

        >>> md = "# Title\\n## Section\\n> quote\\n- item"
        >>> print(render_markdown(md))
        \x1b[1m\x1b[34m# Title\x1b[0m
        \x1b[1m\x1b[36m## Section\x1b[0m
        \x1b[3m\x1b[2m> quote\x1b[0m
        \x1b[33m• item\x1b[0m
    """
    text = re.sub(r"\*\*(.+?)\*\*", f"{BOLD}\\1{RESET}", text)
    text = re.sub(r"\*(.+?)\*", f"{ITALIC}\\1{RESET}", text)
    text = re.sub(r"```(\w*)\n?", f"\n{DIM}┌─ code block{RESET}\n", text)
    text = re.sub(r"```", f"\n{DIM}└─ end{RESET}\n", text)
    text = re.sub(r"`(.+?)`", f"{CYAN}`\\1`{RESET}", text)
    text = re.sub(r"^# (.+)$", f"{BOLD}{BLUE}# \\1{RESET}", text, flags=re.MULTILINE)
    text = re.sub(r"^## (.+)$", f"{BOLD}{CYAN}## \\1{RESET}", text, flags=re.MULTILINE)
    text = re.sub(r"^### (.+)$", f"{BOLD}{GREEN}### \\1{RESET}", text, flags=re.MULTILINE)
    text = re.sub(r"^> (.+)$", f"{ITALIC}{DIM}> \\1{RESET}", text, flags=re.MULTILINE)
    text = re.sub(r"^- (.+)$", f"{YELLOW}• \\1{RESET}", text, flags=re.MULTILINE)
    return text
