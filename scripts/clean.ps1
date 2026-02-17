# ============================================
# Steam Guide Saver — Cleanup
# Запуск: правый клик → "Выполнить с помощью PowerShell"
# Или: powershell -ExecutionPolicy Bypass -File scripts\clean.ps1
# ============================================

# ============================================
# Steam Guide Saver - Cleanup
# Launch: Right-click → "Run with PowerShell"
# Or: powershell -ExecutionPolicy Bypass -File scripts\clean.ps1
# ===========================================

# Переходим в корень проекта (на уровень выше scripts/)
# Go to the root of the project (one level above scripts/)
Set-Location -Path (Split-Path -Parent $PSScriptRoot)

Write-Host "=== Steam Guide Saver — Cleanup ===" -ForegroundColor Cyan
Write-Host "Working dir: $(Get-Location)" -ForegroundColor Gray
Write-Host ""

$folders = @("build", "__pycache__", "dist")

foreach ($folder in $folders) {
    if (Test-Path $folder) {
        Remove-Item -Recurse -Force $folder
        Write-Host "  Deleted: $folder/" -ForegroundColor Green
    } else {
        Write-Host "  Skip:    $folder/" -ForegroundColor Gray
    }
}

$files = @("*.spec", "downloader.log")

foreach ($pattern in $files) {
    $found = Get-ChildItem -Path . -Filter $pattern -ErrorAction SilentlyContinue
    foreach ($file in $found) {
        Remove-Item -Force $file.FullName
        Write-Host "  Deleted: $($file.Name)" -ForegroundColor Green
    }
    if (-not $found) {
        Write-Host "  Skip:    $pattern" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "=== Done! ===" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to close"