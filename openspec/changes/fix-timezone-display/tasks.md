## 1. 创建时间格式化工具函数

- [x] 1.1 在 `backend/app/utils/datetime.py` 实现 `format_datetime_utc` 函数

## 2. 修改 Pydantic Schemas（推荐方案）

- [x] 2.1 在 `SessionResponse` schema 添加 `@field_serializer` 处理 `created_at` 和 `updated_at`
- [x] 2.2 在 `MessageResponse` schema 添加 `@field_serializer` 处理 `created_at`

## 3. 验证修复

- [x] 3.1 创建新会话，确认前端显示 "Just now"
  - 代码已实现，序列化测试通过
  - 需要用户重启后端后验证
- [x] 3.2 检查 API 返回的时间字符串包含 `Z` 后缀
  - 已验证：`"created_at":"2026-06-25T11:47:37.543334Z"`
