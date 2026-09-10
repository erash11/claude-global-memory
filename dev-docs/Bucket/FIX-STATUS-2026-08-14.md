# Fix Status — verified against live Mac state, 2026-08-14

Re-verification of [`SYSTEM-HEALTH-FINDINGS.md`](SYSTEM-HEALTH-FINDINGS.md) (diagnosis
written 2026-08-13 from logs) against the actual machine one day later. The findings doc
instructs "verify each item against current state before acting" — this is that pass.

The first pass (below) was read-only. **Fixes were then applied — see the status section
immediately following.** Acceptance test now passes:
`daily-backup end: OK (0 errors)`, exit 0.

## Status after fixes

| # | Item | Diagnosis verdict | Now |
|---|---|---|---|
| 1 | Second writer still firing | OPEN — root cause | **STILL OPEN** — Windows-only, not reachable from this Mac |
| 2 | Can't push `global-memory` / `skills` | RESOLVED | closed, verified via API write perm + a real 08-14 commit on `origin` |
| 3 | `SecondBrain` diverged | OPEN — doc's fix would fail | **FIXED** — reconciled, both sides' content preserved |
| 4 | CRASHBOX SSD not mounted | OPEN | **STILL OPEN** — physical step, needs you |
| 5 | Memory index "0 chunks" | RESOLVED | closed — 34 chunks, flush patch intact |
| 6 | `Invoke-Rsync` false-OK bug | OPEN — unpatched | **FIXED** — patched, committed, pushed |
| 7 | Manifest gap (2 → 5 dirs) | OPEN | **FIXED** — 6 entries added (5 + `Bucket`) |
| 7 | `codex/sessions` snapshot failing | OPEN | **PENDING** — clean in dry runs, but a dry run writes nothing; awaiting the first live-write result |
| — | Morning briefing failing | NEW | **RETIRED** at your request — job disabled, files kept |
| — | `backup-cloud-stale` | NEW | **FIXED** — was a bug in the check, not the backup |
| — | `MEMORY.md` at 100% | NEW | **STILL OPEN** — deliberately left to you |

Two of the original seven had closed themselves before this pass; the nightly had already
gone 5 errors → 3. After the fixes it reports **0**.

Remaining: the Windows writer (item 1), the SSD (item 4), and `MEMORY.md`.

### Three things to expect, so they don't read as regressions

1. **Tonight's log will probably not say `OK (0 errors)`.** Item 1 is unfixed — the
   Windows box pushes to `SecondBrain` nightly, so `repo-diverged:SecondBrain` returns
   the moment it does. That's the untreated root cause reasserting itself, not these
   fixes failing. It stops recurring only after Prompt 2 runs on Windows.
2. **`.errors.log` is still non-empty, deliberately.** The two resolved morning-briefing
   entries were cleared. The six historical `daily-backup` lines were left as the record
   of what happened. Expect stack-doctor to keep listing `errors-log`, and expect your
   session-start protocol to surface the file — it's history, not a live failure.
3. **`codex/sessions` is not confirmed fixed.** It stopped erroring in dry runs, but
   `-DryRun` passes `rsync -n`, which writes nothing — so a dry run cannot exercise the
   write path that was failing. Confirm against the first non-dry
   `SNAP ... codex/sessions : OK`.

---

## First pass — read-only verification

Everything below is the original determination, written before any fix was applied.
`git fetch` was run in four repos (remote-tracking refs only); no pulls, stashes, rebases,
commits, or pushes at that stage.

### Verdict at a glance

| # | Item | Status |
|---|---|---|
| 1 | Windows still firing daily jobs | **STILL OPEN** — root cause, not actionable from Mac |
| 2 | Mac can't push `global-memory` / `skills` | **RESOLVED** — no action |
| 3 | `SecondBrain` diverged | **STILL OPEN** — and the doc's fix will fail as written |
| 4 | CRASHBOX SSD not mounted | **STILL OPEN** — see correction in item 4 |
| 5 | Memory index "Indexed 0 chunks" | **RESOLVED** — no action |
| 6 | `Invoke-Rsync` false-OK bug | **STILL OPEN** — unpatched |
| 7 | Housekeeping (manifest, codex, paths) | **PARTLY OPEN** — manifest gap grew 2 → 5 |
| — | Three problems not in the original doc | **NEW** — see bottom |

