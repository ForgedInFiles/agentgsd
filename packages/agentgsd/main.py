"""
Main implementation for the agentgsd package.

This module provides the core functionality for the agentgsd coding assistant,
including tool registry setup, API interaction, prompt_toolkit UI integration,
and the main agentic loop for processing user requests.
"""

import argparse
import os
import sys
from typing import Any, Optional

from prompt_toolkit import prompt
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory

from shared.api import ApiClient
from shared.commands import load_commands
from shared.config import load_config
from shared.skills import activate_skill, load_skills, skills_xml
from shared.tools import (
    BashTool,
    EditTool,
    EnvTool,
    FindTool,
    GitAddTool,
    GitBranchTool,
    GitCheckoutTool,
    GitCommitTool,
    GitDiffTool,
    GitLogTool,
    GitPullTool,
    GitPushTool,
    GitResetTool,
    GitStatusTool,
    GlobTool,
    GrepTool,
    HeadTool,
    LsTool,
    MkdirTool,
    PwdTool,
    ReadTool,
    TailTool,
    Tool,
    ToolRegistry,
    TreeTool,
    WcTool,
    WriteTool,
)
from shared.tools.indexer_tools import (
    IndexBuildTool,
    IndexSearchTool,
    IndexStatsTool,
)
from shared.tools.web_tools import WebFetchTool, WebSearchTool
from shared.ui import (
    create_keybindings,
)
from shared.ui.enhanced import (
    Colors,
    EnhancedPrompt,
    Icons,
    Notification,
    Theme,
    ThinkingSpinner,
    print_assistant_message,
    print_help_detailed,
    print_separator,
    print_skills_list,
)
from shared.ui.enhanced import (
    print_banner as print_banner_enhanced,
)
from shared.ui.enhanced import (
    print_stats as print_stats_enhanced,
)
from shared.ui.enhanced import (
    print_tool_call as print_tool_call_enhanced,
)
from shared.ui.enhanced import (
    print_tool_result as print_tool_result_enhanced,
)


def compact_conversation(messages, client, system_prompt, token_stats):
    """
    Compact the conversation history to reduce token usage.
    Summarizes older parts of the conversation and keeps the most recent exchanges.
    Returns the new message list.
    """
    # We keep the last 6 messages (3 exchanges) as recent context
    if len(messages) <= 6:
        return messages

    # Prepare the conversation to summarize (all except the last 6 messages)
    conversation_to_summarize = ""
    for msg in messages[0 : len(messages) - 6]:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        if role == "user":
            conversation_to_summarize += f"User: {content}\n"
        elif role == "assistant":
            conversation_to_summarize += f"Assistant: {content}\n"
        elif role == "tool":
            tool_name = msg.get("name", "unknown")
            conversation_to_summarize += f"Tool ({tool_name}): {content}\n"
        else:
            conversation_to_summarize += f"{role}: {content}\n"

    # If there's nothing to summarize, return the original messages
    if not conversation_to_summarize.strip():
        return messages

    # Prepare the prompt for summarization
    summary_prompt = f"Please summarize the following conversation concisely, preserving key information and decisions:\n\n{conversation_to_summarize}"

    # We'll use a simple system prompt for summarization
    system_prompt_summary = "You are a helpful assistant that summarizes conversations."

    # Prepare the messages for the summarization call
    summary_messages = [
        {"role": "system", "content": system_prompt_summary},
        {"role": "user", "content": summary_prompt},
    ]

    try:
        # Make the API call for summarization
        response = client.call_api(summary_messages, system_prompt_summary, {})
        # Extract the summary from the response
        summary_text = ""
        for block in response.get("content", []):
            if block.get("type") == "text":
                summary_text += block.get("text", "")
        # If we got a summary, use it; otherwise, fall back to a placeholder
        if not summary_text.strip():
            summary_text = "[Summary generation failed or returned empty]"
    except Exception as e:
        # If summarization fails, we return the original messages to avoid data loss
        # Use Notification to display the error in a user-friendly way
        Notification.warning(f"Compaction failed: {e}", Icons.WARNING)
        return messages

    # Form the summary message from the assistant
    summary_msg = {
        "role": "assistant",
        "content": f"I've summarized the conversation to save context. Summary: {summary_text}",
    }

    # Keep the last 6 messages as recent context
    recent_messages = messages[-6:]

    # The new message list is the summary message followed by the recent messages
    new_messages = [summary_msg] + recent_messages

    # Update token stats with the usage from the summarization call
    try:
        usage = client.get_usage()
        token_stats["input"] += usage.get("input_tokens", 0)
        token_stats["output"] += usage.get("output_tokens", 0)
        token_stats["total"] = token_stats["input"] + token_stats["output"]
    except Exception:
        # If we can't get usage, we leave token_stats as is (it will be updated on the next call)
        pass

    return new_messages


