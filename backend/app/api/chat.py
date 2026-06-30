"""
Chat API routes with SSE streaming support.
"""
import json
from datetime import datetime
from typing import AsyncIterator, List, Dict, Any, Optional
from dataclasses import dataclass
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, async_session_maker
from app.core.config import settings
from app.services import SessionService, MessageService, ProviderService, ConfigService
from app.services.memory_integration import MemoryIntegration
from app.schemas.api import ChatRequest, MessageCreate
from app.providers.base import (
    ChatMessage,
    ProviderConfig,
    ProviderError,
    ToolCall as ProviderToolCall,
)
from app.providers.factory import create_provider
from app.tools import (
    ToolExecutor,
    ToolExecutorBuilder,
    WebSearchTool,
    DbQueryTool,
    ToolResult,
)
from app.models import Session as SessionModel

router = APIRouter(tags=["chat"])


def get_session_service(db: AsyncSession = Depends(get_db)) -> SessionService:
    """Dependency for session service."""
    return SessionService(db)


def get_message_service(db: AsyncSession = Depends(get_db)) -> MessageService:
    """Dependency for message service."""
    return MessageService(db)


def get_provider_service(db: AsyncSession = Depends(get_db)) -> ProviderService:
    """Dependency for provider service."""
    return ProviderService(db)


def get_config_service(db: AsyncSession = Depends(get_db)) -> ConfigService:
    """Dependency for config service."""
    return ConfigService(db)


def build_tool_executor(
    enabled_tools: list,
    config_service: ConfigService
) -> ToolExecutor:
    """
    Build a tool executor with enabled tools.

    Args:
        enabled_tools: List of enabled tool names.
        config_service: Config service for tool configuration.

    Returns:
        Configured ToolExecutor instance.
    """
    builder = ToolExecutorBuilder().with_whitelist(enabled_tools)

    # Add web search tool if enabled
    if "web_search" in enabled_tools:
        builder = builder.with_tool(WebSearchTool(), timeout=30.0)

    # Add db query tool if enabled
    if "db_query" in enabled_tools:
        builder = builder.with_tool(
            DbQueryTool(db_session_factory=async_session_maker),
            timeout=10.0
        )

    return builder.build()


async def build_messages_for_chat(
    session: SessionModel,
    message_service: MessageService,
    user_message: str,
    memory_integration: Optional[MemoryIntegration] = None
) -> list:
    """
    Build message history for chat with optional memory context injection.

    Args:
        session: Session model.
        message_service: Message service.
        user_message: The new user message.
        memory_integration: Memory integration helper (optional).

    Returns:
        List of messages in OpenAI format.
    """
    messages = []

    # Get base system prompt
    system_prompt = session.system_prompt or settings.DEFAULT_SYSTEM_PROMPT

    # Inject memory context if enabled
    if memory_integration and settings.MEMORY_ENABLED:
        system_prompt = await memory_integration.inject_memory_context(
            session_id=str(session.id),
            user_message=user_message,
            base_system_prompt=system_prompt
        )

    # Add system prompt
    messages.append({"role": "system", "content": system_prompt})

    # Get message history
    db_messages, total_count = await message_service.get_by_session(str(session.id), limit=100)
    for msg in db_messages:
        msg_dict = message_service.to_chat_message(msg)
        if msg_dict.get("content") or msg_dict.get("tool_calls"):
            messages.append(msg_dict)

    # Add the new user message
    messages.append({"role": "user", "content": user_message})

    return messages, total_count


def format_sse_event(event_type: str, data: dict) -> str:
    """
    Format a Server-Sent Event.

    Args:
        event_type: Event type name.
        data: Event data dictionary.

    Returns:
        Formatted SSE string.
    """
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


