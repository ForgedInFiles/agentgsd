"""
Web-related tools for agentgsd.

This module provides tools for searching the web and fetching web content.
It uses duckduckgo-search for searching and urllib for fetching.
"""

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from shared.tools.base import Tool


class WebSearchTool(Tool):
    """
    Tool for searching the web using DuckDuckGo.
    """

    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the web using DuckDuckGo. Returns a list of search results with titles, snippets, and URLs.",
            parameters={
                "query": "string",
                "max_results": "number?",
            },
        )

    def execute(self, args: Dict[str, Any]) -> str:
        """
        Execute the web search.
        """
        query = args.get("query")
        if not query:
            return "error: Query is required"

        max_results = int(args.get("max_results", 5))

        try:
            from ddgs import DDGS
        except ImportError:
            return "error: ddgs library not installed. Run 'pip install ddgs'."

        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                if not results:
                    return f"No results found for query: {query}"

                output = []
                for i, r in enumerate(results, 1):
                    output.append(f"{i}. {r['title']}\n   URL: {r['href']}\n   Snippet: {r['body']}\n")

                return "\n".join(output)
        except Exception as e:
            return f"error: Failed to perform web search: {str(e)}"


class WebFetchTool(Tool):
    """
    Tool for fetching the content of a web page and converting it to readable text.
    """

    def __init__(self):
        super().__init__(
            name="web_fetch",
            description="Fetch the content of a URL and return a simplified text version. Useful for reading documentation or articles.",
            parameters={
                "url": "string",
            },
        )

    def execute(self, args: Dict[str, Any]) -> str:
        """
        Execute the web fetch.
        """
        url = args.get("url")
        if not url:
            return "error: URL is required"

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                content_type = response.headers.get_content_type()
                charset = response.headers.get_content_charset() or "utf-8"
                
                if "text/html" not in content_type and "text/plain" not in content_type:
                    return f"error: Unsupported content type: {content_type}"

                raw_content = response.read().decode(charset, errors="replace")

                if "text/html" in content_type:
                    return self._clean_html(raw_content)
                else:
                    return raw_content

        except urllib.error.URLError as e:
            return f"error: Failed to fetch URL: {str(e)}"
        except Exception as e:
            return f"error: An unexpected error occurred: {str(e)}"

    def _clean_html(self, html: str) -> str:
        """
        A simple HTML to text converter that removes scripts, styles, and tags
        to provide a readable version of the page content.
        """
        # Remove script and style elements
        html = re.sub(r"<(script|style|nav|footer|header).*?>.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove other tags but keep their content
        text = re.sub(r"<.*?>", " ", html)
        
        # Unescape common HTML entities
        text = (
            text.replace("&nbsp;", " ")
            .replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&quot;", '"')
            .replace("&#39;", "'")
        )
        
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\n\s*\n", "\n\n", text)
        
        return text.strip()
