# Machine Migration and the Backup Path Contract

**Date:** 2026-08-03
**Status:** Phase 1 COMPLETE (verified) · Phase 2 COMPLETE (both exit criteria met) · Phase 3 pending hardware

| Phase | State | Evidence |
|---|---|---|
| 1 — Rescue | Done 2026-08-03 | 22,878/22,879 files SHA-256 matched source; the one mismatch was a file edited mid-run, recopied and verified. `MANIFEST/sha256-manifest.csv` on SSD |
| 2 — Close the hole | Done 2026-08-03 | Canary test: a gitignored `.db` reached the SSD in one cycle. Default-deny test: an unmanifested dir raised `manifest-unmanaged`. Receipts verified on both SSD and Drive |
| 3 — Port to macOS | Pending MacBook | Procedure written: `~/.claude/MIGRATION-MACOS.md`. Not yet executed |
**Extends:** `2026-08-02-durability-contract-and-ownership.md`, `2026-07-27-scheduled-job-durability-design.md`
**Target machine:** MacBook Neo (Apple Silicon, macOS)
**Rescue destination:** `D:\AssistantBackup` — WD easystore, USB, 3,726 GB total / 1,236 GB free

## Why now

Shell commands were flagged by Baylor IT. Access to the machine and to Baylor storage
may be withdrawn with little notice. The goal is that a brand-new personal machine can
reconstitute the entire working system — projects, research, memory, automation — with
nothing lost.

The prompting concern was continuity. The audit found a correctness problem underneath
it that is worse than the continuity problem and would have survived the migration
untouched.

## Evidence

All figures verified on 2026-08-03 against the live machine, not inferred from
configuration.

### What is actually safe

| Surface | State |
|---|---|
| 18 DEV git repos | All have GitHub remotes, **0 unpushed commits** across every one |
| `dotclaude`, `claude-skills`, `claude-global-memory`, `claude-memory-compiler` | Pushed clean |
| `SecondBrain` | Pushed, 2 local commits outstanding |
| `KeystoneOS-DailyBackup` | Ran 2026-08-03 00:35–00:52, exit 0, 0 errors, per-path receipts in log |
| `~/.claude/projects`, `.codex`, `.gemini` → Google Drive | Current as of 2026-08-03 |
| `RESTORE.md` | Exists, thorough, mirrored to GitHub + Google Drive |

A false alarm worth recording: the Google Drive `codex` and `gemini` snapshot folders
carry directory mtimes of 2026-07-23 and 2026-06-24, which reads as stale. The backup
log shows both were snapshotted successfully at 00:37 on 2026-08-03. Robocopy does not
touch the parent directory mtime when no files change. **Folder mtime is not a freshness
signal.** This is the same class of misleading state claim catalogued in the KeystoneOS
verification habits note.

### Finding 1 — the structural hole (critical)

`daily-backup.ps1` selects a backup mechanism by asking whether a directory is a git
repo. Git repos are covered by `git push`; non-repos are covered by robocopy snapshot to
Baylor OneDrive. Nothing covers **gitignored files inside git repos**. Git will not push
them and the snapshot job skips the whole folder because it is a repo.

Measured payload, excluding `node_modules`, `.venv`, `__pycache__`, `.git`, `.next`,
`dist`, `.pytest_cache`:

| Repo | Orphaned | Files |
|---|---|---|
| Risk_Stratification_Engine | 1,819.5 MB | 984 |
| ForcePlate_DecisionSystem | 1,701.9 MB | 131 |
| morning-briefing | 326.1 MB | 6,190 |
| SportScienceResearchRepo | 262.0 MB | 162 |
| CFB_Victory_Model | 57.5 MB | 103 |
| DataBase_GPS_Reporting | 27.7 MB | 128 |
| ValdReport | 21.0 MB | 1 |
| KeystoneOS | 10.2 MB | 1,010 |
| 10 others | < 5 MB combined | 174 |
| **Total** | **4.13 GB** | **8,883** |

`ForcePlate_DecisionSystem` publishes 7 MB to GitHub against 1,709 MB on disk. The
excluded set includes `data/forceplate.db` (173 MB) — the live database the decision
system runs on — ignored by `.gitignore:2: data/*.db`.

**This data has no copy anywhere.** Not GitHub, not OneDrive, not Google Drive. The
report "all repos pushed clean, 0 unpushed" is true and nearly meaningless: it describes
tracked files only.

### Finding 2 — the non-repo set depends on Baylor

32 DEV folders have no git repo. All 32 are snapshotted nightly, **exclusively to Baylor
OneDrive** — 3.05 GB, of which `Football` is 2,966.7 MB. `RESTORE.md` already marks this
row "Survives leaving Baylor? NO." Under the scenario now being planned for, the primary
copy and the only backup are lost in the same event.

Supporting evidence for default-deny: the OneDrive snapshot holds 33 folders against 32
current non-repos. `CFB_Victory_Model`, `project-triage`, and `Website` have since become
git repos and are still being snapshotted as though they were not, while their gitignored
contents are counted nowhere. The set of covered paths has already drifted from the set of
paths that exist, silently, with no error surfaced.

