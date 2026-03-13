"""
Shared UI module for terminal interactions and prompt_toolkit integration.

This module provides comprehensive UI components for building terminal-based
AI coding assistants with features including:
- Custom command and skill completion using prompt_toolkit
- Key binding configuration
- Help and command popup displays
- Tool call and result formatting
- Token statistics display

Example usage:
    from shared.ui.prompts import (
        CommandCompleter,
        create_keybindings,
        get_prompt_config,
        print_banner,
        print_tool_call,
        print_tool_result,
        print_stats,
    )

    # Create prompt configuration
    config = get_prompt_config()

    # Get user input
    user_input = prompt(">>> ", **config)
"""

__version__ = "1.0.0"

from shared.ui.prompts import (
    CommandCompleter,
    create_keybindings,
    get_prompt_config,
    print_banner,
    print_tool_call,
    print_tool_result,
    print_stats,
    show_commands_popup,
    show_help_popup,
    style,
)

__all__ = [
    "CommandCompleter",
    "create_keybindings",
    "get_prompt_config",
    "print_banner",
    "print_tool_call",
    "print_tool_result",
    "print_stats",
    "show_commands_popup",
    "show_help_popup",
    "style",
]
