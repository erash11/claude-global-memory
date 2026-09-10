# System Health Findings — 2026-08-14

> **Superseded in part.** These findings were written 2026-08-13 from logs. They were
> re-verified against live state and acted on 2026-08-14 — see
> [`FIX-STATUS-2026-08-14.md`](FIX-STATUS-2026-08-14.md) for what held, what had already
> resolved, and what was wrong. Items 2 and 5 had closed themselves; items 3, 6 and 7 are
> now fixed; items 1 and 4 remain open. Three corrections to the text below are marked
> inline as **[CORRECTION 2026-08-14]**.

Diagnosis from reading the Drive backup logs (both machines), `dotclaude` (RESTORE.md,
MIGRATION-MACOS.md, `scripts/daily-backup.ps1`, `scripts/backup-manifest.json`), and the
backup tree in Google Drive. Ordered by severity. Each item has the evidence and the fix.

## The headline

The Windows→Mac migration (executed 2026-08-05) left **both machines running the nightly
backup against the same GitHub repos and the same Drive folders**. The Windows machine is
running the *Mac-ported* script, which fails daily but reports false success on snapshots.
The two writers are causing repo divergence ping-pong. On top of that, the Mac currently
can't push two repos at all, and the SSD capture layer hasn't run since migration.

Net effect today: **your only fully reliable backup layer is whatever was last pushed to
GitHub successfully — and two repos are stuck.**

---

## 1. Windows machine is still firing daily jobs with the Mac script — RETIRE OR REPAIR

**Evidence:** `Backups` log folder (Windows) `daily-backup-2026-08-13.err.log`: the task
runs `C:\Users\eric_rash\.claude\scripts\daily-backup.ps1`, which since the 2026-08-05
port calls `/usr/bin/rsync` (line 107) and `$HOME/DEV` (line 244). On Windows both fail:
"`/usr/bin/rsync` is not recognized", "Cannot find path `C:\Users\eric_rash\DEV`". The
out.log also reports `global-memory : DIVERGED (behind=27 ahead=0 dirty=2)` and
`MANIFEST 52 declared dir(s) absent from disk`.

**Worse — false receipts:** the same run logs `SNAP ... : OK` for the CloudStorage
targets. `Invoke-Rsync` returns `($LASTEXITCODE -eq 0)`; when rsync fails to *launch*,
`$LASTEXITCODE` is stale from the previous git call, so a copy that moved zero bytes
reports OK. (See fix 6.)

**Fix, on the Windows machine (one-time, ~10 min):**
1. Reconcile its `global-memory` first — it has 2 dirty files that exist nowhere else:
   ```powershell
   cd $env:USERPROFILE\.claude\global-memory
   git status                       # inspect the 2 dirty files
   git add -A; git commit -m "final windows-machine memory sync"
   git pull --rebase origin main    # replays on top of the Mac's 27 commits
   git push origin main
   ```
2. Then make the Mac the single writer — disable the Windows tasks:
   ```powershell
   Get-ScheduledTask | Where-Object {$_.TaskName -like 'KeystoneOS*' -or $_.TaskName -eq 'MorningBriefing'} |
     Disable-ScheduledTask
   ```
   (Disable, don't unregister — RESTORE.md documents how to re-register if you ever
   want them back.) If instead you *want* the Windows box to keep backing up, restore
   `daily-backup.ps1.win-orig` on that machine — but do not leave two writers on the
   same repos; that is what's manufacturing divergence.

## 2. Mac cannot push `global-memory` and `claude-skills` — WORKING MEMORY IS STRANDED

**Evidence:** Mac log 2026-08-13: `REPO global-memory : committed 1 change(s)` then
`PUSH FAILED`; `REPO skills : PUSH FAILED`. Multiple repos failing at push points at
credentials, not content (auth rot is called out as expected in RESTORE.md).

**Fix, on the Mac:**
```bash
gh auth status                        # if expired: gh auth login
cd ~/.claude/global-memory && git push origin main   # read the real error
cd ~/.claude/skills        && git push origin main
```
If the error is non-fast-forward instead of auth (possible, given item 1's Windows
pushes), reconcile: `git pull --rebase origin main && git push`.

## 3. `SecondBrain` diverged on the Mac

**Evidence:** Mac log: `REPO SecondBrain : DIVERGED (behind=2 ahead=0 dirty=2)`. The
Windows machine pushed SecondBrain changes on 8/13 while the Mac had local edits — the
two-writer problem again, biting your notes vault.

**Fix, on the Mac:**
```bash
cd ~/Desktop/SecondBrain
git status                            # inspect the 2 dirty files
git stash && git pull --ff-only origin main && git stash pop   # merge by hand if both sides touched the same notes
git add -A && git commit -m "reconcile post-migration divergence" && git push
```

> **[CORRECTION 2026-08-14]** The `git stash` above does not work for this case. When the
> local files are *untracked* (which they were — `??`, not `M`), plain `git stash` skips
> them, so the stash is empty and `git pull` then aborts with "untracked working tree
> files would be overwritten." Use `git stash -u`, or rename the local files aside first.
>
> Also: both sides held unique content (08-14 had 320 lines only local, 770 only remote —
> two machines each generating their own briefing for the same day), so no
> single-direction resolution was safe. Actually resolved by renaming the local copies to
> `2026-08-DD.mac-local.md`, fast-forwarding, then committing them alongside. Nothing
> discarded.
The script is right to refuse to auto-merge diverged repos. After item 1, this class of
problem stops recurring.

