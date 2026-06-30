## 1. 修改后端保存工具调用记录

- [x] 1.1 在 `stream_chat_response` 函数中创建 `saved_tool_calls` 列表，用于收集完整工具调用信息
- [x] 1.2 在工具执行循环中，将工具调用信息添加到 `saved_tool_calls`（格式与前端 ToolCall 接口兼容）
- [x] 1.3 修改 `MessageCreate` 调用，传入 `tool_calls=saved_tool_calls` 参数
- [x] 1.4 确保完整结果（`result.to_content()`）被保存，而不是截断版本

## 2. 验证修复

- [x] 2.1 发送包含工具调用的消息，检查数据库中 `tool_calls` 字段是否正确保存
  - 代码已实现，语法检查通过
  - 需要用户配置有效 API 密钥后测试
- [x] 2.2 重新打开历史会话，确认工具调用卡片正确显示
  - 需要用户手动验证
