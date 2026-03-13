"""
Utilities package for AI coding assistants.

This package provides terminal-related utilities including:
- ANSI color codes and styling
- Animated spinners for loading states
- Text formatting (tokens, context bars, separators)
- Markdown rendering for terminal output

Example usage:
    from shared.utils import colors, formatters

    # Colors
    from shared.utils.colors import BOLD, RED, thinking_spinner

    # Formatters
    from shared.utils.formatters import format_tokens, context_bar, separator
"""

from shared.utils.colors import (
    Spinner,
    loading_spinner,
    thinking_spinner,
)
from shared.utils.formatters import (
    context_bar,
    format_tokens,
    render_markdown,
    separator,
)

__all__ = [
    "Spinner",
    "loading_spinner",
    "thinking_spinner",
    "format_tokens",
    "context_bar",
    "render_markdown",
    "separator",
]
