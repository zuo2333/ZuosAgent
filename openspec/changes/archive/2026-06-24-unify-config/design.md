## 上下文

当前项目配置分散在多个位置：
- `.env` — 主配置文件（但未被所有组件使用）
- `vite.config.ts` — 前端构建配置（硬编码端口）
- `docker-compose.yml` — Docker 环境变量
- `start-backend.ps1` / `start-frontend.ps1` — 启动脚本（硬编码值）

这导致配置不一致，且修改配置需要同时更新多个文件。

## 目标 / 非目标

**目标：**
- 建立 `.env` 作为配置的单一真相来源
- 所有组件通过标准方式从 `.env` 读取配置
- 修改配置只需改一处，所有组件自动生效

**非目标：**
- 不改变现有业务功能
- 不改变 Docker 部署的配置方式（已正确使用环境变量）
- 不引入复杂的配置中心（如 Consul、etcd）

## 决策

### 1. 配置文件格式：`.env`

**选择**：使用 `.env` 文件作为配置源

**理由**：
- 已有 `.env` 文件，改动最小
- 被广泛支持（Python pydantic-settings、Node.js dotenv、Docker Compose）
- 简单易维护，适合单机部署

### 2. 后端配置读取

**选择**：保持 pydantic-settings 自动加载

**理由**：
- 后端 `backend/app/core/config.py` 已正确使用 `pydantic-settings`
- 自动从 `.env` 读取，无需修改

### 3. 前端配置读取

**选择**：Vite 通过 `loadEnv` 或 `define` 注入环境变量

**实现**：
```typescript
// vite.config.ts
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
    server: {
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8001',
          changeOrigin: true,
        },
      },
    },
  }
})
```

**理由**：
- Vite 原生支持 `loadEnv`
- 构建时注入，无需运行时依赖

### 4. 启动脚本配置读取

**选择**：PowerShell 脚本解析 `.env` 文件

**实现**：
```powershell
# 读取 .env 文件
Get-Content ".env" | ForEach-Object {
  if ($_ -match "^([^#][^=]+)=(.*)$") {
    $name = $matches[1].Trim()
    $value = $matches[2].Trim()
    Set-Item -Path "env:$name" -Value $value
  }
}
```

**理由**：
- 无需额外依赖
- 与 Docker Compose 行为一致

### 5. 统一启动入口

**选择**：创建 `start.ps1` 和 `stop.ps1` 统一入口脚本

**实现**：
```powershell
# start.ps1 - 一键启动所有服务
# 1. 检查 .env 文件存在
# 2. 检查 PostgreSQL 服务运行
# 3. 启动后端（后台运行）
# 4. 启动前端（后台运行）
# 5. 显示服务地址和状态

# stop.ps1 - 一键停止所有服务
# 1. 停止后端进程
# 2. 停止前端进程
# 3. 确认所有服务已停止
```

**理由**：
- 简化开发体验，一条命令启动/停止
- 统一管理所有服务进程
- 支持优雅启动和停止
- 显示服务状态便于调试

## 风险 / 权衡

| 风险 | 缓解措施 |
|------|----------|
| `.env` 文件缺失导致启动失败 | 脚本检查文件存在，提供友好错误提示 |
| 环境变量名冲突 | 使用统一前缀（已有 `VITE_`、`POSTGRES_` 等） |
| 敏感信息泄露 | `.env` 在 `.gitignore` 中，提供 `.env.example` 模板 |