async def stream_chat_response(
    messages: list,
    model: str,
    temperature: float,
    max_tokens: int,
    tool_executor: ToolExecutor,
    provider,
    session_id: str
) -> AsyncIterator[str]:
    """
    Stream chat response with tool call events.

    Args:
        messages: Message history.
        model: Model identifier.
        temperature: Sampling temperature.
        max_tokens: Maximum tokens.
        tool_executor: Tool executor.
        provider: Model provider.
        session_id: Session ID.

    Yields:
        SSE formatted strings.
    """
    max_iterations = 10
    tools = tool_executor.get_openai_tools(allowed_only=True) if tool_executor else None

    # Convert to ChatMessage format
    chat_messages = []
    for msg in messages:
        if isinstance(msg, dict):
            chat_messages.append(ChatMessage(**msg))
        else:
            chat_messages.append(msg)

    accumulated_content = ""
    tool_call_history = []

    for iteration in range(max_iterations):
        # On last iteration, force a final response by not providing tools
        is_last_iteration = iteration == max_iterations - 1
        current_tools = None if is_last_iteration else tools

        try:
            # First, make a non-streaming call to check for tool calls
            completion = await provider.chat(
                messages=chat_messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=current_tools,
                tool_choice="auto" if current_tools else None,
            )

            if completion.tool_calls and not is_last_iteration:
                # Process tool calls
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

                # Add to message history
                chat_messages.append(ChatMessage(**assistant_msg))
                tool_call_history.append(assistant_msg)

                # Execute tools and collect complete info for this iteration only
                iteration_tool_calls = []  # Independent list for this iteration
                tool_messages_to_save = []

                for tool_call in completion.tool_calls:
                    # Record start time
                    started_at = datetime.utcnow()

                    # Emit tool_call_start event
                    yield format_sse_event("tool_call_start", {
                        "tool_name": tool_call.name,
                        "tool_call_id": tool_call.id,
                        "arguments": tool_call.arguments
                    })

                    # Execute tool
                    result = await tool_executor.execute(
                        tool_call.name,
                        tool_call.arguments
                    )

                    # Record end time
                    completed_at = datetime.utcnow()

                    # Emit tool_call_end event
                    yield format_sse_event("tool_call_end", {
                        "tool_call_id": tool_call.id,
                        "status": "success" if result.is_success else "error",
                        "result": result.to_content()[:500]  # Truncate for event
                    })

                    # Collect complete tool call info for this iteration
                    iteration_tool_calls.append({
                        "id": tool_call.id,
                        "message_id": None,
                        "tool_name": tool_call.name,
                        "arguments": tool_call.arguments,
                        "status": "success" if result.is_success else "error",
                        "result": result.to_content(),
                        "error": None if result.is_success else (result.error or "Tool execution failed"),
                        "started_at": started_at.isoformat(),
                        "completed_at": completed_at.isoformat(),
                    })

                    # Add tool result to messages for LLM context
                    tool_msg = {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result.to_content(),
                        "name": tool_call.name
                    }
                    chat_messages.append(ChatMessage(**tool_msg))

                    # Collect tool message for storage
                    tool_messages_to_save.append({
                        "tool_call_id": tool_call.id,
                        "content": result.to_content()
                    })

                # STEP 1: Save assistant(tool_calls) with complete info for this iteration
                async with async_session_maker() as db_session:
                    assistant_message_service = MessageService(db_session)
                    await assistant_message_service.create(
                        session_id,
                        MessageCreate(
                            role="assistant",
                            content=completion.content or "",
                            tool_calls=iteration_tool_calls if iteration_tool_calls else None
                        )
                    )
                    await db_session.commit()

                # STEP 2: Save all tool messages
                async with async_session_maker() as db_session:
                    tool_message_service = MessageService(db_session)
                    for tool_msg_data in tool_messages_to_save:
                        await tool_message_service.create(
                            session_id,
                            MessageCreate(
                                role="tool",
                                content=tool_msg_data["content"],
                                tool_call_id=tool_msg_data["tool_call_id"]
                            )
                        )
                    await db_session.commit()

            else:
                # No tool calls - stream the final response
                accumulated_content = completion.content or ""

                # If we reached max iterations and still have tool calls (edge case),
                # add a note about it
                if is_last_iteration and completion.tool_calls:
                    accumulated_content = (
                        "已达到工具调用上限，以下是基于当前信息生成的回复：\n\n" +
                        (accumulated_content or "请根据以上搜索结果整理答案。")
                    )

                # Stream the content
                if accumulated_content:
                    yield format_sse_event("content_delta", {
                        "content": accumulated_content
                    })

                # Emit done event with final content for frontend to use
                yield format_sse_event("done", {
                    "content": accumulated_content
                })

                # Save the final assistant message with tool_calls = None
                async with async_session_maker() as db_session:
                    independent_message_service = MessageService(db_session)
                    await independent_message_service.create(
                        session_id,
                        MessageCreate(
                            role="assistant",
                            content=accumulated_content,
                            tool_calls=None  # Final response has no tool_calls
                        )
                    )
                    await db_session.commit()

                return

        except ProviderError as e:
            yield format_sse_event("error", {
                "message": str(e),
                "code": "provider_error"
            })
            return

        except Exception as e:
            yield format_sse_event("error", {
                "message": f"Unexpected error: {str(e)}",
                "code": "internal_error"
            })
            return

    # This should not be reached due to is_last_iteration handling above
    # But as a safety fallback, try to generate a final response
    yield format_sse_event("content_delta", {
        "content": "已达到工具调用上限。请稍后重试，或尝试简化您的问题。"
    })
    yield format_sse_event("done", {
        "content": "已达到工具调用上限。请稍后重试，或尝试简化您的问题。"
    })


