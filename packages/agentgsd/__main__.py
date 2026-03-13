"""
Entry point for running agentgsd as a module.

This module allows running the agentgsd package as a Python module using:
    python -m agentgsd

Or from the packages directory:
    python -m packages.agentgsd
"""

from packages.agentgsd.main import main

if __name__ == "__main__":
    main()
