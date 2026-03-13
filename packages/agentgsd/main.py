"""
Main implementation for the agentgsd package.

This module provides the core functionality for the agentgsd coding assistant,
including tool registry setup, API interaction, prompt_toolkit UI integration,
and the main agentic loop for processing user requests.
"""

import argparse
import os
import sys
from typing import Any, Dict, List, Optional

from prompt_toolkit import prompt
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings

from shared.api import ApiClient
from shared.config import load_config
from shared.skills import load_skills, skills_xml, activate_skill
from shared.tools import (
    Tool,
    ToolRegistry,
    ReadTool,
    WriteTool,
    EditTool,
    MkdirTool,
    LsTool,
    TreeTool,
    GrepTool,
    FindTool,
    BashTool,
)
from shared.tools.web_tools import WebSearchTool, WebFetchTool
from shared.utils.colors import thinking_spinner, loading_spinner
from shared.utils.formatters import (
    format_tokens,
    context_bar,
    render_markdown,
    separator,
)
from shared.ui import (
    style,
    print_banner,
    print_tool_call,
    print_tool_result,
    print_stats,
    show_help_popup,
    create_keybindings,
    get_prompt_config,
)


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
    registry.register(GrepTool())
    registry.register(FindTool())
    registry.register(BashTool())
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

        def execute(self, args: Dict[str, Any]) -> str:
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


def run_tool(registry: ToolRegistry, name: str, args: Dict[str, Any]) -> str:
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

    def __init__(self, registry: ToolRegistry, skills: List[Any]):
        """Initialize the completer with available commands, tools, and skills.
        
        Args:
            registry: ToolRegistry containing available tools
            skills: List of loaded skill objects
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
        ]
        self.tools = list(registry._tools.keys())
        self.skills = [skill.name for skill in skills]

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
        }
        return meta.get(cmd, "Command")


def get_input(registry: ToolRegistry, skills: List[Any]) -> str:
    """
    Get user input using prompt_toolkit with completion support.

    Args:
        registry: The tool registry for completion suggestions.
        skills: List of loaded skills for completion.

    Returns:
        str: The user's input string.
    """
    kb = create_keybindings()
    completer = CommandCompleter(registry, skills)

    history_path = os.path.expanduser("~/.agentgsd_history")
    os.makedirs(os.path.dirname(history_path) or ".", exist_ok=True)

    try:
        user_input = prompt(
            [("class:prompt", "❯ "), ("bold", "")],
            completer=completer,
            complete_while_typing=True,
            style=style,
            auto_suggest=AutoSuggestFromHistory(),
            history=FileHistory(history_path),
            key_bindings=kb,
            multiline=False,
        )
        return user_input.strip()
    except (KeyboardInterrupt, EOFError):
        raise


def handle_command(
    user_input: str,
    messages: List[Dict[str, Any]],
    token_stats: Dict[str, int],
) -> Optional[str]:
    """
    Handle special commands (/q, /c, /h, /stats, /s).

    Args:
        user_input: The user's input string.
        messages: The conversation messages list (for clearing).
        token_stats: Token statistics dict (for resetting).

    Returns:
        Optional[str]: None to continue, "quit" to exit, or result string to display.
    """
    from shared.utils.colors import GREEN, YELLOW, DIM, MAGENTA, BOLD, RESET

    if user_input in ("/q", "/quit", "/exit"):
        return "quit"

    if user_input == "/c":
        messages.clear()
        token_stats["input"] = 0
        token_stats["output"] = 0
        token_stats["total"] = 0
        print(f"\n{GREEN}✓{RESET} Conversation cleared")
        return None

    if user_input in ("/h", "/help"):
        show_help_popup(None)
        return None

    if user_input == "/stats":
        config = load_config()
        pct = (token_stats["total"] / config.context_window * 100) if config.context_window else 0
        bar = context_bar(token_stats["total"], config.context_window)
        stats = f"  {DIM}│{RESET} 📊 {BOLD}In:{format_tokens(token_stats['input'])}{RESET} {DIM}·{RESET} {BOLD}Out:{format_tokens(token_stats['output'])}{RESET} {DIM}·{RESET} {BOLD}Ctx:{pct:.1f}%{RESET} {bar}"
        print(stats)
        return None

    if user_input in ("/s", "/skills"):
        skills = load_skills()
        if not skills:
            print(f"\n{DIM}No skills loaded. Set SKILLS_PATH environment variable.{RESET}")
        else:
            print(f"\n{DIM}Available Skills:{RESET}")
            for skill in skills:
                print(f"  {GREEN}{skill.name:20}{RESET} {skill.description}")
        return None

    return "continue"


def process_response(
    response: Dict[str, Any],
    registry: ToolRegistry,
    messages: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Process API response and execute any tool calls.

    Args:
        response: The API response dictionary.
        registry: The tool registry for executing tools.
        messages: The conversation messages list to append to.

    Returns:
        List of tool results to send back to the API.
    """
    from shared.utils.colors import CYAN

    tool_results = []
    content_blocks = response.get("content", [])

    for block in content_blocks:
        if block.get("type") == "text":
            text_content = block.get("text", "")
            print(f"\n{separator('─', CYAN)}")
            print(render_markdown(text_content))
            print(f"{separator('─', CYAN)}")

        if block.get("type") == "tool_use":
            tool_name = block.get("name")
            tool_args = block.get("input", {})
            print_tool_call(tool_name, tool_args)

            result = run_tool(registry, tool_name, tool_args)
            print_tool_result(result)

            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.get("id"),
                    "content": result,
                }
            )

    messages.append({"role": "assistant", "content": content_blocks})

    return tool_results


