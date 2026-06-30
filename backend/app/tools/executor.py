"""
Tool Executor module.

Implements tool registration, whitelist checking, execution dispatch,
and timeout control.
"""
import asyncio
from typing import Dict, Any, Optional, List, Set

from app.tools.base import (
    Tool,
    ToolResult,
    ToolError,
    ToolTimeoutError,
    ToolNotAllowedError,
    ToolExecutionError,
    ToolRegistry,
)


class ToolExecutor:
    """
    Executor for managing and running tools.

    Provides:
    - Tool registration and management
    - Whitelist-based access control
    - Execution dispatch with parameter validation
    - Timeout control for tool execution

    Usage:
        executor = ToolExecutor(
            whitelist=["web_search", "db_query"],
            default_timeout=30.0
        )

        # Register tools
        executor.register(WebSearchTool())
        executor.register(DbQueryTool())

        # Execute a tool
        result = await executor.execute("web_search", {"query": "python async"})

        # Get tools for OpenAI format
        tools = executor.get_openai_tools()
    """

    def __init__(
        self,
        whitelist: Optional[List[str]] = None,
        default_timeout: float = 30.0
    ) -> None:
        """
        Initialize the tool executor.

        Args:
            whitelist: List of allowed tool names. If None, all tools are allowed.
            default_timeout: Default timeout in seconds for tool execution.
        """
        self._registry = ToolRegistry()
        self._whitelist: Optional[Set[str]] = set(whitelist) if whitelist else None
        self._default_timeout = default_timeout
        self._timeouts: Dict[str, float] = {}  # Per-tool timeouts

    @property
    def whitelist(self) -> Optional[Set[str]]:
        """Get the current whitelist."""
        return self._whitelist

    def set_whitelist(self, tools: List[str]) -> None:
        """
        Set the tool whitelist.

        Args:
            tools: List of allowed tool names.
        """
        self._whitelist = set(tools)

    def add_to_whitelist(self, tool_name: str) -> None:
        """
        Add a tool to the whitelist.

        Args:
            tool_name: Tool name to add.
        """
        if self._whitelist is None:
            self._whitelist = set()
        self._whitelist.add(tool_name)

    def remove_from_whitelist(self, tool_name: str) -> bool:
        """
        Remove a tool from the whitelist.

        Args:
            tool_name: Tool name to remove.

        Returns:
            True if removed, False if not in whitelist.
        """
        if self._whitelist and tool_name in self._whitelist:
            self._whitelist.remove(tool_name)
            return True
        return False

    def is_allowed(self, tool_name: str) -> bool:
        """
        Check if a tool is allowed.

        Args:
            tool_name: Tool name to check.

        Returns:
            True if the tool is allowed, False otherwise.
        """
        # If no whitelist, all tools are allowed
        if self._whitelist is None:
            return True
        return tool_name in self._whitelist

    def register(self, tool: Tool, timeout: Optional[float] = None) -> None:
        """
        Register a tool.

        Args:
            tool: Tool instance to register.
            timeout: Optional timeout for this specific tool.

        Raises:
            ValueError: If a tool with the same name is already registered.
        """
        self._registry.register(tool)
        if timeout is not None:
            self._timeouts[tool.name] = timeout

    def unregister(self, name: str) -> bool:
        """
        Unregister a tool.

        Args:
            name: Name of the tool to unregister.

        Returns:
            True if unregistered, False if not found.
        """
        if name in self._timeouts:
            del self._timeouts[name]
        return self._registry.unregister(name)

    def get_tool(self, name: str) -> Optional[Tool]:
        """
        Get a registered tool by name.

        Args:
            name: Tool name.

        Returns:
            Tool instance or None.
        """
        return self._registry.get(name)

    def list_tools(self) -> List[str]:
        """Get list of registered tool names."""
        return self._registry.list_tools()

    def list_allowed_tools(self) -> List[str]:
        """Get list of allowed (whitelisted) tool names."""
        all_tools = self.list_tools()
        if self._whitelist is None:
            return all_tools
        return [t for t in all_tools if t in self._whitelist]

    def get_timeout(self, tool_name: str) -> float:
        """
        Get the timeout for a specific tool.

        Args:
            tool_name: Tool name.

        Returns:
            Timeout in seconds.
        """
        return self._timeouts.get(tool_name, self._default_timeout)

    def set_timeout(self, tool_name: str, timeout: float) -> None:
        """
        Set timeout for a specific tool.

        Args:
            tool_name: Tool name.
            timeout: Timeout in seconds.
        """
        self._timeouts[tool_name] = timeout

    async def execute(
        self,
        tool_name: str,
        params: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> ToolResult:
        """
        Execute a tool with the given parameters.

        Performs whitelist checking, parameter validation,
        and timeout-controlled execution.

        Args:
            tool_name: Name of the tool to execute.
            params: Parameters for the tool.
            timeout: Optional timeout override.

        Returns:
            ToolResult containing output or error.

        Note:
            This method never raises exceptions - all errors are
            returned as ToolResult with error message.
        """
        # Check whitelist
        if not self.is_allowed(tool_name):
            return ToolResult(
                error=f"Tool '{tool_name}' is not allowed. "
                      f"Allowed tools: {self.list_allowed_tools()}"
            )

        # Get tool
        tool = self.get_tool(tool_name)
        if tool is None:
            return ToolResult(
                error=f"Tool '{tool_name}' is not registered. "
                      f"Available tools: {self.list_tools()}"
            )

        # Validate parameters
        if hasattr(tool, 'validate_parameters'):
            validation_error = tool.validate_parameters(params)
            if validation_error:
                return ToolResult(error=f"Parameter validation failed: {validation_error}")

        # Determine timeout
        effective_timeout = timeout if timeout is not None else self.get_timeout(tool_name)

        # Execute with timeout
        try:
            result = await asyncio.wait_for(
                tool.execute(**params),
                timeout=effective_timeout
            )
            return result

        except asyncio.TimeoutError:
            return ToolResult(
                error=f"Tool '{tool_name}' execution timed out after {effective_timeout} seconds"
            )

        except ToolError as e:
            return ToolResult(error=str(e))

        except Exception as e:
            return ToolResult(
                error=f"Tool '{tool_name}' execution failed: {str(e)}"
            )

    async def execute_safe(
        self,
        tool_name: str,
        params: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> ToolResult:
        """
        Execute a tool safely with all error handling.

        This is an alias for execute() - the execute method already
        handles all errors and returns them as ToolResult.

        Args:
            tool_name: Name of the tool to execute.
            params: Parameters for the tool.
            timeout: Optional timeout override.

        Returns:
            ToolResult containing output or error.
        """
        return await self.execute(tool_name, params, timeout)

    def get_openai_tools(self, allowed_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get tools in OpenAI function calling format.

        Args:
            allowed_only: If True, only return whitelisted tools.

        Returns:
            List of tool definitions in OpenAI format.
        """
        tools = self._registry.get_all()

        if allowed_only and self._whitelist is not None:
            tools = [t for t in tools if t.name in self._whitelist]

        result = []
        for tool in tools:
            if hasattr(tool, 'to_openai_tool'):
                result.append(tool.to_openai_tool())
            else:
                # Fallback for basic Tool protocol
                result.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters,
                    }
                })

        return result

    def clear(self) -> None:
        """Clear all registered tools and timeouts."""
        self._registry = ToolRegistry()
        self._timeouts.clear()


class ToolExecutorBuilder:
    """
    Builder for creating ToolExecutor instances.

    Provides a fluent interface for configuring and building
    tool executors.

    Usage:
        executor = (ToolExecutorBuilder()
            .with_whitelist(["web_search", "db_query"])
            .with_default_timeout(30.0)
            .with_tool(WebSearchTool(), timeout=30.0)
            .with_tool(DbQueryTool(), timeout=10.0)
            .build())
    """

    def __init__(self) -> None:
        """Initialize the builder."""
        self._whitelist: Optional[List[str]] = None
        self._default_timeout: float = 30.0
        self._tools: List[tuple[Tool, Optional[float]]] = []

    def with_whitelist(self, tools: List[str]) -> "ToolExecutorBuilder":
        """
        Set the tool whitelist.

        Args:
            tools: List of allowed tool names.

        Returns:
            self for chaining.
        """
        self._whitelist = tools
        return self

    def with_default_timeout(self, timeout: float) -> "ToolExecutorBuilder":
        """
        Set the default timeout.

        Args:
            timeout: Default timeout in seconds.

        Returns:
            self for chaining.
        """
        self._default_timeout = timeout
        return self

    def with_tool(self, tool: Tool, timeout: Optional[float] = None) -> "ToolExecutorBuilder":
        """
        Add a tool to be registered.

        Args:
            tool: Tool instance.
            timeout: Optional timeout for this tool.

        Returns:
            self for chaining.
        """
        self._tools.append((tool, timeout))
        return self

    def build(self) -> ToolExecutor:
        """
        Build the ToolExecutor instance.

        Returns:
            Configured ToolExecutor instance.
        """
        executor = ToolExecutor(
            whitelist=self._whitelist,
            default_timeout=self._default_timeout
        )

        for tool, timeout in self._tools:
            executor.register(tool, timeout)

        return executor
