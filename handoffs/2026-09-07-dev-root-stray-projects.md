# Handoff — 2026-09-07 — Stray projects consolidated into DEV

## What this was

Eric asked for a disk-wide sweep for project folders living outside `~/DEV` that
belong in it. Four were found and moved. Side effects of the moves were repaired
in the same session, and one report was committed and pushed.

## What moved

| From | To | Files |
|---|---|---|
| `~/printing-press` | `~/DEV/CLI_Dev/printing-press` | 3149 (335M) |
| `~/Documents/ChatGPT/PlayerPersonel` | `~/DEV/Football/PlayerPersonel` | 43 |
| `~/Desktop/Claude outputs` | `~/DEV/Football/PFF_Data_Project/outputs/` | 6 |
| `~/Desktop/Life-OS` | `~/DEV/Life-OS` | 13 |

File counts verified against the originals after each move. Old paths are gone.

## Decisions and the reasoning that would otherwise be lost

- **`printing-press` was the whole point.** `DEV/CLI_Dev` had existed empty since
  2026-05-21, and `START-HERE.md` recorded that the Printing Press tree "exists in
  NO backup" — it builds two of the eight `~/go/bin` CLIs
  (`zotero-research-library`, `catapult-openfield-connect`). Moving it into DEV
  brings it under the backup manifest.
- **A symlink was left at `~/printing-press`.** The binary's help text and the
  drive skills reference that path. `strings` on the binary showed the path only
  in help strings, not hardcoded, so a bare `mv` was safe — the symlink is belt
  and braces. Verified with `cli-printing-press library list`: both CLIs still resolve.
- **`Claude outputs` went to `PFF_Data_Project/outputs/`, NOT `PracticeIntensity/`.**
  The report header names `DEV/Football/PFF_Data_Project/data/pff.db` as its source.
  `PracticeIntensity/` turned out to be an abandoned PythonAnywhere scratch dir
  (dotfile copies, a stray `app.py`), not a real project. Confirmed `outputs/` is
  not gitignored via `git check-ignore` before moving files in.
- **`Life-OS` became its own DEV root folder rather than going under `KeystoneOS/`.**
  Depth-2 discovery rule plus the gitignored-subtree trap
  (`KeystoneOS/outputs/**` is ignored) made a root folder the safe choice.
- **Committing the reports was Eric's call, made with the risk stated.** The
  per-snap report contains 22 named athletes with workload values. He was offered
  a hold-the-named-file option and chose to commit all six. Repo is private.

## Side effects found and repaired

- **`DEV/Life-OS` was absent from the backup manifest**, which is *default-deny* —
  the move would have failed the backup health check. Added to
  `~/.claude/scripts/backup-manifest.json` as `class: personal`, `destinations: [ssd]`,
  copying the `DEV/Baylor_Doc_Style` shape. **Classification was chosen, not reviewed
  — reclassify if wrong.**
- **Backup coverage is narrower than first claimed.** `DEV/CLI_Dev` routes to `ssd`
  only, so `printing-press` is protected only on nights CRASHBOX is attached — not
  by GitHub or Drive. Both docs were corrected to say this precisely after an
  initial over-claim of "now inside backup".
- 7 files under `DEV/Life-OS` hardcoded `~/Desktop/Life-OS` (both plists, the bisync
  script, log paths). All repointed. The plists are **not loaded** — `launchctl list`
  showed nothing — so nothing was running and nothing broke.
- `~/.codex/config.toml` pinned `Documents/ChatGPT/PlayerPersonel` as a trusted
  project. Repointed to the new path.

## Files created or modified

Moved (see table above), plus:

- `~/DEV/PLATFORM.md` — `CLI_Dev/` row rewritten; new `Life-OS/` row; connectors
  section now names the local workspace
- `~/DEV/FOOTBALL.md` — `PFF_Data_Project/` row notes `outputs/`; new
  `PlayerPersonel/` row; sub-project count 14 → 15
- `~/.claude/START-HERE.md` — the "NO backup" warning replaced with the resolved
  state and the ssd-only caveat