def setup_environment(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
) -> tuple[ApiClient, ToolRegistry, List[Any], object]:
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
    from shared.utils.colors import RED, YELLOW, DIM, RESET

    config = load_config(provider=provider, model=model, api_key=api_key)

    if not config.api_key and config.provider not in ["ollama", "lmstudio"]:
        print(
            f"{RED}✗{RESET} Error: API key not found for provider {YELLOW}{config.provider}{RESET}"
        )
        sys.exit(1)

    print_banner(model=config.model)

    client = ApiClient(
        provider=config.provider,
        api_url=config.api_url,
        api_key=config.api_key,
        model=config.model,
        max_tokens=config.max_tokens,
        timeout=config.timeout,
    )

    registry = create_tool_registry()
    skills = load_skills()

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
    skills: List[Any],
    messages: List[Dict[str, Any]],
    token_stats: Dict[str, int],
) -> Optional[str]:
    """
    Get and handle user input.

    Args:
        registry: The tool registry for completion suggestions.
        skills: List of loaded skills.
        messages: The conversation messages list.
        token_stats: Token statistics dict.

    Returns:
        Optional[str]: None to continue, "quit" to exit, or "continue" to proceed.
    """
    user_input = get_input(registry, skills)

    if not user_input:
        return None

    result = handle_command(user_input, messages, token_stats)
    if result == "quit":
        return "quit"
    if result is None:
        return None

    messages.append({"role": "user", "content": user_input})
    return "continue"


def process_agent_loop(
    client: ApiClient,
    registry: ToolRegistry,
    messages: List[Dict[str, Any]],
    token_stats: Dict[str, int],
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
    from shared.utils.colors import MAGENTA, RESET

    while True:
        thinking = thinking_spinner(f"{MAGENTA}🧠 Thinking{RESET}...")
        thinking.start()

        try:
            response = client.call_api(messages, system_prompt, registry.make_schema())
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


def print_exit_message(token_stats: Dict[str, int], context_window: int) -> None:
    """
    Print the exit message with statistics.

    Args:
        token_stats: Token statistics to display.
        context_window: Context window size for percentage calculation.
    """
    from shared.utils.colors import DIM, MAGENTA, BOLD, RESET

    print(f"\n{DIM}┌─{RESET}")
    print(f"{DIM}│{RESET} {MAGENTA}⚡{RESET} Thanks for using {BOLD}agentgsd{RESET}")
    print_stats(token_stats, context_window)
    print(f"{DIM}└─{RESET}\n")


def main_interaction_loop(
    client: ApiClient, registry: ToolRegistry, skills: List[Any], config, system_prompt: str
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
    from shared.utils.colors import RED, RESET

    messages: List[Dict[str, Any]] = []
    token_stats = {"input": 0, "output": 0, "total": 0}

    while True:
        try:
            result = handle_user_input(registry, skills, messages, token_stats)

            if result == "quit":
                print_exit_message(token_stats, config.context_window)
                break
            if result is None:
                continue

            # Process agent interaction
            process_agent_loop(client, registry, messages, token_stats, system_prompt)

            # Display token statistics
            print_stats(token_stats, config.context_window)

        except (KeyboardInterrupt, EOFError):
            print_exit_message(token_stats, config.context_window)
            break
        except Exception as err:
            print(f"\n{RED}✗ Error: {err}{RESET}")
            import traceback

            traceback.print_exc()


def main():
    """
    Main entry point for the agentgsd coding assistant.
    """
    parser = argparse.ArgumentParser(description="agentgsd - elite coding assistant")
    parser.add_argument("--provider", help="API provider (openrouter, gemini, groq, mistral, ollama, lmstudio)")
    parser.add_argument("--model", help="Model identifier")
    parser.add_argument("--api-key", help="API key for the provider")
    args = parser.parse_args()

    # Set up environment
    client, registry, skills, config = setup_environment(
        provider=args.provider,
        model=args.model,
        api_key=args.api_key
    )

    # Build system prompt
    system_prompt = build_system_prompt()

    # Start main interaction loop
    main_interaction_loop(client, registry, skills, config, system_prompt)


if __name__ == "__main__":
    main()
