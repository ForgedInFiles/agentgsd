"""Configuration settings for the monorepo.

This module provides configuration classes and functions for managing
OpenRouter API settings, model selection, and application configuration.

Environment Variables:
    OPENROUTER_API_KEY (str): API key for OpenRouter service.
    MODEL (str): Model identifier. Default: "nvidia/nemotron-3-super-120b-a12b:free"
    MAX_TOKENS (int): Maximum tokens for API responses. Default: 8192.
    CONTEXT_WINDOW (int): Context window size for models. Default: 200000.
    SKILLS_PATH (str): Path to skills directory. Default: "./skills".
    API_TIMEOUT (int): Timeout for API requests in seconds. Default: 120.
    OPENROUTER_API_URL (str): Custom URL for OpenRouter API. Optional.

Example usage:
    Load configuration from environment variables:
        >>> import os
        >>> os.environ["OPENROUTER_API_KEY"] = "sk-or-..."
        >>> os.environ["MODEL"] = "nvidia/nemotron-3-super-120b-a12b:free"
        >>> os.environ["MAX_TOKENS"] = "4096"
        >>>
        >>> config = load_config()
        >>> print(config.provider)
        openrouter
        >>> print(config.model)
        nvidia/nemotron-3-super-120b-a12b:free
        >>> print(config.max_tokens)
        4096

    Use default configuration:
        >>> config = default_config()
        >>> print(config.provider)
        openrouter
        >>> print(config.model)
        nvidia/nemotron-3-super-120b-a12b:free
        >>> print(config.api_url)
        https://openrouter.ai/api/v1

    Access configuration values:
        >>> config = load_config()
        >>> print(f"Using {config.model} via OpenRouter")
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Configuration class for managing application settings.

    This class holds all configuration settings including API provider,
    API keys, model selection, and various operational parameters.

    Attributes:
        api_key: The API key for the selected service.
        api_url: The base URL for the API endpoint.
        model: The model identifier to use.
        max_tokens: Maximum number of tokens for API responses.
        context_window: Context window size for the model.
        skills_path: Path to the skills directory.
        timeout: Timeout for API requests in seconds.
        provider: The API provider to use (openrouter, gemini, groq, mistral, ollama, lmstudio).

    Example:
        >>> config = Config(
        ...     api_key="sk-or-...",
        ...     api_url="https://openrouter.ai/api/v1",
        ...     model="nvidia/nemotron-3-super-120b-a12b:free",
        ...     max_tokens=8192,
        ...     context_window=200000,
        ...     skills_path="./skills",
        ...     timeout=120,
        ...     provider="openrouter"
        ... )
        >>> print(config.model)
        nvidia/nemotron-3-super-120b-a12b:free
    """

    api_key: str
    api_url: str
    model: str
    max_tokens: int
    context_window: int
    skills_path: str
    timeout: int
    provider: str = "openrouter"


def default_config(provider: str = "openrouter") -> Config:
    """Create a Config instance with default values for a provider.

    Returns a Config object populated with default settings based on provider.

    Args:
        provider: The API provider (default: "openrouter").

    Returns:
        Config: A configuration object with default values.
    """
    defaults = {
        "openrouter": {
            "url": "https://openrouter.ai/api/v1/messages",
            "model": "nvidia/nemotron-3-super-120b-a12b:free",
        },
        "gemini": {
            "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
            "model": "gemini-3.1-flash-lite-preview",
        },
        "groq": {
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "model": "llama-3.3-70b-versatile",
        },
        "mistral": {
            "url": "https://api.mistral.ai/v1/chat/completions",
            "model": "mistral-large-latest",
        },
        "ollama": {
            "url": "http://localhost:11434/v1/chat/completions",
            "model": "llama3.3",
        },
        "lmstudio": {
            "url": "http://localhost:1234/v1/chat/completions",
            "model": "local-model",
        },
    }

    provider_defaults = defaults.get(provider, defaults["openrouter"])

    return Config(
        api_key="",
        api_url=provider_defaults["url"],
        model=provider_defaults["model"],
        max_tokens=8192,
        context_window=200000,
        skills_path="./skills",
        timeout=120,
        provider=provider,
    )


def load_config(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Config:
    """Load configuration from environment variables and optional overrides.

    Reads configuration from environment variables with fallbacks to default
    values. Overrides with provided arguments if available.

    Args:
        provider: Optional provider override.
        model: Optional model override.
        api_key: Optional API key override.

    Returns:
        Config: A configuration object populated from environment variables
            with defaults applied for any missing values.

    Raises:
        ValueError: If required API key is missing.
    """
    # 1. Determine provider
    provider = provider or os.environ.get("PROVIDER", "openrouter").lower()
    
    # 2. Get defaults for that provider
    config = default_config(provider)

    # 3. Determine API Key
    if api_key:
        config.api_key = api_key
    else:
        # Provider-specific env vars
        env_vars = {
            "openrouter": "OPENROUTER_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "groq": "GROQ_API_KEY",
            "mistral": "MISTRAL_API_KEY",
        }
        env_var = env_vars.get(provider)
        if env_var:
            config.api_key = os.environ.get(env_var, "")
        
        # Generic fallback
        if not config.api_key:
            config.api_key = os.environ.get("API_KEY", "")

    # 4. Determine Model
    config.model = model or os.environ.get("MODEL", config.model)

    # 5. Determine API URL
    url_env_vars = {
        "openrouter": "OPENROUTER_API_URL",
        "gemini": "GEMINI_API_URL",
        "groq": "GROQ_API_URL",
        "mistral": "MISTRAL_API_URL",
        "ollama": "OLLAMA_API_URL",
        "lmstudio": "LMSTUDIO_API_URL",
    }
    url_env_var = url_env_vars.get(provider)
    if url_env_var:
        config.api_url = os.environ.get(url_env_var, config.api_url)

    # 6. Other settings
    config.max_tokens = int(os.environ.get("MAX_TOKENS", config.max_tokens))
    config.context_window = int(os.environ.get("CONTEXT_WINDOW", config.context_window))
    config.skills_path = os.environ.get("SKILLS_PATH", config.skills_path)
    config.timeout = int(os.environ.get("API_TIMEOUT", config.timeout))

    return config
