"""
Semantic Codebase Indexer for agentgsd.

A TF-IDF based indexer that provides semantic search capabilities
for codebases without requiring external APIs or services.
"""

import ast
import os
import re
import json
import math
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from concurrent.futures import ThreadPoolExecutor


@dataclass
class CodeSymbol:
    """Represents a code symbol (function, class, method, etc.)."""

    name: str
    type: str  # function, class, method, module
    file_path: str
    line_start: int
    line_end: int
    signature: str
    docstring: str
    context: str  # surrounding code context
    imports: List[str]


@dataclass
class IndexedFile:
    """Represents an indexed source file."""

    file_path: str
    symbols: List[CodeSymbol]
    full_text: str
    language: str


class TFIDFVectorizer:
    """Simple TF-IDF vectorizer using pure Python."""

    def __init__(self):
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.doc_count: int = 0

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        text = text.lower()
        tokens = re.findall(r"\b\w+\b", text)
        return tokens

    def _compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        """Compute term frequency."""
        tf = defaultdict(int)
        for token in tokens:
            tf[token] += 1
        total = len(tokens)
        return {k: v / total for k, v in tf.items()}

    def _compute_idf(self, doc_term_freqs: List[Dict[str, int]]):
        """Compute inverse document frequency."""
        num_docs = len(doc_term_freqs)
        idf = defaultdict(int)

        for doc_tf in doc_term_freqs:
            for term in doc_tf.keys():
                idf[term] += 1

        self.idf = {k: math.log(num_docs / v) + 1 for k, v in idf.items()}
        self.doc_count = num_docs

    def fit(self, documents: List[str]):
        """Build vocabulary from documents."""
        doc_term_freqs = []

        for doc in documents:
            tokens = self._tokenize(doc)
            tf = self._compute_tf(tokens)
            doc_term_freqs.append(tf)

            for token in set(tokens):
                if token not in self.vocabulary:
                    self.vocabulary[token] = len(self.vocabulary)

        self._compute_idf(doc_term_freqs)

    def transform(self, document: str) -> List[float]:
        """Transform document to TF-IDF vector."""
        tokens = self._tokenize(document)
        tf = self._compute_tf(tokens)

        vector = [0.0] * len(self.vocabulary)

        for token, freq in tf.items():
            if token in self.vocabulary:
                idx = self.vocabulary[token]
                idf = self.idf.get(token, 1.0)
                vector[idx] = freq * idf

        return vector

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = math.sqrt(sum(a * a for a in vec1))
        mag2 = math.sqrt(sum(b * b for b in vec2))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot_product / (mag1 * mag2)


