## 为什么

当会话操作（删除、更新）失败时（如会话已被其他客户端删除），前端 store 中仍保留过期的会话数据，导致用户继续操作不存在的会话。需要在操作失败时自动刷新会话列表，保持前端与后端数据同步。

## 变更内容

- 在 `deleteSession` 失败时自动刷新会话列表
- 在 `updateSession` 失败时自动刷新会话列表
- 在 `setCurrentSession` 导致 `fetchMessages` 失败时自动刷新会话列表
- 提供更友好的错误提示

## 功能 (Capabilities)

### 新增功能

（无）

### 修改功能

- `session-management`: 增强会话操作的错误处理，失败时自动同步数据

## 影响

- `frontend/src/stores/sessionStore.ts` - 修改 `deleteSession` 和 `updateSession` 方法