@router.post("/chat", summary="Send a chat message")
async def chat(
    request: ChatRequest,
    session_service: SessionService = Depends(get_session_service),
    message_service: MessageService = Depends(get_message_service),
    provider_service: ProviderService = Depends(get_provider_service),
    config_service: ConfigService = Depends(get_config_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a chat message and receive a streaming response.

    Uses Server-Sent Events (SSE) for streaming.
    Event types:
    - content_delta: {"delta": "text"} - Streaming text
    - tool_call_start: {"tool_name": "...", "tool_call_id": "..."}
    - tool_call_end: {"tool_call_id": "...", "status": "success/failed"}
    - done: {} - Conversation complete
    - error: {"message": "...", "code": "..."}
    """
    # Get session
    session = await session_service.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Determine provider
    provider_id = session.provider_id
    if not provider_id:
        provider_id = await config_service.get_default_provider()

    # Get provider configuration
    provider_model = await provider_service.get(provider_id)
    if not provider_model:
        # Try to find any active provider as fallback
        providers, _ = await provider_service.get_list(is_active=True, limit=1)
        if providers:
            provider_model = providers[0]
            provider_id = provider_model.id
        else:
            raise HTTPException(
                status_code=400,
                detail="No provider configured. Please add a provider in Settings."
            )

    # Decrypt API key
    api_key = await provider_service.get_decrypted_api_key(provider_id)

    # Build provider config
    provider_config = ProviderConfig.from_db_model(provider_model, api_key)

    # Create provider instance
    try:
        provider = create_provider(provider_config)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create provider: {str(e)}"
        )

    # Determine model and parameters
    # Priority: Session > Provider default > Global default
    model = session.model
    if not model:
        # Check provider's default model
        provider_config = provider_model.config or {}
        model = provider_config.get("default_model")
    if not model:
        model = await config_service.get_default_model()

    temperature = request.temperature
    if temperature is None:
        temperature = float(session.temperature) if session.temperature else await config_service.get_default_temperature()
    max_tokens = request.max_tokens
    if max_tokens is None:
        max_tokens = session.max_tokens or await config_service.get_default_max_tokens()

    # Get enabled tools
    import json as json_module
    enabled_tools = []
    if session.enabled_tools:
        if isinstance(session.enabled_tools, str):
            enabled_tools = json_module.loads(session.enabled_tools)
        else:
            enabled_tools = list(session.enabled_tools)

    # Build tool executor
    tool_executor = build_tool_executor(enabled_tools, config_service)

    # Initialize memory integration
    memory_integration = None
    if settings.MEMORY_ENABLED:
        memory_integration = MemoryIntegration(db)

    # Build message history (with memory context injection)
    messages, message_count = await build_messages_for_chat(
        session, message_service, request.message, memory_integration
    )

    # Save user message
    await message_service.create(
        request.session_id,
        MessageCreate(role="user", content=request.message)
    )

    # Check for checkpoint trigger (every N messages)
    new_message_count = message_count + 1
    checkpoint_needed = await memory_integration.check_checkpoint_trigger(
        request.session_id, new_message_count
    ) if memory_integration else False

    # Stream response
    async def generate():
        async for chunk in stream_chat_response(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            tool_executor=tool_executor,
            provider=provider,
            session_id=request.session_id
        ):
            yield chunk

        # After streaming completes, handle checkpoint if needed
        if checkpoint_needed:
            async with async_session_maker() as checkpoint_db:
                checkpoint_integration = MemoryIntegration(checkpoint_db)
                db_messages, _ = await message_service.get_by_session(request.session_id, limit=100)
                await checkpoint_integration.handle_checkpoint(
                    user_id="default",
                    session_id=request.session_id,
                    messages=db_messages
                )
                await checkpoint_db.commit()

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.post("/chat/end", summary="End a chat session")
async def end_chat(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    End a chat session and trigger memory extraction.
    Call this when the user closes or switches sessions.
    """
    from app.services.session_service import SessionService
    from app.services.message_service import MessageService

    session_service = SessionService(db)
    message_service = MessageService(db)

    # Get session
    session = await session_service.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get messages
    messages, _ = await message_service.get_by_session(session_id, limit=1000)

    # Trigger memory extraction
    if settings.MEMORY_ENABLED and messages:
        memory_integration = MemoryIntegration(db)
        result = await memory_integration.handle_session_end(
            user_id="default",
            session_id=session_id,
            messages=messages
        )
        await db.commit()
        return {
            "status": "success",
            "memories_extracted": result.get("extracted", 0)
        }

    return {"status": "success", "memories_extracted": 0}
