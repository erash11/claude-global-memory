# 2026-10-12 — Windows laptop storage cleanup + migration verification

Machine: Baylor Windows laptop (BU-1979FJ4), hands-off since 2026-10-08.

## What and why
C: was 98% full (12 GB free). Eric asked for cleanup commands, then whether
cleanup would disrupt last week's laptop-to-Mac migration. Verified the
migration first, closed the open HANDOFF.md items, then freed space.

## Migration verification (result: Mac has everything)
- Tier A memory (81 files): all on GitHub; 6 locally different files were
  each committed earlier and later edited on the Mac — nothing lost.
- global-memory handoffs (66) exact; transcripts (152) all on GitHub except today's.
- Session jsonl since handoff (81): 79 exact; this session new; 10-08 handoff
  session missing only its last ~9 min.
- claude-memory-compiler daily/ + knowledge/ are gitignored. All 87 + 232 are
  in `claude.zip` (daily/2026-10-08.md is in `claude-delta-2026-10-08`,
  byte-identical). Eric checked the Mac: 119 daily / 467 knowledge, and
  Windows-only 2026-04-14.md present — import confirmed.
- Mac ran "windows import merge 2026-10-11" in dotclaude and global-memory.

## HANDOFF.md "Remaining" items closed
1. `public-desktop-backup-files.zip` verified good: 4,807,485,616 bytes inside
   (51,202 entries vs 51,176 files — the extra are folder entries).
2. Uploaded to `My Drive/_FROM_WORK_LAPTOP/_FROM_WORK_LAPTOP/` and size-matched:
   catapult-hubpro-local.zip 2052438, public-desktop-backup-files.zip
   2427340112, zotero-research-bridge.zip 81063796.
5. Final transcript push had already landed (1716965 / 9b03cea on 10-08).

## Space freed
- Docker Desktop › Troubleshoot › Clean/Purge data (WSL 2): docker_data.vhdx
  164 GB -> 1.5 GB. Memsearch index on Windows is gone (Mac has its own).
- npm cache cleaned (2.2 GB). C: 12 GB -> 166 GB free.
- Decided: do not uninstall Docker (2-3 GB, likely needs admin, laptop retiring).

## Change made
- `~/.claude/hooks/memsearch-sync.js`: skip on win32 unless
  `MEMSEARCH_ON_WINDOWS=1` (dotclaude 4061678). Mac unchanged. Only copy —
  Codex has no memsearch hook. Tested: exits in ~120 ms, no worker, no lock.

## Next (Eric, by hand, after closing Claude sessions)
1. Recycle Bin: restore screen recordings / RTP-*.mp3 / Photos.zip /
   headshot if wanted, then empty.
2. `& "$HOME\.local\bin\uv.exe" cache clean` (23 GB; was locked by a running uv
   process this session). One uvx MCP server re-downloads on first start.
3. `Remove-Item "$env:TEMP\*" -Recurse -Force -EA SilentlyContinue` (20 GB;
   blocked by a safety guard inside Claude). Contents checked: Docker logs,
   WSL crash dumps, swap vhdx, Claude scratch, PP Recruiting scratch (finals on Drive).

## Gotchas
- Box (251 GB) and OneDrive (153 GB) are almost entirely online-only
  placeholders (0.1 / 6.8 GB on disk); "Local Settings" and "Application Data"
  are junctions that double-count AppData in size scans.
- Global-memory: Mac also writes transcripts/2026-10-12.md; the Windows copy
  is saved as 2026-10-12.windows.md.