def create_tool_registry() -> ToolRegistry:
    """
    Create and populate the tool registry with all available tools.

    This function initializes a ToolRegistry and registers all the tools
    needed for the agentgsd coding assistant, including file operations,
    search operations, shell commands, and skill activation.

    Returns:
        ToolRegistry: A registry containing all registered tools.

    Example:
        >>> registry = create_tool_registry()
        >>> tool = registry.get("read")
        >>> print(tool.name)
        read
    """
    registry = ToolRegistry()

    registry.register(ReadTool())
    registry.register(WriteTool())
    registry.register(EditTool())
    registry.register(MkdirTool())
    registry.register(LsTool())
    registry.register(TreeTool())
    registry.register(HeadTool())
    registry.register(TailTool())
    registry.register(WcTool())
    registry.register(PwdTool())
    registry.register(GrepTool())
    registry.register(GlobTool())
    registry.register(FindTool())
    registry.register(BashTool())
    registry.register(EnvTool())
    registry.register(GitStatusTool())
    registry.register(GitDiffTool())
    registry.register(GitLogTool())
    registry.register(GitBranchTool())
    registry.register(GitCommitTool())
    registry.register(GitAddTool())
    registry.register(GitResetTool())
    registry.register(GitCheckoutTool())
    registry.register(GitPushTool())
    registry.register(GitPullTool())
    registry.register(IndexBuildTool())
    registry.register(IndexSearchTool())
    registry.register(IndexStatsTool())
    registry.register(WebSearchTool())
    registry.register(WebFetchTool())

    class SkillTool(Tool):
        """Tool for activating agent skills."""

        def __init__(self):
            super().__init__(
                name="skill",
                description="Activate an agent skill",
                parameters={"name": "string"},
            )

        def execute(self, args: dict[str, Any]) -> str:
            """Activate an agent skill.

            Args:
                args: Dictionary containing:
                    - name (str): Name of the skill to activate (required)

            Returns:
                str: Result of skill activation or error message
            """
            name = args.get("name", "")
            return activate_skill(name)

    registry.register(SkillTool())

    return registry


def run_tool(registry: ToolRegistry, name: str, args: dict[str, Any]) -> str:
    """
    Execute a tool by name with the given arguments.

    Args:
        registry: The tool registry containing registered tools.
        name: Name of the tool to execute.
        args: Dictionary of arguments to pass to the tool.

    Returns:
        str: The result of executing the tool, or an error message.

    Example:
        >>> registry = create_tool_registry()
        >>> result = run_tool(registry, "read", {"path": "example.txt"})
    """
    try:
        tool = registry.get(name)
    except KeyError:
        return f"error: Tool not found: {name}"

    try:
        return tool.execute(args)
    except Exception as err:
        return f"error: {err}"


