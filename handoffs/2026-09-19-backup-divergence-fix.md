# 2026-09-19 — daily-backup false "diverged" errors, and two unbacked DEV repos

Machine: Mac (`~/DEV`). Third session of the day. The two earlier sessions are covered by
`2026-09-19-mac-dev-sync-and-typesafe-setup.md`; this one does not overlap it except that
both touch `scripts/backup-manifest.json`.

## What was being worked on and why

Started as "run the Python smoke test from the TypeSafe project". That passed, which left the
three `daily-backup` errors from the startup banner as the real work: `repo-diverged:global-memory`,
`repo-diverged:dotclaude`, and `manifest-unmanaged:AppliedPerformance-Site|Linda_Projects`.

## Decisions made, with the reasoning

- **The two `repo-diverged` errors were not divergence at all, and the script was wrong to
  call them that.** `daily-backup.ps1` line 52 used to read:

  ```powershell
  if ($behind -gt 0 -and ($ahead -gt 0 -or $dirty -gt 0)) {   # OLD
  ```

  Being *behind* with a dirty tree is not divergence. `dotclaude` and `global-memory` are
  **permanently dirty**, because live session transcripts and `.jsonl` logs are written into
  them while a session runs. So every single day the other machine pushed, the pre-check
  produced a false error and returned before syncing at all. It fired on 09-18 and 09-19.

- **Fix: let git decide instead of guessing.** `DIVERGED` now means behind AND ahead.
  Behind-only attempts `git pull --ff-only` and records an error (`repo-behind-blocked:<name>`)
  only if git itself refuses, logging git's own message so the blocking file is named.

  Verified empirically against throwaway repos, not assumed:
  - behind + dirty, dirty file does **not** overlap the incoming commit → `--ff-only` exits 0,
    fast-forwards, and the uncommitted edit survives.
  - behind + dirty, dirty file **does** overlap → git exits 1 with
    "Your local changes to the following files would be overwritten by merge", and the edit
    also survives. So nothing is ever lost by trying.

  This keeps the original intent of the line ("never merge blindly from automation") while
  removing the false positives.

- **`AppliedPerformance-Site` and `Linda_Projects` classified `institutional`.** Both are
  Baylor work: the Applied Performance department site, and supervision planning for Linda
  Mungai (Applied Performance Specialist). Both are `isRepo: true` with **private** GitHub
  remotes, confirmed with `gh repo view`. That matters for `Linda_Projects`, which holds
  `02_SupervisorPlan_I983_CONFIDENTIAL.md`.
  Destinations `["ssd", "github"]` — **not** `baylor`, which the manifest has deprecated
  (the log says "TARGET baylor deprecated in manifest - snapshots to it SKIPPED").

- **`Linda_Projects` turned out to be a redundant clone, and the `manifest-unmanaged` error
  for it was a symptom, not a real coverage gap.** `~/DEV` holds **two** folders for the one
  GitHub repo `erash11/Linda_Projects`:
  - `~/DEV/Linda Projects` — with a **space**. The original. Already in the manifest all
    along, at line 787. Always backed up.
  - `~/DEV/Linda_Projects` — with an **underscore**. Cloned by this morning's `/dev-sync`,
    which matched local folders by repo name, did not find `Linda_Projects`, and concluded
    the repo was missing locally.

  The two are byte-identical outside `.git` and sit on the same commit `031f96a`. Default-deny
  then flagged the new clone as unmanaged, which is what produced the error. The manifest now
  carries **two entries for one repo**, at lines 787 and 799. Left that way on purpose: while
  the duplicate folder exists on disk, an entry for it is what keeps the health check quiet.
  The clean end state is to delete `~/DEV/Linda_Projects` and remove the line-799 entry —
  that needs Eric, because the folder holds confidential personnel files, so it is not
  something to delete unasked.

  **The general trap: `/dev-sync` matches DEV folders to GitHub repos by name, so a folder
  whose name differs from its repo name looks missing and gets cloned a second time.** Check
  `git remote get-url origin` before believing a repo is absent locally. `AppliedPerformance-Site`
  was checked the same way and has no space-named twin, so its entry is a genuine new one.

- **Inserted the manifest entries, did not re-sort the file.** A full alphabetical sort of the
  `DEV/` block churned 7 unrelated entries, because the file is not globally sorted — some
  `DEV/` entries were appended after the non-`DEV` block. Reverted that and inserted each entry
  at its alphabetical spot inside the existing run instead. Diff is 30 lines.
  `json.dumps(d, indent=1, ensure_ascii=False) + "\n"` round-trips this file byte-identically,
  which is what makes a minimal diff possible — check that before rewriting it.

