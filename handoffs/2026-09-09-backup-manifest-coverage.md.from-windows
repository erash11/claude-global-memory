# Handoff — 2026-09-09 — Backup manifest coverage closed

## What was being worked on and why

`/backup` was run on demand. It ended `ERROR (2 errors)`:

1. `repo-diverged:dotclaude` — `~/.claude` was 1 commit behind origin with 2 dirty files.
2. `manifest-unmanaged:` — 49 `~/DEV` directories were absent from
   `~/.claude/scripts/backup-manifest.json`. The manifest is default-deny, so those 49 were
   **not being backed up anywhere** except whatever GitHub already held.

Eric confirmed all 49 matter: they are fallout from an earlier GitHub consolidation migration,
not a classification backlog.

## Decisions made (and the reasoning that would otherwise be lost)

- **Fixed the divergence with `git -C ~/.claude pull --rebase --autostash`.** behind=1 ahead=0
  meant a clean fast-forward; `--autostash` preserved the 2 uncommitted edits. The backup script
  refuses to merge diverged repos by design, so this had to be done by hand.
- **Added all 49 in one pass rather than folder-by-folder.** Two shapes only:
  - 47 git repos → copied the `DEV/AgentAssist` shape: `isRepo:true`, real `erash11` remote,
    `captureOrphans:true`, `captureWorkingTree:true`, `destinations:["ssd","github"]`.
  - 2 plain dirs (`_ARCHIVE` 4.3 GB, `docs`) → copied the `DEV/Life-OS` shape: `isRepo:false`,
    `destinations:["ssd"]`, capture flags false.
- **Dropped `baylor` from every new entry.** It is `deprecated:true` in the manifest and the
  newest existing entry (`DEV/Life-OS`, commit `3444c0b`) already omits it.
- **Verified from source, not inference, that this is safe.** `grep` of `daily-backup.ps1`
  confirmed `Sync-Repo` (the auto-commit + push function) runs on a hardcoded list of four
  memory repos only. The manifest loop calls `Capture-RepoData` or `Snapshot-Additive`. So
  adding 47 project repos does **not** auto-commit or push them — important, since several
  have open PRs and dirty working trees.
- **`class` is inert.** It is read nowhere in the script. Set `institutional` by default,
  `personal` for obviously-personal projects. Documentation value only.
- **Removed `DEV/AI_Analyst` and `DEV/token-dashboard`.** Both had moved into `~/DEV/_ARCHIVE/`,
  which is now itself in the manifest, so removing the stale entries preserved coverage.
  `DEV/DexaProject` was deliberately left declared-but-absent — it lives on Google Drive.
- **Sorted `paths[]` alphabetically.** Produced a large diff (695+/109-), so a Python set-compare
  against `HEAD:scripts/backup-manifest.json` was run to prove 0 lost, 0 changed, 49 added.

## Files created or modified

- `~/.claude/scripts/backup-manifest.json` — 78 → 127 → **125 entries**.
- `~/.claude/projects/-Users-kristinarash-DEV/memory/project_backup-sync-system.md` — appended
  section "Manifest coverage closed + job-count baseline reset (2026-09-09)".
- `~/.claude/global-memory/transcripts/.errors.log` — archived to
  `.errors.log.archived-2026-09-09`, then emptied with `cp /dev/null`.
- `~/.claude/global-memory/handoffs/2026-09-09-backup-manifest-coverage.md` — this file.

## Verification (what actually proves it worked)

- Dry run: `OK (0 errors)`, no `manifest-unmanaged` line.
- Full run 18:54–18:59: `backup-state.json` → `status:"OK"`, `errors:[]`, **`okCount:76`**.
- SSD spot-check: `/Volumes/CRASHBOX/AssistantBackup/DEV-nonrepo/_ARCHIVE` = 5.2 GB,
  `.../docs` = 640 K. Both landed.
- All four memory repos pushed; 0 `PUSH FAILED`.
- Final dry run after the 2 removals: `OK (0 errors)`, warning now names only `DexaProject`.

## Things a future session must know

- **The job-count completeness signal changed.** The old rule (9 jobs = SSD absent,
  31 = SSD attached) is superseded. A full run with CRASHBOX attached is now **76 jobs**.
- **`CAPTURE` log lines undercount.** The script only logs a `CAPTURE` line when a repo has
  files git does not carry. 18 log lines with 65 capture jobs running is normal. Read `okCount`.
- **`~/.claude` now tracks session transcripts.** Eric's own commit `8a3d55c` (15:44 today)
  un-ignored `projects/`. The dotclaude repo now carries ~368 MB of `.jsonl`. Pushes still
  succeed (no file over 40 MB) but are slower. This invalidates the older
  "Tier A memory is NOT in git" note in the backup memory file.
- **Writing a large file under `$HOME` with a `cat > file <<EOF` heredoc is blocked by dcg**
  (`core.filesystem:redirect-truncate-root-home`). Use the Write tool. See
  `project_dcg-guard-blocks.md`.

## Next actions, most important first

1. Nothing blocking. Coverage is complete and verified.
2. Optional: decide whether 368 MB of session transcripts belongs in the dotclaude repo
   long-term, or whether it should be size-capped/pruned. It will grow every day.
3. Optional: `printing-press-library` is 1.3 GB inside a repo with `captureWorkingTree:true`.
   If that is gitignored dependencies, it is the biggest nightly runtime lever. Not a problem yet.
4. Still open from earlier work (untouched tonight): the two `Test-Path` calls in
   `daily-backup.ps1` have no watchdog, unlike `Invoke-Rsync`.
