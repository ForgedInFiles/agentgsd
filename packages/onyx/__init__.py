"""
Onyx - A minimal coding assistant.

This package provides a lightweight AI coding assistant that uses the shared
API client and tool system to interact with language models. It supports
file operations, search, and shell commands through a simple CLI interface.

Usage:
    from packages.onyx import main

    # Run the assistant
    main()

Or from command line:
    python -m packages.onyx

Environment Variables:
    OPENROUTER_API_KEY: API key for OpenRouter (default provider)
    ANTHROPIC_API_KEY: API key for Anthropic
    MODEL: Model to use (defaults to free model based on provider)

Example:
    >>> # Start the assistant
    >>> python -m packages.onyx
    nanocode | nvidia/nemotron-3-super-120b-a12b:free (OpenRouter) | /path/to/dir

    ❯ Read the file at path/to/file.py
    ─────────────────────────────────────────────────────────
    ⏺ Tool execution results...
"""

from packages.onyx.main import main

__all__ = ["main"]

__version__ = "1.0.0"