class CommandCompleter(Completer):
    """Custom completer for commands, tools, and file paths."""

    def __init__(
        self, registry: ToolRegistry, skills: list[Any], commands: Optional[list[Any]] = None
    ):
        """Initialize the completer with available commands, tools, and skills.

        Args:
            registry: ToolRegistry containing available tools
            skills: List of loaded skill objects
            commands: List of loaded command objects
        """
        self.registry = registry
        self.commands = [
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
            "/compact",
        ]
        self.tools = list(registry._tools.keys())
        self.skills = [skill.name for skill in skills]
        self.custom_commands = [cmd.name for cmd in (commands or [])]
        # Add custom commands to completion list
        for cmd in commands or []:
            self.commands.append(f"/{cmd.name}")
        # Store custom command metadata for completion display
        self.custom_command_meta = {f"/{cmd.name}": cmd.description for cmd in (commands or [])}

    def get_completions(self, document, complete_event):
        """Get completions for the current input.

        Args:
            document: The current document state from prompt_toolkit
            complete_event: The completion event from prompt_toolkit

        Yields:
            Completion: Suggested completions for commands, tools, skills, or file paths
        """
        text = document.text_before_cursor
        words = text.split()

        if text.startswith("/"):
            for cmd in self.commands:
                if cmd.startswith(text):
                    yield Completion(
                        cmd,
                        start_position=-len(text),
                        display=HTML(f"<b>{cmd}</b>"),
                        display_meta=self._get_command_meta(cmd),
                    )

        if any(kw in text for kw in ["skill:", "activate"]):
            for skill in self.skills:
                if skill.startswith(words[-1] if words else ""):
                    yield Completion(
                        skill,
                        start_position=-len(words[-1]) if words else 0,
                        display=HTML(f"<b>{skill}</b>"),
                        display_meta="Agent Skill",
                    )

        if any(kw in text for kw in ["path:", "read ", "write ", "edit "]):
            try:
                last_word = words[-1] if words else ""
                if "/" in last_word or last_word.startswith("."):
                    path_prefix = last_word
                    base = os.path.dirname(path_prefix) or "."
                    prefix = os.path.basename(path_prefix)

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
        """Get metadata/tooltip for a command.

        Args:
            cmd: The command string (e.g., "/help", "/stats")

        Returns:
            str: Human-readable description of the command for display in completer
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
            "/compact": "Compact conversation to save context",
        }
        # Check if it's a custom command with metadata
        if cmd in getattr(self, "custom_command_meta", {}):
            return self.custom_command_meta[cmd]
        return meta.get(cmd, "Command")


class InputCounter:
    """Tracks character/word count for large input handling."""

    def __init__(self, max_length: int = 50000):
        self.max_length = max_length
        self.warning_threshold = max_length - 5
        self.last_text = ""

    def get_counter_display(self, text: str = "") -> Optional[str]:
        """Get the counter display text if input is large enough."""
        if not text:
            text = self.last_text

        char_count = len(text)
        word_count = len(text.split()) if text.strip() else 0

        if char_count >= self.warning_threshold:
            if char_count >= self.max_length:
                status = "MAX"
            elif char_count >= self.warning_threshold + 1000:
                status = f"{char_count}/{self.max_length}"
            else:
                status = f"{char_count}/{self.max_length}"

            return f"[{status} | {word_count} words]"
        return None

    def update_text(self, text: str):
        """Update the cached text."""
        self.last_text = text


def get_input(
    registry: ToolRegistry, skills: list[Any], commands: Optional[list[Any]] = None
) -> str:
    """
    Get user input using prompt_toolkit with completion support.

    Args:
        registry: The tool registry for completion suggestions.
        skills: List of loaded skills for completion.
        commands: List of loaded custom commands for completion.

    Returns:
        str: The user's input string.
    """
    from shared.config import load_config

    config = load_config()
    counter = InputCounter(config.max_input_length)

    kb = create_keybindings()
    completer = CommandCompleter(registry, skills, commands)

    history_path = os.path.expanduser("~/.agentgsd_history")
    os.makedirs(os.path.dirname(history_path) or ".", exist_ok=True)

    try:
        user_input = prompt(
            HTML("<prompt>❯ </prompt>"),
            completer=completer,
            complete_while_typing=True,
            style=EnhancedPrompt.get_style(),
            auto_suggest=AutoSuggestFromHistory(),
            history=FileHistory(history_path),
            key_bindings=kb,
            multiline=False,
        )
        counter.update_text(user_input)

        # Show counter in bottom toolbar if input is large
        counter_display = counter.get_counter_display()
        if counter_display:
            print(f"\n{counter_display}")

        return user_input.strip()
    except (KeyboardInterrupt, EOFError):
        raise


def handle_command(
    user_input: str,
    messages: list[dict[str, Any]],
    token_stats: dict[str, int],
    client: ApiClient,
    system_prompt: str,
    commands: Optional[list[Any]] = None,
) -> Optional[str]:
    """
    Handle special commands (/q, /c, /h, /stats, /s, /compact).

    Args:
        user_input: The user's input string.
        messages: The conversation messages list (for clearing).
        token_stats: Token statistics dict (for resetting).
        client: The API client for making requests.
        system_prompt: The system prompt for the API.
        commands: List of loaded custom commands.

    Returns:
        Optional[str]: None to continue, "quit" to exit, or result string to display.
    """
    from shared.config import load_config as load_config_func

    if commands is None:
        commands = []

    # Check for custom command execution (starts with / but not a built-in command)
    if user_input.startswith("/"):
        # Parse command and arguments
        parts = user_input[1:].split(" ", 1)
        cmd_name = parts[0]
        cmd_args = parts[1] if len(parts) > 1 else ""

        # Check if it's a custom command
        for cmd in commands:
            if cmd.matches(cmd_name):
                # Execute the custom command
                command_content = cmd.execute(cmd_args)
                print()
                print_separator("light", Colors.DIM)
                print(f"{Colors.BRIGHT_CYAN}Executing: /{cmd.name}{Colors.RESET}")
                print(f"{Colors.DIM}Arguments: {cmd_args or '(none)'}{Colors.RESET}")
                print_separator("light", Colors.DIM)
                # Add command content to messages and return "continue" to process it
                messages.append({"role": "user", "content": command_content})
                return "continue"

    if user_input in ("/q", "/quit", "/exit"):
        return "quit"

    if user_input == "/c":
        messages.clear()
        token_stats["input"] = 0
        token_stats["output"] = 0
        token_stats["total"] = 0
        Notification.success("Conversation cleared", Icons.CHECK)
        return None

    if user_input in ("/h", "/help"):
        commands = load_commands()
        print_help_detailed(commands)
        return None

    if user_input in ("/cmds", "/commands"):
        commands = load_commands()
        if not commands:
            Notification.info(
                "No custom commands found. Add .md files to ~/.agentgsd/commands/ or .agentgsd/commands/"
            )
        else:
            print()
            print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}Custom Commands{Colors.RESET}")
            print(f"{Colors.BRIGHT_CYAN}{'─' * 40}{Colors.RESET}\n")
            for cmd in commands:
                alias_info = (
                    f" (aliases: {', '.join(['/' + a for a in cmd.aliases])})"
                    if cmd.aliases
                    else ""
                )
                print(f"  {Colors.BRIGHT_YELLOW}/{cmd.name}{alias_info}{Colors.RESET}")
                print(f"    {Colors.DIM}{cmd.description}{Colors.RESET}\n")
        return None

    if user_input == "/stats":
        from shared.config import load_config as load_config_func

        config = load_config_func()
        print_stats_enhanced(token_stats, config.context_window)
        return None

    if user_input == "/compact":
        messages = compact_conversation(messages, client, system_prompt, token_stats)
        Notification.warning("Conversation compacted", Icons.WARNING)
        return None

    if user_input in ("/s", "/skills"):
        skills = load_skills()
        print_skills_list(skills)
        return None

    return "continue"


def process_response(
    response: dict[str, Any],
    registry: ToolRegistry,
    messages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Process API response and execute any tool calls.
    """

    tool_results = []
    content_blocks = response.get("content", [])

    # Collect all text blocks to display as a single message
    text_blocks = []
    for block in content_blocks:
        if block.get("type") == "text":
            text_content = block.get("text", "")
            text_blocks.append(text_content)
        elif block.get("type") == "tool_use":
            tool_name = block.get("name")
            tool_args = block.get("input", {})
            print_tool_call_enhanced(tool_name, tool_args)

            result = run_tool(registry, tool_name, tool_args)
            print_tool_result_enhanced(result)

            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.get("id"),
                    "content": result,
                }
            )

    # Display all text content as a single framed message
    if text_blocks:
        full_text = "".join(text_blocks)
        print()
        print_separator("light", Colors.DIM)
        print_assistant_message(full_text)
        print_separator("light", Colors.DIM)

    messages.append({"role": "assistant", "content": content_blocks})

    return tool_results


