"""
Setup configuration for agentgsd-monorepo.

This file provides backward compatibility with older build systems that
expect a setup.py file. The actual configuration is defined in pyproject.toml
following PEP 517/518 standards.

Usage:
    # Install in development mode
    pip install -e .

    # Install with dev dependencies
    pip install -e ".[dev]"

    # Build a distribution
    python -m build

Note:
    Modern pip versions (>= 21.3) fully support pyproject.toml and this file
    is not strictly required. See PEP 517 and PEP 518 for more details.
"""

from setuptools import setup

if __name__ == "__main__":
    setup()
