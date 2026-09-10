# Unified Cross-Harness Memory Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `memsearch`'s semantic index cover Codex memory and synced meetings (today it only covers Claude), and generate one unified daily snapshot injected into both Claude Code's and Codex's session start, so opening either tool shows the same picture of recent work.

**Architecture:** A new shared JSON config (`data/memory-index-paths.json`) becomes the single source of truth for what `memsearch` indexes — both the existing Claude `SessionEnd` hook and a new Codex `Stop` hook read it. A new `keystone.ps1 meeting-sync` command does the mechanical (non-agent) parts of Fireflies sync/export so it can run unattended on the existing morning cadence. A new `keystone.ps1 snapshot` command generates one capped markdown file summarizing recent Claude/Codex/meeting/project activity; both Claude's and Codex's `SessionStart` hooks read that same file.

**Tech Stack:** PowerShell 7 (`keystone.ps1`, `codex-hooks/*.ps1`), Node.js (`~/.claude/hooks/*.js`), `memsearch` CLI (Python/Milvus, already installed and running), `fireflies-pp-cli` (already installed).

## Global Constraints

- Every hook change must fail closed: a missing/unreachable `memsearch`, `fireflies-pp-cli`, or Docker/Milvus must never block a session start or a `Stop` event. Log and continue.
- Do not touch the memory-compiler's own existing Claude `SessionStart`/`SessionEnd` hooks — add alongside, never replace.
- The Codex `Stop` hook currently has a 10s timeout (`scripts\install-codex-hooks.ps1`), but `memsearch index` needs up to 45s internally (per existing `project_memsearch_setup.md` memory) — this must be raised or the new indexing step will be killed every time, exactly like the bug already fixed once on the Claude side.
- Detached/fire-and-forget subprocess indexing is known-unreliable on Windows (documented in `~/.claude/hooks/memsearch-sync.js`'s own comments) — always run `memsearch index` synchronously with an explicit timeout, never fire-and-forget.
- All new PATHS config entries use `{HOME}` as a placeholder token (not `~`), expanded by each consumer to its own home-directory value.

---

### Task 1: Shared corpus path config

**Files:**
- Create: `data/memory-index-paths.json`
- Test: `tests/keystone-memory-index-paths.ps1`

**Interfaces:**
- Produces: a JSON file with shape `{"paths": [<string>, ...]}`, each string using `{HOME}` as a placeholder for the user's home directory. Consumed by Task 2 (Node) and Task 3 (PowerShell).

- [ ] **Step 1: Write the failing test**

```powershell
# tests/keystone-memory-index-paths.ps1
$ErrorActionPreference = "Stop"
function Assert-True($Condition, $Message) { if (-not $Condition) { throw $Message } }
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$configPath = Join-Path $repoRoot "data\memory-index-paths.json"

Assert-True (Test-Path -LiteralPath $configPath) "data/memory-index-paths.json must exist."
$json = Get-Content -Raw -LiteralPath $configPath | ConvertFrom-Json
Assert-True ($json.paths -is [array]) "paths must be an array."
Assert-True ($json.paths.Count -ge 5) "Expected at least 5 indexed paths."
foreach ($p in $json.paths) {
    Assert-True ($p -like "*{HOME}*") "Each path must use the {HOME} placeholder token: $p"
}
$expected = @(
    "{HOME}/.claude/global-memory/transcripts",
    "{HOME}/.claude/claude-memory-compiler/daily",
    "{HOME}/.claude/claude-memory-compiler/knowledge",
    "{HOME}/Desktop/SecondBrain/Knowledge/library",
    "{HOME}/Desktop/SecondBrain/Inbox/meetings",
    "{HOME}/.codex/memories"
)
foreach ($e in $expected) {
    Assert-True ($json.paths -contains $e) "Missing expected path entry: $e"
}
Write-Host "keystone memory-index-paths tests passed"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.\tests\keystone-memory-index-paths.ps1`
Expected: FAIL — `data/memory-index-paths.json must exist.`

- [ ] **Step 3: Write the config file**

```json
{
  "paths": [
    "{HOME}/.claude/global-memory/transcripts",
    "{HOME}/.claude/projects/C--Users-eric-rash/memory",
    "{HOME}/.claude/claude-memory-compiler/daily",
    "{HOME}/.claude/claude-memory-compiler/knowledge",
    "{HOME}/Desktop/SecondBrain/Knowledge/library",
    "{HOME}/Desktop/SecondBrain/Inbox/meetings",
    "{HOME}/.codex/memories"
  ]
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.\tests\keystone-memory-index-paths.ps1`
Expected: `keystone memory-index-paths tests passed`

- [ ] **Step 5: Commit**

```bash
git add data/memory-index-paths.json tests/keystone-memory-index-paths.ps1
git commit -m "feat: add shared memsearch corpus path config"
```

---

### Task 2: Point the Claude memsearch-sync hook at the shared config

**Files:**
- Modify: `~/.claude/hooks/memsearch-sync.js` (i.e. `C:\Users\eric_rash\.claude\hooks\memsearch-sync.js`)

**Interfaces:**
- Consumes: `data/memory-index-paths.json` (Task 1) at
  `C:\Users\eric_rash\Desktop\DEV\KeystoneOS\data\memory-index-paths.json`.
- Produces: no change to external behavior — same lock file, same timeout, same log paths as before. Only the source of the `PATHS` array changes.

This hook lives outside the KeystoneOS repo (it's a global Claude Code hook) and fires regardless of which project is open, so it must reference the KeystoneOS repo by an absolute path — consistent with how `scripts/codex-hooks/session-start.ps1` already defaults `$ClaudeCompilerRoot` to an absolute path.

- [ ] **Step 1: Read the current file to confirm the exact `PATHS` block to replace**

The current hardcoded block (already read during design) is:

```javascript
const PATHS = [
  path.join(os.homedir(), '.claude', 'global-memory', 'transcripts'),
  path.join(os.homedir(), '.claude', 'projects', 'C--Users-eric-rash', 'memory'),
  path.join(os.homedir(), '.claude', 'claude-memory-compiler', 'daily'),
  path.join(os.homedir(), '.claude', 'claude-memory-compiler', 'knowledge'),
  path.join(os.homedir(), 'Desktop', 'SecondBrain', 'Knowledge', 'library'),
];
```

- [ ] **Step 2: Replace it with a config-driven resolver, falling back to the old hardcoded list if the config is missing or unparseable**

```javascript
const KEYSTONE_INDEX_CONFIG = path.join(
  os.homedir(), 'Desktop', 'DEV', 'KeystoneOS', 'data', 'memory-index-paths.json'
);

function resolvePaths() {
  const fallback = [
    path.join(os.homedir(), '.claude', 'global-memory', 'transcripts'),
    path.join(os.homedir(), '.claude', 'projects', 'C--Users-eric-rash', 'memory'),
    path.join(os.homedir(), '.claude', 'claude-memory-compiler', 'daily'),
    path.join(os.homedir(), '.claude', 'claude-memory-compiler', 'knowledge'),
    path.join(os.homedir(), 'Desktop', 'SecondBrain', 'Knowledge', 'library'),
  ];
  try {
    const raw = fs.readFileSync(KEYSTONE_INDEX_CONFIG, 'utf8');
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed.paths) || parsed.paths.length === 0) return fallback;
    return parsed.paths.map(p => p.replace('{HOME}', os.homedir()).split('/').join(path.sep));
  } catch (_) {
    return fallback;
  }
}

const PATHS = resolvePaths();
```

- [ ] **Step 3: Manually verify the resolver picks up the new config**

Run: `node -e "console.log(require('C:/Users/eric_rash/.claude/hooks/memsearch-sync.js'))"` will actually execute the hook (it runs top-level code, not a module export) — instead verify with a standalone check:

```powershell
node -e "const fs=require('fs'),os=require('os'),path=require('path'); const raw=fs.readFileSync(path.join(os.homedir(),'Desktop','DEV','KeystoneOS','data','memory-index-paths.json'),'utf8'); const parsed=JSON.parse(raw); console.log(parsed.paths.map(p => p.replace('{HOME}', os.homedir()).split('/').join(path.sep)))"
```

Expected: prints 7 resolved absolute Windows paths, including `...\Desktop\SecondBrain\Inbox\meetings` and `...\.codex\memories`.

- [ ] **Step 4: Commit**

```bash
git -C "C:\Users\eric_rash\.claude" add hooks/memsearch-sync.js
git -C "C:\Users\eric_rash\.claude" commit -m "feat: read memsearch corpus paths from KeystoneOS shared config"
```

(If `~/.claude` is not its own git repo, skip the commit and note in the KeystoneOS commit message for Task 1 that this file was updated manually.)

---

### Task 3: Codex-side auto-index hook

**Files:**
- Create: `scripts/codex-hooks/memsearch-sync.ps1`
- Modify: `scripts/codex-hooks/stop.ps1`
- Modify: `scripts/install-codex-hooks.ps1` (raise the Stop hook timeout)
- Test: `tests/codex-memsearch-sync.ps1`

**Interfaces:**
- Consumes: `data/memory-index-paths.json` (Task 1); `Resolve-KeystoneRoot` from `scripts/codex-hooks/common.ps1`.
- Produces: `Invoke-MemsearchSync -KeystoneRoot <path>` — called from `stop.ps1`; writes to the same `.errors.log` / lock file paths the JS hook already uses so both sides share one troubleshooting trail.

- [ ] **Step 1: Write the failing test**

```powershell
# tests/codex-memsearch-sync.ps1
$ErrorActionPreference = "Stop"
function Assert-True($Condition, $Message) { if (-not $Condition) { throw $Message } }
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("codex-memsearch-test-" + [System.Guid]::NewGuid().ToString("n"))
try {
    New-Item -ItemType Directory -Force -Path (Join-Path $tempRoot "scripts\codex-hooks") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $tempRoot "data") | Out-Null
    Copy-Item -LiteralPath (Join-Path $repoRoot "scripts\codex-hooks\common.ps1") -Destination (Join-Path $tempRoot "scripts\codex-hooks\common.ps1")
    Copy-Item -LiteralPath (Join-Path $repoRoot "scripts\codex-hooks\memsearch-sync.ps1") -Destination (Join-Path $tempRoot "scripts\codex-hooks\memsearch-sync.ps1")

    # Fixture: an index-paths config pointing at a path that does not exist, proving
    # the hook filters missing paths and still exits 0 without calling memsearch.
    '{"paths":["{HOME}/keystone-memsearch-test-does-not-exist"]}' |
        Set-Content -LiteralPath (Join-Path $tempRoot "data\memory-index-paths.json") -Encoding UTF8

    $script = Join-Path $tempRoot "scripts\codex-hooks\memsearch-sync.ps1"
    & $script -Root $tempRoot
    Assert-True ($LASTEXITCODE -eq 0 -or $null -eq $LASTEXITCODE) "Hook must exit cleanly when no configured paths exist."
    Write-Host "codex memsearch-sync tests passed"
}
finally { if (Test-Path $tempRoot) { Remove-Item -LiteralPath $tempRoot -Recurse -Force } }
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.\tests\codex-memsearch-sync.ps1`
Expected: FAIL — `scripts\codex-hooks\memsearch-sync.ps1` not found.

- [ ] **Step 3: Write `scripts/codex-hooks/memsearch-sync.ps1`**

```powershell
param([string]$Root)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $ScriptDir "common.ps1")

function Resolve-IndexPaths {
    param([string]$KeystoneRoot)

    $configPath = Join-Path $KeystoneRoot "data\memory-index-paths.json"
    if (-not (Test-Path -LiteralPath $configPath)) { return @() }

    try {
        $json = Get-Content -Raw -LiteralPath $configPath | ConvertFrom-Json
    }
    catch {
        return @()
    }

    if (-not $json.paths) { return @() }

    $homeDir = $env:USERPROFILE
    return @($json.paths |
        ForEach-Object { ($_ -replace '\{HOME\}', $homeDir) -replace '/', '\' } |
        Where-Object { Test-Path -LiteralPath $_ })
}

try {
    $keystoneRoot = Resolve-KeystoneRoot -Root $Root -ScriptPath $MyInvocation.MyCommand.Path
    $transcriptsDir = Join-Path $env:USERPROFILE ".claude\global-memory\transcripts"
    $errLog = Join-Path $transcriptsDir ".errors.log"
    $indexLog = Join-Path $transcriptsDir ".memsearch-index.log"
    $lockFile = Join-Path $transcriptsDir ".memsearch-index.lock"
    $lockStaleMs = 30000

    $paths = Resolve-IndexPaths -KeystoneRoot $keystoneRoot
    if ($paths.Count -eq 0) { exit 0 }

    $memsearch = Get-Command memsearch -ErrorAction SilentlyContinue
    if (-not $memsearch) { exit 0 }

    $haveLock = $false
    try {
        $fs = [System.IO.File]::Open($lockFile, [System.IO.FileMode]::CreateNew)
        $fs.Close()
        $haveLock = $true
    }
    catch {
        $stale = $true
        try {
            $ageMs = ((Get-Date) - (Get-Item -LiteralPath $lockFile).LastWriteTime).TotalMilliseconds
            $stale = $ageMs -ge $lockStaleMs
        }
        catch { $stale = $true }
        if (-not $stale) { exit 0 }
        try {
            Set-Content -LiteralPath $lockFile -Value ([string]$PID) -Encoding UTF8
            $haveLock = $true
        }
        catch { exit 0 }
    }

    try {
        $env:PYTHONIOENCODING = "utf-8"
        $env:PYTHONUTF8 = "1"

        $stdoutFile = [System.IO.Path]::GetTempFileName()
        $stderrFile = [System.IO.Path]::GetTempFileName()
        $proc = Start-Process -FilePath $memsearch.Source `
            -ArgumentList (@("index") + $paths) `
            -NoNewWindow -PassThru `
            -RedirectStandardOutput $stdoutFile -RedirectStandardError $stderrFile

        $finished = $proc.WaitForExit(45000)
        $out = (Get-Content -Raw -LiteralPath $stdoutFile -ErrorAction SilentlyContinue) + `
               (Get-Content -Raw -LiteralPath $stderrFile -ErrorAction SilentlyContinue)
        Remove-Item -LiteralPath $stdoutFile, $stderrFile -ErrorAction SilentlyContinue

        if (-not $finished) {
            try { $proc.Kill() } catch {}
            Add-Content -LiteralPath $indexLog -Value "[$( (Get-Date).ToString('o') )] codex memsearch-sync: timed out at 45s (non-fatal, next run catches up)"
        }
        elseif ($proc.ExitCode -ne 0) {
            Add-Content -LiteralPath $errLog -Value "[$( (Get-Date).ToString('o') )] codex memsearch-sync: index exit $($proc.ExitCode): $($out.Substring(0, [Math]::Min(300, $out.Length)))"
        }
        else {
            Set-Content -LiteralPath $indexLog -Value ($out.Trim() + "`n") -Encoding UTF8
        }
    }
    finally {
        if ($haveLock) { try { Remove-Item -LiteralPath $lockFile -ErrorAction SilentlyContinue } catch {} }
    }
}
catch {
    # Never fail the Codex Stop event over indexing problems.
}

