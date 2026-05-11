[CmdletBinding()]
param(
    [string]$CodexHome = (Join-Path $env:USERPROFILE '.codex'),
    [string]$RoamingRoot = (Join-Path $env:APPDATA 'com.carry.codex-tools'),
    [string]$BackupRoot = '',
    [string]$TargetProvider = 'openai',
    [string]$PythonExe = 'python'
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($BackupRoot)) {
    $scriptDir = $PSScriptRoot
    if ([string]::IsNullOrWhiteSpace($scriptDir) -and -not [string]::IsNullOrWhiteSpace($PSCommandPath)) {
        $scriptDir = Split-Path -Parent $PSCommandPath
    }
    if ([string]::IsNullOrWhiteSpace($scriptDir)) {
        $scriptDir = (Get-Location).Path
    }
    $BackupRoot = Join-Path $scriptDir 'codex_repair_backups'
}

function Test-CodexBlank {
    param([object]$Value)
    return [string]::IsNullOrWhiteSpace([string]$Value)
}

function Get-CodexThreadRepairPlanFromRows {
    param(
        [Parameter(Mandatory = $true)][object[]]$Threads,
        [Parameter(Mandatory = $true)][string[]]$ChildThreadIds,
        [string]$TargetProvider = 'openai'
    )

    $childSet = @{}
    foreach ($childId in $ChildThreadIds) {
        if (-not [string]::IsNullOrWhiteSpace($childId)) {
            $childSet[[string]$childId] = $true
        }
    }

    $providerIds = New-Object System.Collections.Generic.List[string]
    $metadataIds = New-Object System.Collections.Generic.List[string]
    $excludedIds = New-Object System.Collections.Generic.List[string]
    $archivedSkipped = 0

    foreach ($thread in $Threads) {
        $id = [string]$thread.id
        $archived = 0
        if ($null -ne $thread.archived) {
            $archived = [int]$thread.archived
        }
        if ($archived -ne 0) {
            $archivedSkipped += 1
            continue
        }

        if ($childSet.ContainsKey($id)) {
            $excludedIds.Add($id)
            continue
        }

        $provider = [string]$thread.model_provider
        if ($provider -eq 'codex' -and $provider -ne $TargetProvider) {
            $providerIds.Add($id)
        }

        if ((Test-CodexBlank $thread.title) -or (Test-CodexBlank $thread.first_user_message)) {
            $metadataIds.Add($id)
        }
    }

    [pscustomobject]@{
        TargetProvider = $TargetProvider
        ProviderThreadIds = @($providerIds)
        MetadataThreadIds = @($metadataIds)
        ExcludedChildThreadIds = @($excludedIds)
        ArchivedSkippedCount = $archivedSkipped
    }
}

function Get-CodexProcesses {
    Get-Process -ErrorAction SilentlyContinue |
        Where-Object { $_.ProcessName -in @('Codex', 'codex') } |
        Sort-Object ProcessName, Id
}

function Get-CodexProcessText {
    $processes = @(Get-CodexProcesses)
    if ($processes.Count -eq 0) {
        return '没有检测到 Codex/codex 进程。'
    }
    return ($processes | ForEach-Object { '{0} pid={1}' -f $_.ProcessName, $_.Id }) -join ', '
}