- **TypeSafe STATUS: merged both machines' records rather than picking one.** A concurrent
  session on this machine had pushed the Windows verification to `TypeSafe_Sandbox` while this
  session was proving the Mac side. Rebase conflicted on `docs/STATUS.md`; resolved by keeping
  both dated bullets.

## Files created or modified

- `/Users/kristinarash/.claude/scripts/daily-backup.ps1` — the line-52 rewrite.
  Backup at `daily-backup.ps1.bak-2026-09-19`.
- `/Users/kristinarash/.claude/scripts/backup-manifest.json` — +2 entries, `generated` → 2026-09-19.
  Backup at `backup-manifest.json.bak-2026-09-19`.
- `/Users/kristinarash/DEV/TypeSafe_Sandbox/docs/STATUS.md` — Mac smoke test passes; restart
  gotcha narrowed.
- `/Users/kristinarash/.claude/global-memory/handoffs/2026-09-19-backup-divergence-fix.md` — this file.

Commits: `bd6b451` (dotclaude), `b7d2d00` (TypeSafe_Sandbox). Both pushed.

## Resolution, later the same day (and a privacy finding)

Eric approved deleting the duplicate. Done in two halves:

- **Manifest entry removed.** `DEV/Linda_Projects` is gone from `backup-manifest.json`;
  138 paths now. Backup at `backup-manifest.json.bak-2026-09-19b`.
- **Folder deletion handed to Eric.** `dcg` blocks recursive force-delete on any home path
  (`core.filesystem:rm-rf-root-home`) and says to have the user run it. Not worked around; a
  guard on destructive actions is not something to route past. Eric runs a recursive force
  delete on `/Users/kristinarash/DEV/Linda_Projects`. Until he does, the backup logs one
  harmless `manifest-unmanaged:Linda_Projects` line.

**The surviving `DEV/Linda Projects` entry was left exactly as it is, on purpose.** Its note,
written 2026-08-19 by stack-doctor, reads: *"the most restrictive routing available: SSD only.
Contains a file marked CONFIDENTIAL (I-983). Deliberately NOT routed to github or baylor.
Eric to confirm classification."* It is `class: personal`, `isRepo: false`, `remote: null`,
`destinations: ["ssd"]`.

**But that intent no longer matches reality, and this predates this session.** On 2026-09-09 the
folder was put under git and pushed to `github.com/erash11/Linda_Projects`, and the pushed commit
`031f96a` contains `02_SupervisorPlan_I983_CONFIDENTIAL.md`, `source/I983_page3.png` and
`source/I983_page5.png`. The repo is **private**, confirmed with `gh repo view`.

So the manifest says "deliberately not on GitHub" while the I-983 material has been on GitHub
since 2026-09-09. The entry's `isRepo: false` / `remote: null` are now factually wrong too.
**Left unchanged deliberately** — correcting them to `isRepo: true` plus a `github` destination
would quietly bless a routing decision the note explicitly reserved for Eric. His call:

- Accept it: set `isRepo: true`, add the remote, keep or add `github`, and rewrite the note so
  it stops claiming something untrue.
- Reject it: purge the I-983 files from the GitHub repo's history and delete the remote, then
  fix `isRepo`/`remote` to match whatever is left.

## Next actions, most important first

1. **Watch tomorrow's 09:0x `daily-backup` run.** Expect no `repo-diverged` line and no manifest
   error. The fix's success path was proven on test repos, but the real job has not yet run a
   day where it is genuinely behind. Log: `~/.claude/scripts/logs/daily-backup.log`.
2. **`INDEX full set: Indexed 0 chunks` on 09-19**, against 91 chunks on 09-18. Not counted as an
   error by the script, so it is silent. Flagged to Eric; not investigated. See Tier A
   `project_memory-compiler-pipeline` — "Indexed 0 chunks" is a known dead-flush tell.
3. **Decide on the duplicate `Linda_Projects` clone** (see above). Recommended: delete
   `~/DEV/Linda_Projects`, keep `~/DEV/Linda Projects`, then remove the line-799 manifest entry.
   Nothing is lost — identical content, same commit, pushed.
4. Nothing is built on top of the TypeSafe API yet on either machine. The API answers; no Baylor
   workflow uses it.

## Anything mid-flight

- Two pre-existing `daily-backup.ps1` bugs found on 09-17 are **still unfixed** and were out of
  scope here: it counts a no-op push (`Everything up-to-date`) as an error, and it writes every
  log line twice.
- `TARGET SSD /Volumes/CRASHBOX` was not mounted on the 09-19 run, so orphan and working-tree
  capture was skipped. Not an error, but the `ssd` destination on the two new manifest entries
  is unexercised until the drive is plugged in.
- Two sessions were writing to `~/.claude` at the same time today. Both pushes landed cleanly and
  nothing was lost, but check `git log` before assuming a change is yours.