exit 0
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.\tests\codex-memsearch-sync.ps1`
Expected: `codex memsearch-sync tests passed`

- [ ] **Step 5: Wire the hook into `stop.ps1`**

Modify `scripts/codex-hooks/stop.ps1` — add the call after the existing event write, still inside the `try` block, still swallowing errors:

```powershell
param([string]$Root)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $ScriptDir "common.ps1")

try {
    $keystoneRoot = Resolve-KeystoneRoot -Root $Root -ScriptPath $MyInvocation.MyCommand.Path
    $pipelineInput = @($input)
    if ($pipelineInput.Count -gt 0) {
        $rawInput = $pipelineInput -join [Environment]::NewLine
    }
    else {
        $rawInput = [Console]::In.ReadToEnd()
    }
    Write-CodexHookEvent -Root $keystoneRoot -EventName "Stop" -RawInput $rawInput | Out-Null

    $memsearchSyncScript = Join-Path $ScriptDir "memsearch-sync.ps1"
    if (Test-Path -LiteralPath $memsearchSyncScript) {
        & $memsearchSyncScript -Root $keystoneRoot
    }
}
catch {
    # Stop hooks are side-effect-only; emitting stdout can trip Codex's Stop-specific JSON validator.
}
```

- [ ] **Step 6: Raise the Stop hook timeout in the installer**

Modify `scripts/install-codex-hooks.ps1` — change:

```powershell
Merge-KeystoneHook -Config $config -EventName "Stop" -Group (
    New-HookGroup -Matcher "" -Hook (
        New-CommandHook -ScriptPath $stopScript -StatusMessage "Saving KeystoneOS stop checkpoint..." -Timeout 10
    )
)
```

to:

```powershell
Merge-KeystoneHook -Config $config -EventName "Stop" -Group (
    New-HookGroup -Matcher "" -Hook (
        New-CommandHook -ScriptPath $stopScript -StatusMessage "Saving KeystoneOS stop checkpoint..." -Timeout 50
    )
)
```

(50s matches the reasoning already recorded for the Claude-side hook: `memsearch index` has an internal ~45s cap, so the outer hook timeout must exceed it or the harness kills the process before it can exit cleanly.)

- [ ] **Step 7: Re-apply the installer so `~/.codex/hooks.json` picks up the new timeout**

Run: `.\scripts\install-codex-hooks.ps1 -Apply`
Expected: reports installed hooks; back up file created at `C:\Users\eric_rash\.codex\hooks.json.bak-<timestamp>`.

- [ ] **Step 8: Commit**

```bash
git add scripts/codex-hooks/memsearch-sync.ps1 scripts/codex-hooks/stop.ps1 scripts/install-codex-hooks.ps1 tests/codex-memsearch-sync.ps1
git commit -m "feat: index Codex memory into memsearch after every Codex session"
```

---

### Task 4: `keystone.ps1 meeting-sync` — unattended meeting ingestion

**Files:**
- Modify: `scripts/keystone.ps1` (add `ValidateSet` entry, `Invoke-MeetingSync` function, switch case)
- Modify: `scripts/morning-cadence.ps1` (add the new step)
- Test: `tests/keystone-meeting-sync.ps1`

**Interfaces:**
- Produces: `Invoke-MeetingSync` — returns `[pscustomobject]@{ NewCount; GenericCount; VaultDir }` or `$null` if `fireflies-pp-cli` is unavailable or sync fails.
- This is the mechanical subset of the existing `meeting-sync` skill (sync, find, export, state update, structured-header insert) — it deliberately skips the skill's AI-driven generic-title renaming step, since this path must run unattended from a scheduled task with no agent present. Generic titles are counted and reported instead; the interactive `/meeting-sync` and `/name-meetings` skills remain available for cleanup.

- [ ] **Step 1: Write the failing test**

```powershell
# tests/keystone-meeting-sync.ps1
$ErrorActionPreference = "Stop"
function Assert-True($Condition, $Message) { if (-not $Condition) { throw $Message } }
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("keystone-meeting-sync-test-" + [System.Guid]::NewGuid().ToString("n"))
try {
    New-Item -ItemType Directory -Force -Path (Join-Path $tempRoot "scripts") | Out-Null
    Copy-Item -LiteralPath (Join-Path $repoRoot "scripts\keystone.ps1") -Destination (Join-Path $tempRoot "scripts\keystone.ps1")
    $script = Join-Path $tempRoot "scripts\keystone.ps1"

    # No fireflies-pp-cli guaranteed on a clean PATH fixture — simulate that case by
    # temporarily shadowing PATH so Get-Command cannot find it, proving the command
    # skips cleanly instead of throwing.
    $originalPath = $env:PATH
    $env:PATH = ""
    try {
        $output = (& $script meeting-sync *>&1 | Out-String)
        Assert-True ($output -match "not found on PATH; skipped") "Missing fireflies-pp-cli must be a clean skip, not a crash."
    }
    finally {
        $env:PATH = $originalPath
    }
    Write-Host "keystone meeting-sync tests passed"
}
finally { if (Test-Path $tempRoot) { Remove-Item -LiteralPath $tempRoot -Recurse -Force } }
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.\tests\keystone-meeting-sync.ps1`
Expected: FAIL — `meeting-sync` is not in the `ValidateSet`, parameter binding error.

- [ ] **Step 3: Add `meeting-sync` to the `ValidateSet` in `scripts/keystone.ps1`**

Modify line 3 from:

```powershell
    [ValidateSet("today", "morning", "projects", "resume", "paths", "health", "memory", "graphify", "graphsync", "status", "where", "start", "brief", "plan", "control-loop", "closeout", "open", "inventory", "intake", "promote", "dashboard", "heal", "context", "cockpit", "okr-link", "agy-sync")]
