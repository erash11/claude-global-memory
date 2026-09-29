# Mac sync and hook-error cleanup — 2026-09-29

Machine: Mac. Harness: Claude Code.

## What was done and why

Morning `/dev-sync`, then Eric asked how to fix the HOOK FAILURE lines shown at
session start, then whether the database pulls were current, then `/backup` and
`/closeout`.

1. **dev-sync.** dotclaude pulled 3 commits; global-memory pulled 3 (the Windows
   Force Plate Practitioner handoff). `transcripts/2026-09-28.md` conflicted
   (add/add); both sides kept by deleting only the marker lines. Memory mirror:
   15 projects paired, 1 file replaced (memsearch-hook-timeout-cap, Mac newer).
   143 DEV repos checked, 27 active, 116 dormant and clean. `Linda_Projects` on
   GitHub is the local `Linda Projects` folder, not a missing clone.
2. **vald-pull 9/28 failure = Mac asleep.** `.err` shows
   `NameResolutionError ... auth.prd.vald.com`; `pmset -g log` shows maintenance
   sleep across the 16:50-19:02 window. Not a code bug. Re-ran with
   `launchctl kickstart gui/$(id -u)/com.keystone.valdpull`: OK, 1 attempt.
3. **perch-pull 9/26-9/27 failures** had already self-healed; 9/28 run OK.
4. **manifest-unmanaged** fixed: added `DEV/AI_Analyst`, `DEV/Flint`,
   `DEV/RunningTheRoom` to `~/.claude/scripts/backup-manifest.json`
   (destinations `ssd`,`github`; `class` is inert). File is written with
   `json.dumps(indent=1)` to keep its original format (indent=2 rewrote 3,400
   lines). Commit `fd10769` in dotclaude. Coverage check: 0 unmanaged.
5. **repo-behind-blocked** (SecondBrain, global-memory, skills) cleared by the sync.
6. **Memory compiler backlog:** compiled 2026-09-16 and 2026-09-19 by hand
   (`uv run python scripts/compile.py --file daily/<date>.md`), about $2.70,
   knowledge base 301 -> 309 articles. `daily/2026-09-27.md` fails to compile:
   it holds only the 9/27 FLUSH_ERROR line (session limit), no session content.
   It will quarantine after max attempts. Nothing lost; Flint day 2 is in
   `Flint/docs/STATUS.md` and its handoff.
7. **Database pulls** all current to 9/28: GPS (10:04 run imported the 9/28
   practice), VALD, Perch.
8. **Backup** run by hand 11:18 with CRASHBOX mounted. The Mac slept 11:31-11:37
   during the memsearch INDEX step, which made it slow.

## Files modified

- `~/.claude/scripts/backup-manifest.json` (+3 entries)
- `~/.claude/scripts/backup-manifest.json.bak-2026-09-29` (pre-change copy)
- `~/.claude/global-memory/transcripts/2026-09-28.md` (merge)
- `~/DEV/Flint/docs/STATUS.md` (stale "merge the PR" lines marked done)
- this handoff

## Next

1. Pick the day's work: Flint (Supertraining Ch4) was the pending choice.
2. If a Mac launchd job fails with "Failed to resolve" or a DNS error, it slept.
   Kickstart it; do not debug code.
3. Windows handoff item still open: Flint import of the Force Plate Practitioner
   course, only if wanted.