class CodeParser:
    """Parse source code to extract symbols."""

    SUPPORTED_EXTENSIONS = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".go": "go",
        ".rs": "rust",
        ".java": "java",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
    }

    def __init__(self):
        self.ignore_dirs = {
            ".git",
            "__pycache__",
            "node_modules",
            ".venv",
            "venv",
            ".pytest_cache",
            "dist",
            "build",
            ".tox",
        }
        self.ignore_files = {
            ".DS_Store",
            "package-lock.json",
            "yarn.lock",
            "poetry.lock",
            "Pipfile.lock",
        }

    def is_supported(self, file_path: str) -> bool:
        """Check if file is supported for parsing."""
        ext = Path(file_path).suffix.lower()
        return ext in self.SUPPORTED_EXTENSIONS

    def should_ignore(self, path: str) -> bool:
        """Check if path should be ignored."""
        parts = Path(path).parts
        return any(ignored in parts for ignored in self.ignore_dirs)

    def get_language(self, file_path: str) -> str:
        """Get language from file extension."""
        ext = Path(file_path).suffix.lower()
        return self.SUPPORTED_EXTENSIONS.get(ext, "unknown")

    def parse_python(self, file_path: str, content: str) -> List[CodeSymbol]:
        """Parse Python source code."""
        symbols = []

        try:
            tree = ast.parse(content, filename=file_path)
        except SyntaxError:
            return symbols

        for node in ast.walk(tree):
            symbol = None

            if isinstance(node, ast.FunctionDef):
                symbol = self._create_function_symbol(node, file_path, content)
            elif isinstance(node, ast.ClassDef):
                symbol = self._create_class_symbol(node, file_path, content)
            elif isinstance(node, ast.AsyncFunctionDef):
                symbol = self._create_function_symbol(node, file_path, content)

            if symbol:
                symbols.append(symbol)

        return symbols

    def _create_function_symbol(self, node: Any, file_path: str, content: str) -> CodeSymbol:
        """Create symbol for a function."""
        args = [arg.arg for arg in node.args.args]
        signature = f"{node.name}({', '.join(args)})"

        docstring = ast.get_docstring(node) or ""

        context = self._get_context(content, node.lineno, node.end_lineno)
        imports = self._get_file_imports(content)

        return CodeSymbol(
            name=node.name,
            type="function",
            file_path=file_path,
            line_start=node.lineno or 0,
            line_end=node.end_lineno or 0,
            signature=signature,
            docstring=docstring,
            context=context,
            imports=imports,
        )

    def _create_class_symbol(self, node: ast.ClassDef, file_path: str, content: str) -> CodeSymbol:
        """Create symbol for a class."""
        docstring = ast.get_docstring(node) or ""

        base_names = [n.id for n in node.bases if isinstance(n, ast.Name)]
        signature = (
            f"class {node.name}({', '.join(base_names)})" if base_names else f"class {node.name}"
        )

        context = self._get_context(content, node.lineno, node.end_lineno)
        imports = self._get_file_imports(content)

        return CodeSymbol(
            name=node.name,
            type="class",
            file_path=file_path,
            line_start=node.lineno or 0,
            line_end=node.end_lineno or 0,
            signature=signature,
            docstring=docstring,
            context=context,
            imports=imports,
        )

    def _get_context(self, content: str, start: int, end: Optional[int]) -> str:
        """Get surrounding context for a symbol."""
        lines = content.split("\n")

        start_idx = max(0, start - 3)
        end_idx = min(len(lines), (end or start) + 3)

        return "\n".join(lines[start_idx:end_idx])

    def _get_file_imports(self, content: str) -> List[str]:
        """Get imports from file."""
        imports = []

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return imports

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        return imports

    def parse_generic(self, file_path: str, content: str) -> List[CodeSymbol]:
        """Generic parser for non-Python files using regex."""
        symbols = []
        language = self.get_language(file_path)

        if language == "python":
            return self.parse_python(file_path, content)

        func_pattern = r"(?:func|function|def|fn)\s+(\w+)\s*\(([^)]*)\)"
        class_pattern = r"class\s+(\w+)(?:\s*\(|\s*:)"

        for match in re.finditer(func_pattern, content):
            name = match.group(1)
            args = match.group(2)
            line_num = content[: match.start()].count("\n") + 1

            symbols.append(
                CodeSymbol(
                    name=name,
                    type="function",
                    file_path=file_path,
                    line_start=line_num,
                    line_end=line_num,
                    signature=f"{name}({args})",
                    docstring="",
                    context="",
                    imports=[],
                )
            )

        for match in re.finditer(class_pattern, content):
            name = match.group(1)
            line_num = content[: match.start()].count("\n") + 1

            symbols.append(
                CodeSymbol(
                    name=name,
                    type="class",
                    file_path=file_path,
                    line_start=line_num,
                    line_end=line_num,
                    signature=f"class {name}",
                    docstring="",
                    context="",
                    imports=[],
                )
            )

        return symbols


