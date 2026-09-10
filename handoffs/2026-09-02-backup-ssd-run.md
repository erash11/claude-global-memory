# Handoff — 2026-09-02 — SSD backup run + manifest and push cleanup

## What was being worked on and why

Eric connected the CRASHBOX SSD and asked for the backup to run. The SSD layer only
captures on days the drive happens to be attached, so an attached drive is the trigger
for a manual run.

## What actually happened

A backup was **already running** when the request arrived (started 07:08:54). It was not
the 09:00 launchd job — it was started by
`~/DEV/KeystoneOS/scripts/keystone-reconcile.ps1`, which also invokes
`~/.claude/scripts/daily-backup.ps1`. That run was allowed to finish rather than stacking
a second writer.

- Run 1 `20260902-070855` — SSD receipt verified, but ended `ERROR (5 errors)`.
- Errors fixed (see below), then Run 2 `20260902-074149` — `OK (0 errors)`.

## Decisions made, and the reasoning

1. **Did not stack a second backup on top of the running one.** The whole history of this
   system is two-writer corruption. Waited for the process to exit instead.
2. **Pushed the three failed repos by hand from an interactive shell.** All three were
   `ahead 1` with no divergence, so a plain `git push origin main` was safe and could not
   force anything. A dry-run push from the terminal succeeded while the scheduled run's
   push had failed — that is what identified the scheduled-context credential gap.
3. **Classed `DEV/RTP_Constraints_Course` as `personal` (Eric's call, asked explicitly).**
   Manifest classification routes athlete data and is a documented human decision. The
   folder is a constraints-led return-to-performance course for ATC Joe Smith. It is not
   a git repo, so the entry is `isRepo: false`, destination `["ssd"]` only.
4. **Re-ran the backup after the manifest edit** rather than copying the folder by hand,
   so the capture is produced by the real pipeline and leaves a receipt.
5. **Did not touch memsearch.** The first run logged a Milvus Lite open error; the second
   run indexed 10 chunks and reset the hook timeout-streak counter. Memory explicitly
   warns against a reflexive `uv tool install --force memsearch` — it strips a local flush
   patch. The error did not recur; it is "did not recur", not "fixed".
6. **Did not add a line to `global-memory/MEMORY.md`.** Another session rewrote it earlier
   today (correctly dropping the closed backup thread) and it is already 2,503 chars
   against a 2,500 cap. The durable facts went to Tier A instead.

## Files created or modified

| Path | What changed |
|---|---|
| `~/.claude/scripts/backup-manifest.json` | Added `DEV/RTP_Constraints_Course` (personal, ssd). A separate job had also added `DEV/CFB_Forecast_Archive`; both now committed. 76 entries. |
| `~/.claude/scripts/backup-manifest.json.bak-2026-09-02` | Pre-edit backup. Got committed to dotclaude by the run's `git add -A`. Private repo, harmless. |
| `~/.claude/projects/-Users-kristinarash-DEV/memory/project_backup-sync-system.md` | Rewrote the "Current state" block with the two-runs-per-day finding, the push gap, and the SSD layout. Trimmed the section already marked superseded to stay under the size cap. Net +360 chars. |
| `~/.claude/global-memory/handoffs/2026-09-02-backup-ssd-run.md` | This file. |
| `/Volumes/CRASHBOX/AssistantBackup/DEV-nonrepo/RTP_Constraints_Course/` | New on SSD — 6 files. |
| `/Volumes/CRASHBOX/AssistantBackup/_receipts/run-20260902-070855.txt` | Run 1 receipt. |
| `/Volumes/CRASHBOX/AssistantBackup/_receipts/run-20260902-074149.txt` | Run 2 receipt, the clean one. |

Commits: `2d21c65` (auto backup sync, carried the RTP manifest entry),
`9b0ccdb` (CFB_Forecast_Archive entry, **local only, not pushed**).

## Findings worth keeping

- **Two backup runs happen most days.** `keystone-reconcile.ps1` fires one around
  07:00–07:10; launchd `com.keystone.dailybackup` fires at 09:00. Confirmed both ran on
  08-30, 08-31 and 09-01. So `launchctl print ... runs = 0` does **not** mean no backup
  ran — read `~/.claude/scripts/logs/daily-backup.log`, not launchd.
- **The 09:00 schedule is working.** The receipt gaps on 08-30 / 08-31 / 09-01 are the
  drive being unplugged, not a broken timer.
- **Scheduled runs cannot push to GitHub; terminal runs can.** 32 `PUSH FAILED` lines in
  the log. `daily-backup.ps1:74` pipes `git push` through `Out-Null`, so the reason is
  never recorded. `~/.claude/scripts/logs/daily-backup.err` is stale — last written
  2026-08-06 — and must not be read as current. Cause unproven; most likely no keychain
  or credential-helper access in the launchd + reconcile context.
- **SSD layout:** non-repo DEV dirs land under `DEV-nonrepo/`, not `DEV/`. There is no
  `DEV/` on CRASHBOX. `._`-prefixed files are normal AppleDouble xattr sidecars on exFAT.

## Next actions, most important first

1. **Push dotclaude** — `git -C ~/.claude push origin main` (1 commit ahead, `9b0ccdb`).
   Held back because closeout only auto-pushes KeystoneOS.
2. **Clear the memory-compiler backlog** (7 logs, flagged by the SessionStart hook):
   `uv run --directory ~/.claude/claude-memory-compiler python scripts/compile.py`
3. **Decide on the scheduled-push gap.** Options: log the real error by removing the
   `Out-Null` on `daily-backup.ps1:74`, or accept it and push by hand. Diagnosing it
   needs the error text, which the script currently throws away.
4. Three new Fireflies meeting notes are untracked in `~/SecondBrain/Inbox/meetings/`
   (dated 09-01 and 09-02). Left alone — vault ingestion has its own flow.
5. Still open from earlier sessions: rotate the Fireflies API key (now in Keychain).

## Mid-flight / open questions

- The 09:00 launchd backup will fire again today. Harmless — it will find nothing to do
  beyond a normal capture.
- `~/.claude/global-memory/MEMORY.md` is 2,503 chars against a 2,500 cap. Three chars
  over. Left for a deliberate trim rather than a drive-by edit.