- `~/.claude/scripts/backup-manifest.json` — `DEV/Life-OS` entry added (78 paths now)
- `~/.codex/config.toml` — trusted-project path updated
- `~/DEV/Life-OS/` — 7 files repointed off the Desktop path
- `~/.claude/projects/-Users-kristinarash-DEV/memory/project_dcg-guard-blocks.md` — new
- `~/.claude/projects/-Users-kristinarash-DEV/memory/MEMORY.md` — index line added

## Git

`DEV/Football/PFF_Data_Project` — commit `c245634`, six files under `outputs/`,
merged fast-forward into `main` and **pushed** to `github.com/erash11/PFF_Data_Project`
(private). Eric's older `7200041` from 2026-08-30 went up with it. Local and remote
are level.

## Gap found while verifying backup coverage (pre-existing, NOT caused by this session)

`daily-backup.ps1:330` walks `Get-ChildItem $DevRoot -Directory` — **directories only**.
Every loose file at the `~/DEV` root is therefore backed up by nothing:

    CLAUDE.md  COMMANDS.md  FOOTBALL.md  PERFORMANCE.md  PERSONAL.md
    PLATFORM.md  PROGRAM.md  RESEARCH.md  CFBD_API_Access_Verification_2026-08-13.md

`~/DEV` is not a git repo either, so there is no second copy anywhere. These are the
router/index files the whole workspace map depends on, and this session wrote the move
records into three of them. Confirmed absent from both `/Volumes/CRASHBOX/AssistantBackup`
and the Drive `Backups/Machine` root.

Fix would be a `DEV/_root-files` manifest entry plus a file-level branch in the script,
or simply `git init` at `~/DEV` for the routers. Not attempted here — changing the backup
script mid-session was out of scope and carries risk.

Manifest coverage otherwise verified clean: zero unmanaged `DEV/` directories after
adding `DEV/Life-OS`.

## Next actions, most important first

1. **Delete the merged branch** `add-per-snap-and-threshold-outputs` in
   `DEV/Football/PFF_Data_Project`. The `dcg` guard blocks `git branch -d` for agents;
   Eric must run it. Fully merged, so it is clutter only.
2. **Version `DEV/Football/PlayerPersonel`.** It has a `.git` with zero commits and no
   remote — nothing is protected by git. It is covered by the manifest under
   `DEV/Football` (ssd + baylor).
3. **Decide `Life-OS` vs KeystoneOS `dailybackup`.** Both rsync to Google Drive. The
   Life-OS plists are unloaded; either load them (paths are now correct) or delete the
   folder. Also note stack-doctor only watches `com.keystone.*`, so `com.eric.*` jobs
   would be unmonitored.
4. **Confirm the manifest classification** of `DEV/Life-OS` (`personal`/`ssd`).
5. **Back up the `~/DEV` root `.md` routers** — see the gap section above. Nothing
   copies them today.
6. `~/.claude/global-memory/MEMORY.md` is 2548 chars, over its 2500 cap — stack-doctor
   flagged `memfile-full` at session start. Needs consolidation.

## Open questions

- `OUT_Baylor_FB_Per_Snap_Demands_PFF.md` says it follows
  `OUT_Baylor_FB_Game_Demands_2024_2025.md`. That file is **nowhere on the disk** —
  a full `find` outside `Library/` returned nothing. Either it was never saved or it
  was lost. Whoever reads the per-snap report will hit this gap.
- `~/Documents/ChatGPT/` is now an empty directory. Left in place; harmless.

## Not stray — checked and deliberately left alone

`~/SecondBrain` (own home and rules), `~/cli-proxy-api` (third-party binary),
`~/OneDrive - Baylor University/PROJECTS/` (Excel and Word only — a working surface,
not code), `~/Desktop/EricWork` (insurance, spending, one Acro spreadsheet — personal),
`~/Documents/{Codex,Claude,Last30Days}` and `~/Downloads/*` (empty or installer junk),
`~/Desktop/SecondBrain.OLD`.