```

to:

```powershell
    [ValidateSet("today", "morning", "projects", "resume", "paths", "health", "memory", "graphify", "graphsync", "status", "where", "start", "brief", "plan", "control-loop", "closeout", "open", "inventory", "intake", "promote", "dashboard", "heal", "context", "cockpit", "okr-link", "agy-sync", "meeting-sync", "snapshot")]
```

(`snapshot` is added here too, for Task 5 — keeping the `ValidateSet` edit to one place.)

- [ ] **Step 4: Add `Invoke-MeetingSync` function**, placed just above `Invoke-AgySync` (near line 2883 in the current file) in `scripts/keystone.ps1`:

```powershell
function Invoke-MeetingSync {
    Show-Section "Meeting Sync"
    $ff = Get-Command fireflies-pp-cli -ErrorAction SilentlyContinue
    if (-not $ff) { Write-Host "fireflies-pp-cli not found on PATH; skipped."; return $null }

    $vaultDir = "C:\Users\eric_rash\Desktop\SecondBrain\Inbox\meetings"
    New-Item -ItemType Directory -Force -Path $vaultDir | Out-Null
    $statePath = Join-Path $vaultDir ".sync-state.json"
    if (-not (Test-Path -LiteralPath $statePath)) {
        '{"exports":{}}' | Set-Content -LiteralPath $statePath -Encoding UTF8
    }

    & fireflies-pp-cli sync --agent 2>&1 | ForEach-Object { Write-Host $_ }
    if ($LASTEXITCODE -ne 0) {
        Write-Host "fireflies-pp-cli sync failed (exit $LASTEXITCODE); skipping export this run."
        return $null
    }

    $findRaw = & fireflies-pp-cli transcripts find --from 14 --processed-only --json --agent 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "fireflies-pp-cli transcripts find failed; skipping export this run."
        return $null
    }

    try {
        $transcripts = @(($findRaw -join "`n") | ConvertFrom-Json)
    }
    catch {
        Write-Host "Could not parse transcripts find output; skipping."
        return $null
    }

    $state = Get-Content -Raw -LiteralPath $statePath | ConvertFrom-Json
    $exportsMap = @{}
    if ($state.exports) {
        foreach ($p in $state.exports.PSObject.Properties) { $exportsMap[$p.Name] = $p.Value }
    }

    $newCount = 0
    $genericCount = 0
    $genericPattern = '^(zoom meeting|recording|meeting)?$|^\d{4}-\d{2}-\d{2}$'

    foreach ($t in $transcripts) {
        $id = [string]$t.id
        if ($exportsMap.ContainsKey($id)) { continue }
        if ([string]::IsNullOrWhiteSpace($t.title) -or ($t.title.ToLowerInvariant() -match $genericPattern)) {
            $genericCount++
        }

        & fireflies-pp-cli transcripts export $id --vault $vaultDir --agent 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Export failed for $id; continuing."
            continue
        }

        $exportedFile = Get-ChildItem -LiteralPath $vaultDir -Filter "*.md" |
            Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if (-not $exportedFile) { continue }

        $header = @'
