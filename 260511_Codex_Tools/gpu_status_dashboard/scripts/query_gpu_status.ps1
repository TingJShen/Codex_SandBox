param(
    [string]$OutputRoot = ".\current_status"
)

$ErrorActionPreference = "Stop"

$hosts = @(
    @{ Alias = "5A100"; Label = "5A100_a100" },
    @{ Alias = "8A100"; Label = "8A100_young" },
    @{ Alias = "5090_Hao"; Label = "5090_Hao_victory" },
    @{ Alias = "5090_Lian"; Label = "5090_Lian_marathon" }
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$rootPath = Resolve-Path "." | Select-Object -ExpandProperty Path
$outputRootPath = Join-Path $rootPath $OutputRoot
$snapshotDir = Join-Path $outputRootPath $timestamp
$latestDir = Join-Path $outputRootPath "latest"

New-Item -ItemType Directory -Force -Path $outputRootPath | Out-Null
New-Item -ItemType Directory -Force -Path $snapshotDir | Out-Null
New-Item -ItemType Directory -Force -Path $latestDir | Out-Null

$remoteScript = @'
echo "=== GPU ==="
nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits 2>/dev/null
echo "=== APPS ==="
nvidia-smi --query-compute-apps=pid,process_name,used_gpu_memory --format=csv,noheader,nounits 2>/dev/null
echo "=== PMON ==="
nvidia-smi pmon -c 1 2>/dev/null
echo "=== USERS ==="
for p in $(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits 2>/dev/null | sort -u); do
  echo "PID=$p"
  ps -p $p -o user=,pid=,ppid=,etime=,comm=,args= --no-headers
done
echo "=== TJSHEN_CPU_PROCS ==="
ps -u tjshen -o pid=,ppid=,stat=,pcpu=,pmem=,etime=,comm=,args= --sort=-pcpu --no-headers 2>/dev/null
echo "=== TJSHEN_CPU_WAIT_POSSIBLE ==="
ps -u tjshen -o pid=,ppid=,stat=,pcpu=,pmem=,etime=,comm=,args= --sort=-pcpu --no-headers 2>/dev/null | grep -E '^[[:space:]]*[0-9]+[[:space:]]+[0-9]+[[:space:]]+[SD]' | grep -Ev '(systemd|dbus-daemon|pulseaudio|\(sd-pam\)|sshd|ps -u tjshen|awk )'
'@

$combinedLines = New-Object System.Collections.Generic.List[string]

foreach ($machine in $hosts) {
    $alias = $machine.Alias
    $label = $machine.Label
    Write-Host "Querying $alias..."

    $hostHeader = "echo `"HOST $alias $label`""
    $fullRemoteScript = $hostHeader + "`n" + $remoteScript
    $tempScript = Join-Path $env:TEMP "gpu_query_${alias}_$timestamp.sh"
    $normalizedRemoteScript = ($fullRemoteScript -replace "`r`n", "`n" -replace "`r", "`n")
    [System.IO.File]::WriteAllText($tempScript, $normalizedRemoteScript, [System.Text.Encoding]::ASCII)
    $output = Get-Content -Raw $tempScript | & ssh -o BatchMode=yes -o ConnectTimeout=12 $alias "bash -s" 2>&1 | Out-String
    Remove-Item -Force $tempScript
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to query $alias. Output:`n$output"
    }

    $hostFile = Join-Path $snapshotDir "$label.txt"
    $latestHostFile = Join-Path $latestDir "$label.txt"
    $content = $output.TrimEnd() + [Environment]::NewLine
    Set-Content -Path $hostFile -Value $content -Encoding UTF8
    Set-Content -Path $latestHostFile -Value $content -Encoding UTF8

    $combinedLines.Add($content)
}

$combinedPath = Join-Path $snapshotDir "all_hosts.txt"
$latestCombinedPath = Join-Path $latestDir "all_hosts.txt"
$combinedContent = ($combinedLines -join [Environment]::NewLine)
Set-Content -Path $combinedPath -Value $combinedContent -Encoding UTF8
Set-Content -Path $latestCombinedPath -Value $combinedContent -Encoding UTF8

$meta = @(
    "timestamp=$timestamp"
    "snapshot_dir=$snapshotDir"
    "latest_dir=$latestDir"
) -join [Environment]::NewLine

Set-Content -Path (Join-Path $outputRootPath "latest_snapshot.txt") -Value ($snapshotDir + [Environment]::NewLine) -Encoding UTF8
Set-Content -Path (Join-Path $snapshotDir "meta.txt") -Value ($meta + [Environment]::NewLine) -Encoding UTF8

Write-Host "Saved snapshot to $snapshotDir"