---

## 1. Second writer still active — STILL OPEN (root cause)

`~/Desktop/SecondBrain` has 5 unpulled commits, all `chore: daily backup sync [auto]`,
dated 2026-08-12 → 2026-08-14. The most recent was authored **today at 07:55:28 -0500**.

The Mac's own backup ran at 07:23 and *refused* to push (it correctly declines diverged
repos), so the Mac did not author these. Another machine is still writing to shared repos
daily — exactly the two-writer condition the doc identifies as the root cause.

**The writer is a machine running `daily-backup.ps1` — i.e. the Windows box, not the VPS.**
That commit message format is generated at `~/.claude/scripts/daily-backup.ps1:62`:

```powershell
git commit -m ("chore: daily backup sync {0} [auto]" -f (Get-Date -Format 'yyyy-MM-dd'))
```

`scripts/nightly-push.sh` (the VPS script in this repo) does not produce that string. So
Prompt 2 in `AGENT-FIX-PROMPT.md` is aimed at the right machine.

**Not fixable from here.** Item 1's fix and all of Prompt 2 in `AGENT-FIX-PROMPT.md` run
on the Windows machine. Until that's done, item 3 recurs nightly — reconciling SecondBrain
today buys one day.

## 2. Push failures — RESOLVED, no action

| Repo | Ahead/behind | API write perm | `origin/main` tip |
|---|---|---|---|
| `~/.claude` (dotclaude) | 0 / 0 | — | — |
| `~/.claude/global-memory` | 0 / 0 | `push: true` | **2026-08-14** "Handoff: record Business Office entry-point decision" |
| `~/.claude/skills` | 0 / 0 | `push: true` | 2026-08-13 `chore: daily backup sync [auto]` |

The `global-memory` tip is the load-bearing evidence: a real commit from **today** reached
`origin`, so the push path demonstrably works — this is not a repo that simply has nothing
to push.

(A `git push --dry-run` was also clean, but that proves little on its own: with 0 commits
pending it short-circuits before any auth exchange. Same reason the `.errors.log` evidence
below is corroborating rather than conclusive — a run that commits nothing attempts no
push, so it logs no push error either way.)

Corroborating: `repo-push:global-memory, repo-push:skills` appear in both 2026-08-13 runs
and are **absent** from both 2026-08-14 runs.

The doc's primary hypothesis — expired credentials — was wrong. `gh auth status` is ✓ with
`repo` scope and `credential.helper=osxkeychain`. It was almost certainly the doc's own
secondary branch (non-fast-forward from the other writer), which has since cleared.

`global-memory` has 1 dirty file, `transcripts/2026-08-14.md` — today's live transcript.
Expected, not a fault.

## 3. SecondBrain — STILL OPEN, and the documented fix will fail

Current state is **not** what the doc describes, and the difference matters:

```
behind=5  ahead=0  untracked=4     (doc said behind=2 ahead=0 dirty=2)
```

The 4 local files are **untracked** (`??`), not modified. There are no local commits — so
this is not a true divergence, it's a fast-forward blocked by file collisions.

Three of the four collide with incoming commits. Line-level diff (not byte size — size
alone would not prove this) confirms **both sides hold substantial unique content**:

| File | Lines only in LOCAL | Lines only in REMOTE |
|---|---|---|
| `morning-briefings/2026-08-12.md` | 13 | 1 |
| `morning-briefings/2026-08-13.md` | **316** | **678** |
| `morning-briefings/2026-08-14.md` | **320** | **770** |
| `Inbox/status-reports/` | untracked | not in remote — no collision |

Neither side is a superset. Both machines generated *their own* morning briefing for the
same dates, so these are structurally different documents — the local-only lines include
the `# Morning Briefing — Thu Aug 13` heading itself. There is no "just take the bigger
one" answer.