## Project tags
> Tag this meeting against active projects. Add freely. Used by weekly-review to surface drift.

- project/
- person/

## Key topics

## Decisions

## Action items
> Pulled from Fireflies. Mark complete by replacing `[ ]` with `[x]`.

## Open questions

'@
        $content = Get-Content -Raw -LiteralPath $exportedFile.FullName
        Set-Content -LiteralPath $exportedFile.FullName -Value ($header + $content) -Encoding UTF8

        $exportsMap[$id] = [pscustomobject]@{
            filename    = $exportedFile.Name
            exported_at = (Get-Date).ToString("o")
        }
        $newCount++
    }

    ([pscustomobject]@{ exports = $exportsMap }) | ConvertTo-Json -Depth 10 |
        Set-Content -LiteralPath $statePath -Encoding UTF8

    Write-Host "Meetings found (last 14 days): $($transcripts.Count)"
    Write-Host "New exports: $newCount"
    if ($genericCount -gt 0) {
        Write-Host "$genericCount new meeting(s) have generic titles; run /name-meetings interactively to clean them up."
    }

    return [pscustomobject]@{ NewCount = $newCount; GenericCount = $genericCount; VaultDir = $vaultDir }
}
```

- [ ] **Step 5: Add the switch case**, in the `switch ($Command)` block, alongside the existing `"agy-sync"` case:

```powershell
    "meeting-sync" { Invoke-MeetingSync | Out-Null }
```

- [ ] **Step 6: Run test to verify it passes**

Run: `.\tests\keystone-meeting-sync.ps1`
Expected: `keystone meeting-sync tests passed`

- [ ] **Step 7: Wire into the morning cadence**

Modify `scripts/morning-cadence.ps1`:

```powershell
# Runs the KeystoneOS morning packet + dashboard refresh. Called by the
# 'KeystoneOS Morning' scheduled task; safe to run manually.
$ErrorActionPreference = "Stop"
$keystone = Join-Path $PSScriptRoot "keystone.ps1"
$log = Join-Path $PSScriptRoot "..\outputs\morning\cadence.log"
try {
    & $keystone morning *>> $log
    & $keystone meeting-sync *>> $log
    & $keystone dashboard *>> $log
    & $keystone cockpit *>> $log
    Add-Content $log "[$(Get-Date -Format o)] cadence OK"
} catch {
    Add-Content $log "[$(Get-Date -Format o)] cadence FAILED: $_"
    exit 1
}
```

(`meeting-sync` runs before the snapshot step added in Task 5, once that's wired in, so same-day meetings are present in the corpus before the snapshot summarizes "recent activity.")

- [ ] **Step 8: Commit**

```bash
git add scripts/keystone.ps1 scripts/morning-cadence.ps1 tests/keystone-meeting-sync.ps1
git commit -m "feat: add unattended meeting-sync command wired into the morning cadence"
```

---

### Task 4b: Fix fragile export-file detection in `Invoke-MeetingSync`

**Added after Task 4's review.** The task reviewer flagged that identifying
"the file that was just exported" by picking the newest `LastWriteTime` in
`SecondBrain/Inbox/meetings/` is fragile in a live, accumulating vault
directory (as opposed to the isolated test fixture): if
`fireflies-pp-cli transcripts export` ever exits 0 without writing a new
file, this silently grabs an unrelated existing meeting file and prepends a
duplicate header block to it — and since that edit itself updates the
file's mtime, a mis-attributed file can keep "winning" on subsequent runs.
Confirmed with Eric: fix now rather than accept, even though the existing
interactive `meeting-sync` skill uses the same heuristic today.

**Files:**
- Modify: `scripts/keystone.ps1` (the `Invoke-MeetingSync` function added in
  Task 4)
- Modify: `tests/keystone-meeting-sync.ps1`

**Interfaces:**
- No change to `Invoke-MeetingSync`'s signature or return shape
  (`[pscustomobject]@{ NewCount; GenericCount; VaultDir }` / `$null`).

- [ ] **Step 1: Write the failing test**

Add a new fixture case to `tests/keystone-meeting-sync.ps1` proving the
by-ID detection: create a vault with an existing unrelated `.md` file whose
`LastWriteTime` is artificially set to be newer than "now" (so the old
newest-mtime heuristic would have picked it), stub `fireflies-pp-cli` as a
local script on `PATH` that both "exports" nothing (simulating the export
step no-op'ing) for one call and writes a real new file (simulating a real
export) for another, and assert the unrelated file is never modified in the
no-op case while the real new file is correctly detected and header-tagged
in the export case. Append this to the existing test file rather than
replacing it — the existing "missing fireflies-pp-cli" case must keep
passing unchanged.

```powershell
# Additional fixture appended to tests/keystone-meeting-sync.ps1, before the
# final `finally` block of the existing test:

$tempRoot2 = Join-Path ([System.IO.Path]::GetTempPath()) ("keystone-meeting-sync-byid-test-" + [System.Guid]::NewGuid().ToString("n"))
try {
    New-Item -ItemType Directory -Force -Path (Join-Path $tempRoot2 "scripts"), (Join-Path $tempRoot2 "vault"), (Join-Path $tempRoot2 "bin") | Out-Null
    Copy-Item -LiteralPath (Join-Path $repoRoot "scripts\keystone.ps1") -Destination (Join-Path $tempRoot2 "scripts\keystone.ps1")

    # Pre-existing unrelated file, deliberately touched to be the "newest" file
    # in the vault before export runs — the old heuristic would wrongly pick this.
    $unrelated = Join-Path $tempRoot2 "vault\2026-01-01_unrelated-meeting.md"
    Set-Content -LiteralPath $unrelated -Value "# Unrelated meeting`nOriginal content, must not change." -Encoding UTF8
    (Get-Item -LiteralPath $unrelated).LastWriteTime = (Get-Date).AddMinutes(5)

    # Fake fireflies-pp-cli: sync/find succeed with one transcript; export for
    # that transcript writes a real, ID-named file so by-ID matching can find it.
    $fakeCli = Join-Path $tempRoot2 "bin\fireflies-pp-cli.ps1"
    @'
param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Rest)
$vaultArgIndex = [array]::IndexOf($Rest, "--vault")
switch ($Rest[0]) {
    "sync" { exit 0 }
    "transcripts" {
        if ($Rest[1] -eq "find") {
            '[{"id":"tx-real-1","title":"Real Meeting"}]' | Write-Output
            exit 0
        }
        if ($Rest[1] -eq "export") {
            $vaultDir = $Rest[$vaultArgIndex + 1]
            Set-Content -LiteralPath (Join-Path $vaultDir "2026-07-13_real-meeting.md") -Value "# Real meeting`nExported content." -Encoding UTF8
            exit 0
        }
    }
}
'@ | Set-Content -LiteralPath $fakeCli -Encoding UTF8

    $wrapperCmd = Join-Path $tempRoot2 "bin\fireflies-pp-cli.cmd"
    "@echo off`r`npowershell -NoProfile -File `"$fakeCli`" %*" | Set-Content -LiteralPath $wrapperCmd -Encoding ASCII

    $originalPath2 = $env:PATH
    $env:PATH = (Join-Path $tempRoot2 "bin") + ";" + $originalPath2
    try {
        $script2 = Join-Path $tempRoot2 "scripts\keystone.ps1"
        # Point the function at our fixture vault instead of the hardcoded real path —
        # the fixed implementation must accept the vault path as a parameter for this
        # to be testable; see Step 2.
        & $script2 meeting-sync -VaultDir (Join-Path $tempRoot2 "vault") *>&1 | Out-Null

        $unrelatedContent = Get-Content -Raw -LiteralPath $unrelated
        Assert-True ($unrelatedContent -eq "# Unrelated meeting`nOriginal content, must not change.") "Unrelated newest-mtime file must NOT be modified."

        $realFile = Join-Path $tempRoot2 "vault\2026-07-13_real-meeting.md"
        Assert-True (Test-Path -LiteralPath $realFile) "The genuinely-exported file must exist."
        $realContent = Get-Content -Raw -LiteralPath $realFile
        Assert-True ($realContent -match "## Project tags") "The genuinely-exported file must be header-tagged."
    }
    finally {
        $env:PATH = $originalPath2
    }
    Write-Host "keystone meeting-sync by-id detection tests passed"
}
finally { if (Test-Path $tempRoot2) { Remove-Item -LiteralPath $tempRoot2 -Recurse -Force } }
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.\tests\keystone-meeting-sync.ps1`
Expected: FAIL — either the unrelated file gets modified, or `-VaultDir` is
not a recognized parameter yet.

- [ ] **Step 3: Fix `Invoke-MeetingSync` to detect the exported file by diffing the directory listing, not by newest mtime**

Modify the function's signature and export loop in `scripts/keystone.ps1`:

```powershell
function Invoke-MeetingSync {
    param([string]$VaultDir = "C:\Users\eric_rash\Desktop\SecondBrain\Inbox\meetings")

    Show-Section "Meeting Sync"
    $ff = Get-Command fireflies-pp-cli -ErrorAction SilentlyContinue
    if (-not $ff) { Write-Host "fireflies-pp-cli not found on PATH; skipped."; return $null }

    New-Item -ItemType Directory -Force -Path $VaultDir | Out-Null
    $statePath = Join-Path $VaultDir ".sync-state.json"
    if (-not (Test-Path -LiteralPath $statePath)) {
        '{"exports":{}}' | Set-Content -LiteralPath $statePath -Encoding UTF8
    }

    & fireflies-pp-cli sync --agent 2>&1 | ForEach-Object { Write-Host $_ }
    if ($LASTEXITCODE -ne 0) {
        Write-Host "fireflies-pp-cli sync failed (exit $LASTEXITCODE); skipping export this run."
        return $null
    }

    $findRaw = & fireflies-pp-cli transcripts find --from 14 --processed-only --json --agent 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "fireflies-pp-cli transcripts find failed; skipping export this run."
        return $null
    }

    try {
        $transcripts = @(($findRaw -join "`n") | ConvertFrom-Json)
    }
    catch {
        Write-Host "Could not parse transcripts find output; skipping."
        return $null
    }

    $state = Get-Content -Raw -LiteralPath $statePath | ConvertFrom-Json
    $exportsMap = @{}
    if ($state.exports) {
        foreach ($p in $state.exports.PSObject.Properties) { $exportsMap[$p.Name] = $p.Value }
    }

    $newCount = 0
    $genericCount = 0
    $genericPattern = '^(zoom meeting|recording|meeting)?$|^\d{4}-\d{2}-\d{2}$'

    foreach ($t in $transcripts) {
        $id = [string]$t.id
        if ($exportsMap.ContainsKey($id)) { continue }
        if ([string]::IsNullOrWhiteSpace($t.title) -or ($t.title.Trim().ToLowerInvariant() -match $genericPattern)) {
            $genericCount++
        }

        $before = @(Get-ChildItem -LiteralPath $VaultDir -Filter "*.md" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name)

        & fireflies-pp-cli transcripts export $id --vault $VaultDir --agent 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Export failed for $id; continuing."
            continue
        }

        $after = @(Get-ChildItem -LiteralPath $VaultDir -Filter "*.md" -ErrorAction SilentlyContinue)
        $newFiles = @($after | Where-Object { $before -notcontains $_.Name })

        if ($newFiles.Count -eq 0) {
            Write-Host "Export for $id reported success but no new file appeared in the vault; skipping to avoid tagging the wrong file."
            continue
        }
        if ($newFiles.Count -gt 1) {
            Write-Host "Export for $id produced $($newFiles.Count) new files; using the most recently written one and logging the rest."
        }
        $exportedFile = $newFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1

        $header = @'
## Project tags
> Tag this meeting against active projects. Add freely. Used by weekly-review to surface drift.

- project/
- person/

## Key topics

## Decisions

## Action items
> Pulled from Fireflies. Mark complete by replacing `[ ]` with `[x]`.

## Open questions

