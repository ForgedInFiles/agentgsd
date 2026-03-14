"""
Key bindings for prompt_toolkit integration.

This module contains functions for creating and managing key bindings
for the terminal-based AI coding assistant interface.
"""

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

from shared.utils.colors import BOLD, RED, RESET, YELLOW


def create_keybindings() -> KeyBindings:
    """
    Create key bindings for the prompt_toolkit interface.

    Returns:
        KeyBindings: Configured key bindings for the application.
    """
    kb = KeyBindings()

    @kb.add(Keys.ControlC, eager=True)
    def _(event):
        """Handle Ctrl+C - send keyboard interrupt."""
        event.app.exit(exception=KeyboardInterrupt(), style="class:aborting")

    @kb.add(Keys.ControlD, eager=True)
    def _(event):
        """Handle Ctrl+D - send EOF."""
        buffer = event.current_buffer
        if buffer.text:
            buffer.delete(len(buffer.text))
        else:
            event.app.exit(exception=EOFError(), style="class:aborting")

    @kb.add(Keys.Enter, eager=False)
    def _(event):
        """Handle Enter - accept line if complete, otherwise insert newline."""
        buff = event.current_buffer
        if buff.complete_state:
            # Get the completion object from the complete_state
            completion = None
            if hasattr(buff.complete_state, "completion"):
                completion = buff.complete_state.completion
            elif hasattr(buff.complete_state, "current_completion"):
                completion = buff.complete_state.current_completion

            if completion is not None:
                buff.apply_completion(completion)
            else:
                # Fallback: just validate and handle
                buff.validate_and_handle()
        else:
            buff.validate_and_handle()

    @kb.add(Keys.Tab, eager=True)
    def _(event):
        """Handle Tab - trigger completion."""
        buff = event.current_buffer
        if buff.complete_state:
            buff.complete_next()
        else:
            buff.start_completion()

    @kb.add(Keys.BackTab, eager=True)
    def _(event):
        """Handle Shift+Tab - trigger completion backwards."""
        buff = event.current_buffer
        if buff.complete_state:
            buff.complete_previous()
        else:
            buff.start_completion()

    return kb
