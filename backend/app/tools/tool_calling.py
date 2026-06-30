"""
Tool Calling Adapter module.

Implements Function Calling message format adaptation for OpenAI format
and the tool calling loop (model -> tool call -> execute -> result -> model).
"""
import json
from typing import List, Dict, Any, Optional, AsyncIterator, Callable, Awaitable
from dataclasses import dataclass

from app.providers.base import (
    ChatMessage,
    ToolCall,
    ChatCompletionResult,
    ProviderError,
)
from app.tools.base import ToolResult
from app.tools.executor import ToolExecutor


# ============================================================================
# Message Formatting
# ============================================================================

def format_tool_call_message(
    tool_call: ToolCall,
    role: str = "assistant"
) -> Dict[str, Any]:
    """
    Format a tool call as an assistant message.

    Args:
        tool_call: ToolCall object.
        role: Message role (usually "assistant").

    Returns:
        Message dictionary in OpenAI format.
    """
    return {
        "role": role,
        "content": None,
        "tool_calls": [
            {
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.name,
                    "arguments": json.dumps(tool_call.arguments)
                }
            }
        ]
    }


def format_tool_result_message(
    tool_result: ToolResult,
    tool_call_id: str,
    tool_name: str
) -> Dict[str, Any]:
    """
    Format a tool result as a tool message.

    Args:
        tool_result: ToolResult object.
        tool_call_id: ID of the tool call this is responding to.
        tool_name: Name of the tool.

    Returns:
        Message dictionary in OpenAI format.
    """
    return {
        "role": "tool",
        "tool_call_id": tool_call_id,
        "content": tool_result.to_content(),
        "name": tool_name
    }


def messages_to_openai_format(messages: List[ChatMessage]) -> List[Dict[str, Any]]:
    """
    Convert ChatMessage objects to OpenAI format dictionaries.

    Args:
        messages: List of ChatMessage objects.

    Returns:
        List of message dictionaries.
    """
    result = []
    for msg in messages:
        msg_dict: Dict[str, Any] = {"role": msg.role}

        if msg.content is not None:
            msg_dict["content"] = msg.content

        if msg.name:
            msg_dict["name"] = msg.name

        if msg.tool_calls:
            msg_dict["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in msg.tool_calls
            ]

        if msg.tool_call_id:
            msg_dict["tool_call_id"] = msg.tool_call_id

        result.append(msg_dict)

    return result


# ============================================================================
# Tool Calling Loop
# ============================================================================

@dataclass
class ToolCallLoopConfig:
    """Configuration for the tool calling loop."""
    max_iterations: int = 10
    stop_on_error: bool = False


@dataclass
class ToolCallLoopResult:
    """Result of the tool calling loop."""
    final_content: Optional[str] = None
    messages: List[Dict[str, Any]] = None
    tool_calls_made: int = 0
    iterations: int = 0
    finish_reason: Optional[str] = None

    def __post_init__(self):
        if self.messages is None:
            self.messages = []


