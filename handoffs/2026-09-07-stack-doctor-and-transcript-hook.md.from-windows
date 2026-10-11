# 2026-09-07 — Stack doctor pass + transcript-capture hook fix

## What this session was

A `/claude-stack-doctor` run that surfaced two issues (`errors-log`,
`memfile-full:MEMORY.md`), then a follow-on fix to the Stop hook that was
refilling the error log. Both are finished and verified.

## Starting state

`stack-check.ps1` exited 1 with:
- `errors-log` — `.errors.log` non-empty (5 `missing transcript_path` lines,
  a compiler-backlog escalation, and the weekly stack-doctor entry)
- `memfile-full:MEMORY.md` — 2472/2500 chars, no headroom

## What was done

### 1. Memory compiler backlog — drained
Three daily logs were never compiled (`2026-09-02`, `2026-09-03`, `2026-09-07`).

Root cause is by design, not a bug: `compile.py` applies
`MAX_LOGS_PER_AUTO_RUN` **only when `--auto` is passed**, and it defers the
*oldest* logs. An unattended run therefore drains the queue slowly. The comment
at `scripts/compile.py:468` records why the cap exists — a 28-log batch once
became a 9.5M-token incident. **Do not raise the cap.** The manual catch-up is
the intended escape hatch:

```bash
cd ~/.claude/claude-memory-compiler && \
  /Users/kristinarash/.local/bin/uv run --directory ~/.claude/claude-memory-compiler \
  python scripts/compile.py       # no --auto → no cap
```

Knowledge base went 231 → 246 articles. Deliberate cost: ~$1.04.

### 2. A stranded flush — recovered
`scripts/session-flush-262b8cae-…-20260903-194011.md` was a flush that died on
09-03. Re-ran it by hand; result `saved to daily log (1816 chars)` and the
context file was deleted, which is the success signal.

Worth knowing: **the recovered content lands in *today's* daily log, not the
log for the date the session happened.** `daily/2026-09-03.md` is still a
215-byte stub. Nothing was lost, but do not expect back-dating.

### 3. `MEMORY.md` — consolidated 2472 → 2237 chars
- RTP CLA course detail moved to a new Tier A file (below).
- The "Open PRs" line was stale. Verified with `gh search prs --author=@me`:
  printing-press-library #1667/#1668, SpeedProfiling #9, KeystoneOS #17,
  ForcePlate_DecisionSystem #2 and cmj-traffic-light #1 are **all merged**.
  The only open PRs are `AgentAssist #1` (draft) and `CFB_Analytics_Lab #1`.

### 4. The Stop hook — patched at source
`transcript-capture.js` logged an error whenever `transcript_path` was absent.
Codex `gpt-5.6*` sessions never supply one, so every such session appended a
line to `.errors.log`, which meant the log was never clean and the weekly
check flagged it forever.

The fix distinguishes two cases that were previously collapsed into one
condition:
- `transcript_path` **null/absent** → nothing to capture → return quietly.
- `transcript_path` **supplied but not on disk** → real breakage → still logged,
  now with the message `transcript_path does not exist`.

All 5 archived occurrences were the null case; zero were a broken path. The
new message string doubles as a regression tell — if the *old* wording
(`missing transcript_path`) reappears, a copy of the file was reverted.

**There are TWO copies of this hook and both had to be patched:**

| Path | Registered in | In git? |
|---|---|---|
| `~/.claude/hooks/transcript-capture.js` | `~/.claude/settings.json:319` | yes (dotclaude) |
| `~/.codex/hooks/transcript-capture.js` | `~/.codex/hooks.json:68` | **no** — `~/.codex` is not a repo |

The Codex copy is the one that was actually producing the failures. Patching
only the Claude copy would have fixed nothing while appearing to succeed.
`~/.codex` is covered by the daily rsync backup (`backup-manifest.json`), so it
is backed up but not version controlled.

Tested on both copies, three input shapes each: null path → silent; supplied
bad path → exactly one log line; real transcript → summary appended. Test
residue was removed from `.errors.log` and from
`transcripts/2026-09-07.md`.

## Files created or modified

| Path | Change |
|---|---|
| `~/.claude/hooks/transcript-capture.js` | hook fix — committed, dotclaude `13bd075` |
| `~/.codex/hooks/transcript-capture.js` | same fix — **not in git**, rsync-backed-up only |
| `~/.claude/global-memory/MEMORY.md` | consolidated — committed, global-memory `1e5f61c` |
| `~/.claude/global-memory/transcripts/.errors.log` | cleared — committed |
| `~/.claude/global-memory/transcripts/.errors.log.archived-2026-09-07` | archive of the cleared entries |
| `~/.claude/projects/-Users-kristinarash-DEV/memory/project_rtp-cla-course.md` | new Tier A memory — **gitignored**, rsync-backed-up only |
| `~/.claude/projects/-Users-kristinarash-DEV/memory/MEMORY.md` | index pointer added — gitignored |
| `~/.claude/claude-memory-compiler/daily/2026-09-07.md` | recovered flush content (compiler-owned) |
| `~/.claude/claude-memory-compiler/knowledge/` | +15 compiled articles (compiler-owned) |

## Verified state at sign-off

`stack-check.ps1` → **ALL CLEAR** (exit 0). `.errors.log` 0 bytes.
`MEMORY.md` 2237/2500 (89%). Backup 9h old, all four memory repos synced,
Drive receipt confirmed.

## Next actions

1. **Nothing is blocking.** The next real signal is Monday's weekly
   `com.keystone.stackdoctor` run (10:30). If `errors-log` flags again with
   `missing transcript_path` lines, a hook copy reverted — check the `~/.codex`
   one first, since it is not protected by git.
2. Two unrelated pre-existing edits sit uncommitted in the dotclaude repo:
   `START-HERE.md` and `scripts/backup-manifest.json`. They are not from this
   session and were deliberately left alone. Decide whether they are wanted.
3. `~/.claude/claude-memory-compiler` is parked on branch
   `session-start-progressive-disclosure` with no upstream, plus a stray
   `hooks/session-start.py.bak-2026-08-29`. Pre-existing; not touched.
4. Nothing was pushed. The 09:00 `com.keystone.dailybackup` job pushes
   dotclaude and global-memory. If you want them remote sooner, push by hand.

## Open questions

None. Both issues were closed and re-verified in-session.
