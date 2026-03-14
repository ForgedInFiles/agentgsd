"""
Indexer tool for agentgsd.

Provides semantic search capabilities using TF-IDF indexing.
"""

import os
from typing import Any, Dict

from shared.tools.base import Tool
from shared.indexer import CodebaseIndexer
from shared.utils.colors import CYAN, DIM, GREEN, RESET, YELLOW


_global_indexer = None


def get_indexer() -> CodebaseIndexer:
    """Get or create the global indexer."""
    global _global_indexer
    if _global_indexer is None:
        _global_indexer = CodebaseIndexer(".")
    return _global_indexer


class IndexBuildTool(Tool):
    """
    Build or rebuild the semantic code index.

    Scans the codebase and creates a TF-IDF index for semantic search.
    """

    def __init__(self):
        super().__init__(
            name="index_build",
            description="Build semantic code index for search",
            parameters={"max_files": "number?", "path": "string?"},
        )

    def execute(self, args: Dict[str, Any]) -> str:
        indexer = get_indexer()

        path = args.get("path")
        if path:
            indexer.root_path = path

        max_files = args.get("max_files")

        stats = indexer.build_index(max_files=max_files)

        return (
            f"{GREEN}✓{RESET} Index built successfully\n"
            f"{CYAN}Stats:{RESET}\n"
            f"  Files indexed: {stats['total_files']}\n"
            f"  Symbols found: {stats['total_symbols']}\n"
            f"  Vocabulary: {stats['vocabulary_size']}\n"
            f"  Languages: {', '.join(stats['languages'])}"
        )


class IndexSearchTool(Tool):
    """
    Search the semantic code index.

    Uses TF-IDF similarity to find relevant code based on natural language queries.
    """

    def __init__(self):
        super().__init__(
            name="index_search",
            description="Search indexed code using semantic similarity",
            parameters={"query": "string", "top_k": "number?"},
        )

    def execute(self, args: Dict[str, Any]) -> str:
        indexer = get_indexer()

        query = args.get("query", "")
        top_k = args.get("top_k", 10)

        if not indexer.indexed_files:
            return f"{YELLOW}⚠{RESET} Index not built yet. Use index_build first."

        results = indexer.search(query, top_k=top_k)

        if not results:
            return f"{DIM}(no results found){RESET}"

        lines = [f'{CYAN}Search Results for: "{query}"{RESET}', ""]

        for i, r in enumerate(results, 1):
            lines.append(f"{i}. {GREEN}{r['file']}{RESET} (similarity: {r['similarity']:.3f})")

            if r.get("symbols"):
                lines.append(f"   {DIM}Symbols:{RESET}")
                for s in r["symbols"][:3]:
                    lines.append(f"   - {s['name']} ({s['type']}) at line {s['line']}")

            lines.append("")

        return "\n".join(lines)


class IndexStatsTool(Tool):
    """
    Get statistics about the current index.
    """

    def __init__(self):
        super().__init__(
            name="index_stats",
            description="Show index statistics",
            parameters={},
        )

    def execute(self, args: Dict[str, Any]) -> str:
        indexer = get_indexer()

        if not indexer.indexed_files:
            return f"{YELLOW}⚠{RESET} Index not built yet. Use index_build first."

        stats = indexer.get_stats()

        lines = [
            f"{CYAN}Index Statistics:{RESET}",
            f"  Files indexed: {stats['total_files']}",
            f"  Symbols: {stats['total_symbols']}",
            f"  Vocabulary: {stats['vocabulary_size']}",
            f"  Languages: {', '.join(stats['languages'])}",
        ]

        return "\n".join(lines)


class ThinkTool(Tool):
    """
    Display the agent's thought process.

    Shows recent thoughts and reasoning steps.
    """

    def __init__(self, thought_stream=None):
        super().__init__(
            name="think",
            description="Show agent thought process",
            parameters={"show": "string?"},
        )
        self.thought_stream = thought_stream

    def execute(self, args: Dict[str, Any]) -> str:
        from shared.workflows import ThoughtStream

        show = args.get("show", "recent")

        stream = self.thought_stream or ThoughtStream(enabled=False)

        if show == "recent":
            thoughts = stream.thoughts[-10:]
        elif show == "all":
            thoughts = stream.thoughts
        elif show == "summary":
            summary = stream.get_summary()
            lines = [f"{CYAN}Thought Summary:{RESET}"]
            for ttype, count in summary.items():
                if count > 0:
                    lines.append(f"  {ttype}: {count}")
            return "\n".join(lines)
        else:
            return f"{YELLOW}Unknown show option: {show}. Use: recent, all, or summary"

        if not thoughts:
            return f"{DIM}(no thoughts recorded){RESET}"

        from shared.workflows.thoughts import ThoughtPrinter

        lines = []
        for thought in thoughts:
            lines.append(
                f"[{thought.timestamp.strftime('%H:%M:%S')}] {thought.thought_type.value}: {thought.message}"
            )

        return "\n".join(lines)
