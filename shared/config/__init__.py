"""Configuration management module for the monorepo.

This module provides configuration management for the application,
including API settings, model configuration, and path settings.

Example usage:
    >>> from shared.config import load_config, default_config, Config

    >>> # Load configuration from environment variables
    >>> config = load_config()

    >>> # Or use default configuration
    >>> config = default_config()

    >>> # Access configuration values
    >>> print(config.model)
    >>> print(config.api_key)
"""

from shared.config.settings import Config, default_config, load_config

__all__ = ["Config", "default_config", "load_config"]