function Get-CodexAccountItems {
    param([string]$Root)

    $path = Join-Path $Root 'accounts.json'
    if (-not (Test-Path -LiteralPath $path)) {
        throw "找不到账号文件: $path"
    }

    $payload = Get-Content -Raw -LiteralPath $path -Encoding UTF8 | ConvertFrom-Json
    $currentId = [string]$payload.currentAccountId
    $activeId = ''
    if ($null -ne $payload.settings -and $null -ne $payload.settings.activeAccountId) {
        $activeId = [string]$payload.settings.activeAccountId
    }
    $effectiveId = $activeId
    if ([string]::IsNullOrWhiteSpace($effectiveId)) {
        $effectiveId = $currentId
    }
    $items = @()
    foreach ($account in @($payload.accounts)) {
        $updated = 0L
        if ($null -ne $account.updatedAt) {
            $updated = [int64]$account.updatedAt
        }
        $label = [string]$account.label
        if ([string]::IsNullOrWhiteSpace($label)) {
            $label = [string]$account.email
        }
        $markers = New-Object System.Collections.Generic.List[string]
        if (-not [string]::IsNullOrWhiteSpace($activeId) -and [string]$account.id -eq $activeId) {
            $markers.Add('active')
        }
        if (-not [string]::IsNullOrWhiteSpace($currentId) -and [string]$account.id -eq $currentId) {
            $markers.Add('current')
        }
        $marker = ''
        if ($markers.Count -gt 0) {
            $marker = ' ' + (($markers | Select-Object -Unique) -join '+')
        }
        $items += [pscustomobject]@{
            Id = [string]$account.id
            Label = $label
            Email = [string]$account.email
            PlanType = [string]$account.planType
            UsageError = [string]$account.usageError
            UpdatedAt = $updated
            Display = ('{0}  [{1}]{2}' -f $label, $account.planType, $marker)
        }
    }

    [pscustomobject]@{
        CurrentAccountId = $currentId
        ActiveAccountId = $activeId
        EffectiveAccountId = $effectiveId
        Items = @($items | Sort-Object UpdatedAt -Descending)
    }
}

function New-CodexRepairBackup {
    param(
        [string]$SourceCodexHome,
        [string]$SourceRoamingRoot,
        [string]$DestinationRoot
    )

    $stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $backupDir = Join-Path $DestinationRoot "codex_thread_repair_$stamp"
    $codexDir = Join-Path $backupDir 'codex'
    $roamingDir = Join-Path $backupDir 'roaming'
    New-Item -ItemType Directory -Force -Path $codexDir, $roamingDir | Out-Null

    foreach ($name in @('state_5.sqlite', 'state_5.sqlite-wal', 'state_5.sqlite-shm', 'session_index.jsonl', '.codex-global-state.json')) {
        $source = Join-Path $SourceCodexHome $name
        if (Test-Path -LiteralPath $source) {
            Copy-Item -LiteralPath $source -Destination (Join-Path $codexDir $name) -Force
        }
    }

    foreach ($name in @('accounts.json', 'accounts.json.last-good.json', 'accounts.json.prev-good.json')) {
        $source = Join-Path $SourceRoamingRoot $name
        if (Test-Path -LiteralPath $source) {
            Copy-Item -LiteralPath $source -Destination (Join-Path $roamingDir $name) -Force
        }
    }

    $manifest = [pscustomobject]@{
        createdAt = (Get-Date).ToString('o')
        codexHome = $SourceCodexHome
        roamingRoot = $SourceRoamingRoot
        note = 'Backup made before Codex thread visibility repair.'
    }
    $manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $backupDir 'MANIFEST.json') -Encoding UTF8
    return $backupDir
}

