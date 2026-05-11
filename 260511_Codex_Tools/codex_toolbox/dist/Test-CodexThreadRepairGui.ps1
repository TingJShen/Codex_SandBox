$ErrorActionPreference = 'Stop'

$scriptPath = Join-Path $PSScriptRoot 'CodexThreadRepairGui.ps1'
$env:CODEX_REPAIR_NO_GUI = '1'
. $scriptPath

function Assert-Equal {
    param(
        [object]$Actual,
        [object]$Expected,
        [string]$Message
    )
    if ($Actual -ne $Expected) {
        throw "$Message. Expected '$Expected', got '$Actual'."
    }
}

function Assert-SetEqual {
    param(
        [string[]]$Actual,
        [string[]]$Expected,
        [string]$Message
    )
    $actualSorted = @($Actual | Sort-Object)
    $expectedSorted = @($Expected | Sort-Object)
    $actualJson = ConvertTo-Json $actualSorted -Compress
    $expectedJson = ConvertTo-Json $expectedSorted -Compress
    if ($actualJson -ne $expectedJson) {
        throw "$Message. Expected $expectedJson, got $actualJson."
    }
}

$threads = @(
    [pscustomobject]@{
        id = 'main-codex'
        archived = 0
        model_provider = 'codex'
        title = 'legacy main'
        first_user_message = 'legacy main'
    },
    [pscustomobject]@{
        id = 'child-codex'
        archived = 0
        model_provider = 'codex'
        title = 'legacy child'
        first_user_message = 'legacy child'
    },
    [pscustomobject]@{
        id = 'main-empty'
        archived = 0
        model_provider = 'openai'
        title = ''
        first_user_message = ''
    },
    [pscustomobject]@{
        id = 'child-empty'
        archived = 0
        model_provider = 'openai'
        title = ''
        first_user_message = ''
    },
    [pscustomobject]@{
        id = 'archived-codex'
        archived = 1
        model_provider = 'codex'
        title = 'archived'
        first_user_message = 'archived'
    }
)

$plan = Get-CodexThreadRepairPlanFromRows -Threads $threads -ChildThreadIds @('child-codex', 'child-empty') -TargetProvider 'openai'

Assert-Equal $plan.TargetProvider 'openai' 'Target provider should be retained'
Assert-SetEqual $plan.ProviderThreadIds @('main-codex') 'Only non-child live legacy provider threads should be relabeled'
Assert-SetEqual $plan.MetadataThreadIds @('main-empty') 'Only non-child live empty metadata threads should be repaired'
Assert-SetEqual $plan.ExcludedChildThreadIds @('child-codex', 'child-empty') 'Child threads should be tracked as excluded'
Assert-Equal $plan.ArchivedSkippedCount 1 'Archived threads should be skipped'

$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('codex_repair_gui_test_' + [guid]::NewGuid().ToString('N'))
$fakeHome = Join-Path $tempRoot 'codex'
$fakeRoaming = Join-Path $tempRoot 'roaming'
New-Item -ItemType Directory -Force -Path $fakeHome, $fakeRoaming | Out-Null

