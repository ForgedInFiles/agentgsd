# ApiClient Class Reference

The `ApiClient` class provides a unified interface for making API calls to either OpenRouter or Anthropic language models. It handles authentication, request formatting, token tracking, and response parsing.

## Overview

Located in `shared/api/client.py`, the `ApiClient` class is designed to be flexible and easy to use, supporting both OpenRouter and Anthropic providers with appropriate authentication methods.

## Class Definition

```python
class ApiClient:
    """
    API client for calling OpenRouter and Anthropic language models.
    
    This class provides a unified interface for making API calls to either
    OpenRouter or Anthropic. It handles authentication, request formatting,
    token tracking, and response parsing.
    """
```

## Constructor

### Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `provider` | str | The API provider to use. Either "openrouter" or "anthropic". | "openrouter" |
| `api_url` | Optional[str] | The base URL for API requests. If not provided, uses default based on provider. | None |
| `api_key` | Optional[str] | The API key for authentication. If not provided, reads from environment variable (OPENROUTER_API_KEY or ANTHROPIC_API_KEY). | None |
| `model` | Optional[str] | The model identifier to use. If not provided, uses default based on provider. | None |
| `max_tokens` | Optional[int] | Maximum tokens to generate in responses. | 8192 |
| `timeout` | int | Request timeout in seconds. | 120 |
| `http_referer` | str | HTTP Referer header for OpenRouter. | "https://github.com/agentgsd" |
| `x_title` | str | X-Title header for OpenRouter. | "agentgsd" |
| `anthropic_version` | str | Anthropic API version header. | "2023-06-01" |

### Usage Examples

```python
# Use defaults (OpenRouter)
client = ApiClient()

# Use Anthropic with explicit credentials
client = ApiClient(
    provider="anthropic",
    api_key="sk-ant-...",
    model="claude-3-5-sonnet-20241022"
)

# Use custom OpenRouter endpoint
client = ApiClient(
    api_url="https://openrouter.ai/api/v1/chat/completions",
    model="openai/gpt-4o"
)
```

## Methods

### `_build_headers() -> Dict[str, str]`

Build request headers based on the provider.

**Returns:** Dictionary of HTTP headers appropriate for the configured provider.

**Example:**
```python
client = ApiClient()
headers = client._build_headers()
print(headers["Authorization"])  # Bearer sk-or-...
```

### `_build_payload(messages, system_prompt, tools=None) -> Dict[str, Any]`

Build the request payload based on the provider.

**Parameters:**
- `messages`: List of message dictionaries with 'role' and 'content'
- `system_prompt`: System prompt to guide the model's behavior
- `tools`: Optional list of tool definitions for function calling

**Returns:** Dictionary payload for the API request.

**Example:**
```python
client = ApiClient()
messages = [{"role": "user", "content": "Hello"}]
payload = client._build_payload(messages, "Be helpful.")
print(payload["model"])  # nvidia/nemotron-3-super-120b-a12b:free
```

### `call_api(messages, system_prompt, tools=None) -> Dict[str, Any]`

Call the API with the given messages and return the response.

This method sends a request to the configured API provider with the provided messages and system prompt. It handles authentication, builds the appropriate request headers and payload, and tracks token usage.

**Parameters:**
- `messages`: List of message dictionaries. Each message should have 'role' (one of "system", "user", "assistant", or "tool") and 'content' (string or list of content blocks). For tool results, include 'tool_use_id' to reference the original tool call.
- `system_prompt`: System prompt that guides the model's behavior and provides context about the assistant's capabilities.
- `tools`: Optional list of tool definitions for function calling. Each tool should have 'name', 'description', and 'input_schema'. Use `make_schema()` to generate this from a tool registry.

**Returns:** Dictionary containing the API response.

**For OpenRouter, typical structure:**
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

**For Anthropic, typical structure:**
```json
{
  "id": "msg_...",
  "model": "claude-3-5-sonnet-20241022",
  "content": [{"type": "text", "text": "..."}],
  "usage": {
    "input_tokens": 100,
    "output_tokens": 50
  }
}
```

**Raises:**
- `urllib.error.URLError`: If the request fails due to network issues.
- `ValueError`: If the API returns an error response.
- `TimeoutError`: If the request times out.

**Example:**
```python
client = ApiClient()
messages = [
    {"role": "user", "content": "What files are in the current directory?"}
]
response = client.call_api(
    messages,
    "You are a helpful coding assistant.",
    tools=client.make_schema()
)

# Process response
for block in response.get("content", []):
    if block["type"] == "text":
        print(block["text"])
    elif block["type"] == "tool_use":
        print(f"Tool call: {block['name']}")
```

### `get_usage() -> Dict[str, int]`

Get the cumulative token usage statistics.

**Returns:** Dictionary with 'input_tokens', 'output_tokens', and 'total_tokens'.

**Example:**
```python
client = ApiClient()
client.call_api(messages, "System prompt")
usage = client.get_usage()
print(f"Total tokens used: {usage['total_tokens']}")  # Total tokens used: 150
```

### `reset_usage() -> None`

Reset the token usage counters to zero.