## 4. CRASHBOX SSD not mounted — the gitignored-data layer hasn't run since migration

**Evidence:** every Mac run: `TARGET SSD /Volumes/CRASHBOX/AssistantBackup NOT MOUNTED —
orphan and working-tree capture SKIPPED`. Per RESTORE.md this layer is the *only* backup
for gitignored data (`forceplate.db` 173 MB, Risk_Stratification outputs 1.8 GB, etc.)
and uncommitted working-tree edits.

**Fix:** plug the 500 GB CRASHBOX SSD into the Mac and leave it attached; confirm the
next morning's log shows the orphan/working-tree capture ran and the SSD receipt
verified. Until then, treat gitignored data as unprotected.

> **[CORRECTION 2026-08-14]** Still open, and still the right fix. But note the scope: the
> *Drive* layer is healthy, verified directly against the Drive API (a receipt written
> locally at 07:23 CDT was on Google's servers at 12:23:54Z, matching to the second). A
> `backup-cloud-stale (218h)` alarm from stack-doctor suggested otherwise; that was a bug
> in the check — it watched `RESTORE.md`, which the job *copies* rather than rewrites, so
> its mtime never advanced. Fixed to watch the per-run receipts instead.
>
> So the exposure is narrower than "no offsite backup": only SSD-routed data (gitignored
> files and uncommitted working-tree edits) is unprotected.

## 5. Memory index: "Indexed 0 chunks"

**Evidence:** Mac log: `INDEX path set: 9 paths from memory-index-paths.json` →
`INDEX full set: Indexed 0 chunks.` Nine paths in, zero chunks out means indexing is
broken, not empty. Known post-`pip install` failure mode from RESTORE.md/MIGRATION:
the memsearch **local flush patch must be re-applied after every install**, and Milvus
(localhost:19530) must be running — Apple Silicon support was flagged as unconfirmed,
Docker is the fallback.

**Fix, on the Mac:** check `~/.claude/global-memory/transcripts/.errors.log` (the
documented symptom location), re-apply the flush patch per the compiler repo notes,
confirm Milvus is up, then reindex. The index is rebuildable; nothing is lost.

> **[CORRECTION 2026-08-14]** This resolved on its own — 2026-08-13 07:03 logged
> `Indexed 0 chunks`, 2026-08-14 07:24 logged `Indexed 34 chunks`. The flush patch is
> intact, `memsearch search` works, both venvs are healthy.
>
> **The Milvus prerequisite is wrong.** Port 19530 is closed and Docker isn't installed,
> yet indexing works. Milvus is not in the path — don't set it up chasing this.

## 6. `Invoke-Rsync` can report OK without copying anything

**Evidence:** item 1's false `SNAP … OK` lines. Root cause in
`dotclaude/scripts/daily-backup.ps1` (~line 100): `& /usr/bin/rsync @a` followed by
`return ($LASTEXITCODE -eq 0)` — if the binary can't launch, `$LASTEXITCODE` is never
set by this call.

**Fix (small patch to `Invoke-Rsync`):**
```powershell
$rsync = '/usr/bin/rsync'
if (-not (Test-Path $rsync)) { $Errors.Add('rsync-missing'); return $false }
$global:LASTEXITCODE = 0
& $rsync @a 2>&1 | Select-Object -Last 3 | Add-Content -Path $LogFile
return ($LASTEXITCODE -eq 0)
```
This also makes the script fail loudly instead of silently if it ever runs on a machine
without rsync again. Commit to `dotclaude` so both machines inherit it.

## 7. Housekeeping (low severity)

- **Manifest:** Mac log asks for 2 additions: `COG_S2_Position_Reports`, `S2_Evaluation`
  → add to `backup-manifest.json` (default-deny is doing its job).
- **Windows codex snapshot skip:** Mac log shows `SNAP skip (missing):
  ~/.codex/memories` (fine if Codex on Mac keeps memories elsewhere — verify once) and
  `codex/sessions : FAILED (rsync exit 1)` — rerun manually with output visible to see
  which file it chokes on (likely a permissions or in-use sqlite file; consider adding
  `--exclude` for live lock files).
- **Paths:** the Mac home is `/Users/kristinarash` — any script or plist that assumes
  `eric_rash` on the Mac is wrong. MIGRATION-MACOS.md's launchd template with `YOURNAME`
  must be filled with `kristinarash`.

---

## Order of operations

1. Mac: fix pushes (item 2) — unblocks working memory today.
2. Windows: final memory sync, then disable tasks (item 1) — ends the two-writer war.
3. Mac: reconcile SecondBrain (item 3).
4. Mac: attach CRASHBOX (item 4).
5. Patch `Invoke-Rsync` in dotclaude (item 6).
6. Memory index + manifest additions (items 5, 7) as time allows.

After 1–4, the next morning's `daily-backup` log should end `end: OK (0 errors)` with a
verified receipt — that's the acceptance test.
