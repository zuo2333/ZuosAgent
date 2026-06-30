## 修改需求

### 需求:消息存储格式（遵循 OpenAI 规范）

系统必须按照以下格式存储消息，符合 OpenAI API 规范：

1. **assistant(工具调用) 消息**：`tool_calls` 字段包含当前轮次的完整信息（id, tool_name, arguments, status, result, started_at, completed_at）
2. **tool 消息**：存储 `tool_call_id` 和 `content`（工具执行结果），用于 API 消息格式
3. **assistant(最终响应) 消息**：`tool_calls` 字段必须为 `null`
4. **不累积历史**：每条 assistant(tool_calls) 只包含当前轮次的工具调用，不累积历史轮次

#### 场景:单轮工具调用

- **当** LLM 返回工具调用并执行后返回最终响应
- **那么** 消息顺序为：user → assistant(tool_calls) → tool → assistant(响应)
- **那么** assistant(tool_calls) 包含完整的工具调用信息
- **那么** 最终 assistant 消息的 tool_calls 为 null

#### 场景:多轮工具调用

- **当** LLM 进行多轮工具调用
- **那么** 每条 assistant(tool_calls) 只包含当前轮次的工具调用
- **那么** 最终 assistant 消息的 tool_calls 为 null
- **那么** 继续对话时 API 消息格式正确

#### 场景:继续对话不报错

- **当** 用户在多轮工具调用后继续提问
- **那么** API 消息格式符合 OpenAI 规范，请求成功

#### 场景:前端正确显示历史工具调用

- **当** 加载包含工具调用的历史消息
- **那么** 前端从 assistant.tool_calls 直接获取完整信息
- **那么** ToolCallCard 正确显示工具调用的请求和结果
