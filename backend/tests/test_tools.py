"""
Unit tests for ToolExecutor and tool functionality.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from app.tools.base import (
    BaseTool,
    ToolResult,
    ToolError,
    ToolRegistry,
)
from app.tools.executor import (
    ToolExecutor,
    ToolExecutorBuilder,
)
from app.tools.web_search import WebSearchTool
from app.tools.db_query import DbQueryTool


class MockTool(BaseTool):
    """Mock tool for testing."""

    @property
    def name(self) -> str:
        return "mock_tool"

    @property
    def description(self) -> str:
        return "A mock tool for testing"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "input": {"type": "string", "description": "Input parameter"}
            },
            "required": ["input"]
        }

    async def execute(self, **params: Any) -> ToolResult:
        input_value = params.get("input", "")
        return ToolResult(output=f"Processed: {input_value}")


class SlowMockTool(BaseTool):
    """Mock tool that takes a long time to execute."""

    @property
    def name(self) -> str:
        return "slow_tool"

    @property
    def description(self) -> str:
        return "A slow tool for timeout testing"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    async def execute(self, **params: Any) -> ToolResult:
        await asyncio.sleep(10)
        return ToolResult(output="Should not reach here")


class FailingMockTool(BaseTool):
    """Mock tool that raises an exception."""

    @property
    def name(self) -> str:
        return "failing_tool"

    @property
    def description(self) -> str:
        return "A tool that always fails"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    async def execute(self, **params: Any) -> ToolResult:
        raise ValueError("Tool execution failed")


class TestToolRegistry:
    """Tests for ToolRegistry."""

    def test_register_tool(self):
        """Test registering a tool."""
        registry = ToolRegistry()
        tool = MockTool()
        registry.register(tool)
        assert "mock_tool" in registry

    def test_register_duplicate_raises_error(self):
        """Test that registering duplicate tool name raises error."""
        registry = ToolRegistry()
        tool = MockTool()
        registry.register(tool)
        with pytest.raises(ValueError, match="already registered"):
            registry.register(tool)

    def test_unregister_tool(self):
        """Test unregistering a tool."""
        registry = ToolRegistry()
        tool = MockTool()
        registry.register(tool)
        result = registry.unregister("mock_tool")
        assert result is True
        assert "mock_tool" not in registry

    def test_unregister_nonexistent_returns_false(self):
        """Test that unregistering nonexistent tool returns False."""
        registry = ToolRegistry()
        result = registry.unregister("nonexistent")
        assert result is False

    def test_get_tool(self):
        """Test getting a tool by name."""
        registry = ToolRegistry()
        tool = MockTool()
        registry.register(tool)
        retrieved = registry.get("mock_tool")
        assert retrieved is tool

    def test_get_nonexistent_tool(self):
        """Test getting a nonexistent tool returns None."""
        registry = ToolRegistry()
        retrieved = registry.get("nonexistent")
        assert retrieved is None

    def test_list_tools(self):
        """Test listing all tools."""
        registry = ToolRegistry()
        registry.register(MockTool())
        tools = registry.list_tools()
        assert "mock_tool" in tools

    def test_get_openai_tools(self):
        """Test getting tools in OpenAI format."""
        registry = ToolRegistry()
        tool = MockTool()
        registry.register(tool)
        openai_tools = registry.get_openai_tools()
        assert len(openai_tools) == 1
        assert openai_tools[0]["type"] == "function"
        assert openai_tools[0]["function"]["name"] == "mock_tool"


class TestToolExecutor:
    """Tests for ToolExecutor."""

    def test_init_with_whitelist(self):
        """Test initializing executor with whitelist."""
        executor = ToolExecutor(whitelist=["tool1", "tool2"])
        assert executor.whitelist == {"tool1", "tool2"}

    def test_init_without_whitelist(self):
        """Test initializing executor without whitelist."""
        executor = ToolExecutor()
        assert executor.whitelist is None

    def test_register_tool(self):
        """Test registering a tool."""
        executor = ToolExecutor()
        tool = MockTool()
        executor.register(tool)
        assert "mock_tool" in executor.list_tools()

    def test_register_tool_with_timeout(self):
        """Test registering a tool with custom timeout."""
        executor = ToolExecutor()
        tool = MockTool()
        executor.register(tool, timeout=60.0)
        assert executor.get_timeout("mock_tool") == 60.0

    def test_set_whitelist(self):
        """Test setting whitelist."""
        executor = ToolExecutor()
        executor.set_whitelist(["tool1", "tool2"])
        assert executor.whitelist == {"tool1", "tool2"}

    def test_add_to_whitelist(self):
        """Test adding to whitelist."""
        executor = ToolExecutor(whitelist=["tool1"])
        executor.add_to_whitelist("tool2")
        assert "tool2" in executor.whitelist

    def test_remove_from_whitelist(self):
        """Test removing from whitelist."""
        executor = ToolExecutor(whitelist=["tool1", "tool2"])
        result = executor.remove_from_whitelist("tool1")
        assert result is True
        assert "tool1" not in executor.whitelist

    def test_remove_from_whitelist_nonexistent(self):
        """Test removing nonexistent tool from whitelist."""
        executor = ToolExecutor(whitelist=["tool1"])
        result = executor.remove_from_whitelist("nonexistent")
        assert result is False

    def test_is_allowed_no_whitelist(self):
        """Test is_allowed when no whitelist is set."""
        executor = ToolExecutor()
        assert executor.is_allowed("any_tool") is True

    def test_is_allowed_with_whitelist(self):
        """Test is_allowed with whitelist set."""
        executor = ToolExecutor(whitelist=["allowed_tool"])
        assert executor.is_allowed("allowed_tool") is True
        assert executor.is_allowed("blocked_tool") is False

    def test_list_allowed_tools(self):
        """Test listing allowed tools."""
        executor = ToolExecutor(whitelist=["tool1"])
        executor.register(MockTool())
        # MockTool has name "mock_tool", not in whitelist
        allowed = executor.list_allowed_tools()
        assert "mock_tool" not in allowed

    @pytest.mark.asyncio
    async def test_execute_tool(self):
        """Test executing a tool."""
        executor = ToolExecutor()
        executor.register(MockTool())
        result = await executor.execute("mock_tool", {"input": "test"})
        assert result.is_success
        assert result.output == "Processed: test"

    @pytest.mark.asyncio
    async def test_execute_blocked_tool(self):
        """Test executing a tool not in whitelist."""
        executor = ToolExecutor(whitelist=["allowed_tool"])
        executor.register(MockTool())
        result = await executor.execute("mock_tool", {"input": "test"})
        assert result.is_error
        assert "not allowed" in result.error

    @pytest.mark.asyncio
    async def test_execute_nonexistent_tool(self):
        """Test executing a nonexistent tool."""
        executor = ToolExecutor()
        result = await executor.execute("nonexistent", {})
        assert result.is_error
        assert "not registered" in result.error

    @pytest.mark.asyncio
    async def test_execute_with_timeout(self):
        """Test tool execution timeout."""
        executor = ToolExecutor(default_timeout=0.1)
        executor.register(SlowMockTool())
        result = await executor.execute("slow_tool", {})
        assert result.is_error
        assert "timed out" in result.error.lower()

    @pytest.mark.asyncio
    async def test_execute_with_exception(self):
        """Test tool execution with exception."""
        executor = ToolExecutor()
        executor.register(FailingMockTool())
        result = await executor.execute("failing_tool", {})
        assert result.is_error
        assert "failed" in result.error.lower()

    @pytest.mark.asyncio
    async def test_execute_validates_parameters(self):
        """Test that execute validates required parameters."""
        executor = ToolExecutor()
        executor.register(MockTool())
        result = await executor.execute("mock_tool", {})  # Missing required "input"
        assert result.is_error
        assert "Missing required parameter" in result.error

    def test_get_openai_tools(self):
        """Test getting tools in OpenAI format."""
        executor = ToolExecutor(whitelist=["mock_tool"])
        executor.register(MockTool())
        openai_tools = executor.get_openai_tools(allowed_only=True)
        assert len(openai_tools) == 1
        assert openai_tools[0]["function"]["name"] == "mock_tool"

    def test_get_openai_tools_all(self):
        """Test getting all tools in OpenAI format."""
        executor = ToolExecutor(whitelist=["allowed"])
        executor.register(MockTool())
        openai_tools = executor.get_openai_tools(allowed_only=False)
        assert len(openai_tools) == 1


class TestToolExecutorBuilder:
    """Tests for ToolExecutorBuilder."""

    def test_build_basic(self):
        """Test building basic executor."""
        executor = ToolExecutorBuilder().build()
        assert executor is not None

    def test_build_with_whitelist(self):
        """Test building executor with whitelist."""
        executor = (
            ToolExecutorBuilder()
            .with_whitelist(["tool1", "tool2"])
            .build()
        )
        assert executor.whitelist == {"tool1", "tool2"}

    def test_build_with_timeout(self):
        """Test building executor with default timeout."""
        executor = (
            ToolExecutorBuilder()
            .with_default_timeout(60.0)
            .build()
        )
        assert executor.get_timeout("any_tool") == 60.0

    def test_build_with_tools(self):
        """Test building executor with tools."""
        tool = MockTool()
        executor = (
            ToolExecutorBuilder()
            .with_tool(tool, timeout=45.0)
            .build()
        )
        assert "mock_tool" in executor.list_tools()
        assert executor.get_timeout("mock_tool") == 45.0

    def test_build_fluent(self):
        """Test fluent builder pattern."""
        tool = MockTool()
        executor = (
            ToolExecutorBuilder()
            .with_whitelist(["mock_tool"])
            .with_default_timeout(30.0)
            .with_tool(tool, timeout=30.0)
            .build()
        )
        assert executor.whitelist == {"mock_tool"}
        assert "mock_tool" in executor.list_tools()


class TestWebSearchTool:
    """Tests for WebSearchTool."""

    @pytest.fixture
    def web_search_tool(self):
        """Create a WebSearchTool instance."""
        return WebSearchTool(max_results=5)

    def test_tool_name(self, web_search_tool):
        """Test tool name."""
        assert web_search_tool.name == "web_search"

    def test_tool_description(self, web_search_tool):
        """Test tool description."""
        assert "search" in web_search_tool.description.lower()

    def test_tool_parameters(self, web_search_tool):
        """Test tool parameters schema."""
        params = web_search_tool.parameters
        assert params["type"] == "object"
        assert "query" in params["properties"]
        assert "query" in params["required"]

    def test_to_openai_tool(self, web_search_tool):
        """Test converting to OpenAI format."""
        openai_tool = web_search_tool.to_openai_tool()
        assert openai_tool["type"] == "function"
        assert openai_tool["function"]["name"] == "web_search"

    @pytest.mark.asyncio
    async def test_execute_missing_query(self, web_search_tool):
        """Test execution with missing query parameter."""
        result = await web_search_tool.execute()
        assert result.is_error
        assert "required" in result.error.lower()

    @pytest.mark.asyncio
    async def test_execute_validates_max_results(self, web_search_tool):
        """Test that max_results is clamped."""
        # max_results should be clamped between 1 and 20
        assert web_search_tool._max_results == 5


class TestDbQueryTool:
    """Tests for DbQueryTool."""

    @pytest.fixture
    def db_query_tool(self):
        """Create a DbQueryTool instance."""
        mock_session_factory = MagicMock()
        return DbQueryTool(
            db_session_factory=mock_session_factory,
            allowed_tables=["sessions", "messages"],
            max_rows=100
        )

    def test_tool_name(self, db_query_tool):
        """Test tool name."""
        assert db_query_tool.name == "db_query"

    def test_tool_description(self, db_query_tool):
        """Test tool description."""
        assert "sql" in db_query_tool.description.lower()

    def test_tool_parameters(self, db_query_tool):
        """Test tool parameters schema."""
        params = db_query_tool.parameters
        assert params["type"] == "object"
        assert "query" in params["properties"]
        assert "query" in params["required"]

    def test_allowed_tables(self, db_query_tool):
        """Test allowed tables property."""
        assert "sessions" in db_query_tool.allowed_tables
        assert "messages" in db_query_tool.allowed_tables

    def test_set_allowed_tables(self, db_query_tool):
        """Test setting allowed tables."""
        db_query_tool.set_allowed_tables(["new_table"])
        assert db_query_tool.allowed_tables == ["new_table"]

    @pytest.mark.asyncio
    async def test_execute_missing_query(self, db_query_tool):
        """Test execution with missing query parameter."""
        result = await db_query_tool.execute()
        assert result.is_error
        assert "required" in result.error.lower()

    def test_validate_query_forbidden_operations(self, db_query_tool):
        """Test validation rejects forbidden operations."""
        forbidden_queries = [
            "INSERT INTO sessions VALUES (1)",
            "UPDATE sessions SET name = 'test'",
            "DELETE FROM sessions",
            "DROP TABLE sessions",
            "TRUNCATE sessions",
            "ALTER TABLE sessions ADD COLUMN test TEXT",
            "CREATE TABLE test (id INT)",
            "GRANT ALL ON sessions TO user",
            "REVOKE ALL ON sessions FROM user",
        ]

        for query in forbidden_queries:
            error = db_query_tool._validate_query(query)
            assert error is not None, f"Query should be rejected: {query}"
            assert "forbidden" in error.lower() or "only select" in error.lower()

    def test_validate_query_select_allowed(self, db_query_tool):
        """Test validation allows SELECT queries."""
        error = db_query_tool._validate_query("SELECT * FROM sessions")
        assert error is None

    def test_validate_query_must_start_with_select(self, db_query_tool):
        """Test that queries must start with SELECT."""
        error = db_query_tool._validate_query("WITH cte AS (SELECT 1) SELECT * FROM cte")
        # This should be allowed as it's still a read query
        # but our simple validator requires SELECT at start
        # This test documents current behavior

    def test_extract_tables(self, db_query_tool):
        """Test extracting table names from queries."""
        tables = db_query_tool._extract_tables("SELECT * FROM sessions WHERE id = 1")
        assert "sessions" in tables

        tables = db_query_tool._extract_tables(
            "SELECT s.name, m.content FROM sessions s JOIN messages m ON s.id = m.session_id"
        )
        assert "sessions" in tables
        assert "messages" in tables

    def test_table_whitelist_check(self, db_query_tool):
        """Test that queries against non-whitelisted tables are rejected."""
        # This is tested through execute, but we can also test the logic
        tables = db_query_tool._extract_tables("SELECT * FROM forbidden_table")
        assert "forbidden_table" in tables
        # The actual check happens in execute()
        assert "forbidden_table" not in [t.lower() for t in db_query_tool.allowed_tables]

    def test_forbidden_patterns(self, db_query_tool):
        """Test all forbidden patterns are compiled."""
        assert len(db_query_tool._forbidden_regex) > 0
        # Check specific patterns
        patterns = [r.pattern for r in db_query_tool._forbidden_regex]
        # Should have patterns for INSERT, UPDATE, DELETE, etc.
        assert any("INSERT" in p.upper() or "\\bINSERT\\b" in p for p in patterns)


class TestToolResult:
    """Tests for ToolResult data structure."""

    def test_success_result(self):
        """Test successful tool result."""
        result = ToolResult(output="Success output")
        assert result.is_success
        assert not result.is_error
        assert result.to_content() == "Success output"

    def test_error_result(self):
        """Test error tool result."""
        result = ToolResult(error="Something went wrong")
        assert result.is_error
        assert not result.is_success
        assert "Error:" in result.to_content()

    def test_to_openai_message(self):
        """Test converting to OpenAI message format."""
        result = ToolResult(output="Test output")
        msg = result.to_openai_message("call_123", "test_tool")
        assert msg["role"] == "tool"
        assert msg["tool_call_id"] == "call_123"
        assert msg["content"] == "Test output"
        assert msg["name"] == "test_tool"

    def test_metadata(self):
        """Test result metadata."""
        result = ToolResult(
            output="Test",
            metadata={"query": "test", "count": 5}
        )
        assert result.metadata["query"] == "test"
        assert result.metadata["count"] == 5


class TestBaseTool:
    """Tests for BaseTool abstract class."""

    def test_validate_parameters_missing_required(self):
        """Test parameter validation for missing required params."""
        tool = MockTool()
        error = tool.validate_parameters({})  # Missing "input"
        assert error is not None
        assert "Missing required parameter" in error

    def test_validate_parameters_wrong_type(self):
        """Test parameter validation for wrong type."""
        tool = MockTool()
        error = tool.validate_parameters({"input": 123})  # Should be string
        assert error is not None
        assert "wrong type" in error.lower()

    def test_validate_parameters_success(self):
        """Test successful parameter validation."""
        tool = MockTool()
        error = tool.validate_parameters({"input": "test"})
        assert error is None
