"""
Base module for Tool abstraction.

Defines the Tool protocol and common data structures
that all tools must implement.
"""
from typing import Protocol, Dict, Any, Optional, List, runtime_checkable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio


# ============================================================================
# Tool Result Data Structures
# ============================================================================

@dataclass
class ToolResult:
    """
    Result of tool execution.

    Contains either successful output or an error message.
    Used to format tool responses for the model.
    """
    output: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_success(self) -> bool:
        """Check if the tool execution was successful."""
        return self.error is None

    @property
    def is_error(self) -> bool:
        """Check if the tool execution failed."""
        return self.error is not None

    def to_content(self) -> str:
        """Get the content for the model (output or error)."""
        if self.is_success:
            return self.output or ""
        return f"Error: {self.error}"

    def to_openai_message(self, tool_call_id: str, name: str) -> Dict[str, Any]:
        """Convert to OpenAI tool message format."""
        return {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": self.to_content(),
            "name": name,
        }


# ============================================================================
# Tool Exceptions
# ============================================================================

class ToolError(Exception):
    """Base exception for tool-related errors."""
    def __init__(self, message: str, tool_name: Optional[str] = None):
        super().__init__(message)
        self.tool_name = tool_name


class ToolTimeoutError(ToolError):
    """Exception raised when tool execution times out."""
    def __init__(self, tool_name: str, timeout_seconds: float):
        super().__init__(
            f"Tool '{tool_name}' execution timed out after {timeout_seconds} seconds",
            tool_name
        )
        self.timeout_seconds = timeout_seconds


class ToolNotAllowedError(ToolError):
    """Exception raised when a tool is not in the whitelist."""
    def __init__(self, tool_name: str):
        super().__init__(
            f"Tool '{tool_name}' is not allowed",
            tool_name
        )


class ToolExecutionError(ToolError):
    """Exception raised when tool execution fails."""
    def __init__(self, tool_name: str, original_error: Exception):
        super().__init__(
            f"Tool '{tool_name}' execution failed: {str(original_error)}",
            tool_name
        )
        self.original_error = original_error


# ============================================================================
# Tool Protocol
# ============================================================================

@runtime_checkable
class Tool(Protocol):
    """
    Protocol defining the interface for tools.

    All tools must implement this protocol to be used with the ToolExecutor.
    Tools follow the OpenAI function calling format.

    Usage:
        class MyTool:
            name = "my_tool"
            description = "Does something useful"
            parameters = {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The query"}
                },
                "required": ["query"]
            }

            async def execute(self, query: str) -> ToolResult:
                # Do something
                return ToolResult(output="Result")

        # Use with executor
        executor = ToolExecutor(whitelist=["my_tool"])
        executor.register(MyTool())
        result = await executor.execute("my_tool", {"query": "test"})
    """

    @property
    def name(self) -> str:
        """Unique identifier for this tool."""
        ...

    @property
    def description(self) -> str:
        """Human-readable description of what the tool does."""
        ...

    @property
    def parameters(self) -> Dict[str, Any]:
        """
        JSON Schema for the tool parameters.

        Follows OpenAI function calling format:
        {
            "type": "object",
            "properties": {
                "param_name": {
                    "type": "string",
                    "description": "Parameter description"
                }
            },
            "required": ["param_name"]
        }
        """
        ...

    async def execute(self, **params: Any) -> ToolResult:
        """
        Execute the tool with the given parameters.

        Args:
            **params: Tool parameters as keyword arguments.

        Returns:
            ToolResult containing output or error.
        """
        ...


# ============================================================================
# Base Tool Implementation
# ============================================================================

class BaseTool(ABC):
    """
    Base class for tool implementations.

    Provides common functionality for tools including
    JSON schema generation and parameter validation.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this tool."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what the tool does."""
        ...

    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """JSON Schema for the tool parameters."""
        ...

    @abstractmethod
    async def execute(self, **params: Any) -> ToolResult:
        """Execute the tool with the given parameters."""
        ...

    def to_openai_tool(self) -> Dict[str, Any]:
        """
        Convert to OpenAI tool format.

        Returns:
            Dictionary in OpenAI function calling format.
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }

    def validate_parameters(self, params: Dict[str, Any]) -> Optional[str]:
        """
        Validate parameters against the schema.

        This is a basic validation. For more robust validation,
        use a JSON Schema validator like jsonschema.

        Args:
            params: Parameters to validate.

        Returns:
            Error message if validation fails, None if valid.
        """
        schema = self.parameters
        required = schema.get("required", [])
        properties = schema.get("properties", {})

        # Check required parameters
        for req in required:
            if req not in params:
                return f"Missing required parameter: {req}"

        # Check parameter types (basic check)
        for key, value in params.items():
            if key in properties:
                expected_type = properties[key].get("type")
                if expected_type:
                    if not self._check_type(value, expected_type):
                        return f"Parameter '{key}' has wrong type. Expected {expected_type}"

        return None

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches the expected JSON Schema type."""
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None),
        }

        expected = type_map.get(expected_type)
        if expected is None:
            return True  # Unknown type, skip validation

        return isinstance(value, expected)


# ============================================================================
# Tool Registry
# ============================================================================

class ToolRegistry:
    """
    Registry for managing tool instances.

    Maintains a collection of registered tools and provides
    lookup and management functionality.
    """

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """
        Register a tool.

        Args:
            tool: Tool instance to register.

        Raises:
            ValueError: If a tool with the same name is already registered.
        """
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")
        self._tools[tool.name] = tool

    def unregister(self, name: str) -> bool:
        """
        Unregister a tool.

        Args:
            name: Name of the tool to unregister.

        Returns:
            True if unregistered, False if not found.
        """
        if name in self._tools:
            del self._tools[name]
            return True
        return False

    def get(self, name: str) -> Optional[Tool]:
        """
        Get a tool by name.

        Args:
            name: Tool name.

        Returns:
            Tool instance or None if not found.
        """
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        """Get list of registered tool names."""
        return list(self._tools.keys())

    def get_all(self) -> List[Tool]:
        """Get all registered tools."""
        return list(self._tools.values())

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """Get all tools in OpenAI format."""
        return [tool.to_openai_tool() for tool in self._tools.values() if hasattr(tool, 'to_openai_tool')]

    def __contains__(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self._tools

    def __len__(self) -> int:
        """Get the number of registered tools."""
        return len(self._tools)
