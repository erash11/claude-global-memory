# Codex Memory Bridge

The Codex memory bridge gives Codex a small, reliable adapter into KeystoneOS and the existing Claude memory infrastructure.

It does not replace Claude Code hooks, Claude memory compiler, Codex memories, Obsidian, SecondBrain, or Graphify. KeystoneOS remains the cross-harness control plane that points each agent to the right source of truth.

## What Codex Gets

On `SessionStart`, Codex receives a compact startup packet with:

- KeystoneOS root path
- daily KeystoneOS command surface
- registered active projects and startup checks
- latest KeystoneOS handoff note
- latest project intake artifact
- Claude memory compiler startup context, when available

`SessionStart` is the only KeystoneOS Codex lifecycle hook that emits context JSON on stdout.

On `PreCompact`, KeystoneOS stores the raw hook event under:

```powershell
outputs\codex-hooks\pre-compact\
```

It emits no stdout. Codex validates `PreCompact` with a stricter event-specific schema, so the hook is side-effect-only.

On `Stop`, KeystoneOS stores the raw hook event under:

```powershell
outputs\codex-hooks\stop\
```

It also emits no stdout for the same reason.

Those generated event files are ignored by git. They are breadcrumbs for local recovery, not source-controlled memory.

## Compatibility Model

Claude Code and Codex can coexist as long as they share sources of truth through KeystoneOS and keep their lifecycle adapters separate.

- Shared truth: KeystoneOS project registry, Codex memories, Claude memory compiler output, SecondBrain, Obsidian, and Graphify maps.
- Codex adapter: narrow PowerShell hooks in `scripts\codex-hooks\`.
- Claude adapter: Claude Code hooks and memory compiler scripts remain owned by the Claude environment.
- Cross-harness rule: read/query other memory layers, but do not overwrite them from lifecycle hooks.

## Memory Retrieval Scopes

KeystoneOS keeps Claude Code, Codex, SecondBrain, project repositories, and Graphify as separate owners. The router now exposes two retrieval scopes:

- `fast` (default): Codex memory, Claude global memory, and SecondBrain. This is used by `context`, `brief`, and morning startup.
- `broad`: adds the Claude compiler, Baylor WorkDrive, Graphify reports, and agy conversation digests. Use it intentionally with `.\scripts\keystone.ps1 memory "<query>" -Scope broad`.

Results show source authority (`canonical`, `synthesis`, `working`, or `derived`), sensitivity, and freshness. Broad sources can be stale or restricted; those labels are part of the result contract. Ripgrep is required for bounded retrieval, and missing optional agy files do not prevent core Keystone commands from running.
## Scripts

```powershell
.\scripts\codex-hooks\session-start.ps1 -NoClaude
.\scripts\codex-hooks\pre-compact.ps1
.\scripts\codex-hooks\session-end.ps1
.\scripts\codex-hooks\stop.ps1
.\scripts\install-codex-hooks.ps1
.\scripts\install-codex-hooks.ps1 -Apply
```

The installer defaults to dry-run. `-Apply` backs up the existing Codex hook file and then merges KeystoneOS hooks into:

```powershell
C:\Users\eric_rash\.codex\hooks.json
```

The installer preserves existing non-Keystone hooks and removes/replaces only previous KeystoneOS `codex-hooks` entries so repeated installs stay idempotent.

If the existing Claude memory compiler hook uses `/c/Users/...` paths, the installer preserves that original command and adds a Windows-native `commandWindows` override for Codex.

The `SessionEnd` adapter is deliberately split in two. The foreground hook
queues a job and exits within Codex's three-second limit. A hidden background
worker extracts new user/final-assistant messages from the raw Codex JSONL and
passes a disposable Markdown context file to the existing Claude memory
compiler. Per-session processed-line markers prevent unchanged transcripts from
being flushed twice.

## Trust Step

After installing or changing hooks, Codex may require review through `/hooks` before running them automatically. Review the generated commands and trust the KeystoneOS entries if they match this repo.

## Rollback

Backups are written next to the Codex hook file:

```powershell
C:\Users\eric_rash\.codex\hooks.json.bak-YYYYMMDD-HHMMSS-fff
```

To roll back, replace `hooks.json` with the newest known-good backup.

## Operating Rule

Keep the bridge narrow:

- Read Claude and Codex memory.
- Write KeystoneOS event breadcrumbs.
- `SessionEnd` may submit a temporary, filtered Codex context to the Claude
  memory compiler; it must not directly edit compiled articles.
- Do not overwrite Codex memory, SecondBrain, or Obsidian from a lifecycle hook.
- Use explicit KeystoneOS commands for heavier work such as memory search, project intake, and Graphify sync.
