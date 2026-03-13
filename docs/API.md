# ApiClient Class Reference

The `ApiClient` class provides a unified interface for making API calls to multiple language model providers including OpenRouter, Gemini, Groq, Mistral, Ollama, and LMStudio. It handles authentication, request formatting, token tracking, and response parsing.

## Overview

Located in `shared/api/client.py`, the `ApiClient` class is designed to be provider-aware, handling different authentication headers and translating between the assistant's internal message format and the formats required by various providers.

## Class Definition

```python
class ApiClient:
    """
    API client for calling various language model providers.
    
    This class provides an interface for making API calls to different providers
    including OpenRouter, Gemini, Groq, Mistral, Ollama, and LMStudio.
    """
```

## Constructor

### Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `provider` | str | The API provider to use (e.g., "openrouter", "gemini", "groq", "mistral", "ollama", "lmstudio"). | "openrouter" |
| `api_url` | Optional[str] | The base URL for API requests. | None |
| `api_key` | Optional[str] | The API key for authentication. | None |
| `model` | Optional[str] | The model identifier to use. | None |
| `max_tokens` | Optional[int] | Maximum tokens to generate in responses. | 8192 |
| `timeout` | int | Request timeout in seconds. | 120 |

### Usage Examples

```python
# Use defaults (OpenRouter)
client = ApiClient()

# Use Groq with explicit credentials
client = ApiClient(
    provider="groq",
    api_key="gsk_...",
    model="llama3-70b-8192"
)

# Use local Ollama
client = ApiClient(
    provider="ollama",
    api_url="http://localhost:11434/v1/chat/completions",
    model="llama3"
)
```

## Methods

### `_build_headers() -> Dict[str, str]`

Build request headers based on the provider.

**Returns:** Dictionary of HTTP headers appropriate for the configured provider.

### `_build_payload(messages, system_prompt, tools=None) -> Dict[str, Any]`

Build the request payload based on the provider. It handles the translation between the assistant's internal Anthropic-style messages and the OpenAI-style format used by many providers.

### `call_api(messages, system_prompt, tools=None) -> Dict[str, Any]`

Call the API with the given messages and return the response in a normalized format.

**Parameters:**
- `messages`: List of message dictionaries.
- `system_prompt`: System prompt that guides the model's behavior.
- `tools`: Optional list of tool definitions for function calling.

**Returns:** Dictionary containing the API response in a normalized Anthropic-style format.

**Normalized structure:**
```json
{
  "id": "msg_...",
  "model": "llama3-70b-8192",
  "content": [{"type": "text", "text": "..."}],
  "usage": {
    "input_tokens": 100,
    "output_tokens": 50
  }
}
```

## Token Tracking

The `ApiClient` automatically tracks token usage for all API calls. Usage statistics are available via `get_usage()` and can be reset with `reset_usage()`.

## Provider Configuration

See [Providers Documentation](./PROVIDERS.md) for detailed information about configuring each supported provider.

## Error Handling

The `ApiClient` handles various error conditions:

1. **Missing API Key**: Raises an error if an API key is required but not provided.
2. **API Errors**: Raises `ValueError` with descriptive error messages from the API response.
3. **Network Errors**: Propagates `urllib.error.URLError` for connectivity issues.

## See Also

- [CLI Documentation](./CLI.md) - For how to configure the client via CLI flags
- [Providers Documentation](./PROVIDERS.md) - For detailed provider information
- [Tools Documentation](./TOOLS.md) - For information about available tools

---

[← Back to Documentation](./README.md)