def setup_environment(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
) -> tuple[ApiClient, ToolRegistry, list[Any], object]:
    """
    Set up the application environment.

    Validates the API key, loads configuration, creates the tool registry,
    and loads skills.

    Args:
        provider: Optional provider override.
        model: Optional model override.
        api_key: Optional API key override.

    Returns:
        tuple: (client, registry, skills, config) where:
            - client: ApiClient instance
            - registry: ToolRegistry instance
            - skills: List of loaded skills
            - config: Configuration object

    Raises:
        SystemExit: If API key is not found.
    """
    from shared.utils.colors import RED, RESET, YELLOW

    config = load_config(provider=provider, model=model, api_key=api_key)

    if not config.api_key and config.provider not in ["ollama", "lmstudio"]:
        print(
            f"{RED}✗{RESET} Error: API key not found for provider {YELLOW}{config.provider}{RESET}"
        )
        sys.exit(1)

    skills = load_skills()
    load_commands()
    print_banner_enhanced(model=config.model, provider=config.provider, skills_count=len(skills))

    client = ApiClient(
        provider=config.provider,
        api_url=config.api_url,
        api_key=config.api_key,
        model=config.model,
        max_tokens=config.max_tokens,
        timeout=config.timeout,
    )

    registry = create_tool_registry()

    return client, registry, skills, config


