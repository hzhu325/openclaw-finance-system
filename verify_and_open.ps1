$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host ""
Write-Host "=== OpenClaw Finance System: One-Click Verification ===" -ForegroundColor Cyan
Write-Host "Project: $root"
Write-Host ""

Write-Host "[1/4] Generate latest signal, risk review, HITL card and backtest..." -ForegroundColor Yellow
python -B .\scripts\run_mvp.py --symbol TEST --mode backtest

Write-Host ""
Write-Host "[2/4] Run automated tests..." -ForegroundColor Yellow
python -B -m unittest discover -s tests

Write-Host ""
Write-Host "[3/4] Start local dashboard server..." -ForegroundColor Yellow
$chosen = $null
foreach ($port in 8765..8785) {
  $used = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
  if (-not $used) {
    $chosen = $port
    break
  }
}

if ($null -eq $chosen) {
  throw "No available port from 8765 to 8785. Close another local service and retry."
}

$server = Start-Process -FilePath python -ArgumentList @("-B", "-m", "http.server", "$chosen", "--bind", "127.0.0.1") -WorkingDirectory $root -WindowStyle Hidden -PassThru
Start-Sleep -Seconds 1

$url = "http://127.0.0.1:$($chosen)/dashboard.html"

Write-Host ""
Write-Host "[4/4] Open dashboard..." -ForegroundColor Yellow
Start-Process $url

Write-Host ""
Write-Host "Dashboard URL:" -ForegroundColor Green
Write-Host $url -ForegroundColor Green
Write-Host ""
Write-Host "Verification checklist:"
Write-Host "1. Symbol shows TEST."
Write-Host "2. Risk decision shows APPROVE_WITH_HUMAN_CONFIRMATION."
Write-Host "3. HITL status shows PENDING_HUMAN_APPROVAL."
Write-Host "4. Debate, indicators and backtest sections are visible."
Write-Host ""
Write-Host "Local server PID: $($server.Id)"
Write-Host "To stop it later, close the python process from Task Manager."
Write-Host ""
