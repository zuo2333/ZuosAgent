# =============================================================================
# 启动前端服务
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
Load-EnvFile -EnvFile $EnvFile

# 获取配置
$FrontendPort = Get-EnvOrDefault -Name "FRONTEND_PORT" -Default "5173"
$ApiBaseUrl = Get-EnvOrDefault -Name "VITE_API_BASE_URL" -Default "http://localhost:8001"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "启动前端服务" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "端口: $FrontendPort" -ForegroundColor Gray
Write-Host "API 地址: $ApiBaseUrl" -ForegroundColor Gray
Write-Host ""

# 切换到前端目录
Set-Location "$ProjectRoot/frontend"

# 启动服务
npm run dev
