"""
Shared API client module for AI coding assistants.

This package provides a reusable API client for calling OpenRouter and Anthropic APIs.
It handles authentication, request building, token tracking, and tool schema generation.

Usage:
    from shared.api import ApiClient

    # Initialize with default OpenRouter settings
    client = ApiClient()

    # Or configure for Anthropic
    client = ApiClient(
        provider="anthropic",
        api_url="https://api.anthropic.com/v1/messages",
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
        model="claude-3-5-sonnet-20241022"
    )

    # Make an API call
    response = client.call_api(
        messages=[{"role": "user", "content": "Hello!"}],
        system_prompt="You are a helpful assistant."
    )

    # Get token usage statistics
    usage = client.get_usage()
    print(f"Input tokens: {usage['input_tokens']}")
    print(f"Output tokens: {usage['output_tokens']}")
"""

from .client import ApiClient

__all__ = ["ApiClient"]
