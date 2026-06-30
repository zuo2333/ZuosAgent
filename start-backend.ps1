# =============================================================================
# 启动后端服务
# =============================================================================
param(
    [string]$EnvFile = ".env"
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# 切换到项目根目录
Set-Location $ProjectRoot

# 加载环境变量
. "$ScriptDir/env-loader.ps1"
Load-EnvFile -EnvPath $EnvFile

# 获取配置
$BackendPort = Get-EnvOrDefault -Name "BACKEND_PORT" -Default "8001"
$DatabaseUrl = Get-EnvOrDefault -Name "DATABASE_URL" -Default "postgresql+asyncpg://llmchat:llmchat_secret@localhost:5432/llmchat"
$EncryptionKey = Get-EnvOrDefault -Name "ENCRYPTION_KEY" -Default ""
$SecretKey = Get-EnvOrDefault -Name "SECRET_KEY" -Default "secret"
$Debug = Get-EnvOrDefault -Name "DEBUG" -Default "false"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "启动后端服务" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "端口: $BackendPort" -ForegroundColor Gray
Write-Host "数据库: $DatabaseUrl" -ForegroundColor Gray
Write-Host ""

# 切换到后端目录
Set-Location "$ProjectRoot/backend"

# 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port $BackendPort
