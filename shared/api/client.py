"""
API client for calling OpenRouter language models.

This class provides an interface for making API calls to OpenRouter.
It handles authentication, request formatting, token tracking, and response parsing.
"""

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional


class ApiClient:
    """
    API client for calling OpenRouter language models.

    This class provides an interface for making API calls to OpenRouter.
    It handles authentication, request formatting, token tracking, and response parsing.

    Attributes:
        provider: The API provider (always "openrouter").
        api_url: The base URL for API requests.
        api_key: The API key for authentication.
        model: The model identifier to use.
        max_tokens: Maximum tokens to generate in responses.
        timeout: Request timeout in seconds.
        http_referer: HTTP Referer header (OpenRouter only).
        x_title: X-Title header (OpenRouter only).

    Example:
        >>> client = ApiClient()
        >>> messages = [{"role": "user", "content": "What is 2+2?"}]
        >>> response = client.call_api(messages, "You are a math assistant.")
        >>> print(response["content"][0]["text"])
        4
    """

    DEFAULT_OPENROUTER_URL = "https://openrouter.ai/api/v1/messages"
    DEFAULT_OPENROUTER_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
    DEFAULT_MAX_TOKENS = 8192

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        timeout: int = 120,
        http_referer: str = "https://github.com/agentgsd",
        x_title: str = "agentgsd",
    ):
        """
        Initialize the API client.

        Args:
            api_url: The base URL for API requests. If not provided, uses default.
            api_key: The API key for authentication. If not provided, reads from
                     environment variable OPENROUTER_API_KEY.
            model: The model identifier to use. If not provided, uses default.
            max_tokens: Maximum tokens to generate in responses. Defaults to 8192.
            timeout: Request timeout in seconds. Defaults to 120.
            http_referer: HTTP Referer header for OpenRouter. Defaults to GitHub URL.
            x_title: X-Title header for OpenRouter. Defaults to "agentgsd".
        """
        self.provider = "openrouter"  # Always use OpenRouter

        self.api_url = api_url or self.DEFAULT_OPENROUTER_URL

        env_key = "OPENROUTER_API_KEY"
        self.api_key = api_key or os.environ.get(env_key)
        if not self.api_key:
            raise EnvironmentError(
                f"API key not provided and {env_key} environment variable not set. "
                f"Get your key at: https://openrouter.ai/keys"
            )

        self.model = model or self.DEFAULT_OPENROUTER_MODEL

        self.max_tokens = max_tokens or self.DEFAULT_MAX_TOKENS
        self.timeout = timeout

        # OpenRouter-specific headers
        self.http_referer = http_referer
        self.x_title = x_title

        # Token usage tracking
        self._input_tokens = 0
        self._output_tokens = 0

    def _build_headers(self) -> Dict[str, str]:
        """
        Build request headers for OpenRouter.

        Returns:
            Dictionary of HTTP headers for OpenRouter API.

        Example:
            >>> client = ApiClient()
            >>> headers = client._build_headers()
            >>> print(headers["Authorization"])
            Bearer sk-or-...
        """
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": self.http_referer,
            "X-Title": self.x_title,
        }

    def _build_payload(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Build the request payload for OpenRouter.

        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            system_prompt: System prompt to guide the model's behavior.
            tools: Optional list of tool definitions for function calling.

        Returns:
            Dictionary payload for the API request.

        Example:
            >>> client = ApiClient()
            >>> messages = [{"role": "user", "content": "Hello"}]
            >>> payload = client._build_payload(messages, "Be helpful.")
            >>> print(payload["model"])
            nvidia/nemotron-3-super-120b-a12b:free
        """
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
        }

        if system_prompt:
            payload["system"] = system_prompt

        if tools:
            payload["tools"] = tools

        return payload

    def call_api(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Call the API with the given messages and return the response.

        This method sends a request to the OpenRouter API with the provided messages
        and system prompt. It handles authentication, builds the appropriate request
        headers and payload, and tracks token usage.

        Args:
            messages: List of message dictionaries. Each message should have 'role'
                      (one of "system", "user", "assistant", or "tool") and 'content'
                      (string or list of content blocks). For tool results, include
                      'tool_use_id' to reference the original tool call.
            system_prompt: System prompt that guides the model's behavior and provides
                          context about the assistant's capabilities.
            tools: Optional list of tool definitions for function calling. Each tool
                   should have 'name', 'description', and 'input_schema'. Use
                   make_schema() to generate this from a tool registry.

        Returns:
            Dictionary containing the API response.

        For OpenRouter, typical structure:
        ```json
        {
          "id": "msg_...",
          "model": "nvidia/nemotron-3-super-120b-a12b:free",
          "content": [{"type": "text", "text": "..."}],
          "usage": {
            "input_tokens": 100,
            "output_tokens": 50
          }
        }
        ```

        Raises:
            urllib.error.URLError: If the request fails due to network issues.
            ValueError: If the API returns an error response.
            TimeoutError: If the request times out.

        Example:
            >>> client = ApiClient()
            >>> messages = [
            ...     {"role": "user", "content": "What files are in the current directory?"}
            ... ]
            >>> response = client.call_api(
            ...     messages,
            ...     "You are a helpful coding assistant.",
            ...     tools=client.make_schema()
            ... )
            >>>
            >>> # Process response
            >>> for block in response.get("content", []):
            ...     if block["type"] == "text":
            ...         print(block["text"])
            ...     elif block["type"] == "tool_use":
            ...         print(f"Tool call: {block['name']}")
        """
        headers = self._build_headers()
        payload = self._build_payload(messages, system_prompt, tools)

        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(self.api_url, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                response_data = response.read().decode("utf-8")
                result = json.loads(response_data)

                # Track token usage
                usage = result.get("usage", {})
                self._input_tokens += usage.get("input_tokens", 0)
                self._output_tokens += usage.get("output_tokens", 0)

                return result

        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            try:
                error_json = json.loads(error_body)
                error_msg = error_json.get("error", {}).get("message", str(e))
            except json.JSONDecodeError:
                error_msg = f"HTTP {e.code}: {error_body}"
            raise ValueError(f"API error: {error_msg}") from e

    def get_usage(self) -> Dict[str, int]:
        """
        Get the cumulative token usage statistics.

        Returns:
            Dictionary with 'input_tokens', 'output_tokens', and 'total_tokens'.

        Example:
            >>> client = ApiClient()
            >>> client.call_api(messages, "System prompt")
            >>> usage = client.get_usage()
            >>> print(f"Total tokens used: {usage['total_tokens']}")  # Total tokens used: 150
        """
        return {
            "input_tokens": self._input_tokens,
            "output_tokens": self._output_tokens,
            "total_tokens": self._input_tokens + self._output_tokens,
        }

    def reset_usage(self) -> None:
        """
        Reset the token usage counters to zero.

        Example:
            >>> client = ApiClient()
            >>> client.call_api(messages, "System prompt")
            >>> print(client.get_usage()["total_tokens"])  # 150
            >>> client.reset_usage()
            >>> print(client.get_usage()["total_tokens"])  # 0
        """
        self._input_tokens = 0
        self._output_tokens = 0

    def make_schema(self, tools: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Generate tool schema for API function calling.

        This method converts a tool registry (dictionary of tool definitions) into the
        format required by OpenRouter for function calling.

        Args:
            tools: Optional dictionary of tool definitions. If not provided, returns
                   an empty list. The dictionary should have tool names as keys and
                   tuples of (description, parameters, function) as values, where:
                     - description: Human-readable description of what the tool does
                     - parameters: Dictionary of parameter names to types (e.g.,
                                   {"path": "string", "content": "string"})
                                   Use "type?" suffix for optional parameters
                                   (e.g., {"limit": "number?"})
                     - function: The callable to execute

        Returns:
            List of tool schema dictionaries, each containing:
              - name: Tool name
              - description: Human-readable description
              - input_schema: JSON schema for tool input

        Example:
            >>> def read_file(args):
            ...     with open(args["path"]) as f:
            ...         return f.read()
            >>>
            >>> tools = {
            ...     "read": (
            ...         "Read file content",
            ...         {"path": "string"},
            ...         read_file
            ...     ),
            ...     "write": (
            ...         "Write content to file",
            ...         {"path": "string", "content": "string"},
            ...         lambda args: open(args["path"], "w").write(args["content"])
            ...     )
            ... }
            >>>
            >>> schema = ApiClient.make_schema(tools)
            >>> print(json.dumps(schema, indent=2))
            # [
            #   {
            #     "name": "read",
            #     "description": "Read file content",
            #     "input_schema": {
            #       "type": "object",
            #       "properties": {"path": {"type": "string"}},
            #       "required": ["path"]
            #     }
            #   },
            #   ...
            # ]

        Example with optional parameters:
            >>> tools = {
            ...     "head": (
            ...         "Show first N lines of file",
            ...         {"path": "string", "n": "number?"},
            ...         head_file
            ...     )
            ... }
            >>> schema = ApiClient.make_schema(tools)
            >>> # 'n' will not be in 'required' list
        """
        result = []
        if tools:
            for tool_name, (description, parameters, _) in tools.items():
                properties = {}
                required = []
                for param_name, param_type in parameters.items():
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
                        "name": tool_name,
                        "description": description,
                        "input_schema": {
                            "type": "object",
                            "properties": properties,
                            "required": required,
                        },
                    }
                )
        return result
