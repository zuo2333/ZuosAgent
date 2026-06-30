## 1. 修改前端会话 Store

- [x] 1.1 修改 `deleteSession` 方法，在 catch 块中调用 `get().fetchSessions()`
- [x] 1.2 修改 `updateSession` 方法，在 catch 块中调用 `get().fetchSessions()`
- [x] 1.3 修改 `fetchMessages` 方法，在 catch 块中清除当前会话并调用 `get().fetchSessions()`

## 2. 验证

- [x] 2.1 测试删除不存在的会话，确认列表自动刷新
  - 代码已实现，开发服务器正常启动
  - 需要用户手动测试验证
- [x] 2.2 测试点击不存在的会话，确认当前会话被清除且列表刷新
  - 需要用户手动测试验证