**Example:**
```python
client = ApiClient()
client.call_api(messages, "System prompt")
print(client.get_usage()["total_tokens"])  # 150
client.reset_usage()
print(client.get_usage()["total_tokens"])  # 0
```

### `make_schema(tools=None) -> List[Dict[str, Any]]`

Generate tool schema for API function calling.

This method converts a tool registry (dictionary of tool definitions) into the format required by OpenRouter/Anthropic for function calling.

**Parameters:**
- `tools`: Optional dictionary of tool definitions. If not provided, returns an empty list. The dictionary should have tool names as keys and tuples of (description, parameters, function) as values, where:
  - description: Human-readable description of what the tool does
  - parameters: Dictionary of parameter names to types (e.g., {"path": "string", "content": "string"})
    Use "type?" suffix for optional parameters (e.g., {"limit": "number?"})
  - function: The callable to execute

**Returns:** List of tool schema dictionaries, each containing:
- name: Tool name
- description: Human-readable description
- input_schema: JSON schema for tool input

**Example:**
```python
def read_file(args):
    with open(args["path"]) as f:
        return f.read()

tools = {
    "read": (
        "Read file content",
        {"path": "string"},
        read_file
    ),
    "write": (
        "Write content to file",
        {"path": "string", "content": "string"},
        lambda args: open(args["path"], "w").write(args["content"])
    )
}

schema = ApiClient.make_schema(tools)
print(json.dumps(schema, indent=2))
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
```

**Example with optional parameters:**
```python
tools = {
    "head": (
        "Show first N lines of file",
        {"path": "string", "n": "number?"},
        head_file
    )
}
schema = ApiClient.make_schema(tools)
# 'n' will not be in 'required' list
```

## Token Tracking

The `ApiClient` automatically tracks token usage for all API calls made through it. Usage statistics are available via the `get_usage()` method and can be reset with `reset_usage()`.

The tracking includes:
- Input tokens (tokens sent to the model)
- Output tokens (tokens generated by the model)
- Total tokens (sum of input and output)

## Provider-Specific Details

### OpenRouter

When using the OpenRouter provider:
- Authentication: Bearer token in Authorization header
- Required headers: `Authorization`, `HTTP-Referer`, `X-Title`
- System prompt format: String value in `system` field
- Default model: `nvidia/nemotron-3-super-120b-a12b:free`
- Default URL: `https://openrouter.ai/api/v1/messages`

### Anthropic

When using the Anthropic provider:
- Authentication: `x-api-key` header
- Required headers: `x-api-key`, `anthropic-version`
- System prompt format: Array of content blocks in `system` field
- Default model: `claude-3-5-sonnet-20241022`
- Default URL: `https://api.anthropic.com/v1/messages`

## Error Handling

The `ApiClient` handles various error conditions:

1. **Missing API Key**: Raises `EnvironmentError` if API key is not provided and not set in environment
2. **Invalid Provider**: Raises `ValueError` if provider is not "openrouter" or "anthropic"
3. **API Errors**: Raises `ValueError` with error message from API response
4. **Network Errors**: Propagates `urllib.error.URLError` for network issues
5. **Timeouts**: Raises `TimeoutError` if request exceeds timeout duration

Example error handling:
```python
try:
    client = ApiClient()
    response = client.call_api(messages, system_prompt)
except EnvironmentError as e:
    print(f"API key error: {e}")
except ValueError as e:
    print(f"API error: {e}")
except urllib.error.URLError as e:
    print(f"Network error: {e}")
```

## Integration with agentgsd

In the agentgsd application, the `ApiClient` is used indirectly through the `call_api` function in `agentgsd.py`, which creates an instance with default OpenRouter settings and handles the conversational loop.

To use the `ApiClient` directly in your own code or skills:

```python
from shared.api.client import ApiClient

# Initialize client
client = ApiClient()

# Make API call
messages = [{"role": "user", "content": "Explain quantum computing"}]
response = client.call_api(
    messages,
    "You are a physics expert.",
    tools=client.make_schema(TOOLS)  # Pass your tool registry
)

# Handle response
for block in response.get("content", []):
    if block["type"] == "text":
        print(block["text"])
    elif block["type"] == "tool_use":
        # Execute tool and continue conversation
        tool_result = execute_tool(block)
        # Continue conversation with tool result
```

## Best Practices

1. **Environment Variables**: Store API keys in environment variables rather than hardcoding
2. **Token Management**: Monitor token usage with `get_usage()` to avoid exceeding context limits
3. **Error Handling**: Always wrap API calls in try-except blocks to handle network and API errors gracefully
4. **Tool Schema**: Use `make_schema()` to generate proper tool definitions for function calling
5. **Provider Selection**: Choose the appropriate provider based on your needs (OpenRouter for model variety, Anthropic for specific Claude models)
6. **Timeouts**: Adjust timeout values based on expected response lengths and model complexity

## See Also

- [Tools Documentation](./TOOLS.md) - For information about available tools
- [Skills Documentation](./SKILLS.md) - For information about the skills system
- [Main Application](../agentgsd.py) - For how the API client is used in agentgsd