**The doc's fix is wrong for this state.** It recommends:

```bash
git stash && git pull --ff-only origin main && git stash pop
```

Plain `git stash` does not include untracked files — it needs `-u`. As written, the stash
would be empty, and `git pull` would then abort with "untracked working tree files would
be overwritten." Nothing would be lost, but nothing would be fixed either.

A blind resolution in either direction discards real content: local is larger for 08-12,
remote is larger for 08-13 and 08-14. **This needs a per-file merge decision, not a
command.** Recommend diffing all three before touching anything.

## 4. CRASHBOX SSD — STILL OPEN, and worse than documented

`/Volumes` contains only `Macintosh HD`. Every run still logs `TARGET SSD ... NOT MOUNTED`.
Physical step; nobody can do it remotely.

**Correction — an earlier revision of this doc claimed the Drive layer was down too. It
isn't.** Stack-doctor reported:

```
cloud check: Drive-side copy STALE (218h old) - DriveFS sync may be broken
```

That was a **false alarm in the check itself**, since fixed. The heartbeat queried
`RESTORE.md`'s Drive-side `modifiedTime` on the premise that the backup job rewrites it
every run. It doesn't — it *copies* it (`Copy-Item -Force`, `daily-backup.ps1:411`), so
the copy carries the source's mtime, and `RESTORE.md` hadn't changed since 2026-08-05.

Direct verification via the Drive API: the receipt written locally at 07:23 CDT was on
Google's servers at `2026-08-14T12:23:54Z` — **matching the local mtime to the second**.
DriveFS sync is healthy. The check now queries the newest per-run receipt instead, and
reports `sync path verified`.

**Net: Drive is working; the SSD layer is not.** Gitignored data (`forceplate.db`
~173 MB, Risk_Stratification outputs ~1.8 GB) and uncommitted working-tree edits are
SSD-only by design, so those remain unprotected until CRASHBOX is attached. Everything
routed to Drive or GitHub is covered.

## 5. Memory index — RESOLVED, no action

| Run | Result |
|---|---|
| 2026-08-13 07:03 | `Indexed 0 chunks` |
| 2026-08-14 07:24 | `Indexed 34 chunks` |

Independently confirmed by stack-doctor: `memsearch` present at `~/.local/bin/memsearch`,
`search: OK`, both venvs OK (3.14.6 / 3.12.13), `last-flush.json` 1h old, no `FLUSH_ERROR`
in recent dailies. The flush patch is intact.

**Do not chase Milvus.** The doc names it a prerequisite, but port 19530 is closed and
Docker isn't installed — yet indexing works. That prerequisite is obsolete or was never
right. Acting on it would waste time setting up a service nothing uses.

## 6. `Invoke-Rsync` false-OK bug — STILL OPEN, unpatched

`~/.claude/scripts/daily-backup.ps1` lines 99–109 are unchanged:

```powershell
& /usr/bin/rsync @a 2>&1 | Select-Object -Last 3 | Add-Content -Path $LogFile
return ($LASTEXITCODE -eq 0)
```

Zero occurrences of `rsync-missing` or `$global:LASTEXITCODE = 0` in the file.

Low practical risk *on this Mac* — `/usr/bin/rsync` exists — but this is the bug that
produced the false `SNAP OK` receipts on Windows, and the fix is small and self-contained.
The doc's patch is correct as written.

## 7. Housekeeping — PARTLY OPEN

**Manifest gap grew from 2 to 5.** The doc lists two directories; today's log lists five:

```
CFB_Analytics_Lab, COG_S2_Position_Reports, Football_Data_DEV, S2_Evaluation, Terminal_Fluency
```

All five confirmed present under `~/DEV`. Default-deny is working as designed — these are
simply unclassified.

**`codex/sessions` snapshot — still failing**, `rsync exit 1` on every run through today.
Reproduction attempt: the *exact* nightly invocation, including all six `--exclude`
patterns the `Snapshot` function passes, run by hand → **exit 0, empty stderr**. (Exit
code read directly, not through a pipe — piping to `tail` returns `tail`'s status, which
is how an earlier pass of this check produced a wrong reading.)

