## 修改需求

### 需求:工具消息存储顺序

当 LLM 返回工具调用请求时，系统必须按正确的顺序存储消息：
1. 首先存储包含 `tool_calls` 的 `assistant` 消息（当前实现缺失此步骤）
2. 然后存储每个 `tool` 角色的消息（工具执行结果）
3. 最后存储最终的 `assistant` 响应消息

消息顺序必须符合 OpenAI API 规范：`tool` 消息必须紧跟在包含对应 `tool_calls` 的 `assistant` 消息之后。

#### 场景:工具调用消息顺序正确

- **当** 用户发送触发工具调用的消息
- **那么** 数据库中的消息顺序为：user → assistant(tool_calls) → tool → ... → assistant(response)

#### 场景:继续对话不报错

- **当** 用户在包含工具调用的对话后继续提问
- **那么** 构建的消息历史符合 API 规范，请求成功

## 新增需求

### 需求:前端过滤工具消息

前端显示消息列表时必须过滤 `role="tool"` 的消息，因为工具调用信息已通过 `assistant.tool_calls` 字段渲染为 ToolCallCard 组件。

#### 场景:工具消息不重复显示

- **当** 加载包含工具调用的历史消息
- **那么** 工具调用信息仅在 assistant 消息的 ToolCallCard 中显示一次
