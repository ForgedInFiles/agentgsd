"""
Shared utilities module for AI coding assistants.

This package provides common utilities used across multiple AI coding assistants
in the monorepo, including terminal colors, formatting, spinners, and markdown
rendering.

Available submodules:
    - colors: ANSI color constants and spinner utilities
    - formatters: Terminal formatting utilities for tokens, context bars, etc.

Example usage:
    from shared.utils.colors import BOLD, BLUE, RESET, thinking_spinner
    from shared.utils.formatters import format_tokens, context_bar, separator

    # Use colors
    print(f"{BOLD}{BLUE}Hello{RESET}")

    # Use spinner
    spinner = thinking_spinner("Processing...")
    spinner.start()
    # ... do work ...
    spinner.stop("Done!")
"""

__version__ = "1.0.0"
