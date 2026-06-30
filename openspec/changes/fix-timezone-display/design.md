## 上下文

后端使用 `datetime.utcnow()` 存储 UTC 时间，但返回 JSON 时缺少时区标识：

```python
# 当前返回
"created_at": "2026-06-25T08:00:00.123456"

# 应该返回
"created_at": "2026-06-25T08:00:00.123456Z"
```

JavaScript 的 `new Date()` 将无时区标识的字符串解析为本地时间，导致时间计算错误。

## 目标 / 非目标

**目标：**
- 后端返回 ISO 8601 格式时间，带 `Z` 后缀标识 UTC
- 前端正确显示相对时间
- 方案统一、可扩展

**非目标：**
- 不修改数据库存储方式
- 不添加用户时区设置功能

## 决策

### 决策 1：使用 Pydantic field_serializer（推荐方案）

**问题分析：** 当前 service 层的 `to_response` 返回 dict 包含 datetime 对象，FastAPI 通过 `response_model` 让 Pydantic 序列化。Pydantic v2 默认不加 `Z` 后缀。

**方案：** 创建 Pydantic mixin，使用 `field_serializer` 统一处理时间字段

```python
# app/schemas/base.py
from datetime import datetime
from pydantic import BaseModel, field_serializer

class UTCDatetimeMixin(BaseModel):
    """Mixin for UTC datetime serialization."""
    
    @field_serializer('*')
    def serialize_datetime_fields(self, value, _info):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"
        return value
```

**理由：**
- **统一性**：所有继承该 mixin 的 schema 自动处理
- **可扩展**：新增 schema 只需继承即可
- **声明式**：符合 Pydantic 设计理念，无需修改 service 层

### 决策 2：创建通用的时间格式化工具函数

**方案：** 创建 `format_datetime_utc` 工具函数供特殊情况使用

```python
# app/utils/datetime.py
from datetime import datetime

def format_datetime_utc(dt: datetime) -> str:
    """Format datetime as ISO 8601 with UTC timezone indicator."""
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"
```

### 决策 3：修改现有 schemas 继承 mixin

**涉及 schemas：**
- `SessionResponse` - 有 `created_at`, `updated_at`
- `MessageResponse` - 有 `created_at`

## 风险 / 权衡

| 风险 | 缓解措施 |
|------|----------|
| 微秒精度过高 | 可接受：ISO 8601 标准允许 |
| 现有数据无需迁移 | 不需要：只是显示格式变化 |
| Pydantic 版本兼容 | 已确认项目使用 Pydantic v2 |
