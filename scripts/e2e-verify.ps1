# End-to-End Verification Script for LLM Chat Application (PowerShell)
# Run this script after starting the application with docker-compose up -d

param(
    [string]$ApiBase = "http://localhost:8001",
    [string]$FrontendBase = "http://localhost:5173"
)

$ErrorActionPreference = "Continue"

Write-Host "=== LLM Chat Application E2E Verification ===" -ForegroundColor Cyan
Write-Host ""

$passCount = 0
$failCount = 0

function Check-Pass {
    param([string]$message)
    Write-Host "[PASS] " -ForegroundColor Green -NoNewline
    Write-Host $message
    $script:passCount++
}

function Check-Fail {
    param([string]$message)
    Write-Host "[FAIL] " -ForegroundColor Red -NoNewline
    Write-Host $message
    $script:failCount++
}

# 1. Health Check
Write-Host "1. Checking Health Endpoints..."

try {
    $response = Invoke-WebRequest -Uri "$ApiBase/health" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Check-Pass "Backend health check"
    } else {
        Check-Fail "Backend health check"
    }
} catch {
    Check-Fail "Backend health check"
}

try {
    $response = Invoke-WebRequest -Uri "$ApiBase/" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Check-Pass "Backend root endpoint"
    } else {
        Check-Fail "Backend root endpoint"
    }
} catch {
    Check-Fail "Backend root endpoint"
}

try {
    $response = Invoke-WebRequest -Uri "$FrontendBase/" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Check-Pass "Frontend accessible"
    } else {
        Check-Fail "Frontend accessible"
    }
} catch {
    Check-Fail "Frontend accessible"
}

Write-Host ""

# 2. API Endpoints
Write-Host "2. Testing API Endpoints..."

# Create session
$sessionId = ""
try {
    $body = @{name = "E2E Test Session"} | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "$ApiBase/api/sessions" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 10
    if ($response.id) {
        Check-Pass "Create session"
        $sessionId = $response.id
    } else {
        Check-Fail "Create session"
    }
} catch {
    Check-Fail "Create session"
}

# List sessions
try {
    $response = Invoke-RestMethod -Uri "$ApiBase/api/sessions" -TimeoutSec 10
    Check-Pass "List sessions"
} catch {
    Check-Fail "List sessions"
}

# Get session
if ($sessionId) {
    try {
        $response = Invoke-RestMethod -Uri "$ApiBase/api/sessions/$sessionId" -TimeoutSec 10
        Check-Pass "Get session by ID"
    } catch {
        Check-Fail "Get session by ID"
    }
} else {
    Check-Fail "Get session by ID (no session ID)"
}

# Update session
if ($sessionId) {
    try {
        $body = @{name = "Updated E2E Session"} | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "$ApiBase/api/sessions/$sessionId" -Method Put -Body $body -ContentType "application/json" -TimeoutSec 10
        Check-Pass "Update session"
    } catch {
        Check-Fail "Update session"
    }
} else {
    Check-Fail "Update session (no session ID)"
}

# Create provider
$providerId = ""
try {
    $body = @{name = "E2E Test Provider"; provider_type = "openai"} | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "$ApiBase/api/providers" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 10
    if ($response.id) {
        Check-Pass "Create provider"
        $providerId = $response.id
    } else {
        Check-Fail "Create provider"
    }
} catch {
    Check-Fail "Create provider"
}

# List providers
try {
    $response = Invoke-RestMethod -Uri "$ApiBase/api/providers" -TimeoutSec 10
    Check-Pass "List providers"
} catch {
    Check-Fail "List providers"
}

# Get global config
try {
    $response = Invoke-RestMethod -Uri "$ApiBase/api/config" -TimeoutSec 10
    Check-Pass "Get global config"
} catch {
    Check-Fail "Get global config"
}

Write-Host ""

# 3. Cleanup
Write-Host "3. Cleaning up test data..."

# Delete test session
if ($sessionId) {
    try {
        Invoke-RestMethod -Uri "$ApiBase/api/sessions/$sessionId" -Method Delete -TimeoutSec 10
        Check-Pass "Delete session"
    } catch {
        Check-Fail "Delete session"
    }
} else {
    Check-Fail "Delete session (no session ID)"
}

# Delete test provider
if ($providerId) {
    try {
        Invoke-RestMethod -Uri "$ApiBase/api/providers/$providerId" -Method Delete -TimeoutSec 10
        Check-Pass "Delete provider"
    } catch {
        Check-Fail "Delete provider"
    }
} else {
    Check-Fail "Delete provider (no provider ID)"
}

Write-Host ""

# 4. Docker Health Checks
Write-Host "4. Checking Docker Containers..."

$containers = docker ps --format "{{.Names}} {{.Status}}"

if ($containers -match "llm-chat-postgres") {
    if ($containers -match "llm-chat-postgres.*healthy") {
        Check-Pass "PostgreSQL container healthy"
    } else {
        Check-Pass "PostgreSQL container running"
    }
} else {
    Check-Fail "PostgreSQL container"
}

if ($containers -match "llm-chat-backend") {
    Check-Pass "Backend container running"
} else {
    Check-Fail "Backend container"
}

if ($containers -match "llm-chat-frontend") {
    Check-Pass "Frontend container running"
} else {
    Check-Fail "Frontend container"
}

Write-Host ""

# Summary
Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host "Passed: $passCount" -ForegroundColor Green
Write-Host "Failed: $failCount" -ForegroundColor Red
Write-Host ""

if ($failCount -eq 0) {
    Write-Host "All checks passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Some checks failed. Please review the output above." -ForegroundColor Red
    exit 1
}