### Finding 3 — GitHub cannot absorb this payload

17 files exceed GitHub's 100 MB hard push limit; 23 more fall in the 50–100 MB warning
band. Largest: `Football/SpeedProfiling/data/data_tagged.rds` (875 MB),
`Football/PFF_Data_Project/data/pff.db` (518 MB). Git LFS was considered and rejected:
volume exceeds the free tier, and frequently-rewritten `.db` files pathologically bloat
LFS history.

### Finding 4 — credentials are correctly excluded and undocumented

Roughly 10 live credential files exist (`.env` across `ForcePlate_DecisionSystem`,
`DataBase_GPS_Reporting`, `PlayerProfiles_FB`, `Football/PFF_Data_Project`,
`reMarkale_extract`, plus `morning-briefing/secrets/gmail_credentials.json` and
`gmail_token.json`). Excluding their values from every backup is correct and stays.
There is no record of **which keys each project requires or where to reissue them**, so a
restored machine yields code that cannot run.

### Finding 5b — uncommitted work in tracked files is covered by nothing

Discovered during Phase 1 execution, after the original findings were written.

The hole in Finding 1 has a mirror image. `DEV-repo-data` rescues *untracked and ignored*
files via `git ls-files --others`. Tracked files are assumed covered by GitHub. But a
tracked file with **uncommitted modifications** is covered by neither: the SSD skips it as
tracked, and GitHub holds only its last committed state.

Measured 2026-08-03: 7 such files across `KeystoneOS` (4), `CFB_Victory_Model` (2), and
`project-triage` (1) — including 77 uncommitted lines in `decisions/log.md`, the
append-only architectural decision record.

Three related but distinct exposures now exist, and the manifest design must address all
three rather than the first alone:

| Git state | Covered by |
|---|---|
| Tracked, committed, pushed | GitHub |
| Untracked or ignored | SSD `DEV-repo-data` |
| **Tracked, modified, uncommitted** | **nothing until 2026-08-03** |

Mitigated in Phase 1 by snapshotting working-tree diffs to `DEV-working-tree/`. Phase 2
must make this continuous: the nightly job captures `git diff` state per repo, or commits
it, rather than trusting "tracked" to mean "safe."

A second-order note: `git stash push -u` followed by `stash pop` renormalizes line endings
on restored untracked files under this repo's CRLF settings. Content is preserved; hashes
are not. Any verification comparing hashes across a stash cycle must normalize line
endings before concluding corruption.

### Finding 5 — the Mac port is small, except where it isn't

Only 3 files hardcode Windows paths: `~/.claude/CLAUDE.md`, `scripts/daily-backup.ps1`,
`scripts/fix-msys-ad-stall.ps1`. `settings.json` and the hooks are already portable —
better than `RESTORE.md` currently claims, and that claim should be corrected.

9 scheduled tasks require launchd equivalents: `KeystoneOS Morning`, `-DailyBackup`,
`-AgySync`, `-StackDoctor`, `-Reconcile`, `-Rituals`, `-Adjudicate`, `-MsysKeepAlive`,
`MorningBriefing`. `-MsysKeepAlive` exists solely to work around the MSYS2/AD spinlock
stall and should be **retired, not ported** — the failure mode does not exist on macOS.

A loose grep flags 37 skills referencing Windows-specific commands. That is an upper
bound including incidental path examples; it requires triage rather than bulk porting.
Known true blockers: `everything-search` (Everything CLI is Windows-only; replace with
`mdfind`), and `claude-stack-doctor`, `closeout`, `project-triage`, `forecast-capture`,
which shell out to PowerShell scripts.

## Decisions

1. **Mirror everything to personal storage, including institutional athlete data.**
   Decided by Eric on 2026-08-03 after the compliance exposure was presented. Recorded
   plainly: this data carries third-party obligations held by Baylor, and mirroring it to
   personal storage is a deliberate, informed choice, not an oversight. It is therefore
   tagged rather than blended, so it stays identifiable and purgeable.

2. **External SSD as the rescue tier; Google Drive for ongoing deltas.** The SSD is
   offline, physically held, unaffected by any account suspension, and has 1,236 GB free
   against a 7.2 GB need. Drive is retained for deltas because it is already mounted,
   trusted, and reachable from the Mac. Whether Drive can additionally absorb a full
   bulk copy is unverified — see Risks; the design does not depend on it either way.

3. **Replace repo-detection with an explicit path manifest.** This is the root-cause fix
   and the reason the migration is sequenced behind it.

## Architecture — the backup path contract

`backup-manifest.json` becomes the single authority on what is backed up and where.
Every path is listed explicitly with a class and destinations.

```json
{
  "path": "DEV/ForcePlate_DecisionSystem",
  "class": "code+data",
  "destinations": ["github", "ssd", "drive"],
  "notes": "data/*.db gitignored; SSD and Drive carry the database"
}
```

Classes: `config`, `code`, `code+data`, `personal`, `institutional`.

Three properties are required:

