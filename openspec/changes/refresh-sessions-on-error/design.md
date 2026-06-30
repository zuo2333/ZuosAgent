## 上下文

当前 `sessionStore.ts` 中的 `deleteSession` 和 `updateSession` 方法在失败时只设置错误状态，不会刷新会话列表。这导致前端可能显示不存在的会话。

## 目标 / 非目标

**目标：**
- 操作失败时自动刷新会话列表
- 保持前端与后端数据同步

**非目标：**
- 不修改后端代码
- 不添加重试机制

## 决策

### 决策 1：在 catch 块中调用 fetchSessions

**方案：** 在 `deleteSession`、`updateSession` 和 `fetchMessages` 的 catch 块中调用 `get().fetchSessions()`

```typescript
// deleteSession
catch (error) {
  set({ error: ..., isLoading: false })
  get().fetchSessions()
}

// updateSession
catch (error) {
  set({ error: ..., isLoading: false })
  get().fetchSessions()
}

// fetchMessages (当会话不存在时)
catch (error) {
  set({ error: ..., isLoading: false })
  // 如果会话不存在，清除当前会话并刷新列表
  set({ currentSession: null, messages: [] })
  get().fetchSessions()
}
```

**理由：** 简单有效，确保失败后数据同步

### 决策 2：fetchMessages 失败时清除当前会话

**场景：** 用户点击一个已被删除的会话，`fetchMessages` 返回 404

**处理方式：**
1. 清除 `currentSession`（因为会话不存在）
2. 清空 `messages`
3. 刷新会话列表

## 风险 / 权衡

| 风险 | 缓解措施 |
|------|----------|
| 刷新可能也失败 | 可接受：用户已看到错误提示，可以手动刷新页面 |