function Invoke-CodexRepairPython {
    param(
        [string]$SourceCodexHome,
        [string]$SourceRoamingRoot,
        [string]$SelectedAccountId,
        [string]$Provider,
        [string]$PythonCommand,
        [switch]$DryRun
    )

    $pythonCode = @'
from __future__ import annotations

import argparse
import datetime as dt
import json
import sqlite3
import shutil
from pathlib import Path


ACCOUNT_FILES = [
    "accounts.json",
    "accounts.json.last-good.json",
    "accounts.json.prev-good.json",
]


def collapse_text(value):
    return str(value or "").replace("\r", " ").replace("\n", " ").strip()


def normalize_path(raw_path):
    text = str(raw_path or "").strip()
    if text.startswith("\\\\?\\"):
        return text[4:]
    return text


def dedupe_paths(paths):
    result = []
    seen = set()
    for raw_path in paths:
        path = normalize_path(raw_path)
        if not path:
            continue
        key = path.replace("/", "\\").rstrip("\\").lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(path)
    return result


def resolve_rollout_path(raw_path, codex_home):
    normalized = normalize_path(raw_path)
    if not normalized:
        return None
    direct = Path(normalized)
    if direct.exists():
        return direct
    lowered = normalized.lower()
    for anchor in ("sessions\\", "archived_sessions\\"):
        needle = anchor.lower()
        if needle in lowered:
            suffix = normalized[lowered.index(needle):].replace("\\", "/")
            candidate = codex_home / Path(suffix)
            if candidate.exists():
                return candidate
    return None


def extract_message_from_rollout(path):
    try:
        with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
            for line in handle:
                if not line.strip():
                    continue
                payload = json.loads(line)
                if payload.get("type") == "event_msg":
                    event = payload.get("payload", {})
                    if event.get("type") == "user_message":
                        message = collapse_text(event.get("message"))
                        if message:
                            return message
                if payload.get("type") == "response_item":
                    item = payload.get("payload", {})
                    if item.get("type") != "message" or item.get("role") != "user":
                        continue
                    parts = []
                    for content in item.get("content", []):
                        if content.get("type") == "input_text":
                            text = collapse_text(content.get("text"))
                            if text:
                                parts.append(text)
                    message = collapse_text(" ".join(parts))
                    if message:
                        return message
    except (OSError, json.JSONDecodeError):
        return None
    return None


def patch_rollout_provider(raw_path, codex_home, target_provider, dry_run):
    rollout_path = resolve_rollout_path(raw_path, codex_home)
    if rollout_path is None:
        return {"patched": False, "reason": "missing_rollout"}

    try:
        lines = rollout_path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    except OSError as exc:
        return {"patched": False, "reason": "read_failed", "error": str(exc)}

    changed = False
    output_lines = []
    for line in lines:
        if not line.strip():
            output_lines.append(line)
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            output_lines.append(line)
            continue
        if payload.get("type") == "session_meta":
            meta = payload.get("payload")
            if isinstance(meta, dict) and meta.get("model_provider") != target_provider:
                meta["model_provider"] = target_provider
                changed = True
                output_lines.append(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
                continue
        output_lines.append(line)

    if not changed:
        return {"patched": False, "reason": "session_meta_already_ok_or_missing", "path": str(rollout_path)}

    backup_path = None
    if not dry_run:
        stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = rollout_path.with_name(rollout_path.name + f".codex-thread-repair-{stamp}.bak")
        shutil.copy2(rollout_path, backup_path)
        rollout_path.write_text("\n".join(output_lines) + "\n", encoding="utf-8")
    return {
        "patched": True,
        "path": str(rollout_path),
        "backup": str(backup_path) if backup_path else None,
    }


def to_iso8601(timestamp):
    if timestamp is None:
        raw = 0.0
    else:
        raw = float(timestamp)
    if raw > 10_000_000_000:
        raw /= 1000.0
    return dt.datetime.fromtimestamp(raw, tz=dt.timezone.utc).isoformat().replace("+00:00", "Z")


def read_index_stats(path):
    if not path.exists():
        return {"lines": 0, "unique_ids": 0}
    ids = []
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            ids.append(json.loads(line).get("id"))
        except json.JSONDecodeError:
            pass
    return {"lines": len(ids), "unique_ids": len(set(x for x in ids if x))}


def account_summary(roaming_root):
    path = roaming_root / "accounts.json"
    if not path.exists():
        return {"exists": False}
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    settings = payload.get("settings")
    active_account_id = None
    if isinstance(settings, dict):
        active_account_id = settings.get("activeAccountId")
    return {
        "exists": True,
        "currentAccountId": payload.get("currentAccountId"),
        "activeAccountId": active_account_id,
        "accountCount": len(payload.get("accounts") or []),
    }


def set_current_account(roaming_root, account_id, dry_run):
    changed = []
    if not account_id:
        return changed
    for name in ACCOUNT_FILES:
        path = roaming_root / name
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        payload["currentAccountId"] = account_id
        settings = payload.get("settings")
        if not isinstance(settings, dict):
            settings = {}
            payload["settings"] = settings
        settings["activeAccountId"] = account_id
        changed.append(str(path))
        if not dry_run:
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return changed


def path_key(raw_path):
    return normalize_path(raw_path).replace("/", "\\").rstrip("\\").lower()


def workspace_visibility_summary(codex_home, live_non_child):
    path = codex_home / ".codex-global-state.json"
    if not path.exists():
        return {
            "exists": False,
            "path": str(path),
            "activeBeforeCount": 0,
            "activeWorkspaceRoots": [],
            "activeWorkspaceVisibleTopLevelThreadCount": 0,
            "activeWorkspaceHiddenTopLevelThreadCount": len(live_non_child),
            "savedWorkspaceRootsCount": 0,
            "projectOrderCount": 0,
        }

    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    current_active = payload.get("active-workspace-roots")
    if not isinstance(current_active, list):
        current_active = []

    saved = payload.get("electron-saved-workspace-roots")
    if not isinstance(saved, list):
        saved = []
    project_order = payload.get("project-order")
    if not isinstance(project_order, list):
        project_order = []

    active_keys = {path_key(root) for root in current_active if collapse_text(root)}
    visible = [
        row for row in live_non_child
        if path_key(row["cwd"]) in active_keys
    ]
    by_cwd = {}
    for row in live_non_child:
        cwd = normalize_path(row["cwd"])
        if not cwd:
            continue
        key = path_key(cwd)
        if key not in by_cwd:
            by_cwd[key] = {"root": cwd, "count": 0}
        by_cwd[key]["count"] += 1

    return {
        "exists": True,
        "path": str(path),
        "activeBeforeCount": len(dedupe_paths(current_active)),
        "activeWorkspaceRoots": dedupe_paths(current_active),
        "activeWorkspaceVisibleTopLevelThreadCount": len(visible),
        "activeWorkspaceHiddenTopLevelThreadCount": len(live_non_child) - len(visible),
        "savedWorkspaceRootsCount": len(dedupe_paths(saved)),
        "projectOrderCount": len(dedupe_paths(project_order)),
        "topLevelThreadRootsCount": len(by_cwd),
        "topLevelThreadCountsByRoot": sorted(by_cwd.values(), key=lambda item: (-item["count"], item["root"].lower())),
    }


def update_global_workspace_roots(codex_home, live_non_child, dry_run):
    path = codex_home / ".codex-global-state.json"
    if not path.exists():
        return {
            "exists": False,
            "path": str(path),
            "added": [],
            "savedBeforeCount": 0,
            "savedAfterCount": 0,
        }

    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    thread_roots = [row["cwd"] for row in live_non_child if collapse_text(row["cwd"])]
    added_by_key = {}

    for key in ("electron-saved-workspace-roots", "project-order"):
        existing = payload.get(key)
        if not isinstance(existing, list):
            existing = []
        before_keys = {path_key(root) for root in existing if collapse_text(root)}
        updated = dedupe_paths([*existing, *thread_roots])
        payload[key] = updated
        for root in updated:
            key_value = path_key(root)
            if key_value and key_value not in before_keys:
                added_by_key.setdefault(key_value, root)

    if not dry_run:
        path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

    saved_roots = payload.get("electron-saved-workspace-roots")
    if not isinstance(saved_roots, list):
        saved_roots = []

    return {
        "exists": True,
        "path": str(path),
        "added": list(added_by_key.values()),
        "savedAfterCount": len(dedupe_paths(saved_roots)),
        "note": "active-workspace-roots is runtime-owned by Codex Desktop and is not treated as a durable repair target.",
    }


def load_state(con):
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    threads = list(cur.execute("""
        SELECT id, rollout_path, title, first_user_message, model_provider, archived, updated_at, created_at, cwd
        FROM threads
    """))
    child_ids = {
        str(row["child_thread_id"])
        for row in cur.execute("""
            SELECT DISTINCT e.child_thread_id
            FROM thread_spawn_edges e
            JOIN threads t ON t.id = e.child_thread_id
            WHERE t.archived = 0
        """)
    }
    return threads, child_ids


def diagnose(codex_home, roaming_root, target_provider):
    state_db = codex_home / "state_5.sqlite"
    con = sqlite3.connect(state_db)
    threads, child_ids = load_state(con)
    live = [row for row in threads if int(row["archived"] or 0) == 0]
    non_child_live = [row for row in live if str(row["id"]) not in child_ids]
    provider_counts = {}
    for row in live:
        provider = str(row["model_provider"] or "<null>")
        provider_counts[provider] = provider_counts.get(provider, 0) + 1
    provider_candidates = [
        str(row["id"])
        for row in non_child_live
        if str(row["model_provider"] or "") == "codex"
        and str(row["model_provider"] or "") != target_provider
    ]
    metadata_candidates = [
        str(row["id"])
        for row in non_child_live
        if not collapse_text(row["title"]) or not collapse_text(row["first_user_message"])
    ]
    workspace_visibility = workspace_visibility_summary(codex_home, non_child_live)
    archived_count = len(threads) - len(live)
    index_stats = read_index_stats(codex_home / "session_index.jsonl")
    con.close()
    return {
        "stateDb": str(state_db),
        "account": account_summary(roaming_root),
        "liveThreads": len(live),
        "archivedThreads": archived_count,
        "liveChildThreads": len(child_ids),
        "liveTopLevelThreads": len(non_child_live),
        "providerCounts": provider_counts,
        "targetProvider": target_provider,
        "providerCandidateCount": len(provider_candidates),
        "providerCandidateIds": provider_candidates,
        "metadataCandidateCount": len(metadata_candidates),
        "metadataCandidateIds": metadata_candidates,
        "workspaceVisibility": workspace_visibility,
        "indexStats": index_stats,
    }


def repair(codex_home, roaming_root, account_id, target_provider, dry_run):
    before = diagnose(codex_home, roaming_root, target_provider)
    state_db = codex_home / "state_5.sqlite"
    con = sqlite3.connect(state_db)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    threads, child_ids = load_state(con)

    live_non_child = [
        row for row in threads
        if int(row["archived"] or 0) == 0 and str(row["id"]) not in child_ids
    ]

    provider_updated = []
    rollout_provider_patched = []
    rollout_provider_unresolved = []
    for row in live_non_child:
        if str(row["model_provider"] or "") == "codex" and str(row["model_provider"] or "") != target_provider:
            rollout_result = patch_rollout_provider(row["rollout_path"], codex_home, target_provider, dry_run)
            if rollout_result.get("patched"):
                rollout_provider_patched.append({"id": str(row["id"]), **rollout_result})
            else:
                rollout_provider_unresolved.append({"id": str(row["id"]), **rollout_result})
            provider_updated.append(str(row["id"]))
            if not dry_run:
                cur.execute("UPDATE threads SET model_provider = ? WHERE id = ?", (target_provider, row["id"]))

    metadata_updated = []
    metadata_unresolved = []
    for row in live_non_child:
        current_title = collapse_text(row["title"])
        current_first = collapse_text(row["first_user_message"])
        if current_title and current_first:
            continue
        rollout = resolve_rollout_path(row["rollout_path"], codex_home)
        if rollout is None:
            metadata_unresolved.append({"id": str(row["id"]), "reason": "missing_rollout"})
            continue
        message = extract_message_from_rollout(rollout)
        if not message:
            metadata_unresolved.append({"id": str(row["id"]), "reason": "missing_user_message"})
            continue
        new_title = current_title or message
        new_first = current_first or message
        metadata_updated.append(str(row["id"]))
        if not dry_run:
            cur.execute(
                "UPDATE threads SET title = ?, first_user_message = ? WHERE id = ?",
                (new_title, new_first, row["id"]),
            )

    account_files_changed = set_current_account(roaming_root, account_id, dry_run)
    workspace_roots = update_global_workspace_roots(codex_home, live_non_child, dry_run)

    index_thread_count = 0
    if not dry_run:
        rows = list(cur.execute("""
            SELECT id, title, first_user_message, updated_at, created_at
            FROM threads
            WHERE archived = 0
            ORDER BY updated_at ASC, created_at ASC, id ASC
        """))
        with (codex_home / "session_index.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
            for row in rows:
                thread_id = str(row["id"])
                if thread_id in child_ids:
                    continue
                name = collapse_text(row["title"]) or collapse_text(row["first_user_message"]) or thread_id
                payload = {
                    "id": thread_id,
                    "thread_name": name,
                    "updated_at": to_iso8601(row["updated_at"]),
                }
                handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
                index_thread_count += 1

    if not dry_run:
        con.commit()
    con.close()
    after = diagnose(codex_home, roaming_root, target_provider)
    return {
        "dryRun": dry_run,
        "before": before,
        "after": after,
        "accountFilesChanged": account_files_changed,
        "providerUpdatedCount": len(provider_updated),
        "providerUpdatedIds": provider_updated,
        "rolloutProviderPatchedCount": len(rollout_provider_patched),
        "rolloutProviderPatched": rollout_provider_patched,
        "rolloutProviderUnresolved": rollout_provider_unresolved,
        "workspaceRootsAddedCount": len(workspace_roots.get("added") or []),
        "workspaceRootsAdded": workspace_roots.get("added") or [],
        "workspaceRoots": workspace_roots,
        "currentWorkspaceVisibleTopLevelThreadCount": after.get("workspaceVisibility", {}).get("activeWorkspaceVisibleTopLevelThreadCount"),
        "currentWorkspaceHiddenTopLevelThreadCount": after.get("workspaceVisibility", {}).get("activeWorkspaceHiddenTopLevelThreadCount"),
        "metadataUpdatedCount": len(metadata_updated),
        "metadataUpdatedIds": metadata_updated,
        "metadataUnresolved": metadata_unresolved,
        "rebuiltIndexTopLevelThreadCount": index_thread_count if not dry_run else before["liveTopLevelThreads"],
        "excludedChildThreads": before["liveChildThreads"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--codex-home", required=True)
    parser.add_argument("--roaming-root", required=True)
    parser.add_argument("--account-id", default="")
    parser.add_argument("--target-provider", default="openai")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    codex_home = Path(args.codex_home).resolve()
    roaming_root = Path(args.roaming_root).resolve()
    summary = repair(codex_home, roaming_root, args.account_id, args.target_provider, args.dry_run)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
'@

    $tempScript = Join-Path ([System.IO.Path]::GetTempPath()) ('codex_thread_repair_{0}.py' -f ([guid]::NewGuid().ToString('N')))
    Set-Content -LiteralPath $tempScript -Value $pythonCode -Encoding UTF8
    try {
        $args = @(
            $tempScript,
            '--codex-home', $SourceCodexHome,
            '--roaming-root', $SourceRoamingRoot,
            '--account-id', $SelectedAccountId,
            '--target-provider', $Provider
        )
        if ($DryRun) {
            $args += '--dry-run'
        }
        $output = & $PythonCommand @args 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Python 修复脚本失败(exit $LASTEXITCODE): $($output -join [Environment]::NewLine)"
        }
        return (($output -join [Environment]::NewLine) | ConvertFrom-Json)
    }
    finally {
        Remove-Item -LiteralPath $tempScript -Force -ErrorAction SilentlyContinue
    }
}

function Start-CodexThreadRepairGui {
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing

    $form = New-Object System.Windows.Forms.Form
    $form.Text = 'Codex 线程主列表修复'
    $form.Size = New-Object System.Drawing.Size(900, 640)
    $form.StartPosition = 'CenterScreen'
    $form.Font = New-Object System.Drawing.Font('Microsoft YaHei UI', 9)

    $status = New-Object System.Windows.Forms.Label
    $status.Location = New-Object System.Drawing.Point(16, 16)
    $status.Size = New-Object System.Drawing.Size(850, 32)
    $status.Text = '准备就绪'
    $status.ForeColor = [System.Drawing.Color]::DarkSlateGray
    $form.Controls.Add($status)

    $accountLabel = New-Object System.Windows.Forms.Label
    $accountLabel.Location = New-Object System.Drawing.Point(16, 60)
    $accountLabel.Size = New-Object System.Drawing.Size(120, 24)
    $accountLabel.Text = '修复到账号'
    $form.Controls.Add($accountLabel)

    $accountBox = New-Object System.Windows.Forms.ComboBox
    $accountBox.Location = New-Object System.Drawing.Point(140, 56)
    $accountBox.Size = New-Object System.Drawing.Size(520, 28)
    $accountBox.DropDownStyle = 'DropDownList'
    $accountBox.DisplayMember = 'Display'
    $form.Controls.Add($accountBox)

    $refreshButton = New-Object System.Windows.Forms.Button
    $refreshButton.Location = New-Object System.Drawing.Point(675, 55)
    $refreshButton.Size = New-Object System.Drawing.Size(90, 30)
    $refreshButton.Text = '刷新'
    $form.Controls.Add($refreshButton)

    $previewButton = New-Object System.Windows.Forms.Button
    $previewButton.Location = New-Object System.Drawing.Point(775, 55)
    $previewButton.Size = New-Object System.Drawing.Size(90, 30)
    $previewButton.Text = '预览'
    $form.Controls.Add($previewButton)

    $repairButton = New-Object System.Windows.Forms.Button
    $repairButton.Location = New-Object System.Drawing.Point(16, 96)
    $repairButton.Size = New-Object System.Drawing.Size(220, 36)
    $repairButton.Text = '等待 Codex 关闭并修复'
    $form.Controls.Add($repairButton)

    $processLabel = New-Object System.Windows.Forms.Label
    $processLabel.Location = New-Object System.Drawing.Point(250, 104)
    $processLabel.Size = New-Object System.Drawing.Size(615, 24)
    $processLabel.Text = Get-CodexProcessText
    $form.Controls.Add($processLabel)

    $logBox = New-Object System.Windows.Forms.TextBox
    $logBox.Location = New-Object System.Drawing.Point(16, 148)
    $logBox.Size = New-Object System.Drawing.Size(850, 430)
    $logBox.Multiline = $true
    $logBox.ScrollBars = 'Vertical'
    $logBox.ReadOnly = $true
    $logBox.Font = New-Object System.Drawing.Font('Consolas', 9)
    $form.Controls.Add($logBox)

    $timer = New-Object System.Windows.Forms.Timer
    $timer.Interval = 1000
    $script:CodexRepairPending = $false

    function Append-RepairLog {
        param([string]$Text)
        $stamp = Get-Date -Format 'HH:mm:ss'
        $logBox.AppendText("[$stamp] $Text`r`n")
    }

    function Set-RepairStatus {
        param(
            [string]$Text,
            [System.Drawing.Color]$Color
        )
        $status.Text = $Text
        $status.ForeColor = $Color
    }

    function Load-RepairAccounts {
        $accountBox.Items.Clear()
        $accounts = Get-CodexAccountItems -Root $RoamingRoot
        foreach ($item in $accounts.Items) {
            [void]$accountBox.Items.Add($item)
        }
        if ($accountBox.Items.Count -gt 0) {
            $selectedIndex = 0
            for ($i = 0; $i -lt $accountBox.Items.Count; $i++) {
                if ($accountBox.Items[$i].Id -eq $accounts.EffectiveAccountId) {
                    $selectedIndex = $i
                    break
                }
            }
            $accountBox.SelectedIndex = $selectedIndex
        }
        Append-RepairLog ("账号文件 activeAccountId={0}; currentAccountId={1}; 候选账号={2}" -f ($accounts.ActiveAccountId -as [string]), ($accounts.CurrentAccountId -as [string]), $accountBox.Items.Count)
    }

    function Get-SelectedRepairAccountId {
        if ($null -eq $accountBox.SelectedItem) {
            throw '请先选择一个账号。'
        }
        return [string]$accountBox.SelectedItem.Id
    }

    function Invoke-Preview {
        $selectedId = Get-SelectedRepairAccountId
        Append-RepairLog '开始预览，不写入 live 数据。'
        $summary = Invoke-CodexRepairPython -SourceCodexHome $CodexHome -SourceRoamingRoot $RoamingRoot -SelectedAccountId $selectedId -Provider $TargetProvider -PythonCommand $PythonExe -DryRun
        $text = $summary | ConvertTo-Json -Depth 8
        Append-RepairLog $text
        Set-RepairStatus '预览完成，尚未写入。' ([System.Drawing.Color]::DarkSlateGray)
    }

    function Invoke-RepairNow {
        $selectedId = Get-SelectedRepairAccountId
        Set-RepairStatus 'Codex 已关闭，正在备份并修复...' ([System.Drawing.Color]::DarkOrange)
        Append-RepairLog '检测到 Codex 已关闭。'
        $backupDir = New-CodexRepairBackup -SourceCodexHome $CodexHome -SourceRoamingRoot $RoamingRoot -DestinationRoot $BackupRoot
        Append-RepairLog "已创建备份: $backupDir"
        $summary = Invoke-CodexRepairPython -SourceCodexHome $CodexHome -SourceRoamingRoot $RoamingRoot -SelectedAccountId $selectedId -Provider $TargetProvider -PythonCommand $PythonExe
        $summaryPath = Join-Path $backupDir 'REPAIR_SUMMARY.json'
        $summary | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $summaryPath -Encoding UTF8
        Append-RepairLog ($summary | ConvertTo-Json -Depth 8)
        Append-RepairLog "修复摘要已写入: $summaryPath"
        $message = '已修复：provider {0} 条，空标题 {1} 条；补充项目根 {2} 个；已排除子线程 {3} 条；顶层索引 {4} 条。当前工作区可见 {5} 条，其他工作区 {6} 条。' -f `
            $summary.providerUpdatedCount, `
            $summary.metadataUpdatedCount, `
            $summary.workspaceRootsAddedCount, `
            $summary.excludedChildThreads, `
            $summary.rebuiltIndexTopLevelThreadCount, `
            $summary.currentWorkspaceVisibleTopLevelThreadCount, `
            $summary.currentWorkspaceHiddenTopLevelThreadCount
        Set-RepairStatus $message ([System.Drawing.Color]::ForestGreen)
        [System.Windows.Forms.MessageBox]::Show($message, 'Codex 线程修复完成', 'OK', 'Information') | Out-Null
    }

    $refreshButton.Add_Click({
        try {
            $processLabel.Text = Get-CodexProcessText
            Load-RepairAccounts
            Set-RepairStatus '刷新完成' ([System.Drawing.Color]::DarkSlateGray)
        }
        catch {
            Set-RepairStatus $_.Exception.Message ([System.Drawing.Color]::Firebrick)
            Append-RepairLog $_.Exception.Message
        }
    })

    $previewButton.Add_Click({
        try {
            Invoke-Preview
        }
        catch {
            Set-RepairStatus $_.Exception.Message ([System.Drawing.Color]::Firebrick)
            Append-RepairLog $_.Exception.ToString()
        }
    })

    $repairButton.Add_Click({
        try {
            [void](Get-SelectedRepairAccountId)
            $script:CodexRepairPending = $true
            $repairButton.Enabled = $false
            $previewButton.Enabled = $false
            $refreshButton.Enabled = $false
            Append-RepairLog '开始监控 Codex/codex 进程。请正常关闭 Codex Desktop。'
            Set-RepairStatus '等待 Codex Desktop 完全关闭...' ([System.Drawing.Color]::DarkOrange)
            $timer.Start()
        }
        catch {
            Set-RepairStatus $_.Exception.Message ([System.Drawing.Color]::Firebrick)
            Append-RepairLog $_.Exception.Message
        }
    })

    $timer.Add_Tick({
        try {
            $processLabel.Text = Get-CodexProcessText
            if (-not $script:CodexRepairPending) {
                return
            }
            $processes = @(Get-CodexProcesses)
            if ($processes.Count -gt 0) {
                Set-RepairStatus ('仍在等待关闭: {0}' -f (Get-CodexProcessText)) ([System.Drawing.Color]::DarkOrange)
                return
            }
            $timer.Stop()
            $script:CodexRepairPending = $false
            Invoke-RepairNow
        }
        catch {
            $timer.Stop()
            $script:CodexRepairPending = $false
            $repairButton.Enabled = $true
            $previewButton.Enabled = $true
            $refreshButton.Enabled = $true
            Set-RepairStatus $_.Exception.Message ([System.Drawing.Color]::Firebrick)
            Append-RepairLog $_.Exception.ToString()
        }
    })

    $form.Add_Shown({
        try {
            Load-RepairAccounts
            $processLabel.Text = Get-CodexProcessText
            Append-RepairLog '子线程不会被恢复：不改 provider，不修元数据，不写入顶层索引。'
        }
        catch {
            Set-RepairStatus $_.Exception.Message ([System.Drawing.Color]::Firebrick)
            Append-RepairLog $_.Exception.ToString()
        }
    })

    [void]$form.ShowDialog()
}

if ($env:CODEX_REPAIR_NO_GUI -ne '1') {
    Start-CodexThreadRepairGui
}