def build_system_prompt() -> str:
    """
    Build the system prompt for the AI assistant.

    Returns:
        str: The formatted system prompt including skills XML.
    """
    skills_xml_content = skills_xml()
    return f"""You are agentgsd, an elite coding assistant. Current directory: {os.getcwd()}.
Be concise, precise, and helpful. Write code when needed.

{skills_xml_content}

When a user's request matches a skill description, use the skill tool to activate it."""


def handle_user_input(
    registry: ToolRegistry,
    skills: list[Any],
    commands: list[Any],
    messages: list[dict[str, Any]],
    token_stats: dict[str, int],
    client: ApiClient,
    system_prompt: str,
) -> Optional[str]:
    """
    Get and handle user input.

    Args:
        registry: The tool registry for completion suggestions.
        skills: List of loaded skills.
        commands: List of loaded custom commands.
        messages: The conversation messages list.
        token_stats: Token statistics dict.
        client: The API client for making requests.
        system_prompt: The system prompt for the API.

    Returns:
        Optional[str]: None to continue, "quit" to exit, or "continue" to proceed.
    """
    user_input = get_input(registry, skills, commands)

    if not user_input:
        return None

    result = handle_command(user_input, messages, token_stats, client, system_prompt, commands)
    if result == "quit":
        return "quit"
    if result is None:
        return None

    messages.append({"role": "user", "content": user_input})
    return "continue"


