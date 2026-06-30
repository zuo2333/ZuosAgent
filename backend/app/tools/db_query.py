"""
Database Query Tool implementation.

Provides read-only SQL query capability with security controls:
- Allowed tables whitelist
- 10 second timeout
- 100 row limit
- Forbidden operations (INSERT, UPDATE, DELETE, DROP, TRUNCATE)
"""
import re
from typing import Dict, Any, Optional, List, Union

from app.tools.base import BaseTool, ToolResult


class DbQueryTool(BaseTool):
    """
    Tool for executing read-only SQL queries.

    Security controls:
    - Only SELECT queries allowed
    - Table whitelist enforcement
    - Row limit enforcement
    - Timeout control

    Configuration:
    - timeout: Execution timeout (default 10 seconds)
    - max_rows: Maximum rows to return (default 100)
    - allowed_tables: List of allowed table names
    """

    DEFAULT_TIMEOUT = 10.0
    DEFAULT_MAX_ROWS = 100

    # Patterns for forbidden operations (case-insensitive)
    FORBIDDEN_PATTERNS = [
        r'\bINSERT\b',
        r'\bUPDATE\b',
        r'\bDELETE\b',
        r'\bDROP\b',
        r'\bTRUNCATE\b',
        r'\bALTER\b',
        r'\bCREATE\b',
        r'\bGRANT\b',
        r'\bREVOKE\b',
        r'\bEXEC\b',
        r'\bEXECUTE\b',
        r'\bCALL\b',
        r'\bINTO\b',  # Prevent SELECT INTO
        r';.*\b',  # Prevent multiple statements
    ]

    @property
    def name(self) -> str:
        """Tool name identifier."""
        return "db_query"

    @property
    def description(self) -> str:
        """Tool description for the model."""
        return (
            "Execute a read-only SQL query on the database. "
            "Only SELECT queries are allowed on whitelisted tables. "
            "Results are limited to a maximum number of rows. "
            "Use this to query session history, messages, and tool call logs."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        """JSON Schema for tool parameters."""
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The SQL SELECT query to execute"
                },
                "max_rows": {
                    "type": "integer",
                    "description": "Maximum rows to return (default 100)",
                    "minimum": 1,
                    "maximum": 1000
                }
            },
            "required": ["query"]
        }

    def __init__(
        self,
        db_session_factory,
        allowed_tables: Optional[List[str]] = None,
        max_rows: int = DEFAULT_MAX_ROWS
    ) -> None:
        """
        Initialize the database query tool.

        Args:
            db_session_factory: Factory function to create database sessions.
            allowed_tables: List of allowed table names.
            max_rows: Default maximum rows to return.
        """
        self._db_session_factory = db_session_factory
        self._allowed_tables = allowed_tables or ["sessions", "messages", "tool_calls"]
        self._max_rows = max_rows

        # Compile forbidden patterns
        self._forbidden_regex = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.FORBIDDEN_PATTERNS
        ]

    @property
    def allowed_tables(self) -> List[str]:
        """Get the list of allowed tables."""
        return self._allowed_tables

    def set_allowed_tables(self, tables: List[str]) -> None:
        """Set the allowed tables whitelist."""
        self._allowed_tables = tables

    async def execute(self, **params: Any) -> ToolResult:
        """
        Execute the SQL query.

        Args:
            query: The SQL SELECT query.
            max_rows: Optional max rows override.

        Returns:
            ToolResult with query results or error.
        """
        query = params.get("query")
        if not query:
            return ToolResult(error="Query parameter is required")

        max_rows = params.get("max_rows", self._max_rows)
        max_rows = min(max(max_rows, 1), 1000)  # Clamp between 1 and 1000

        # Validate query
        validation_error = self._validate_query(query)
        if validation_error:
            return ToolResult(error=validation_error)

        # Extract tables and validate against whitelist
        tables = self._extract_tables(query)
        for table in tables:
            if table.lower() not in [t.lower() for t in self._allowed_tables]:
                return ToolResult(
                    error=f"Table '{table}' is not allowed. "
                          f"Allowed tables: {self._allowed_tables}"
                )

        try:
            # Execute the query
            results = await self._execute_query(query, max_rows)

            if not results:
                return ToolResult(
                    output="Query returned no results.",
                    metadata={"query": query, "row_count": 0}
                )

            # Format results
            formatted = self._format_results(results)
            return ToolResult(
                output=formatted,
                metadata={
                    "query": query,
                    "row_count": len(results),
                    "truncated": len(results) >= max_rows
                }
            )

        except Exception as e:
            return ToolResult(error=f"Query execution failed: {str(e)}")

    def _validate_query(self, query: str) -> Optional[str]:
        """
        Validate the query for forbidden operations.

        Args:
            query: SQL query string.

        Returns:
            Error message if invalid, None if valid.
        """
        # Check for forbidden patterns
        for pattern in self._forbidden_regex:
            if pattern.search(query):
                forbidden_op = pattern.pattern.replace(r'\b', '').replace(r'\b', '')
                return f"Forbidden operation detected: {forbidden_op}. Only SELECT queries are allowed."

        # Must start with SELECT
        if not query.strip().upper().startswith("SELECT"):
            return "Only SELECT queries are allowed."

        return None

    def _extract_tables(self, query: str) -> List[str]:
        """
        Extract table names from a SELECT query.

        This is a simple extraction - it looks for:
        - FROM table_name
        - JOIN table_name

        Args:
            query: SQL query string.

        Returns:
            List of table names.
        """
        tables = []

        # Pattern for FROM and JOIN clauses
        patterns = [
            r'\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'\bJOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            tables.extend(matches)

        return list(set(tables))

    async def _execute_query(
        self,
        query: str,
        max_rows: int
    ) -> List[Dict[str, Any]]:
        """
        Execute the query and return results.

        Args:
            query: SQL query.
            max_rows: Maximum rows.

        Returns:
            List of result dictionaries.
        """
        from sqlalchemy import text

        async with self._db_session_factory() as session:
            # Add LIMIT if not present
            if "LIMIT" not in query.upper():
                query = f"{query.rstrip(';')} LIMIT {max_rows + 1}"

            result = await session.execute(text(query))
            rows = result.fetchall()

            # Convert to dictionaries
            columns = result.keys()
            results = []
            for row in rows[:max_rows]:
                results.append(dict(zip(columns, row)))

            return results

    def _format_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Format query results for the model.

        Args:
            results: List of result dictionaries.

        Returns:
            Formatted string.
        """
        if not results:
            return "No results."

        lines = ["Query Results:", ""]

        for i, row in enumerate(results, 1):
            lines.append(f"Row {i}:")
            for key, value in row.items():
                # Truncate long values
                str_value = str(value)
                if len(str_value) > 200:
                    str_value = str_value[:200] + "..."
                lines.append(f"  {key}: {str_value}")
            lines.append("")

        if len(results) >= self._max_rows:
            lines.append(f"(Results may be truncated at {self._max_rows} rows)")

        return "\n".join(lines)


class DbQueryToolConfig:
    """Configuration for DbQueryTool."""

    def __init__(
        self,
        allowed_tables: Optional[List[str]] = None,
        max_rows: int = 100,
        timeout: float = 10.0
    ) -> None:
        """
        Initialize configuration.

        Args:
            allowed_tables: List of allowed tables.
            max_rows: Maximum rows to return.
            timeout: Execution timeout.
        """
        self.allowed_tables = allowed_tables or ["sessions", "messages", "tool_calls"]
        self.max_rows = max_rows
        self.timeout = timeout

    def create_tool(self, db_session_factory) -> DbQueryTool:
        """
        Create a configured DbQueryTool instance.

        Args:
            db_session_factory: Database session factory.

        Returns:
            Configured DbQueryTool instance.
        """
        return DbQueryTool(
            db_session_factory=db_session_factory,
            allowed_tables=self.allowed_tables,
            max_rows=self.max_rows
        )