So this is **not** a bad exclude pattern and not a permanently locked file. It fails only
under the launchd/nightly context and succeeds interactively — a context difference
(likely TCC/Full Disk Access against the 289 MB source or the CloudStorage mount), which I
could not narrow further without a real run in that context.

**Do item 6 before diagnosing this.** The `rsync exit 1` figure in the log is printed from
`$LASTEXITCODE` inside the very function item 6 says mishandles `$LASTEXITCODE`. Until
that's patched, the reported error code is not trustworthy evidence of what rsync actually
returned — you'd be debugging a number the script may have invented.

**`~/.codex/memories` — verified genuinely absent.** The doc asked to "verify once."
Done: it does not exist on this Mac. The `SNAP skip (missing)` line is correct, not a bug.

**Paths — home is `/Users/kristinarash`**, as the doc expects. ✓

---

## Errors in the docs themselves

These live in a repo you read from other devices, so they're worth fixing at the source.

1. **`AGENT-FIX-PROMPT.md` line 46 sends an agent to `~/Desktop/DEV`.** That directory
   **does not exist** — your projects are at `~/DEV`. An agent following Prompt 1
   verbatim would fail or wander at item 4. (`~/Desktop/SecondBrain` in the same doc *is*
   correct — only the DEV path is wrong.)
2. **Item 5's Milvus prerequisite is obsolete** (see item 5 above).
3. **Item 3's `git stash` fix doesn't handle untracked files** (see item 3 above).
4. **Item 4 understates the exposure** — the Drive layer is down too, not just the SSD.
5. **Both docs say "2 unmanaged dirs"** — it's 5 now.

## Not in the original diagnosis

Surfaced by stack-doctor and the launchd state:

- **`com.keystone.morningbriefing` exits 1.** Cause is in `.errors.log`:
  `morning-briefing: Outlook auth expired - brief sent with 0 email threads` (2026-08-11
  and 2026-08-14). Morning briefs were going out with **zero email context**.
  → **Resolved by retiring the job** (see the status section at the top).
- **False `backup-cloud-stale` alarm** — a bug in stack-doctor, not in the backup.
  See item 4.
- **`MEMORY.md` at 2,492 / 2,500 chars (100%).** No headroom. The next memory write forces
  a consolidation whether or not it's a good moment for one. **Still open** — left alone
  deliberately; consolidating your memory file is your call, not a maintenance task.

---

## Recommended order

Revised from the doc's, based on what's actually still broken and what's cheapest:

| Order | Action | Where | Risk |
|---|---|---|---|
| 1 | Re-auth Outlook (`reauth.sh`) | Mac, interactive | none |
| 2 | Add 5 dirs to `backup-manifest.json` | Mac | none — needs your class call each |
| 3 | Patch `Invoke-Rsync`, commit to dotclaude | Mac | low, self-contained |
| 4 | *Then* diagnose `codex/sessions` — needs 3 done first | Mac | none to diagnose |
| 5 | Investigate DriveFS sync | Mac, interactive | none to diagnose |
| 6 | Reconcile SecondBrain — **merge, don't pick a side** | Mac | **content loss if rushed** |
| 7 | Plug in CRASHBOX SSD | physical | none |
| 8 | Final sync + disable tasks on the **Windows** box | Windows | ends the recurrence |
| 9 | Fix the doc errors above | Bucket repo | none |

Items 1–3 and 5 are independent and safe. Item 4 is deliberately sequenced *after* the
`Invoke-Rsync` patch, because that patch is what makes the error code trustworthy enough
to debug against. Item 6 needs real judgment on three files — roughly 300 local and 700
remote unique lines each for 08-13 and 08-14. Item 8 is the only one that stops item 3
from recurring, and it can't be done from this Mac.

**Acceptance test** (unchanged from the doc): next morning's `daily-backup` log ends
`end: OK (0 errors)` with a verified receipt.
