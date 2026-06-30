"""
Web Search Tool implementation.

Provides web search capabilities using DuckDuckGo.
30 second timeout by default.
"""
import json
from typing import Dict, Any, Optional, List

from app.tools.base import BaseTool, ToolResult
from app.core.config import settings


class WebSearchTool(BaseTool):
    """
    Tool for performing web searches using DuckDuckGo.

    Uses the duckduckgo-search library for searching.
    Returns formatted search results.

    Configuration:
    - timeout: Execution timeout (default 30 seconds)
    - max_results: Maximum number of results to return (default 5)
    """

    DEFAULT_TIMEOUT = 30.0
    DEFAULT_MAX_RESULTS = 5

    @property
    def name(self) -> str:
        """Tool name identifier."""
        return "web_search"

    @property
    def description(self) -> str:
        """Tool description for the model."""
        return (
            "Search the web for information. "
            "Returns a list of search results with titles, URLs, and snippets. "
            "Use this tool when you need to find current information or facts "
            "that may not be in your training data."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        """JSON Schema for tool parameters."""
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query string"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default 5)",
                    "minimum": 1,
                    "maximum": 20
                }
            },
            "required": ["query"]
        }

    def __init__(
        self,
        max_results: int = DEFAULT_MAX_RESULTS,
        region: str = "zh-cn",
        proxy: Optional[str] = None
    ) -> None:
        """
        Initialize the web search tool.

        Args:
            max_results: Default maximum number of results.
            region: Search region (e.g., "us-en", "zh-cn").
            proxy: Proxy URL (e.g., "http://127.0.0.1:7890").
                   If not provided, uses HTTP_PROXY from settings.
        """
        self._max_results = max_results
        self._region = region
        self._proxy = proxy or settings.HTTP_PROXY
        self._client = None

    def _get_client(self):
        """Get or create the DDGS client lazily."""
        if self._client is None:
            try:
                from duckduckgo_search import DDGS
                # Pass proxy to DDGS if available
                self._client = DDGS(proxy=self._proxy) if self._proxy else DDGS()
            except ImportError:
                raise ImportError(
                    "duckduckgo-search is required for web search. "
                    "Install it with: pip install duckduckgo-search"
                )
        return self._client

    async def execute(self, **params: Any) -> ToolResult:
        """
        Execute the web search.

        Args:
            query: The search query string.
            max_results: Optional max results override.

        Returns:
            ToolResult with search results or error.
        """
        query = params.get("query")
        if not query:
            return ToolResult(error="Query parameter is required")

        max_results = params.get("max_results", self._max_results)
        max_results = min(max(max_results, 1), 20)  # Clamp between 1 and 20

        try:
            # Run the synchronous search in a thread
            import asyncio
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: self._search_sync(query, max_results)
            )

            if not results:
                return ToolResult(
                    output="No search results found for the query.",
                    metadata={"query": query, "result_count": 0}
                )

            # Format results for the model
            formatted = self._format_results(results)
            return ToolResult(
                output=formatted,
                metadata={
                    "query": query,
                    "result_count": len(results),
                    "results": results
                }
            )

        except ImportError as e:
            return ToolResult(error=str(e))

        except Exception as e:
            return ToolResult(error=f"Search failed: {str(e)}")

    def _search_sync(self, query: str, max_results: int) -> List[Dict[str, str]]:
        """
        Perform synchronous search.

        Args:
            query: Search query.
            max_results: Maximum results.

        Returns:
            List of result dictionaries.
        """
        client = self._get_client()

        results = []
        try:
            search_gen = client.text(
                query,
                region=self._region,
                max_results=max_results
            )

            for result in search_gen:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", "")
                })

        except Exception as e:
            # Log the error but return empty results
            print(f"Web search error: {e}")

        return results

    def _format_results(self, results: List[Dict[str, str]]) -> str:
        """
        Format search results for the model.

        Args:
            results: List of search result dictionaries.

        Returns:
            Formatted string for the model.
        """
        lines = ["Search Results:", ""]

        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            url = result.get("url", "")
            snippet = result.get("snippet", "No description")

            lines.append(f"[{i}] {title}")
            if url:
                lines.append(f"    URL: {url}")
            lines.append(f"    {snippet}")
            lines.append("")

        return "\n".join(lines)


class WebSearchToolConfig:
    """Configuration for WebSearchTool."""

    def __init__(
        self,
        max_results: int = 5,
        region: str = "zh-cn",
        timeout: float = 30.0,
        proxy: Optional[str] = None
    ) -> None:
        """
        Initialize configuration.

        Args:
            max_results: Default maximum results.
            region: Search region.
            timeout: Execution timeout.
            proxy: Proxy URL (e.g., "http://127.0.0.1:7890").
        """
        self.max_results = max_results
        self.region = region
        self.timeout = timeout
        self.proxy = proxy

    def create_tool(self) -> WebSearchTool:
        """Create a configured WebSearchTool instance."""
        return WebSearchTool(
            max_results=self.max_results,
            region=self.region,
            proxy=self.proxy
        )