try {
    $rolloutDir = Join-Path $fakeHome 'sessions\2026\03\30'
    New-Item -ItemType Directory -Force -Path $rolloutDir | Out-Null
    $rolloutPath = Join-Path $rolloutDir 'rollout-legacy-main.jsonl'
    $sessionMeta = @{
        timestamp = '2026-03-30T10:18:48.441Z'
        type = 'session_meta'
        payload = @{
            id = 'legacy-main'
            model_provider = 'codex'
            cwd = 'D:\Fake'
        }
    }
    $userMessage = @{
        timestamp = '2026-03-30T10:19:00.000Z'
        type = 'event_msg'
        payload = @{
            type = 'user_message'
            message = 'legacy main message'
        }
    }
    @(
        ($sessionMeta | ConvertTo-Json -Compress -Depth 8),
        ($userMessage | ConvertTo-Json -Compress -Depth 8)
    ) | Set-Content -LiteralPath $rolloutPath -Encoding UTF8

    $dbPath = Join-Path $fakeHome 'state_5.sqlite'
    $createDb = @"
import sqlite3
con = sqlite3.connect(r'$dbPath')
cur = con.cursor()
cur.execute('CREATE TABLE threads (id TEXT PRIMARY KEY, rollout_path TEXT, created_at INTEGER, updated_at INTEGER, source TEXT, model_provider TEXT, cwd TEXT, title TEXT, sandbox_policy TEXT, approval_mode TEXT, tokens_used INTEGER, has_user_event INTEGER, archived INTEGER, archived_at INTEGER, git_sha TEXT, git_branch TEXT, git_origin_url TEXT, cli_version TEXT, first_user_message TEXT, agent_nickname TEXT, agent_role TEXT, memory_mode TEXT, model TEXT, reasoning_effort TEXT, agent_path TEXT, created_at_ms INTEGER, updated_at_ms INTEGER)')
cur.execute('CREATE TABLE thread_spawn_edges (parent_thread_id TEXT, child_thread_id TEXT, status TEXT)')
cur.execute('INSERT INTO threads (id, rollout_path, created_at, updated_at, source, model_provider, cwd, title, sandbox_policy, approval_mode, tokens_used, has_user_event, archived, first_user_message, model) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', ('legacy-main', r'$rolloutPath', 1774865920, 1774866860, 'vscode', 'codex', r'D:\Fake', 'legacy main', '{}', 'never', 0, 0, 0, 'legacy main message', 'gpt-5.4'))
cur.execute('INSERT INTO threads (id, rollout_path, created_at, updated_at, source, model_provider, cwd, title, sandbox_policy, approval_mode, tokens_used, has_user_event, archived, first_user_message, model) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', ('outside-workspace', r'$rolloutPath', 1774865921, 1774866861, 'vscode', 'openai', r'D:\OutsideProject', 'outside workspace', '{}', 'never', 0, 0, 0, 'outside workspace message', 'gpt-5.4'))
con.commit()
con.close()
"@
    $createDb | python -

    @{
        'active-workspace-roots' = @('D:\Fake')
        'electron-saved-workspace-roots' = @('D:\Fake')
        'project-order' = @('D:\Fake')
    } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $fakeHome '.codex-global-state.json') -Encoding UTF8

    $accountPayload = @{
        currentAccountId = $null
        settings = @{
            activeAccountId = $null
        }
        accounts = @(
            @{
                id = 'acct-1'
                label = 'acct@example.com'
                email = 'acct@example.com'
                planType = 'plus'
                updatedAt = 1
            }
        )
    } | ConvertTo-Json -Depth 8
    foreach ($name in @('accounts.json', 'accounts.json.last-good.json', 'accounts.json.prev-good.json')) {
        Set-Content -LiteralPath (Join-Path $fakeRoaming $name) -Value $accountPayload -Encoding UTF8
    }

    $repairSummary = Invoke-CodexRepairPython -SourceCodexHome $fakeHome -SourceRoamingRoot $fakeRoaming -SelectedAccountId 'acct-1' -Provider 'openai' -PythonCommand 'python'
    Assert-Equal $repairSummary.providerUpdatedCount 1 'Fake legacy provider thread should be updated in SQLite'
    Assert-Equal $repairSummary.after.account.currentAccountId 'acct-1' 'Repair should set currentAccountId'
    Assert-Equal $repairSummary.after.account.activeAccountId 'acct-1' 'Repair should set settings.activeAccountId for the desktop active profile'
    Assert-Equal $repairSummary.workspaceRootsAddedCount 1 'Repair should add missing top-level thread cwd to durable project roots'
    Assert-Equal $repairSummary.after.workspaceVisibility.activeWorkspaceVisibleTopLevelThreadCount 1 'Only the current active workspace root should be counted as visible in the active UI scope'
    Assert-Equal $repairSummary.after.workspaceVisibility.activeWorkspaceHiddenTopLevelThreadCount 1 'Threads outside the active workspace should be reported as hidden by the current UI scope'

    $globalState = Get-Content -Raw -LiteralPath (Join-Path $fakeHome '.codex-global-state.json') -Encoding UTF8 | ConvertFrom-Json
    Assert-SetEqual @($globalState.'active-workspace-roots') @('D:\Fake') 'Runtime-owned active workspace roots should not be rewritten as a durable repair target'
    Assert-SetEqual @($globalState.'electron-saved-workspace-roots') @('D:\Fake', 'D:\OutsideProject') 'Saved workspace roots should cover all top-level thread cwd values'
    Assert-SetEqual @($globalState.'project-order') @('D:\Fake', 'D:\OutsideProject') 'Project order should cover all top-level thread cwd values'

    $firstLine = Get-Content -LiteralPath $rolloutPath -TotalCount 1 -Encoding UTF8 | ConvertFrom-Json
    Assert-Equal $firstLine.payload.model_provider 'openai' 'Rollout session_meta provider should be patched so app-server backfill cannot revert it'
}
finally {
    Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Output 'All CodexThreadRepairGui tests passed.'
