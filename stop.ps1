# 统一停止脚本 - 一键停止所有服务

Write-Host ""
Write-Host "=========================================="
Write-Host "  LLM Chat Application - Stopping Service"
Write-Host "=========================================="
Write-Host ""

# 停止后端进程 (通过端口)
Write-Host "Stopping backend..."
$backendConns = netstat -ano | findstr "LISTENING" | findstr ":8001"
if ($backendConns) {
    $backendConns | ForEach-Object {
        if ($_ -match "\s+(\d+)$") {
            $processPid = $matches[1]
            Stop-Process -Id ([int]$processPid) -Force -ErrorAction SilentlyContinue
            Write-Host "  Backend service endded (PID: $processPid)"
        }
    }
} else {
    Write-Host "  Backend service not running"
}

# 停止前端进程 (通过端口)
Write-Host "Stopping frontend ..."
$frontendConns = netstat -ano | findstr "LISTENING" | findstr ":5173"
if ($frontendConns) {
    $frontendConns | ForEach-Object {
        if ($_ -match "\s+(\d+)$") {
            $processPid = $matches[1]
            Stop-Process -Id ([int]$processPid) -Force -ErrorAction SilentlyContinue
            Write-Host "  Frontend service endded (PID: $processPid)"
        }
    }
} else {
    Write-Host "  Frontend service not running"
}

Write-Host ""
Write-Host "=========================================="
Write-Host "  ALL SERVICE SUCCESSFULLY ENDDED"
Write-Host "=========================================="
Write-Host ""
