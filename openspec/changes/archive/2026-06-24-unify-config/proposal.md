## 为什么

当前项目配置分散在多个文件中（`.env`、`vite.config.ts`、`docker-compose.yml`、`start-*.ps1`），导致配置不一致和维护困难。例如：`.env` 中 `BACKEND_PORT=8000`，但 `start-backend.ps1` 硬编码 `8001`，导致前端代理无法正确连接后端。

需要建立 **单一真相来源（Single Source of Truth）** 的配置管理机制，确保所有组件使用一致的配置值。

## 变更内容

- 将 `.env` 文件确立为配置的单一真相来源
- 修改 `vite.config.ts` 从环境变量读取后端地址
- 修改 `start-backend.ps1` 和 `start-frontend.ps1` 从 `.env` 读取配置
- 更新 `.env.example` 包含所有必需配置项及注释
- 创建统一的启动脚本 `start.ps1`，一键启动所有服务（前端、后端）
- 创建统一的停止脚本 `stop.ps1`，一键停止所有服务

## 功能 (Capabilities)

### 新增功能

- `unified-config`: 统一配置管理 — 所有配置项集中在 `.env` 文件，各组件通过标准方式读取

### 修改功能

无（这是基础设施改进，不改变业务功能需求）

## 影响

- **配置文件**：`.env`、`.env.example` 需要更新
- **前端**：`vite.config.ts` 需要改为动态读取环境变量
- **启动脚本**：`start-backend.ps1`、`start-frontend.ps1` 需要改为从 `.env` 读取
- **Docker**：`docker-compose.yml` 已使用 `${VAR:-default}` 模式，无需修改