'@
        $content = Get-Content -Raw -LiteralPath $exportedFile.FullName
        Set-Content -LiteralPath $exportedFile.FullName -Value ($header + $content) -Encoding UTF8

        $exportsMap[$id] = [pscustomobject]@{
            filename    = $exportedFile.Name
            exported_at = (Get-Date).ToString("o")
        }
        $newCount++
    }

    ([pscustomobject]@{ exports = $exportsMap }) | ConvertTo-Json -Depth 10 |
        Set-Content -LiteralPath $statePath -Encoding UTF8

    Write-Host "Meetings found (last 14 days): $($transcripts.Count)"
    Write-Host "New exports: $newCount"
    if ($genericCount -gt 0) {
        Write-Host "$genericCount new meeting(s) have generic titles; run /name-meetings interactively to clean them up."
    }

    return [pscustomobject]@{ NewCount = $newCount; GenericCount = $genericCount; VaultDir = $VaultDir }
}
```

The key change: capture the directory's `.md` filenames before calling
`export`, then diff against the listing after — the new file is whatever
name appeared that wasn't there before, not whatever has the newest
`LastWriteTime`. If no new file appears (export silently no-op'd), skip and
log rather than guessing. `$VaultDir` becomes a parameter (defaulting to
the real path) so tests can point it at a fixture directory instead of the
live vault.

- [ ] **Step 4: Run test to verify it passes**

Run: `.\tests\keystone-meeting-sync.ps1`
Expected: both `keystone meeting-sync tests passed` and
`keystone meeting-sync by-id detection tests passed`.

- [ ] **Step 5: Commit**

```bash
git add scripts/keystone.ps1 tests/keystone-meeting-sync.ps1
git commit -m "fix: detect exported meeting file by directory diff, not newest mtime"
```

---

### Task 5: `keystone.ps1 snapshot` — unified daily snapshot

**Files:**
- Modify: `scripts/keystone.ps1` (add `New-UnifiedSnapshot` function, switch case)
- Modify: `scripts/morning-cadence.ps1` (add the new step)
- Test: `tests/keystone-snapshot.ps1`

**Interfaces:**
- Produces: `New-UnifiedSnapshot` — writes `outputs\dashboard\unified-snapshot.md` under the KeystoneOS root and returns its path. Read by Task 6's Claude and Codex `SessionStart` hooks.

- [ ] **Step 1: Write the failing test**

```powershell
# tests/keystone-snapshot.ps1
$ErrorActionPreference = "Stop"
function Assert-True($Condition, $Message) { if (-not $Condition) { throw $Message } }
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("keystone-snapshot-test-" + [System.Guid]::NewGuid().ToString("n"))
try {
    New-Item -ItemType Directory -Force -Path (Join-Path $tempRoot "scripts") | Out-Null
    Copy-Item -LiteralPath (Join-Path $repoRoot "scripts\keystone.ps1") -Destination (Join-Path $tempRoot "scripts\keystone.ps1")
    $script = Join-Path $tempRoot "scripts\keystone.ps1"

    & $script snapshot *>&1 | Out-Null
    $snapshotPath = Join-Path $tempRoot "outputs\dashboard\unified-snapshot.md"
    Assert-True (Test-Path -LiteralPath $snapshotPath) "snapshot command must write outputs\dashboard\unified-snapshot.md"
    $content = Get-Content -Raw -LiteralPath $snapshotPath
    Assert-True ($content -match "## Recent Claude Activity") "Snapshot must contain a Recent Claude Activity section."
    Assert-True ($content -match "## Recent Codex Activity") "Snapshot must contain a Recent Codex Activity section."
    Assert-True ($content -match "## Recent Meetings") "Snapshot must contain a Recent Meetings section."
    Assert-True ($content -match "## Active Projects and Pending Decisions") "Snapshot must contain a project/decisions section."
    Assert-True ($content.Length -le 6100) "Snapshot must respect the size cap (allowing small overhead for the truncation marker)."
    Write-Host "keystone snapshot tests passed"
}
finally { if (Test-Path $tempRoot) { Remove-Item -LiteralPath $tempRoot -Recurse -Force } }
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.\tests\keystone-snapshot.ps1`
Expected: FAIL — `snapshot` is not a valid value (already added to `ValidateSet` in Task 4 Step 3; if done out of order, add it now) or the function doesn't exist.

- [ ] **Step 3: Add `New-UnifiedSnapshot`**, placed just above `Invoke-AgySync` in `scripts/keystone.ps1`:

```powershell
function New-UnifiedSnapshot {
    Show-Section "Unified Snapshot"
    New-Item -ItemType Directory -Force -Path $DashboardDir | Out-Null
    $outPath = Join-Path $DashboardDir "unified-snapshot.md"

    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add("# KeystoneOS Unified Snapshot")
    $lines.Add("Generated: $((Get-Date).ToString('o'))")

    $lines.Add("")
    $lines.Add("## Recent Claude Activity")
    $claudeDailyDir = "C:\Users\eric_rash\.claude\claude-memory-compiler\daily"
    $recentClaude = if (Test-Path -LiteralPath $claudeDailyDir) {
        Get-ChildItem -LiteralPath $claudeDailyDir -Filter "*.md" -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending | Select-Object -First 1
    } else { $null }
    if ($recentClaude) {
        $text = Get-Content -Raw -LiteralPath $recentClaude.FullName
        if ($text.Length -gt 1500) { $text = $text.Substring(0, 1500) + "`n...(truncated)" }
        $lines.Add($text.Trim())
    } else {
        $lines.Add("No recent Claude daily log found.")
    }

    $lines.Add("")
    $lines.Add("## Recent Codex Activity")
    $codexSummary = "C:\Users\eric_rash\.codex\memories\memory_summary.md"
    if (Test-Path -LiteralPath $codexSummary) {
        $text = Get-Content -Raw -LiteralPath $codexSummary
        if ($text.Length -gt 1500) { $text = $text.Substring(0, 1500) + "`n...(truncated)" }
        $lines.Add($text.Trim())
    } else {
        $lines.Add("No Codex memory summary found.")
    }

    $lines.Add("")
    $lines.Add("## Recent Meetings")
    $meetingsDir = "C:\Users\eric_rash\Desktop\SecondBrain\Inbox\meetings"
    $recentMeetings = if (Test-Path -LiteralPath $meetingsDir) {
        @(Get-ChildItem -LiteralPath $meetingsDir -Filter "*.md" -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending | Select-Object -First 5)
    } else { @() }
    if ($recentMeetings.Count -eq 0) {
        $lines.Add("No recent meeting exports found.")
    } else {
        foreach ($m in $recentMeetings) {
            $lines.Add("- $($m.Name) (updated $($m.LastWriteTime.ToString('yyyy-MM-dd')))")
        }
    }

    $lines.Add("")
    $lines.Add("## Active Projects and Pending Decisions")
    foreach ($p in (Get-Projects | Select-Object -First 10)) {
        $lines.Add("- $($p.key): $($p.name) [$($p.status)]")
    }
    $decisionsLog = Join-Path $Root "decisions\log.md"
    if (Test-Path -LiteralPath $decisionsLog) {
        $decisionsText = Get-Content -Raw -LiteralPath $decisionsLog
        if ($decisionsText.Length -gt 1200) { $decisionsText = $decisionsText.Substring(0, 1200) + "`n...(truncated)" }
        $lines.Add("")
        $lines.Add("Latest decision entries:")
        $lines.Add($decisionsText.Trim())
    }

    $text = ($lines -join "`n")
    if ($text.Length -gt 6000) { $text = $text.Substring(0, 6000) + "`n...(truncated)" }

    Set-Content -LiteralPath $outPath -Value $text -Encoding UTF8
    Write-Host "Unified snapshot written: $outPath"
    return $outPath
}
```

- [ ] **Step 4: Add the switch case**

```powershell
    "snapshot" { New-UnifiedSnapshot | Out-Null }
