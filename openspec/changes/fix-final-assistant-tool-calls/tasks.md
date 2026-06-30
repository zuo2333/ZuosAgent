## 1. 后端修改

- [x] 1.1 移除 `saved_tool_calls` 累积变量，改为每轮独立的 `iteration_tool_calls` 列表
- [x] 1.2 修改 assistant(tool_calls) 消息存储：包含完整的工具调用信息（id, tool_name, arguments, status, result）
- [x] 1.3 确保每条 assistant(tool_calls) 只包含当前轮次，不累积历史
- [x] 1.4 修改最终 assistant 消息：tool_calls 明确设为 None

## 2. 测试验证

- [x] 2.1 测试单轮工具调用后消息格式正确
- [x] 2.2 测试多轮工具调用后继续对话不报错
- [x] 2.3 验证前端能正确显示历史工具调用信息