- **Default-deny.** Any directory under `DEV` or `~/.claude` absent from the manifest
  raises a warning and fails the run's health check. A new project cannot silently go
  uncovered. Under today's design, `Risk_Exposure_Windows` and
  `Transformative_Athlete_Experience` were covered only by luck of not being repos.
- **Coverage is computed, not assumed.** For each git repo the job diffs on-disk files
  against `git ls-files` and routes the difference to SSD and Drive. The hole in
  Finding 1 closes by construction and cannot reopen when a new `.gitignore` rule lands.
- **Receipts, not exit codes.** Per the 2026-08-02 durability contract, each run writes a
  unique sentinel to every destination and reads it back. A run that copies nothing
  cannot report success.

## Phase 1 — Rescue

Time-critical and independent of the MacBook. Justified today by disk-failure risk alone.

1. Copy to `D:\AssistantBackup`, preserving structure and tagging class:
   - 4.13 GB of orphaned in-repo data (Finding 1)
   - 3.05 GB of non-repo folders (Finding 2)
   - `~/.claude/projects`, `~/.codex`, `~/.gemini`
   - Fresh clones of all 18 GitHub repos, so the SSD is self-sufficient
   - `~/.claude` config tree
2. Commit and push `SecondBrain`'s 2 outstanding commits.
3. Give `Program_Context_Meet` a GitHub remote — currently the only repo without one.
4. Verify by file count and SHA-256 manifest. Not by exit code.

**Exit criterion:** every byte Eric owns exists on hardware he physically holds, and
nothing he owns depends solely on Baylor storage or on this machine.

## Phase 2 — Close the hole and inventory the keys

1. Author `backup-manifest.json` covering every DEV folder (18 repos + 32 non-repo) plus
   the `~/.claude` subtrees.
2. Rewrite `daily-backup.ps1` against the manifest: default-deny, computed coverage,
   per-destination receipts.
3. Add SSD as a destination alongside OneDrive and Drive, degrading gracefully with a
   warning when the drive is detached rather than failing the run.
4. Write `CREDENTIALS.md` in `dotclaude`: per project, the **key names** required, the
   service that issues them, and the reissue URL. **Never values.**
5. Correct `RESTORE.md`: the `settings.json` path-rewrite claim is wrong, and the
   DEV-NonRepo row must reflect the SSD and Drive destinations.

**Exit criterion:** a deliberately gitignored test file in a repo appears on the SSD
within one backup cycle, and a manifest-absent directory fails the health check.

## Phase 3 — Port to the MacBook and prove it

1. Base toolchain via Homebrew; Python from the python.org installer — **not** the
   Microsoft Store equivalent or `brew install python` as primary, per the prior
   migration failures recorded in `RESTORE.md`.
2. Restore in RESTORE.md order: `~/.claude` from `dotclaude`, then the satellite repos,
   then AI state from Drive, then DEV from SSD and GitHub.
3. Depath the 3 Windows-bound files; author a macOS `CLAUDE.md` variant with Homebrew
   tool paths replacing the pinned Windows binary paths.
4. Port 8 scheduled tasks to launchd; retire `-MsysKeepAlive`.
5. Triage the 37 flagged skills into: works as-is, needs path edit, needs rewrite,
   Windows-only and retired.
6. Rebuild venvs; reapply the memsearch flush patch — its absence is silent except for
   entries in `global-memory/transcripts/.errors.log`.
7. **Execute RESTORE.md literally on the Mac and record every place it is wrong.** A
   migration guide that has never been run is a hypothesis, not a procedure.

**Exit criterion:** `stack-check` reports ALL CLEAR on the Mac, a morning briefing
generates end-to-end, and `RESTORE.md` has been corrected by an actual restore.

## Out of scope

- `node_modules`, `.venv`, `__pycache__` — rebuilt by package managers
- Milvus / memsearch vector index — rebuilt by reindexing, nothing lost
- `~/.codex/work` — 19+ GB of disposable working clones
- **All credential values** — password manager and re-auth flows, by design
- `D:` CRASHBOX legacy content outside `AssistantBackup` — historical, unmanaged
- Baylor OneDrive `00_Primary_Storage_Drive` — institutional, stays

## Risks and open questions

- **Compliance exposure.** Mirroring athlete health and performance data to personally
  controlled storage is the accepted risk in Decision 1. Class tagging bounds it and
  makes later purge one query.
- **Network visibility.** A 7.2 GB egress may itself draw attention given the flagged
  commands. The SSD path is local and avoids this; it is a further reason to prefer it
  over a Drive bulk upload.
- **Google Drive quota** is unverified against a 7.2 GB delta load. Phase 2 must measure
  before enabling Drive as a bulk destination.
- **`Football` is 2.97 GB of the 3.05 GB non-repo set**, much of it `node_modules` and
  `.rds` exports. Phase 1 should measure its post-exclusion size; the real payload is
  likely far smaller.
- **Apple Silicon** support for Milvus is unconfirmed. Acceptable — the index is
  rebuildable, and a Docker fallback exists.
