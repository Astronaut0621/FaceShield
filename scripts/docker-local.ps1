param(
    [ValidateSet("up", "down", "restart", "status", "logs", "test", "urls")]
    [string] $Action = "up",
    [int] $Port = 8000,
    [switch] $Paddle
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

function Get-LanIPv4 {
    $addresses = @(Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object {
            $_.IPAddress -notlike "127.*" -and
            $_.IPAddress -notlike "169.254.*" -and
            $_.InterfaceAlias -notlike "*WSL*" -and
            $_.InterfaceAlias -notlike "*Docker*"
        } |
        Select-Object -ExpandProperty IPAddress)

    if ($addresses) {
        return $addresses[0]
    }

    $ipconfig = ipconfig
    $match = $ipconfig | Select-String -Pattern "IPv4.*?:\s*([0-9.]+)" | Select-Object -First 1
    if ($match) {
        return $match.Matches[0].Groups[1].Value
    }

    return $null
}

function Write-Urls {
    $lanIp = Get-LanIPv4
    Write-Host "Local health:   http://127.0.0.1:$Port/api/health"
    Write-Host "Local mobile:   http://127.0.0.1:$Port/api/mobile/bootstrap"
    if ($lanIp) {
        Write-Host "Phone backend:  http://$lanIp`:$Port/"
        Write-Host "Phone health:   http://$lanIp`:$Port/api/health"
    } else {
        Write-Host "LAN IP was not detected. Run ipconfig and use your active WLAN IPv4 address."
    }
}

function Wait-BackendReady {
    $uri = "http://127.0.0.1:$Port/api/mobile/bootstrap"
    for ($i = 1; $i -le 30; $i++) {
        try {
            $response = Invoke-RestMethod -Uri $uri -TimeoutSec 3
            $isReady = $response.data.status -eq "ok"
            if ($Paddle) {
                $isReady = $isReady -and
                    $response.data.algorithm.backend -eq "paddle" -and
                    $response.data.algorithm.ready -eq $true
            }
            if ($isReady) {
                Write-Host "Backend is ready."
                return
            }
        } catch {
            Start-Sleep -Seconds 1
        }
    }

    Write-Host "Backend did not become ready within 30 seconds. Check logs with:"
    Write-Host ".\scripts\docker-local.ps1 logs"
}

Push-Location $repoRoot
try {
    $env:FACESHIELD_BACKEND_PORT = "$Port"
    $composeFiles = @("compose")
    if ($Paddle) {
        $composeFiles += @("-f", "docker-compose.yml", "-f", "docker-compose.paddle.yml")
    }

    switch ($Action) {
        "up" {
            & docker @composeFiles up -d --build
            Wait-BackendReady
            & docker @composeFiles ps
            Write-Urls
        }
        "down" {
            & docker @composeFiles down
        }
        "restart" {
            & docker @composeFiles up -d --build --force-recreate
            Wait-BackendReady
            & docker @composeFiles ps
            Write-Urls
        }
        "status" {
            & docker @composeFiles ps
        }
        "logs" {
            & docker @composeFiles logs -f --tail=120 backend
        }
        "test" {
            Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/mobile/bootstrap" -TimeoutSec 10 |
                ConvertTo-Json -Depth 6
        }
        "urls" {
            Write-Urls
        }
    }
} finally {
    Pop-Location
}
