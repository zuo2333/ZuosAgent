## 上下文

当前代码存在两个问题：

1. **tool_calls 累积问题**：`saved_tool_calls` 在循环外部定义，累积所有迭代
2. **数据冗余**：工具结果同时存储在 tool 消息和 assistant.tool_calls 中

## 目标 / 非目标

**目标：**
- 完全符合 OpenAI API 消息格式规范
- 数据不冗余，职责清晰
- 消息顺序自然正确
- 前端可正确显示工具调用信息

**非目标：**
- 不修改数据库 schema
- 不修改前端显示逻辑（前端已有 tool_call_id 关联逻辑）

## 决策

### 决策 1：每轮独立存储完整信息

**选择方案：** 每轮的 assistant(tool_calls) 消息存储完整的工具调用信息（包括 result），但不累积历史

**消息存储格式：**

```
user → assistant(tool_calls完整) → tool(结果) → assistant(tool_calls完整) → tool(结果) → assistant(响应)
```

| 消息类型 | 存储内容 | 说明 |
|----------|----------|------|
| assistant(工具调用) | `{id, tool_name, arguments, status, result, ...}` | 完整信息，前端可直接渲染 |
| tool | `tool_call_id + content` | 保持不变，用于 API 消息格式 |
| assistant(最终响应) | 文本内容 | `tool_calls = null` |

**理由：**
- 符合 OpenAI API 规范（消息顺序正确）
- 前端无需修改（ToolCallCard 从 tool_calls 获取 result）
- 数据有冗余但可控（每轮独立，不累积历史）
- 实现简单，改动最小

### 决策 2：移除累积变量

**实现方式：**

```python
for iteration in range(max_iterations):
    # 每轮独立的 tool_calls 列表
    iteration_tool_calls = []

    if completion.tool_calls:
        for tool_call in completion.tool_calls:
            # 执行工具
            result = await tool_executor.execute(...)

            # 添加到当前轮次列表
            iteration_tool_calls.append({
                "id": tool_call.id,
                "tool_name": tool_call.name,
                "arguments": tool_call.arguments,
                "status": "success",
                "result": result.to_content(),
                ...
            })

        # 存储 assistant(tool_calls)，使用 iteration_tool_calls
        await message_service.create(
            session_id,
            MessageCreate(
                role="assistant",
                content=completion.content or "",
                tool_calls=iteration_tool_calls  # 只有当前轮次
            )
        )

    else:
        # 最终响应，tool_calls = null
        await message_service.create(
            session_id,
            MessageCreate(
                role="assistant",
                content=accumulated_content,
                tool_calls=None  # 明确设置为 None
            )
        )
```

## 风险 / 权衡

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 现有会话数据错误 | 用户可能遇到历史会话报错 | 用户可删除有问题的会话 |
| 前端需要适配 | 需确认前端通过 tool_call_id 关联 | 检查前端代码确认兼容性 |
