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
        api_key: The API key for OpenRouter service.
        api_url: The base URL for the API endpoint.
        model: The model identifier to use.
        max_tokens: Maximum number of tokens for API responses.
        context_window: Context window size for the model.
        skills_path: Path to the skills directory.
        timeout: Timeout for API requests in seconds.
        provider: The API provider to use (always "openrouter").

    Example:
        >>> config = Config(
        ...     api_key="sk-or-...",
        ...     api_url="https://openrouter.ai/api/v1",
        ...     model="nvidia/nemotron-3-super-120b-a12b:free",
        ...     max_tokens=8192,
        ...     context_window=200000,
        ...     skills_path="./skills",
        ...     timeout=120
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


def default_config() -> Config:
    """Create a Config instance with default values.

    Returns a Config object populated with default settings:
    - Provider: "openrouter"
    - API URL: "https://openrouter.ai/api/v1"
    - Model: "nvidia/nemotron-3-super-120b-a12b:free"
    - Max tokens: 8192
    - Context window: 200000
    - Skills path: "./skills"
    - Timeout: 120 seconds

    Returns:
        Config: A configuration object with default values.

    Example:
        >>> config = default_config()
        >>> config.provider
        'openrouter'
        >>> config.model
        'nvidia/nemotron-3-super-120b-a12b:free'
        >>> config.max_tokens
        8192
    """
    return Config(
        api_key="",
        api_url="https://openrouter.ai/api/v1",
        model="nvidia/nemotron-3-super-120b-a12b:free",
        max_tokens=8192,
        context_window=200000,
        skills_path="./skills",
        timeout=120,
        provider="openrouter",
    )


def load_config() -> Config:
    """Load configuration from environment variables.

    Reads configuration from environment variables with fallbacks to default
    values. Configures OpenRouter API settings.

    Environment Variables:
        OPENROUTER_API_KEY: API key for OpenRouter service.
        MODEL: Model identifier. Default: "nvidia/nemotron-3-super-120b-a12b:free"
        MAX_TOKENS: Maximum tokens (default: 8192).
        CONTEXT_WINDOW: Context window size (default: 200000).
        SKILLS_PATH: Path to skills directory (default: "./skills").
        API_TIMEOUT: Request timeout in seconds (default: 120).
        OPENROUTER_API_URL: Custom OpenRouter URL (optional).

    Returns:
        Config: A configuration object populated from environment variables
            with defaults applied for any missing values.

    Raises:
        ValueError: If required API key is missing.

    Example:
        Basic usage with environment variables:
            >>> import os
            >>> os.environ["OPENROUTER_API_KEY"] = "sk-or-..."
            >>> os.environ["MODEL"] = "nvidia/nemotron-3-super-120b-a12b:free"
            >>> os.environ["MAX_TOKENS"] = "4096"
            >>>
            >>> config = load_config()
            >>> config.provider
            'openrouter'
            >>> config.model
            'nvidia/nemotron-3-super-120b-a12b:free'
            >>> config.max_tokens
            4096

        Custom model and settings:
            >>> os.environ["MODEL"] = "google/gemini-pro-1.5"
            >>> os.environ["MAX_TOKENS"] = "4096"
            >>> os.environ["API_TIMEOUT"] = "60"
            >>>
            >>> config = load_config()
            >>> config.model
            'google/gemini-pro-1.5'
            >>> config.timeout
            60
    """
    config = default_config()

    # API key (required)
    config.api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not config.api_key:
        raise ValueError(
            "API key not found for provider 'openrouter'. "
            "Set OPENROUTER_API_KEY environment variable."
        )

    # API URL
    config.api_url = os.environ.get("OPENROUTER_API_URL", "https://openrouter.ai/api/v1")

    # Model (with new default)
    config.model = os.environ.get("MODEL", "nvidia/nemotron-3-super-120b-a12b:free")

    # Other settings
    config.max_tokens = int(os.environ.get("MAX_TOKENS", config.max_tokens))
    config.context_window = int(os.environ.get("CONTEXT_WINDOW", config.context_window))
    config.skills_path = os.environ.get("SKILLS_PATH", config.skills_path)
    config.timeout = int(os.environ.get("API_TIMEOUT", config.timeout))
    config.provider = "openrouter"  # Always openrouter

    return config
