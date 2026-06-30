# Unified startup script - Start all services with one command

param(
    [string]$EnvFile = ".env"
)

# Get script directory and project root
$ScriptPath = $MyInvocation.MyCommand.Path
if ([string]::IsNullOrEmpty($ScriptPath)) {
    $ScriptPath = $PSCommandPath
}
$ScriptDir = Split-Path -Parent $ScriptPath
$ProjectRoot = $ScriptDir

Write-Host ""
Write-Host "=========================================="
Write-Host "  LLM Chat Application - Starting"
Write-Host "=========================================="
Write-Host ""

Write-Host "Project Root: $ProjectRoot" -ForegroundColor Gray
Set-Location $ProjectRoot

# Full path to .env
$EnvFilePath = Join-Path $ProjectRoot $EnvFile

# Check .env file
if (-not (Test-Path $EnvFilePath)) {
    Write-Host "Error: Config file $EnvFilePath not found" -ForegroundColor Red
    Write-Host "Please copy .env.example to .env and configure:" -ForegroundColor Yellow
    Write-Host "  cp .env.example .env" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# Load environment variables from .env file
Write-Host "Loading config from $EnvFilePath" -ForegroundColor Gray
Get-Content $EnvFilePath | ForEach-Object {
    if ($_ -match "^\s*#" -or $_ -match "^\s*$") { return }
    if ($_ -match "^([^=]+)=(.*)$") {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        if ($value -match '^"(.*)"$' -or $value -match "^'(.*)'$") {
            $value = $matches[1]
        }
        Set-Item -Path "env:$name" -Value $value -Force
    }
}

# Get config with defaults
$BackendPort = if ($env:BACKEND_PORT) { $env:BACKEND_PORT } else { "8001" }
$FrontendPort = if ($env:FRONTEND_PORT) { $env:FRONTEND_PORT } else { "5173" }
$ApiBaseUrl = if ($env:VITE_API_BASE_URL) { $env:VITE_API_BASE_URL } else { "http://localhost:$BackendPort" }

Write-Host ""
Write-Host "Config:" -ForegroundColor Cyan
Write-Host "  Backend Port: $BackendPort" -ForegroundColor Gray
Write-Host "  Frontend Port: $FrontendPort" -ForegroundColor Gray
Write-Host "  API Base URL: $ApiBaseUrl" -ForegroundColor Gray
Write-Host ""

# Check and start PostgreSQL if needed
Write-Host "Checking PostgreSQL..." -ForegroundColor Yellow
$pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($pgService) {
    if ($pgService.Status -eq "Running") {
        Write-Host "  PostgreSQL running: $($pgService.Name)" -ForegroundColor Green
    } else {
        Write-Host "  PostgreSQL stopped, starting..." -ForegroundColor Yellow
        try {
            Start-Service -Name $pgService.Name -ErrorAction Stop
            # Wait for service to be ready
            $retries = 0
            while ($retries -lt 30) {
                $svc = Get-Service -Name $pgService.Name
                if ($svc.Status -eq "Running") {
                    Write-Host "  PostgreSQL started: $($pgService.Name)" -ForegroundColor Green
                    break
                }
                Start-Sleep -Milliseconds 500
                $retries++
            }
            if ($retries -eq 30) {
                Write-Host "  Warning: PostgreSQL start timeout" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "  Error: Failed to start PostgreSQL - $_" -ForegroundColor Red
            Write-Host "  Please start manually: Start-Service '$($pgService.Name)'" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "  Warning: PostgreSQL not found, ensure database is available" -ForegroundColor Yellow
}
Write-Host ""

# Create logs directory
$LogsDir = Join-Path $ProjectRoot "logs"
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
}

# Start backend in new PowerShell window
Write-Host "Starting backend on port $BackendPort..." -ForegroundColor Yellow
$BackendDir = Join-Path $ProjectRoot "backend"
$BackendCmd = "Set-Location '$BackendDir'; python -m uvicorn app.main:app --host 0.0.0.0 --port $BackendPort"
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", $BackendCmd
Write-Host "  Backend started in new window" -ForegroundColor Green

Start-Sleep -Seconds 3

# Start frontend in new PowerShell window
Write-Host "Starting frontend on port $FrontendPort..." -ForegroundColor Yellow
$FrontendDir = Join-Path $ProjectRoot "frontend"
$FrontendCmd = "Set-Location '$FrontendDir'; npm run dev"
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", $FrontendCmd
Write-Host "  Frontend started in new window" -ForegroundColor Green

Start-Sleep -Seconds 3

# Show addresses
Write-Host ""
Write-Host "=========================================="
Write-Host "  Services Started!" -ForegroundColor Green
Write-Host "=========================================="
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Cyan
Write-Host "  Frontend:     http://localhost:$FrontendPort" -ForegroundColor White
Write-Host "  Backend API:  http://localhost:$BackendPort" -ForegroundColor White
Write-Host "  API Docs:     http://localhost:$BackendPort/docs" -ForegroundColor White
Write-Host ""
Write-Host "Services are running in separate windows." -ForegroundColor Gray
Write-Host "Close those windows to stop the services, or run: .\stop.ps1" -ForegroundColor Yellow
Write-Host ""