class CodebaseIndexer:
    """Main indexer class for semantic code search."""

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.parser = CodeParser()
        self.vectorizer = TFIDFVectorizer()
        self.indexed_files: Dict[str, IndexedFile] = {}
        self.symbol_index: List[CodeSymbol] = []
        self.file_vectors: Dict[str, List[float]] = {}

    def scan_files(self) -> List[str]:
        """Scan for all supported files in the codebase."""
        files = []

        for root, dirs, filenames in os.walk(self.root_path):
            dirs[:] = [d for d in dirs if not self.parser.should_ignore(d)]

            for filename in filenames:
                file_path = os.path.join(root, filename)

                if self.parser.is_supported(file_path) and not self.parser.should_ignore(file_path):
                    files.append(file_path)

        return files

    def index_file(self, file_path: str) -> Optional[IndexedFile]:
        """Index a single file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except (IOError, UnicodeDecodeError):
            return None

        rel_path = str(Path(file_path).relative_to(self.root_path))

        if self.parser.get_language(file_path) == "python":
            symbols = self.parser.parse_python(rel_path, content)
        else:
            symbols = self.parser.parse_generic(rel_path, content)

        indexed_file = IndexedFile(
            file_path=rel_path,
            symbols=symbols,
            full_text=content,
            language=self.parser.get_language(file_path),
        )

        self.indexed_files[rel_path] = indexed_file
        self.symbol_index.extend(symbols)

        return indexed_file

    def build_index(self, max_files: Optional[int] = None) -> Dict[str, Any]:
        """Build the complete index."""
        files = self.scan_files()

        if max_files:
            files = files[:max_files]

        documents = []

        for file_path in files:
            indexed = self.index_file(file_path)
            if indexed:
                doc = " ".join(
                    [
                        " ".join(s.name for s in indexed.symbols),
                        " ".join(s.signature for s in indexed.symbols),
                        " ".join(s.docstring for s in indexed.symbols),
                        indexed.full_text[:5000],
                    ]
                )
                documents.append(doc)

        self.vectorizer.fit(documents)

        for rel_path, indexed in self.indexed_files.items():
            doc = " ".join(
                [
                    " ".join(s.name for s in indexed.symbols),
                    " ".join(s.signature for s in indexed.symbols),
                    indexed.full_text[:5000],
                ]
            )
            self.file_vectors[rel_path] = self.vectorizer.transform(doc)

        return self._get_stats()

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search the index for relevant code."""
        query_vector = self.vectorizer.transform(query)

        results = []

        for rel_path, file_vec in self.file_vectors.items():
            similarity = self.vectorizer.cosine_similarity(query_vector, file_vec)

            if similarity > 0.01:
                indexed = self.indexed_files[rel_path]

                symbol_results = []
                for symbol in indexed.symbols:
                    symbol_doc = f"{symbol.name} {symbol.signature} {symbol.docstring}"
                    symbol_vec = self.vectorizer.transform(symbol_doc)
                    symbol_sim = self.vectorizer.cosine_similarity(query_vector, symbol_vec)

                    if symbol_sim > 0.1:
                        symbol_results.append(
                            {
                                "name": symbol.name,
                                "type": symbol.type,
                                "signature": symbol.signature,
                                "line": symbol.line_start,
                                "similarity": symbol_sim,
                            }
                        )

                symbol_results.sort(key=lambda x: x["similarity"], reverse=True)
                symbol_results = symbol_results[:5]

                results.append(
                    {
                        "file": rel_path,
                        "similarity": similarity,
                        "language": indexed.language,
                        "symbols": symbol_results,
                        "context": indexed.symbols[0].context if indexed.symbols else "",
                    }
                )

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    def search_symbols(self, query: str, top_k: int = 10) -> List[CodeSymbol]:
        """Search for specific symbols."""
        query_vector = self.vectorizer.transform(query)

        results = []

        for symbol in self.symbol_index:
            symbol_doc = f"{symbol.name} {symbol.signature} {symbol.docstring} {symbol.context}"
            symbol_vec = self.vectorizer.transform(symbol_doc)

            similarity = self.vectorizer.cosine_similarity(query_vector, symbol_vec)

            if similarity > 0.05:
                results.append((symbol, similarity))

        results.sort(key=lambda x: x[1], reverse=True)

        return [s[0] for s in results[:top_k]]

    def get_symbol_at_line(self, file_path: str, line: int) -> Optional[CodeSymbol]:
        """Get symbol at specific line in file."""
        indexed = self.indexed_files.get(file_path)

        if not indexed:
            return None

        for symbol in indexed.symbols:
            if symbol.line_start <= line <= symbol.line_end:
                return symbol

        return None

    def save_index(self, path: str):
        """Save index to file."""
        data = {
            "root_path": str(self.root_path),
            "indexed_files": {
                k: {
                    "file_path": v.file_path,
                    "symbols": [asdict(s) for s in v.symbols],
                    "language": v.language,
                }
                for k, v in self.indexed_files.items()
            },
            "vocabulary_size": len(self.vectorizer.vocabulary),
        }

        with open(path, "w") as f:
            json.dump(data, f)

    def load_index(self, path: str) -> bool:
        """Load index from file."""
        try:
            with open(path, "r") as f:
                data = json.load(f)

            self.root_path = Path(data["root_path"])

            for k, v in data["indexed_files"].items():
                symbols = [CodeSymbol(**s) for s in v["symbols"]]
                self.indexed_files[k] = IndexedFile(
                    file_path=v["file_path"], symbols=symbols, full_text="", language=v["language"]
                )
                self.symbol_index.extend(symbols)

            return True
        except (IOError, KeyError, json.JSONDecodeError):
            return False

    def _get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            "total_files": len(self.indexed_files),
            "total_symbols": len(self.symbol_index),
            "vocabulary_size": len(self.vectorizer.vocabulary),
            "languages": list(set(f.language for f in self.indexed_files.values())),
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        return self._get_stats()


def get_or_create_indexer(root_path: str = ".") -> CodebaseIndexer:
    """Get or create a global indexer instance."""
    global _global_indexer

    if "_global_indexer" not in globals():
        _global_indexer = CodebaseIndexer(root_path)

    return _global_indexer


__all__ = [
    "CodeSymbol",
    "IndexedFile",
    "CodebaseIndexer",
    "TFIDFVectorizer",
    "CodeParser",
    "get_or_create_indexer",
]
