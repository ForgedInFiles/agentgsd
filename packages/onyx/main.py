"""
Main implementation for the Onyx minimal coding assistant.

This module provides the core functionality of the Onyx assistant,
including the tool registry, API client integration, and the agentic
loop for handling user requests.

Example usage:
    from packages.onyx.main import main

    # Run the assistant
    main()

The assistant supports the following commands:
    /q - Quit the assistant
    /c - Clear conversation history
"""

import os
import sys

from shared.api import ApiClient
from shared.config import default_config
from shared.tools import ToolRegistry, run_tool
from shared.tools.file_tools import EditTool, ReadTool, WriteTool
from shared.tools.search_tools import GlobTool, GrepTool
from shared.tools.shell_tools import BashTool
from shared.utils.colors import BOLD, BLUE, CYAN, DIM, GREEN, RED, RESET
from shared.utils.formatters import render_markdown, separator


def create_tool_registry() -> ToolRegistry:
    """
    Create and populate a tool registry with Onyx's tool set.

    The registry includes file operations (read, write, edit),
    search tools (glob, grep), and shell execution (bash).

    Returns:
        ToolRegistry: A configured registry with all Onyx tools registered.

    Example:
        >>> registry = create_tool_registry()
        >>> "read" in registry
        True
        >>> "bash" in registry
        True
    """
    registry = ToolRegistry()

    registry.register(ReadTool())
    registry.register(WriteTool())
    registry.register(EditTool())
    registry.register(GlobTool())
    registry.register(GrepTool())
    registry.register(BashTool())

    return registry


def get_provider_info(client: ApiClient) -> str:
    """
    Get provider and model info string for display.

    Args:
        client: ApiClient instance to extract info from.

    Returns:
        str: Formatted string with provider and model name.

    Example:
        >>> client = ApiClient()
        >>> get_provider_info(client)
        'nvidia/nemotron-3-super-120b-a12b:free (OpenRouter)'
    """
    provider = "OpenRouter" if client.provider == "openrouter" else "Anthropic"
    return f"{client.model} ({provider})"


def print_welcome(config) -> None:
    """
    Print welcome banner with assistant info.

    Args:
        config: Configuration object containing model and other settings.

    Example:
        >>> config = default_config()
        >>> print_welcome(config)
    """
    print(
        f"{BOLD}nanocode{RESET} | {DIM}{config.model} ({config.provider}) | {os.getcwd()}{RESET}\n"
    )


def handle_special_commands(user_input: str, messages: list) -> bool:
    """
    Handle special commands (/q, /c).

    Args:
        user_input: The raw user input string.
        messages: The conversation messages list to potentially clear.

    Returns:
        bool: True if a special command was handled, False otherwise.

    Example:
        >>> messages = []
        >>> handle_special_commands("/q", messages)
        True
        >>> messages = [{"role": "user", "content": "hello"}]
        >>> handle_special_commands("/c", messages)
        True
        >>> messages
        []
    """
    if user_input in ("/q", "exit"):
        return True

    if user_input == "/c":
        messages.clear()
        print(f"{GREEN}⏺ Cleared conversation{RESET}")
        return True

    return False


def process_tool_result(tool_name: str, tool_args: dict, result: str) -> None:
    """
    Print tool execution result with formatting.

    Args:
        tool_name: Name of the executed tool.
        tool_args: Arguments passed to the tool.
        result: Result string from tool execution.

    Example:
        >>> process_tool_result("read", {"path": "file.txt"}, "file content...")
    """
    arg_preview = str(list(tool_args.values())[0])[:50]
    print(f"\n{GREEN}⏺ {tool_name.capitalize()}{RESET}({DIM}{arg_preview}{RESET})")

    result_lines = result.split("\n")
    preview = result_lines[0][:60]
    if len(result_lines) > 1:
        preview += f" ... +{len(result_lines) - 1} lines"
    elif len(result_lines[0]) > 60:
        preview += "..."
    print(f"  {DIM}⎿  {preview}{RESET}")


def process_text_block(block: dict) -> None:
    """
    Print a text content block with markdown rendering.

    Args:
        block: Content block dictionary with 'text' key.

    Example:
        >>> block = {"type": "text", "text": "Hello **world**!"}
        >>> process_text_block(block)
    """
    print(f"\n{CYAN}⏺{RESET} {render_markdown(block['text'])}")


def agentic_loop(
    client: ApiClient,
    messages: list,
    system_prompt: str,
    registry: ToolRegistry,
) -> None:
    """
    Execute the agentic loop: call API, execute tools, repeat.

    This function handles the core interaction pattern:
    1. Send messages to API
    2. Process response blocks (text or tool use)
    3. Execute tools and add results to messages
    4. Continue until no more tool calls

    Args:
        client: ApiClient for making API calls.
        messages: Conversation messages list.
        system_prompt: System prompt for the assistant.
        registry: ToolRegistry containing available tools.

    Example:
        >>> client = ApiClient()
        >>> messages = [{"role": "user", "content": "List files"}]
        >>> registry = create_tool_registry()
        >>> agentic_loop(client, messages, "You are helpful.", registry)
    """
    tools_schema = registry.make_schema()

    while True:
        response = client.call_api(messages, system_prompt, tools_schema)
        content_blocks = response.get("content", [])
        tool_results = []

        for block in content_blocks:
            if block["type"] == "text":
                process_text_block(block)

            if block["type"] == "tool_use":
                tool_name = block["name"]
                tool_args = block["input"]

                result = run_tool(registry, tool_name, tool_args)
                process_tool_result(tool_name, tool_args, result)

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block["id"],
                        "content": result,
                    }
                )

        messages.append({"role": "assistant", "content": content_blocks})

        if not tool_results:
            break

        messages.append({"role": "user", "content": tool_results})

    print()


def main() -> None:
    """
    Main entry point for the Onyx coding assistant.

    This function initializes the API client, creates the tool registry,
    and runs the interactive CLI loop. It supports:
    - File operations: read, write, edit
    - Search tools: glob, grep
    - Shell commands: bash
    - Special commands: /q (quit), /c (clear)

    Environment Variables:
        OPENROUTER_API_KEY: API key for OpenRouter (default)
        ANTHROPIC_API_KEY: API key for Anthropic
        MODEL: Model to use (default varies by provider)
        ONYX_PROVIDER: Either "openrouter" or "anthropic"

    Example:
        >>> # Run with default OpenRouter
        >>> main()

        >>> # Or run as module
        >>> # python -m packages.onyx
    """
    config = default_config()

    provider = os.environ.get("ONYX_PROVIDER", config.provider)

    try:
        client = ApiClient(provider=provider)
    except EnvironmentError as e:
        print(f"{RED}⏺ Error: {e}{RESET}")
        sys.exit(1)

    print_welcome(config)

    messages = []
    cwd = os.getcwd()
    system_prompt = f"Concise coding assistant. cwd: {cwd}"
    registry = create_tool_registry()

    while True:
        try:
            print(separator())
            user_input = input(f"{BOLD}{BLUE}❯{RESET} ").strip()
            print(separator())

            if not user_input:
                continue

            if handle_special_commands(user_input, messages):
                break

            messages.append({"role": "user", "content": user_input})
            agentic_loop(client, messages, system_prompt, registry)

        except KeyboardInterrupt:
            break
        except EOFError:
            break
        except Exception as err:
            print(f"{RED}⏺ Error: {err}{RESET}")


if __name__ == "__main__":
    main()
