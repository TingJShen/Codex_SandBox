[CmdletBinding()]
param(
    [string]$PythonExe = 'python',
    [switch]$StopRunning
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSCommandPath
if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = (Get-Location).Path
}

Push-Location $Root
try {
    $DistDir = Join-Path $Root 'dist'
    $ExePath = Join-Path $DistDir 'CodexToolbox.exe'
    $Running = @(Get-Process CodexToolbox -ErrorAction SilentlyContinue | Where-Object {
        -not [string]::IsNullOrWhiteSpace($_.Path) -and
        [string]::Equals($_.Path, $ExePath, [System.StringComparison]::OrdinalIgnoreCase)
    })

    if ($Running.Count -gt 0) {
        if (-not $StopRunning) {
            $ProcessList = ($Running | ForEach-Object { "pid=$($_.Id)" }) -join ', '
            throw "CodexToolbox.exe is running ($ProcessList). Close it first, or rerun with -StopRunning."
        }

        $Running | Stop-Process -Force
        Start-Sleep -Milliseconds 500
    }

    & $PythonExe -m PyInstaller `
        --noconfirm `
        --clean `
        --name CodexToolbox `
        --onefile `
        --windowed `
        --distpath $DistDir `
        --workpath (Join-Path $Root 'build') `
        --specpath $Root `
        (Join-Path $Root 'codex_toolbox\app.py')

    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE."
    }

    Copy-Item -LiteralPath (Join-Path $Root 'CodexThreadRepairGui.ps1') -Destination (Join-Path $Root 'dist\CodexThreadRepairGui.ps1') -Force
    Copy-Item -LiteralPath (Join-Path $Root 'Test-CodexThreadRepairGui.ps1') -Destination (Join-Path $Root 'dist\Test-CodexThreadRepairGui.ps1') -Force
    Write-Output "Built: $ExePath"
}
finally {
    Pop-Location
}
