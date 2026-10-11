# 2026-10-06 (Mac, morning): sync, backup, stack cleanup

## What happened
- `/startup`: everything already in sync; pushed `graphify-out` nightly output. 40 GitHub repos with no local folder are the 10/03 archived set (all `gh repo archive`d). Board already running on :7474.
- `/backup` (manual): OK, 71 jobs, CRASHBOX mounted. Took 2 h.
- `/doctor-plus`: 3 flags (taste rules in vendored `design-taste-frontend`, context-mode plugin injection, duplicate skills). Eric chose to remove only the duplicate skills.
- `/claude-stack-doctor`: 4 issues fixed, now ALL CLEAR.
- Slow backup diagnosed.

## Decisions and reasoning
- **Duplicate skills:** `anthropic-skills:watch` and `anthropic-skills:last30days` set `"off"` in `~/.claude/settings.json` `skillOverrides`. Plugins `watch@claude-video` and `last30days@last30days-skill` keep them (local wins, same rule as the 10-02 overrides). Local `skills/watch` was already off.
- **recall-coverage:** `~/.codex/memories` does not exist on the Mac; Codex there keeps memories in `~/.codex/memories_1.sqlite`. The Windows audit (2026-09-30) shows the folder exists on Windows with 36 files, so the path stays in `memory-index-paths.json`; `stack-check.ps1` now treats it as an expected absence on the Mac only.
- **Memory caps:** USER.md 1356 -> 1297, MEMORY.md 2467 -> 2307. Cut repeats (machine split, Drive storage) and stale text (command centre, long PM line). No facts dropped. USER.md is at 94%, one write from the 95% flag again.
- **Slow INDEX = Mac asleep, not memsearch.** `pmset -g log`: the Mac idle-slept 13 s after the copies finished (06:09:19, battery, manual run had no caffeinate); INDEX then ran only in dark wakes. Nightly runs show 6 min to 8 h, unrelated to chunk count. Awake INDEX is about 6-30 min. Fix: `/backup` now runs under `caffeinate -i`. Nightly (lid closed at 21:00) left as is: Eric chose option A, it always finishes.

## Files changed
- `~/.claude/settings.json` (dotclaude `49b8464`)
- `~/.claude/projects/-Users-kristinarash-DEV/memory/project_skill-bloat-and-promotion.md`
- `~/.claude/skills/claude-stack-doctor/scripts/stack-check.ps1`
- `~/.claude/skills/backup/SKILL.md`
- `~/.claude/global-memory/USER.md`, `MEMORY.md`
- `~/.claude/global-memory/transcripts/.errors.log` (emptied; copy at `.errors.log.archived-2026-10-06`)

## Next
1. Restart Claude Code; type `/` and confirm `watch` and `last30days` each show once.
2. Windows: `/startup` pulls all of this. The Windows stack check is unaffected by the Mac-only exception.
3. Optional: the backup manifest still lists 36 archived folders (harmless log noise). Remove them from the manifest when convenient.
4. Optional: decide whether the context-mode plugin earns its ~4 KB per-session injection (doctor-plus flag, shift 3).
