## 为什么

新建的会话在页面上直接显示为"8小时以前"。原因是后端返回的时间字符串没有时区标识（缺少 `Z` 后缀），JavaScript 将其解析为本地时间而非 UTC 时间，导致时间计算错误。

中国时区是 UTC+8，后端使用 `datetime.utcnow()` 存储 UTC 时间，但返回的 JSON 字符串如 `2026-06-25T08:00:00.123456` 没有 `Z` 后缀，前端将其解析为本地时间 08:00，与实际本地时间 16:00 相差 8 小时。

## 变更内容

- 后端返回时间时添加 `Z` 后缀，符合 ISO 8601 标准
- 前端时间显示函数无需修改，JavaScript 会自动处理时区转换

## 功能 (Capabilities)

### 新增功能

（无）

### 修改功能

- `datetime-serialization`: 后端返回的时间字符串添加 UTC 时区标识（`Z` 后缀）

## 影响

- `backend/app/schemas/api.py` - 修改 `SessionResponse` 和 `MessageResponse`，添加 `@field_serializer`
- `backend/app/utils/datetime.py` - 新增工具函数（如不存在则创建）
