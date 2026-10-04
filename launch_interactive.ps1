# Interactive Launcher for Cytria FAO Scraper
param(
    [string]$Mode = "collect-transactions"
)

$rootDir = $PSScriptRoot
$pythonExe = Join-Path $rootDir ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        $pythonExe = $pythonCmd.Source
    } else {
        Write-Error "[ERROR] Python executable not found in PATH or .venv."
        exit 1
    }
}

$command = @"
`$Host.UI.RawUI.WindowTitle = 'Cytria FAO Scraper (Google Chrome Interactive)'
Set-Location '$rootDir'
`$env:PYTHONPATH = '$rootDir\src'
`$env:PYTHONNOUSERSITE = '1'
Write-Host '========================================================' -ForegroundColor Yellow
Write-Host '     CYTRIA - GENEVA FAO SCRAPER & PIPELINE (CHROME)    ' -ForegroundColor Yellow
Write-Host '========================================================' -ForegroundColor Yellow
Write-Host ''
& '$pythonExe' -m fao_transactions $Mode --headed
Write-Host ''
Write-Host 'Process finished. Press Enter to exit...' -ForegroundColor Gray
[void][System.Console]::ReadLine()
"@

Start-Process powershell.exe -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $command
