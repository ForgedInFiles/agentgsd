"""
ANSI color constants and spinner utilities for terminal output.

This module provides:
- ANSI escape code constants for text styling and colors
- Spinner class for animated terminal spinners
- Factory functions for common spinner types

Example usage:
    from shared.utils.colors import BOLD, BLUE, RESET

    print(f"{BOLD}{BLUE}Important text{RESET}")

    # Using spinners
    from shared.utils.colors import thinking_spinner

    spinner = thinking_spinner("Thinking...")
    spinner.start()
    # ... do work ...
    spinner.stop("Complete!")
"""

import sys
import threading
import time

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"

BLUE = "\033[34m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"
WHITE = "\033[37m"

BG_BLUE = "\033[44m"
BG_DIM = "\033[100m"

SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
THINKING_FRAMES = ["◇◇◇", "◆◇◇", "◇◆◇", "◇◆◆", "◆◆◇", "◇◇◆"]


class Spinner:
    """
    Animated spinner for displaying loading states in the terminal.

    The spinner runs in a separate thread and continuously updates the terminal
    with a rotating animation frame. This provides visual feedback during
    long-running operations.

    Attributes:
        message: The text message displayed alongside the spinner.
        frames: List of animation frames to cycle through.
        color: ANSI color code for the spinner animation.
        running: Boolean indicating if the spinner is currently active.
        thread: The threading.Thread instance running the animation.

    Example:
        >>> spinner = Spinner("Loading data...", SPINNER_FRAMES, CYAN)
        >>> spinner.start()
        >>> # ... perform long operation ...
        >>> spinner.stop("Data loaded!")
        Loading data... ⣽
        Data loaded!
    """

    def __init__(self, message="", frames=SPINNER_FRAMES, color=DIM):
        """
        Initialize a new Spinner instance.

        Args:
            message: Initial message to display with the spinner.
            frames: List of Unicode characters to use as animation frames.
                    Defaults to standard spinner frames.
            color: ANSI color code to use for the spinner. Defaults to DIM.
        """
        self.message = message
        self.frames = frames
        self.color = color
        self.running = False
        self.thread = None

    def _spin(self):
        """
        Internal method that runs the spinner animation loop.

        Continuously cycles through frames and updates the terminal until
        self.running is set to False. Clears the line when stopped.
        """
        i = 0
        while self.running:
            frame = self.frames[i % len(self.frames)]
            sys.stdout.write(f"\r{self.color}{frame}{RESET} {self.message}")
            sys.stdout.flush()
            time.sleep(0.08)
            i += 1
        sys.stdout.write("\r" + " " * (len(self.message) + 5) + "\r")
        sys.stdout.flush()

    def start(self, message=None):
        """
        Start the spinner animation in a background thread.

        Args:
            message: Optional new message to display. If provided, updates
                    self.message before starting.

        Returns:
            Self, for method chaining.

        Example:
            >>> spinner = Spinner()
            >>> spinner.start("Processing")
            >>> # Spinner is now running
        """
        if message:
            self.message = message
        self.running = True
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()
        return self

    def stop(self, final=""):
        """
        Stop the spinner animation.

        Args:
            final: Optional final message to display after stopping.
                  If provided, prints the message to stdout.

        Example:
            >>> spinner = Spinner("Loading...")
            >>> spinner.start()
            >>> # ... do work ...
            >>> spinner.stop("Complete!")
            Complete!
        """
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.5)
        if final:
            sys.stdout.write(f"{final}\n")
            sys.stdout.flush()


def thinking_spinner(message="Thinking"):
    """
    Create a spinner with thinking/diamond animation frames.

    This factory function creates a Spinner instance pre-configured with
    diamond-shaped animation frames (◆◇◇, ◇◆◇, etc.) in magenta color,
    ideal for displaying AI "thinking" states.

    Args:
        message: The message to display with the spinner. Defaults to "Thinking".

    Returns:
        A Spinner instance configured with thinking animation frames.

    Example:
        >>> spinner = thinking_spinner("Analyzing request...")
        >>> spinner.start()
        >>> response = api.call(prompt)
        >>> spinner.stop("Analysis complete!")
    """
    return Spinner(message, THINKING_FRAMES, MAGENTA)


def loading_spinner(message="Loading"):
    """
    Create a spinner with standard loading animation.

    This factory function creates a Spinner instance pre-configured with
    the standard braille-dot spinner frames (⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏) in cyan color,
    ideal for general loading states.

    Args:
        message: The message to display with the spinner. Defaults to "Loading".

    Returns:
        A Spinner instance configured with standard loading animation frames.

    Example:
        >>> spinner = loading_spinner("Fetching data...")
        >>> spinner.start()
        >>> data = fetch_from_api()
        >>> spinner.stop(f"Got {len(data)} items!")
    """
    return Spinner(message, SPINNER_FRAMES, CYAN)
