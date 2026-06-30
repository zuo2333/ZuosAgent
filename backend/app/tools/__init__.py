"""
Tools module.

This module provides the core abstraction for LLM tools,
including the Tool protocol, ToolExecutor, and built-in tools.
"""
from app.tools.base import (
    Tool,
    ToolResult,
    ToolError,
    ToolTimeoutError,
    ToolNotAllowedError,
    BaseTool,
    ToolRegistry,
)
from app.tools.executor import (
    ToolExecutor,
    ToolExecutorBuilder,
)
from app.tools.web_search import WebSearchTool, WebSearchToolConfig
from app.tools.db_query import DbQueryTool, DbQueryToolConfig
from app.tools.tool_calling import (
    ToolCallLoop,
    ToolCallLoopConfig,
    ToolCallLoopResult,
    format_tool_call_message,
    format_tool_result_message,
    messages_to_openai_format,
    execute_tool_call,
    build_tool_call_history,
)

__all__ = [
    # Protocol and base types
    "Tool",
    "ToolResult",
    "ToolError",
    "ToolTimeoutError",
    "ToolNotAllowedError",
    "BaseTool",
    "ToolRegistry",
    # Executor
    "ToolExecutor",
    "ToolExecutorBuilder",
    # Built-in tools
    "WebSearchTool",
    "WebSearchToolConfig",
    "DbQueryTool",
    "DbQueryToolConfig",
    # Tool calling
    "ToolCallLoop",
    "ToolCallLoopConfig",
    "ToolCallLoopResult",
    "format_tool_call_message",
    "format_tool_result_message",
    "messages_to_openai_format",
    "execute_tool_call",
    "build_tool_call_history",
]