```

- [ ] **Step 5: Run test to verify it passes**

Run: `.\tests\keystone-snapshot.ps1`
Expected: `keystone snapshot tests passed`

- [ ] **Step 6: Wire into the morning cadence**, after `meeting-sync`:

```powershell
$ErrorActionPreference = "Stop"
$keystone = Join-Path $PSScriptRoot "keystone.ps1"
$log = Join-Path $PSScriptRoot "..\outputs\morning\cadence.log"
try {
    & $keystone morning *>> $log
    & $keystone meeting-sync *>> $log
    & $keystone snapshot *>> $log
    & $keystone dashboard *>> $log
    & $keystone cockpit *>> $log
    Add-Content $log "[$(Get-Date -Format o)] cadence OK"
} catch {
    Add-Content $log "[$(Get-Date -Format o)] cadence FAILED: $_"
    exit 1
}
```

- [ ] **Step 7: Commit**

```bash
git add scripts/keystone.ps1 scripts/morning-cadence.ps1 tests/keystone-snapshot.ps1
git commit -m "feat: generate a unified cross-harness snapshot on the morning cadence"
```

---

### Task 6: Inject the unified snapshot at session start, both tools

**Files:**
- Create: `~/.claude/hooks/keystone-unified-snapshot.js`
- Modify: `~/.claude/settings.json` (add a third `SessionStart` hook entry)
- Modify: `scripts/codex-hooks/session-start.ps1`
- Test: `tests/codex-session-start-snapshot.ps1`

**Interfaces:**
- Consumes: `outputs\dashboard\unified-snapshot.md` (Task 5), at the fixed path `C:\Users\eric_rash\Desktop\DEV\KeystoneOS\outputs\dashboard\unified-snapshot.md`.
- Produces: for Claude, stdout JSON of shape `{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "..."}}` (same schema the memory-compiler's own `session-start.py` already uses — confirmed by reading it). For Codex, an added `## Unified Snapshot` section appended to the existing startup context text in `session-start.ps1`.

- [ ] **Step 1: Create `~/.claude/hooks/keystone-unified-snapshot.js`**

```javascript
#!/usr/bin/env node
// SessionStart hook: inject KeystoneOS's cross-harness unified snapshot
// (recent Claude/Codex/meeting activity) silently alongside the memory
// compiler's own snapshot. Fails closed: any error means no additionalContext,
// never a thrown error that could block session start.

const fs = require('fs');
const path = require('path');
const os = require('os');

const SNAPSHOT_PATH = path.join(
  os.homedir(), 'Desktop', 'DEV', 'KeystoneOS', 'outputs', 'dashboard', 'unified-snapshot.md'
);

function emit(context) {
  const output = {
    hookSpecificOutput: {
      hookEventName: 'SessionStart',
    },
  };
  if (context) output.hookSpecificOutput.additionalContext = context;
  process.stdout.write(JSON.stringify(output));
}

try {
  const content = fs.readFileSync(SNAPSHOT_PATH, 'utf8');
  emit(content);
}
catch (_) {
  emit(null);
}
```

- [ ] **Step 2: Manually verify the hook's stdout is valid JSON**

Run: `node "C:\Users\eric_rash\.claude\hooks\keystone-unified-snapshot.js"`
Expected: prints one line of JSON with `hookSpecificOutput.additionalContext` set to the snapshot's content (or `hookSpecificOutput` with no `additionalContext` key if the file is missing).

- [ ] **Step 3: Add the hook to `~/.claude/settings.json`**

In the `SessionStart` array (the same one already containing the memory-compiler hook and `gsd-check-update.js`), add a third entry:

```json
      {
        "hooks": [
          {
            "type": "command",
            "command": "node \"C:/Users/eric_rash/.claude/hooks/keystone-unified-snapshot.js\"",
            "timeout": 5,
            "statusMessage": "Loading unified cross-harness snapshot..."
          }
        ]
      }
```

Insert it as a sibling of the existing two entries inside the `SessionStart` array — do not remove or reorder the existing entries.

- [ ] **Step 4: Extend `scripts/codex-hooks/session-start.ps1`**

Add a new function alongside `Get-ClaudeCompilerContext`:

```powershell
function Get-UnifiedSnapshotContext {
    param([string]$KeystoneRoot)

    $snapshotPath = Join-Path $KeystoneRoot "outputs\dashboard\unified-snapshot.md"
    if (-not (Test-Path -LiteralPath $snapshotPath)) {
        return "## Unified Snapshot`nNo unified snapshot found yet; run ``.\scripts\keystone.ps1 snapshot``."
    }

    $excerpt = Get-FileExcerpt -Path $snapshotPath -MaxChars 4000
    return "## Unified Snapshot`n$excerpt"
}
```

Then add it to the `$parts` list in the main `try` block (after the existing `Get-ClaudeCompilerContext` line):

```powershell
    $parts.Add((Get-ClaudeCompilerContext -NoClaude:$NoClaude -UvPath $UvPath -ClaudeCompilerRoot $ClaudeCompilerRoot))
    $parts.Add((Get-UnifiedSnapshotContext -KeystoneRoot $keystoneRoot))
```

- [ ] **Step 5: Write the failing test**

```powershell
# tests/codex-session-start-snapshot.ps1
$ErrorActionPreference = "Stop"
function Assert-True($Condition, $Message) { if (-not $Condition) { throw $Message } }
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("codex-session-start-snapshot-test-" + [System.Guid]::NewGuid().ToString("n"))
try {
    New-Item -ItemType Directory -Force -Path (Join-Path $tempRoot "scripts\codex-hooks") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $tempRoot "outputs\dashboard") | Out-Null
    Copy-Item -LiteralPath (Join-Path $repoRoot "scripts\codex-hooks\common.ps1") -Destination (Join-Path $tempRoot "scripts\codex-hooks\common.ps1")
    Copy-Item -LiteralPath (Join-Path $repoRoot "scripts\codex-hooks\session-start.ps1") -Destination (Join-Path $tempRoot "scripts\codex-hooks\session-start.ps1")
    Set-Content -LiteralPath (Join-Path $tempRoot "outputs\dashboard\unified-snapshot.md") -Encoding UTF8 -Value "# KeystoneOS Unified Snapshot`nUnifiedSnapshotProbeMarker"

    $script = Join-Path $tempRoot "scripts\codex-hooks\session-start.ps1"
    $output = (& $script -Root $tempRoot -NoClaude *>&1 | Out-String)
    $json = $output | ConvertFrom-Json
    $context = $json.hookSpecificOutput.additionalContext
    Assert-True ($context -match "UnifiedSnapshotProbeMarker") "Codex SessionStart context must include the unified snapshot content."
    Write-Host "codex session-start snapshot tests passed"
}
finally { if (Test-Path $tempRoot) { Remove-Item -LiteralPath $tempRoot -Recurse -Force } }
```

- [ ] **Step 6: Run test to verify it fails**

Run: `.\tests\codex-session-start-snapshot.ps1`
Expected: FAIL — context does not contain `UnifiedSnapshotProbeMarker` (function not called yet).

- [ ] **Step 7: Run test to verify it passes** (after Steps 3–4 above are applied)

Run: `.\tests\codex-session-start-snapshot.ps1`
Expected: `codex session-start snapshot tests passed`

- [ ] **Step 8: Commit**

```bash
git add scripts/codex-hooks/session-start.ps1 tests/codex-session-start-snapshot.ps1
git commit -m "feat: inject unified cross-harness snapshot at Claude and Codex session start"
```

(The `~/.claude/hooks/keystone-unified-snapshot.js` and `~/.claude/settings.json` edits live outside the KeystoneOS repo; commit them separately if `~/.claude` is a git repo, otherwise note the manual edit in this commit's body.)

---

### Task 7: Full regression pass

**Files:** none (verification only)

- [ ] **Step 1: Run the full existing KeystoneOS test suite plus all new tests**

Run:
```powershell
Get-ChildItem "C:\Users\eric_rash\Desktop\DEV\KeystoneOS\tests\*.ps1" | ForEach-Object { & $_.FullName }
```
Expected: every script prints its own "... tests passed" line; no unhandled exceptions.

- [ ] **Step 2: End-to-end check — Codex indexing**

Open a Codex session, have it say something distinctive (e.g. a nonsense phrase you'll search for), end the session, then run:
```powershell
memsearch search "<the distinctive phrase>" --top-k 3
```
Expected: a hit pointing at a Codex memory file.

- [ ] **Step 3: End-to-end check — meetings**

Run `.\scripts\keystone.ps1 meeting-sync` (requires `FIREFLIES_API_KEY` configured), then:
```powershell
memsearch search "<a phrase known to be in a recently synced meeting>" --top-k 3
```
Expected: a hit pointing at a file under `SecondBrain\Inbox\meetings\`.

- [ ] **Step 4: End-to-end check — unified snapshot parity**

Run `.\scripts\keystone.ps1 snapshot`, then open a fresh Claude Code session and a fresh Codex session same-day. Confirm both show the same `## Recent Claude Activity` / `## Recent Codex Activity` / `## Recent Meetings` content.

