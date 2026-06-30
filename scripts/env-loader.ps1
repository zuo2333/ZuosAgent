# Environment loader - Load variables from .env file
# Usage: . ./scripts/env-loader.ps1

function Load-EnvFile {
    param(
        [string]$EnvPath = ".env"
    )

    if (-not (Test-Path $EnvPath)) {
        Write-Host "Error: Config file $EnvPath not found" -ForegroundColor Red
        Write-Host "Please copy .env.example to .env and configure" -ForegroundColor Yellow
        Write-Host "  cp .env.example .env" -ForegroundColor Cyan
        exit 1
    }

    Get-Content $EnvPath | ForEach-Object {
        # Skip empty lines and comments
        if ($_ -match "^\s*#" -or $_ -match "^\s*$") {
            return
        }

        # Parse KEY=VALUE format
        if ($_ -match "^([^=]+)=(.*)$") {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()

            # Remove quotes
            if ($value -match '^"(.*)"$' -or $value -match "^'(.*)'$") {
                $value = $matches[1]
            }

            # Set environment variable
            Set-Item -Path "env:$name" -Value $value -Force
        }
    }
}

function Get-EnvOrDefault {
    param(
        [string]$Name,
        [string]$Default
    )

    $value = [Environment]::GetEnvironmentVariable($Name)
    if ([string]::IsNullOrEmpty($value)) {
        return $Default
    }
    return $value
}
