"""
Streaming Thought Process Visualization for agentgsd.

Displays the agent's reasoning in real-time without requiring
external APIs.
"""

import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
from threading import Lock


class ThoughtType(Enum):
    """Types of thoughts the agent can have."""

    ANALYSIS = "analysis"
    PLANNING = "planning"
    DECISION = "decision"
    EXECUTION = "execution"
    VALIDATION = "validation"
    CORRECTION = "correction"
    SUCCESS = "success"
    ERROR = "error"
    INFO = "info"


class ThoughtLevel(Enum):
    """Importance levels for thoughts."""

    DEBUG = "debug"
    INFO = "info"
    IMPORTANT = "important"
    CRITICAL = "critical"


@dataclass
class Thought:
    """Represents a single thought in the reasoning process."""

    id: str
    thought_type: ThoughtType
    level: ThoughtLevel
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    children: List["Thought"] = field(default_factory=list)
    expanded: bool = True


class ThoughtStream:
    """Manages the stream of thoughts for visualization."""

    THEME = {
        ThoughtType.ANALYSIS: ("💭", "cyan"),
        ThoughtType.PLANNING: ("📋", "yellow"),
        ThoughtType.DECISION: ("🤔", "magenta"),
        ThoughtType.EXECUTION: ("⚙️", "blue"),
        ThoughtType.VALIDATION: ("✅", "green"),
        ThoughtType.CORRECTION: ("🔧", "orange"),
        ThoughtType.SUCCESS: ("✓", "green"),
        ThoughtType.ERROR: ("✗", "red"),
        ThoughtType.INFO: ("ℹ️", "white"),
    }

    LEVEL_COLORS = {
        ThoughtLevel.DEBUG: "dim",
        ThoughtLevel.INFO: "white",
        ThoughtLevel.IMPORTANT: "yellow",
        ThoughtLevel.CRITICAL: "red",
    }

    def __init__(self, enabled: bool = True, min_level: ThoughtLevel = ThoughtLevel.INFO):
        self.enabled = enabled
        self.min_level = min_level
        self.thoughts: List[Thought] = []
        self.current_parent: Optional[Thought] = None
        self.lock = Lock()
        self.thought_counter = 0
        self._callbacks: List[Callable[[Thought], None]] = []

    def add_thought(
        self,
        thought_type: ThoughtType,
        message: str,
        level: ThoughtLevel = ThoughtLevel.INFO,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Thought:
        """Add a thought to the stream."""
        if not self.enabled or level.value not in [l.value for l in ThoughtLevel]:
            if level == ThoughtLevel.DEBUG and self.min_level != ThoughtLevel.DEBUG:
                return None

        with self.lock:
            self.thought_counter += 1
            thought = Thought(
                id=f"t_{self.thought_counter}",
                thought_type=thought_type,
                level=level,
                message=message,
                metadata=metadata or {},
            )

            if self.current_parent:
                self.current_parent.children.append(thought)
            else:
                self.thoughts.append(thought)

            for callback in self._callbacks:
                callback(thought)

            return thought

    def start_group(self, thought_type: ThoughtType, message: str) -> Thought:
        """Start a group of related thoughts."""
        thought = self.add_thought(thought_type, message, ThoughtLevel.IMPORTANT)
        self.current_parent = thought
        return thought

    def end_group(self):
        """End the current thought group."""
        self.current_parent = None

    def analysis(self, message: str, **metadata) -> Thought:
        """Add an analysis thought."""
        return self.add_thought(ThoughtType.ANALYSIS, message, ThoughtLevel.INFO, metadata)

    def planning(self, message: str, **metadata) -> Thought:
        """Add a planning thought."""
        return self.add_thought(ThoughtType.PLANNING, message, ThoughtLevel.IMPORTANT, metadata)

    def decision(self, message: str, **metadata) -> Thought:
        """Add a decision thought."""
        return self.add_thought(ThoughtType.DECISION, message, ThoughtLevel.IMPORTANT, metadata)

    def executing(self, message: str, **metadata) -> Thought:
        """Add an execution thought."""
        return self.add_thought(ThoughtType.EXECUTION, message, ThoughtLevel.INFO, metadata)

    def validating(self, message: str, **metadata) -> Thought:
        """Add a validation thought."""
        return self.add_thought(ThoughtType.VALIDATION, message, ThoughtLevel.INFO, metadata)

    def correcting(self, message: str, **metadata) -> Thought:
        """Add a correction thought."""
        return self.add_thought(ThoughtType.CORRECTION, message, ThoughtLevel.IMPORTANT, metadata)

    def success(self, message: str, **metadata) -> Thought:
        """Add a success thought."""
        return self.add_thought(ThoughtType.SUCCESS, message, ThoughtLevel.INFO, metadata)

    def error(self, message: str, **metadata) -> Thought:
        """Add an error thought."""
        return self.add_thought(ThoughtType.ERROR, message, ThoughtLevel.CRITICAL, metadata)

    def info(self, message: str, **metadata) -> Thought:
        """Add an info thought."""
        return self.add_thought(ThoughtType.INFO, message, ThoughtLevel.INFO, metadata)

    def debug(self, message: str, **metadata) -> Thought:
        """Add a debug thought."""
        return self.add_thought(ThoughtType.INFO, message, ThoughtLevel.DEBUG, metadata)

    def on_thought(self, callback: Callable[[Thought], None]):
        """Register a callback for new thoughts."""
        self._callbacks.append(callback)

    def format_thought(self, thought: Thought, indent: int = 0) -> str:
        """Format a thought for display."""
        icon, color = self.THEME.get(thought.thought_type, ("•", "white"))

        prefix = "  " * indent

        timestamp = thought.timestamp.strftime("%H:%M:%S")

        lines = [f"{prefix}{icon} [{timestamp}] {thought.message}"]

        for child in thought.children:
            if child.expanded:
                lines.append(self.format_thought(child, indent + 1))

        return "\n".join(lines)

    def get_display(self) -> str:
        """Get all thoughts formatted for display."""
        lines = ["", "═" * 50, "  🤖 Agent Thoughts", "═" * 50, ""]

        for thought in self.thoughts[-20:]:
            lines.append(self.format_thought(thought))

        lines.append("═" * 50)

        return "\n".join(lines)

    def clear(self):
        """Clear all thoughts."""
        with self.lock:
            self.thoughts.clear()
            self.current_parent = None

    def get_summary(self) -> Dict[str, int]:
        """Get a summary of thought counts by type."""
        summary = {t.value: 0 for t in ThoughtType}

        for thought in self.thoughts:
            summary[thought.thought_type.value] += 1
            for child in thought.children:
                summary[child.thought_type.value] += 1

        return summary


class ThoughtPrinter:
    """Print thoughts to the terminal with colors."""

    COLORS = {
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "dim": "\033[2m",
        "reset": "\033[0m",
        "bold": "\033[1m",
    }

    @classmethod
    def print_thought(cls, thought: Thought, file=None):
        """Print a single thought to terminal."""
        if file is None:
            file = sys.stdout

        icon_map = {
            ThoughtType.ANALYSIS: "💭",
            ThoughtType.PLANNING: "📋",
            ThoughtType.DECISION: "🤔",
            ThoughtType.EXECUTION: "⚙️",
            ThoughtType.VALIDATION: "✅",
            ThoughtType.CORRECTION: "🔧",
            ThoughtType.SUCCESS: "✓",
            ThoughtType.ERROR: "✗",
            ThoughtType.INFO: "ℹ️",
        }

        icon = icon_map.get(thought.thought_type, "•")

        color = ThoughtStream.THEME.get(thought.thought_type, ("", "white"))[1]

        color_code = cls.COLORS.get(color, cls.COLORS["white"])
        reset = cls.COLORS["reset"]

        timestamp = thought.timestamp.strftime("%H:%M:%S")

        print(f"{color_code}{icon} [{timestamp}]{reset} {thought.message}", file=file)

    @classmethod
    def print_stream(cls, stream: ThoughtStream, file=None):
        """Print the entire thought stream."""
        if file is None:
            file = sys.stdout

        print("", file=file)
        print(f"{cls.COLORS['cyan']}{'═' * 50}{cls.COLORS['reset']}", file=file)
        print(f"{cls.COLORS['cyan']}  🤖 Agent Thoughts{cls.COLORS['reset']}", file=file)
        print(f"{cls.COLORS['cyan']}{'═' * 50}{cls.COLORS['reset']}", file=file)
        print("", file=file)

        for thought in stream.thoughts[-20:]:
            cls._print_tree(thought, file=file)

        print(f"{cls.COLORS['cyan']}{'═' * 50}{cls.COLORS['reset']}", file=file)

    @classmethod
    def _print_tree(cls, thought: Thought, indent: int = 0, file=None):
        """Print a thought and its children."""
        cls.print_thought(thought, file)

        for child in thought.children:
            if child.expanded:
                cls._print_tree(child, indent + 1, file)


def create_thought_stream(enabled: bool = True) -> ThoughtStream:
    """Create a new thought stream."""
    return ThoughtStream(enabled=enabled)


__all__ = [
    "ThoughtType",
    "ThoughtLevel",
    "Thought",
    "ThoughtStream",
    "ThoughtPrinter",
    "create_thought_stream",
]
