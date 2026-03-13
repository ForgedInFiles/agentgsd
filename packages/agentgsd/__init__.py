"""
agentgsd - Elite coding assistant powered by OpenRouter with prompt_toolkit UI.

This package provides an AI-powered coding assistant that leverages OpenRouter's
API to interact with large language models. It features a rich terminal UI with
prompt_toolkit integration, skill-based workflows, and comprehensive tool support.

Main Features:
    - OpenRouter API integration for LLM interactions
    - prompt_toolkit-based terminal UI with autocomplete
    - Comprehensive file manipulation tools (read, write, edit, mkdir, ls, tree)
    - Search tools (grep, find, glob)
    - Shell command execution
    - Skills system for extensible workflows
    - Token usage tracking and statistics
    - Markdown rendering for terminal output

Quick Start:
    >>> from agentgsd import main
    >>> main()

Environment Variables:
    OPENROUTER_API_KEY (str): Required. Get from https://openrouter.ai/keys
    SKILLS_PATH (str): Optional. Path to skills directory. Default: "./skills"

Example:
    # Run the assistant
    $ python -m agentgsd

    # Or set the API key and run
    $ export OPENROUTER_API_KEY=your_key_here
    $ python -m agentgsd

Commands:
    /q, /quit, /exit   - Quit the application
    /c, /clear         - Clear conversation history
    /h, /help          - Show help message
    /stats             - Show token statistics
    /s, /skills        - List available skills

Key Bindings:
    Tab              - Trigger autocomplete
    Ctrl+P           - Show commands popup
    F1               - Show help
    Ctrl+C           - Cancel current input
    Ctrl+D           - Quit

Tool Usage:
    The assistant can use various tools to help with coding tasks:
    - read(path)           - Read file with line numbers
    - write(path, content) - Write content to file
    - edit(path, old, new)  - Replace text in file
    - mkdir(path)          - Create directory
    - ls(path?)            - List directory contents
    - tree(path?)          - Show directory tree
    - grep(pat, path?)     - Search files for pattern
    - find(name, path?)    - Find files by name
    - bash(cmd)            - Run shell command
    - skill(name)          - Activate an agent skill

Version: 1.0.0
"""

from packages.agentgsd.main import main

__all__ = ["main"]
__version__ = "1.0.0"