- [ ] **Step 5: Failure-mode check**

Stop Docker Desktop (Milvus unreachable), end a Codex session, confirm it still ends normally (no hang, no error surfaced to the user), then check `~/.claude/global-memory/transcripts/.errors.log` for a logged, non-fatal entry. Restart Docker afterward.

---

## Rollback

Four production-adjacent files were touched outside `git` history that git-based
revert cannot undo on its own (three live outside any git repo entirely; the
fourth is managed by its own installer, not hand-edited). This section is the
recovery procedure for each, current as of 2026-07-13. It assumes no other
context — follow it standalone.

### 1. `C:\Users\eric_rash\.claude\hooks\memsearch-sync.js` (modified in place, Task 2)

**Current state:** `PATHS` is now produced by a `resolvePaths()` function that
reads `data\memory-index-paths.json` (this repo) and falls back to a
hardcoded array if that file is missing, unreadable, or fails to parse.

**No backup file exists** — none is needed, because the fallback array inside
`resolvePaths()` was verified (2026-07-13) to be byte-for-byte identical to
the pre-Task-2 hardcoded `PATHS` array:

```javascript
const fallback = [
  path.join(os.homedir(), '.claude', 'global-memory', 'transcripts'),
  path.join(os.homedir(), '.claude', 'projects', 'C--Users-eric-rash', 'memory'),
  path.join(os.homedir(), '.claude', 'claude-memory-compiler', 'daily'),
  path.join(os.homedir(), '.claude', 'claude-memory-compiler', 'knowledge'),
  path.join(os.homedir(), 'Desktop', 'SecondBrain', 'Knowledge', 'library'),
];
```

This means rollback does not require restoring old file content — it is
achieved purely by making the config unreadable to the hook:

**Rollback steps:**
1. Rename or delete `C:\Users\eric_rash\Desktop\DEV\KeystoneOS\data\memory-index-paths.json`
   (or make it return invalid JSON) so `resolvePaths()`'s `try` block throws
   and hits the `catch`.
2. Verify: run
   `node -e "const fs=require('fs'),os=require('os'),path=require('path'); try { JSON.parse(fs.readFileSync('C:/Users/eric_rash/Desktop/DEV/KeystoneOS/data/memory-index-paths.json','utf8')); console.log('config still readable — rollback NOT in effect'); } catch(e) { console.log('config unreadable — hook will use fallback (rollback in effect)'); }"`
3. No edit to `memsearch-sync.js` itself is required. If a full revert to the
   pre-Task-2 file is ever wanted anyway, the diff is small enough to
   hand-apply: restore the five-line hardcoded `const PATHS = [...]` block
   shown above in place of the `KEYSTONE_INDEX_CONFIG` / `resolvePaths()` /
   `const PATHS = resolvePaths();` block that replaced it.

### 2. `C:\Users\eric_rash\.claude\hooks\keystone-unified-snapshot.js` (new file, Task 6)

**Current state:** new file, not present before this plan. Injects
`outputs\dashboard\unified-snapshot.md` as `additionalContext` on Claude
`SessionStart`, failing closed (emits `hookSpecificOutput` with no
`additionalContext` key on any read error).

**Rollback steps:**
1. Delete the file: `Remove-Item -LiteralPath "C:\Users\eric_rash\.claude\hooks\keystone-unified-snapshot.js"`.
2. Remove its `SessionStart` entry from `C:\Users\eric_rash\.claude\settings.json`
   (see item 3 below — restoring the settings.json backup does both steps
   for that file in one move, but the `.js` file itself must still be
   deleted separately since the backup only reverts the JSON, not the
   filesystem).

### 3. `C:\Users\eric_rash\.claude\settings.json` (modified in place, Task 6)

**Current state:** the `hooks.SessionStart` array has **3** entries (verified
2026-07-13): the memory-compiler's own hook, the `context-mode-cache-heal.mjs`
hook, and the new third entry running
`node "C:/Users/eric_rash/.claude/hooks/keystone-unified-snapshot.js"`
(timeout 5s, statusMessage "Loading unified cross-harness snapshot...").

**Backup:** `C:\Users\eric_rash\.claude\settings.json.bak-20260713-153814` —
confirmed present and valid JSON (2026-07-13), containing exactly **2**
`SessionStart` entries (pre-Task-6 state, i.e. only the memory-compiler and
`context-mode-cache-heal.mjs` hooks).

**Rollback steps:**
1. Confirm the backup still exists and parses:
   `Get-Content -Raw -LiteralPath "C:\Users\eric_rash\.claude\settings.json.bak-20260713-153814" | ConvertFrom-Json | Out-Null` —
   should not throw.
2. Copy it over the live file:
   `Copy-Item -LiteralPath "C:\Users\eric_rash\.claude\settings.json.bak-20260713-153814" -Destination "C:\Users\eric_rash\.claude\settings.json" -Force`
3. Also delete `keystone-unified-snapshot.js` per item 2 above — restoring
   settings.json alone stops it from being invoked, but leaves the dead file
   on disk.

### 4. `C:\Users\eric_rash\.codex\hooks.json` (modified by installer, Task 3)

**Current state:** managed entirely by `scripts\install-codex-hooks.ps1
-Apply`, never hand-edited. Task 3 re-ran the installer to raise the `Stop`
hook timeout from 10s to 50s (for the Codex-side `memsearch index` call to
complete before being killed).

**Backup:** the installer creates a timestamped backup on every run
automatically, before writing. The relevant one for this plan's change is
`C:\Users\eric_rash\.codex\hooks.json.bak-20260713-150022-024`. (Do not
assume this is the only backup — the installer has run multiple times
historically; `Get-ChildItem "C:\Users\eric_rash\.codex\hooks.json.bak-*"`
lists all of them, newest by embedded timestamp in the filename.)

**Rollback steps:**
1. Identify the correct backup (the one immediately preceding the unwanted
   change) from `Get-ChildItem "C:\Users\eric_rash\.codex\hooks.json.bak-*" | Sort-Object Name`.
2. Copy it over the live file:
   `Copy-Item -LiteralPath "C:\Users\eric_rash\.codex\hooks.json.bak-20260713-150022-024" -Destination "C:\Users\eric_rash\.codex\hooks.json" -Force`
3. Alternatively, re-run `scripts\install-codex-hooks.ps1 -Apply` after
   reverting `scripts\install-codex-hooks.ps1`'s `-Timeout 50` back to `-Timeout 10`
   in git — the installer is idempotent and will regenerate a correct
   `hooks.json` from the (now-reverted) source of truth, creating yet another
   fresh backup of the current state first.

No gap here — this file already had a clean, automatic rollback path before
this plan touched it; it's documented here only so all four files affected
this session are in one place.