class ToolCallLoop:
    """
    Implements the tool calling loop.

    Flow:
    1. Send messages to model
    2. If model returns tool_calls, execute them
    3. Add tool results to messages
    4. Repeat until model returns content or max iterations reached

    Usage:
        loop = ToolCallLoop(provider, tool_executor)
        result = await loop.run(messages, model, temperature=0.7)

        # Streaming version
        async for chunk in loop.run_stream(messages, model):
            print(chunk, end="")
    """

    def __init__(
        self,
        provider,  # ModelProvider
        tool_executor: ToolExecutor,
        config: Optional[ToolCallLoopConfig] = None
    ) -> None:
        """
        Initialize the tool calling loop.

        Args:
            provider: ModelProvider instance.
            tool_executor: ToolExecutor instance.
            config: Loop configuration.
        """
        self.provider = provider
        self.tool_executor = tool_executor
        self.config = config or ToolCallLoopConfig()

    async def run(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> ToolCallLoopResult:
        """
        Run the tool calling loop (non-streaming).

        Args:
            messages: Initial messages in OpenAI format.
            model: Model identifier.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            **kwargs: Additional parameters.

        Returns:
            ToolCallLoopResult with final content and message history.
        """
        result = ToolCallLoopResult(messages=list(messages))
        tools = self.tool_executor.get_openai_tools(allowed_only=True)

        for iteration in range(self.config.max_iterations):
            result.iterations = iteration + 1

            # Convert messages to ChatMessage for the provider
            chat_messages = [
                ChatMessage(**msg) if isinstance(msg, dict) else msg
                for msg in result.messages
            ]

            # Call the model
            completion = await self.provider.chat(
                messages=chat_messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None,
                **kwargs
            )

            # Check for tool calls
            if completion.tool_calls:
                # Add assistant message with tool calls
                assistant_msg = {
                    "role": "assistant",
                    "content": completion.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.name,
                                "arguments": json.dumps(tc.arguments)
                            }
                        }
                        for tc in completion.tool_calls
                    ]
                }
                result.messages.append(assistant_msg)

                # Execute each tool call
                for tool_call in completion.tool_calls:
                    tool_result = await self.tool_executor.execute(
                        tool_call.name,
                        tool_call.arguments
                    )

                    result.tool_calls_made += 1

                    # Add tool result message
                    tool_msg = format_tool_result_message(
                        tool_result,
                        tool_call.id,
                        tool_call.name
                    )
                    result.messages.append(tool_msg)

            else:
                # No tool calls - we have the final response
                result.final_content = completion.content
                result.finish_reason = completion.finish_reason

                # Add final assistant message
                result.messages.append({
                    "role": "assistant",
                    "content": completion.content
                })

                break

        else:
            # Max iterations reached
            result.finish_reason = "max_iterations"

        return result

    async def run_stream(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncIterator[str]:
        """
        Run the tool calling loop with streaming.

        For simplicity, this executes tool calls silently and only
        streams the final text response.

        Args:
            messages: Initial messages.
            model: Model identifier.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens.
            **kwargs: Additional parameters.

        Yields:
            Text chunks from the final model response.
        """
        result_messages = list(messages)
        tools = self.tool_executor.get_openai_tools(allowed_only=True)

        for iteration in range(self.config.max_iterations):
            # Convert messages
            chat_messages = [
                ChatMessage(**msg) if isinstance(msg, dict) else msg
                for msg in result_messages
            ]

            # First, do a non-streaming call to check for tool calls
            completion = await self.provider.chat(
                messages=chat_messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None,
                **kwargs
            )

            if completion.tool_calls:
                # Execute tool calls silently
                assistant_msg = {
                    "role": "assistant",
                    "content": completion.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.name,
                                "arguments": json.dumps(tc.arguments)
                            }
                        }
                        for tc in completion.tool_calls
                    ]
                }
                result_messages.append(assistant_msg)

                for tool_call in completion.tool_calls:
                    tool_result = await self.tool_executor.execute(
                        tool_call.name,
                        tool_call.arguments
                    )

                    tool_msg = format_tool_result_message(
                        tool_result,
                        tool_call.id,
                        tool_call.name
                    )
                    result_messages.append(tool_msg)

            else:
                # No tool calls - stream the final response
                chat_messages = [
                    ChatMessage(**msg) if isinstance(msg, dict) else msg
                    for msg in result_messages
                ]

                async for chunk in self.provider.chat_stream(
                    messages=chat_messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                ):
                    yield chunk

                return

        # Max iterations - do one final stream
        chat_messages = [
            ChatMessage(**msg) if isinstance(msg, dict) else msg
            for msg in result_messages
        ]

        async for chunk in self.provider.chat_stream(
            messages=chat_messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=None,  # No more tools
            **kwargs
        ):
            yield chunk


# ============================================================================
# Convenience Functions
# ============================================================================

async def execute_tool_call(
    tool_executor: ToolExecutor,
    tool_call: ToolCall
) -> ToolResult:
    """
    Execute a single tool call.

    Args:
        tool_executor: ToolExecutor instance.
        tool_call: ToolCall to execute.

    Returns:
        ToolResult from execution.
    """
    return await tool_executor.execute(
        tool_call.name,
        tool_call.arguments
    )


def build_tool_call_history(
    messages: List[Dict[str, Any]],
    tool_calls: List[ToolCall],
    tool_results: List[ToolResult]
) -> List[Dict[str, Any]]:
    """
    Build message history with tool calls and results.

    Args:
        messages: Existing messages.
        tool_calls: List of tool calls made.
        tool_results: Corresponding tool results.

    Returns:
        Updated message list.
    """
    result = list(messages)

    # Add assistant message with tool calls
    assistant_msg = {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.name,
                    "arguments": json.dumps(tc.arguments)
                }
            }
            for tc in tool_calls
        ]
    }
    result.append(assistant_msg)

    # Add tool result messages
    for tc, tr in zip(tool_calls, tool_results):
        tool_msg = format_tool_result_message(tr, tc.id, tc.name)
        result.append(tool_msg)

    return result
