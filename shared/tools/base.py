"""
Base classes for the shared tool system.

This module provides the foundation for defining and managing tools in AI coding assistants.
It includes the Tool base class, ToolRegistry for managing tool collections, and the run_tool
utility function for executing tools with error handling.

The tool schema format follows the convention used in onyx.py and agentgsd.py:
    - Tool schema: (description, {param_name: param_type}, function)
    - Parameter types: "string", "number", "boolean" with optional "?" suffix for optional parameters

Example usage:
    # Define a custom tool
    class MyTool(Tool):
        def __init__(self):
            super().__init__(
                name="my_tool",
                description="A custom tool for doing something",
                parameters={"input": "string", "count": "number?"}
            )

        def execute(self, args):
            # Implementation here
            return f"Processed: {args['input']}"

    # Use the registry
    registry = ToolRegistry()
    registry.register(MyTool())

    # Get tool schema for API
    schema = registry.make_schema()

    # Execute with error handling
    result = run_tool(registry, "my_tool", {"input": "hello"})
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional


class Tool(ABC):
    """
    Abstract base class for all tools.

    Tools are the fundamental building blocks of the AI coding assistant system.
    Each tool has a name, description, parameter schema, and an execute method.

    Attributes:
        name: Unique identifier for the tool.
        description: Human-readable description of what the tool does.
        parameters: Dictionary mapping parameter names to type strings.
                    Types are "string", "number", or "boolean" with optional "?" suffix
                    for optional parameters (e.g., "string?", "number?").
        _callable: Optional callable that can be used as an alternative to subclassing.

    Example:
        >>> class ReadTool(Tool):
        ...     def __init__(self):
        ...         super().__init__(
        ...             name="read",
        ...             description="Read file content",
        ...             parameters={"path": "string", "offset": "number?", "limit": "number?"}
        ...         )
        ...
        ...     def execute(self, args):
        ...         with open(args["path"]) as f:
        ...             return f.read()

        >>> tool = ReadTool()
        >>> tool.name
        'read'
        >>> tool.parameters
        {'path': 'string', 'offset': 'number?', 'limit': 'number?'}
    """

    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, str],
        callable: Optional[Callable[[Dict[str, Any]], str]] = None,
    ):
        """
        Initialize a Tool instance.

        Args:
            name: Unique identifier for the tool (e.g., "read", "write", "grep").
            description: Human-readable description of the tool's purpose.
            parameters: Dictionary mapping parameter names to their types.
                        Use "string", "number", or "boolean" with "?" suffix for optional.
                        Example: {"path": "string", "limit": "number?"}
            callable: Optional callable to use instead of subclassing execute method.
                      This allows using simple functions as tools directly.
        """
        self.name = name
        self.description = description
        self.parameters = parameters
        self._callable = callable

    @abstractmethod
    def execute(self, args: Dict[str, Any]) -> str:
        """
        Execute the tool with the given arguments.

        This method must be implemented by subclasses. It should perform
        the tool's action and return a string result.

        Args:
            args: Dictionary of arguments to pass to the tool.
                  Required parameters must be present, optional parameters
                  may be omitted.

        Returns:
            str: The result of executing the tool, or an error message.

        Raises:
            NotImplementedError: If called on the base class without implementation.
            Exception: Any other exception raised during execution will be
                       caught by run_tool and converted to an error message.

        Example:
            >>> class ReadTool(Tool):
            ...     def execute(self, args):
            ...         path = args["path"]
            ...         with open(path) as f:
            ...             return f.read()
            >>> tool = ReadTool()
            >>> result = tool.execute({"path": "example.txt"})
        """
        if self._callable is not None:
            return self._callable(args)
        raise NotImplementedError("Tool subclasses must implement execute method")


class ToolRegistry:
    """
    Registry for managing collections of tools.

    The registry provides a central location to register, retrieve, and list tools.
    It also supports generating API schemas for tool definitions.

    Attributes:
        _tools: Internal dictionary mapping tool names to Tool instances.

    Example:
        >>> registry = ToolRegistry()
        >>> registry.register(ReadTool())
        >>> registry.register(WriteTool())
        >>> tool = registry.get("read")
        >>> tool.name
        'read'
        >>> all_tools = registry.list_tools()
        >>> len(all_tools)
        2
    """

    def __init__(self):
        """Initialize an empty ToolRegistry."""
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """
        Register a tool in the registry.

        Args:
            tool: Tool instance to register.

        Raises:
            ValueError: If a tool with the same name is already registered.

        Example:
            >>> registry = ToolRegistry()
            >>> registry.register(ReadTool())
            >>> # Now available via get()
            >>> tool = registry.get("read")
        """
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        """
        Retrieve a tool by name.

        Args:
            name: Name of the tool to retrieve.

        Returns:
            Tool: The registered tool.

        Raises:
            KeyError: If no tool with the given name is registered.

        Example:
            >>> registry = ToolRegistry()
            >>> registry.register(ReadTool())
            >>> tool = registry.get("read")
            >>> tool.description
            'Read file with line numbers'
        """
        if name not in self._tools:
            raise KeyError(f"Tool not found: {name}")
        return self._tools[name]

    def list_tools(self) -> List[Tool]:
        """
        List all registered tools.

        Returns:
            List[Tool]: List of all registered Tool instances, sorted by name.

        Example:
            >>> registry = ToolRegistry()
            >>> registry.register(WriteTool())
            >>> registry.register(ReadTool())
            >>> tools = registry.list_tools()
            >>> [t.name for t in tools]
            ['read', 'write']
        """
        return sorted(self._tools.values(), key=lambda t: t.name)

    def make_schema(self) -> List[Dict[str, Any]]:
        """
        Generate API schema for all registered tools.

        This method creates a list of tool definitions suitable for passing to
        LLM APIs that support tool/function calling. Each schema includes the
        tool name, description, and JSON schema for input parameters.

        Returns:
            List[Dict]: List of tool schema dictionaries with keys:
                - name: str - Tool identifier
                - description: str - Tool description
                - input_schema: dict - JSON schema for tool input

        Example:
            >>> registry = ToolRegistry()
            >>> registry.register(ReadTool())
            >>> schema = registry.make_schema()
            >>> schema[0]["name"]
            'read'
            >>> schema[0]["input_schema"]["properties"]["path"]["type"]
            'string'
        """
        result = []
        for tool in self.list_tools():
            properties = {}
            required = []
            for param_name, param_type in tool.parameters.items():
                is_optional = param_type.endswith("?")
                base_type = param_type.rstrip("?")
                if base_type == "number":
                    json_type = "integer"
                else:
                    json_type = base_type
                properties[param_name] = {"type": json_type}
                if not is_optional:
                    required.append(param_name)
            result.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": {
                        "type": "object",
                        "properties": properties,
                        "required": required,
                    },
                }
            )
        return result

    def __contains__(self, name: str) -> bool:
        """
        Check if a tool is registered by name.

        Args:
            name: Name of the tool to check.

        Returns:
            bool: True if tool is registered, False otherwise.

        Example:
            >>> registry = ToolRegistry()
            >>> registry.register(ReadTool())
            >>> "read" in registry
            True
            >>> "write" in registry
            False
        """
        return name in self._tools


def run_tool(registry: ToolRegistry, name: str, args: Dict[str, Any]) -> str:
    """
    Execute a tool by name with error handling.

    This is the primary function for executing tools in the system. It handles
    looking up the tool, validating inputs, executing the tool, and catching
    any errors that occur during execution.

    Args:
        registry: ToolRegistry instance containing the registered tools.
        name: Name of the tool to execute.
        args: Dictionary of arguments to pass to the tool.

    Returns:
        str: The result of executing the tool, or an error message starting with "error: "
             if the tool is not found or an exception occurs.

    Example:
        >>> registry = ToolRegistry()
        >>> registry.register(ReadTool())
        >>> result = run_tool(registry, "read", {"path": "example.txt"})
        >>> # Returns file content or error message
        >>> result = run_tool(registry, "nonexistent", {})
        >>> # Returns "error: Tool not found: nonexistent"
    """
    try:
        tool = registry.get(name)
    except KeyError:
        return f"error: Tool not found: {name}"

    try:
        return tool.execute(args)
    except Exception as err:
        return f"error: {err}"


def create_tool_from_function(
    name: str,
    description: str,
    parameters: Dict[str, str],
    func: Callable[[Dict[str, Any]], str],
) -> Tool:
    """
    Create a Tool instance from a simple function.

    This is a convenience function for creating tools from regular functions
    without needing to subclass Tool.

    Args:
        name: Unique identifier for the tool.
        description: Human-readable description of the tool.
        parameters: Dictionary mapping parameter names to type strings.
        func: Function to call when the tool is executed.

    Returns:
        Tool: A Tool instance that wraps the function.

    Raises:
        ValueError: If func is None.

    Example:
        >>> def read_file(args):
        ...     with open(args["path"]) as f:
        ...         return f.read()
        >>> tool = create_tool_from_function(
        ...     "read",
        ...     "Read file content",
        ...     {"path": "string"},
        ...     read_file
        ... )
        >>> tool.name
        'read'
    """
    if func is None:
        raise ValueError("func parameter cannot be None")

    class FunctionTool(Tool):
        """Tool wrapper for executing a simple function.
        
        This internal class wraps a callable function to make it compatible
        with the Tool interface. It's used by create_tool_from_function().
        """
        def __init__(self):
            super().__init__(name, description, parameters, func)

        def execute(self, args):
            """Execute the wrapped function with given arguments.
            
            Args:
                args: Dictionary of arguments to pass to the wrapped function
                
            Returns:
                str: Result of the function execution
                
            Raises:
                RuntimeError: If the wrapped function is None
            """
            if self._callable is None:
                raise RuntimeError("FunctionTool's callable is None")
            return self._callable(args)

    return FunctionTool()
