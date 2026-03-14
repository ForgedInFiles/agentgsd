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
    API client for calling various language model providers.

    This class provides an interface for making API calls to different providers
    including OpenRouter, Gemini, Groq, Mistral, Ollama, and LMStudio.
    """

    def __init__(
        self,
        provider: str = "openrouter",
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        timeout: int = 120,
    ):
        """
        Initialize the API client.

        Args:
            provider: The API provider to use.
            api_url: The base URL for API requests.
            api_key: The API key for authentication.
            model: The model identifier to use.
            max_tokens: Maximum tokens to generate in responses.
            timeout: Request timeout in seconds.
        """
        self.provider = provider.lower()
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens or 8192
        self.timeout = timeout

        # OpenRouter-specific headers defaults
        self.http_referer = "https://github.com/agentgsd"
        self.x_title = "agentgsd"

        # Token usage tracking
        self._input_tokens = 0
        self._output_tokens = 0

    def _build_headers(self) -> Dict[str, str]:
        """
        Build request headers based on the provider.
        """
        headers = {"Content-Type": "application/json"}

        if self.provider == "gemini":
            # Gemini native API uses x-goog-api-key or key as query param
            # But if we use the OpenAI-compatible endpoint, it might use Bearer
            if self.api_key:
                headers["x-goog-api-key"] = self.api_key
        elif self.provider == "ollama" or self.provider == "lmstudio":
            # Usually no auth required for local providers
            pass
        else:
            # OpenRouter, Groq, Mistral use Bearer token
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

        if self.provider == "openrouter":
            headers["HTTP-Referer"] = self.http_referer
            headers["X-Title"] = self.x_title

        return headers

    def _build_payload(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Build the request payload based on the provider.
        """
        # Most providers are OpenAI-compatible
        payload: Dict[str, Any] = {
            "model": self.model,
            "max_tokens": self.max_tokens,
        }

        if self.provider == "openrouter":
            payload["messages"] = messages
            if system_prompt:
                payload["system"] = system_prompt
            if tools:
                payload["tools"] = tools
            return payload

        # Default OpenAI-compatible format translation
        openai_messages = []
        if system_prompt:
            openai_messages.append({"role": "system", "content": system_prompt})

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")

            if role == "assistant" and isinstance(content, list):
                # Handle assistant message with tool calls
                text_content = ""
                tool_calls = []
                for block in content:
                    if block.get("type") == "text":
                        text_content += block.get("text", "")
                    elif block.get("type") == "tool_use":
                        tool_calls.append(
                            {
                                "id": block.get("id"),
                                "type": "function",
                                "function": {
                                    "name": block.get("name"),
                                    "arguments": json.dumps(block.get("input", {})),
                                },
                            }
                        )

                assist_msg = {"role": "assistant"}
                if text_content:
                    assist_msg["content"] = text_content
                if tool_calls:
                    assist_msg["tool_calls"] = tool_calls
                openai_messages.append(assist_msg)

            elif (
                role == "user"
                and isinstance(content, list)
                and content
                and content[0].get("type") == "tool_result"
            ):
                # Handle tool results
                for block in content:
                    if block.get("type") == "tool_result":
                        openai_messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": block.get("tool_use_id"),
                                "content": str(block.get("content", "")),
                            }
                        )
            else:
                # Regular user or assistant message
                if isinstance(content, list):
                    text = "".join(b.get("text", "") for b in content if b.get("type") == "text")
                    openai_messages.append({"role": role, "content": text})
                else:
                    openai_messages.append({"role": role, "content": content})

        payload["messages"] = openai_messages
        if tools:
            # Translate tools to OpenAI format
            openai_tools = []
            for tool in tools:
                openai_tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": tool["name"],
                            "description": tool["description"],
                            "parameters": tool["input_schema"],
                        },
                    }
                )
            payload["tools"] = openai_tools

        return payload

    def call_api(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Call the API and return the response in a normalized format.

        Args:
            messages: List of message dictionaries.
            system_prompt: System prompt string.
            tools: Optional list of tool definitions.
            max_retries: Maximum number of retry attempts for transient errors.
        """
        import time
        import socket

        headers = self._build_headers()
        payload = self._build_payload(messages, system_prompt, tools)

        api_url = self.api_url

        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(api_url, data=data, headers=headers, method="POST")

        last_error = None
        for attempt in range(max_retries):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    response_data = response.read().decode("utf-8")
                    result = json.loads(response_data)

                    # Track token usage
                    usage = result.get("usage", {})
                    self._input_tokens += usage.get("prompt_tokens", usage.get("input_tokens", 0))
                    self._output_tokens += usage.get(
                        "completion_tokens", usage.get("output_tokens", 0)
                    )

                    # Normalize response to Anthropic-style used by agentgsd
                    normalized_result = {
                        "id": result.get("id"),
                        "model": result.get("model"),
                        "content": [],
                        "usage": {
                            "input_tokens": usage.get(
                                "prompt_tokens", usage.get("input_tokens", 0)
                            ),
                            "output_tokens": usage.get(
                                "completion_tokens", usage.get("output_tokens", 0)
                            ),
                        },
                    }

                    if "choices" in result:
                        # OpenAI style
                        choice = result["choices"][0]
                        message = choice.get("message", {})
                        if message.get("content"):
                            normalized_result["content"].append(
                                {"type": "text", "text": message["content"]}
                            )

                        if message.get("tool_calls"):
                            for tool_call in message["tool_calls"]:
                                fn = tool_call.get("function", {})
                                normalized_result["content"].append(
                                    {
                                        "type": "tool_use",
                                        "id": tool_call.get("id"),
                                        "name": fn.get("name"),
                                        "input": json.loads(fn.get("arguments", "{}")),
                                    }
                                )
                    else:
                        # Assume it's already in the expected format (OpenRouter/Anthropic)
                        normalized_result = result

                    return normalized_result

            except (urllib.error.HTTPError, TimeoutError, socket.timeout) as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 2**attempt  # Exponential backoff: 1s, 2s, 4s
                    print(
                        f"\n⚠ Request timed out (attempt {attempt + 1}/{max_retries}). Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                continue

        # All retries failed
        if isinstance(last_error, urllib.error.HTTPError):
            try:
                error_body = last_error.read().decode("utf-8")
                error_json = json.loads(error_body)
                error_msg = error_json.get("error", {}).get("message", str(last_error))
            except (json.JSONDecodeError, AttributeError):
                error_msg = (
                    f"HTTP {last_error.code}: {error_body}"
                    if hasattr(last_error, "code")
                    else str(last_error)
                )
            raise ValueError(f"API error after {max_retries} retries: {error_msg}") from last_error
        else:
            raise ValueError(
                f"Request timed out after {max_retries} retries: {last_error}"
            ) from last_error

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
