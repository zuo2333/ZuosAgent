## 上下文

当前 `stream_chat_response` 函数在保存 assistant 消息时：

```python
# 第 252-254 行
await independent_message_service.create(
    session_id,
    MessageCreate(role="assistant", content=accumulated_content)
)
```

只传了 `content`，没有传 `tool_calls`。而 `tool_call_history` 变量（第 168 行）已经收集了工具调用信息，但没有被使用。

## 目标 / 非目标

**目标：**
- 将工具调用记录持久化到数据库
- 确保前端加载历史消息时能正确显示工具调用卡片

**非目标：**
- 不修改数据库 schema（`tool_calls` 字段已存在）
- 不修改前端代码（前端已支持显示 tool_calls）

## 决策

### 决策 1：使用前端 ToolCall 接口格式

**选择方案：** 保存为前端 `ToolCall` 接口兼容的格式

```json
[
  {
    "id": "call_xxx",
    "message_id": "msg_xxx",
    "tool_name": "web_search",
    "arguments": {"query": "上海天气"},
    "status": "success",
    "result": "...",
    "error": null,
    "started_at": "2026-06-25T06:00:00Z",
    "completed_at": "2026-06-25T06:00:01Z"
  }
]
```

**理由：** 与前端 `ToolCallCard` 组件期望的 `ToolCall` 接口完全兼容。

**注意：** 不能直接使用 `tool_call_history`（OpenAI 格式），需要转换为前端格式。

### 决策 2：在工具执行时收集完整信息

**数据来源：**
- `tool_call_start` 事件包含：`tool_name`, `tool_call_id`, `arguments`
- `tool_call_end` 事件包含：`status`, `result`（截断版本）

**方案：** 创建 `saved_tool_calls` 列表，在执行工具时收集完整信息：

```python
saved_tool_calls = []

# 工具执行时
saved_tool_calls.append({
    "id": tool_call.id,
    "message_id": None,  # 稍后填充
    "tool_name": tool_call.name,
    "arguments": tool_call.arguments,  # 对象，非字符串
    "status": "success" if result.is_success else "error",
    "result": result.to_content(),  # 完整结果
    "error": None if result.is_success else result.error,
    "started_at": datetime.utcnow().isoformat(),
    "completed_at": datetime.utcnow().isoformat(),
})
```

## 风险 / 权衡

| 风险 | 缓解措施 |
|------|----------|
| 现有历史数据没有 tool_calls | 可接受：旧消息继续正常显示，只是没有工具卡片 |
| tool_calls 格式需要与前端兼容 | 使用 OpenAI 标准格式，前端已支持 |