def process_agent_loop(
    client: ApiClient,
    registry: ToolRegistry,
    messages: list[dict[str, Any]],
    token_stats: dict[str, int],
    system_prompt: str,
) -> None:
    """
    Process the agent interaction loop.

    Handles API calls, tool execution, and token tracking until no more
    tool results are returned.

    Args:
        client: The API client for making requests.
        registry: The tool registry for executing tools.
        messages: The conversation messages list.
        token_stats: Token statistics dict to update.
        system_prompt: The system prompt for the API.
    """

    while True:
        thinking = ThinkingSpinner(f"{Theme.THINKING}Processing request...")
        thinking.start()

        try:
            response = client.call_api(messages, system_prompt, registry.make_schema())
        except KeyboardInterrupt:
            thinking.stop()
            Notification.info("Request interrupted by user", Icons.WARNING)
            break
        finally:
            thinking.stop()

        usage = client.get_usage()
        token_stats["input"] += usage.get("input_tokens", 0)
        token_stats["output"] += usage.get("output_tokens", 0)
        token_stats["total"] = token_stats["input"] + token_stats["output"]

        tool_results = process_response(response, registry, messages)

        if not tool_results:
            break

        messages.append({"role": "user", "content": tool_results})


def print_exit_message(token_stats: dict[str, int], context_window: int) -> None:
    """Print the exit message with statistics."""
    print()
    print_separator("light", Colors.DIM)
    print(
        f"{Colors.BRIGHT_CYAN}{Icons.SPARKLE} Thanks for using {Colors.BOLD}agentgsd{Colors.RESET}"
    )
    print_separator("light", Colors.DIM)
    print_stats_enhanced(token_stats, context_window)
    print()


def main_interaction_loop(
    client: ApiClient, registry: ToolRegistry, skills: list[Any], config, system_prompt: str
) -> None:
    """
    Main interaction loop for the agent.

    Handles user input, API calls, tool execution, and error handling
    until the user quits or an unrecoverable error occurs.

    Args:
        client: The API client for making requests.
        registry: The tool registry for executing tools.
        skills: List of loaded skills.
        config: Configuration object.
        system_prompt: The system prompt for the API.
    """

    messages: list[dict[str, Any]] = []
    token_stats = {"input": 0, "output": 0, "total": 0}
    commands = load_commands()

    while True:
        try:
            result = handle_user_input(
                registry, skills, commands, messages, token_stats, client, system_prompt
            )

            if result == "quit":
                print_exit_message(token_stats, config.context_window)
                break
            if result is None:
                continue

            # Process agent interaction
            process_agent_loop(client, registry, messages, token_stats, system_prompt)

            # Display token statistics
            print_stats_enhanced(token_stats, config.context_window)

            # Check if we need to compact the conversation
            if token_stats["total"] > 0.8 * config.context_window:
                messages = compact_conversation(messages, client, system_prompt, token_stats)
                Notification.warning("Conversation compacted to save context", Icons.WARNING)

        except (KeyboardInterrupt, EOFError):
            print_exit_message(token_stats, config.context_window)
            break
        except Exception as err:
            Notification.error(f"Error: {err}", Icons.CROSS)
            import traceback

            traceback.print_exc()


def main():
    """
    Main entry point for the agentgsd coding assistant.
    """
    parser = argparse.ArgumentParser(description="agentgsd - elite coding assistant")
    parser.add_argument(
        "--provider", help="API provider (openrouter, gemini, groq, mistral, ollama, lmstudio)"
    )
    parser.add_argument("--model", help="Model identifier")
    parser.add_argument("--api-key", help="API key for the provider")
    parser.add_argument(
        "--gsdmode", action="store_true", help="Enable gsdmode (Superpowers-inspired workflow)"
    )
    args = parser.parse_args()

    # Set up environment
    client, registry, skills, config = setup_environment(
        provider=args.provider, model=args.model, api_key=args.api_key
    )

    # Build system prompt
    system_prompt = build_system_prompt()

    # Start main interaction loop
    main_interaction_loop(client, registry, skills, config, system_prompt)


if __name__ == "__main__":
    main()
