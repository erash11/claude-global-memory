# 2026-08-07 — Claude Code doctor cleanup + memory-compiler backlog

## What was worked on and why

Ran a full Claude Code health check on the new Mac. The machine was migrated from
Windows (`C:\Users\eric_rash`) recently, and most findings trace back to that migration.
Then cleared a 54-log memory-compiler backlog and fixed two failed repo pushes.

## Decisions made (and the reasoning that would otherwise be lost)

**1. Skill cleanup was scoped by evidence tier, not by a flat "unused" rule.**
133 personal skills live in `~/.claude/skills`; only 31 have ever been invoked.
The naive read ("102 unused") was wrong to act on wholesale, because:
- Transcripts on disk only go back to **2026-05-21**, but daily logs go back to
  **2026-04-14** — a ~5-week blind spot where a skill could have been used.
- Usage was judged across BOTH machines (609 Windows-era transcripts + 62 Mac).
  30 of the 31 "used" verdicts come from Windows activity; only 2 registered on the
  Mac. Judging on Mac data alone would have flagged 131 of 133 as unused — nonsense.

So the 102 were tiered:
- **A (54)** — no invocation in 671 transcripts AND no mention in 135 log/memory files → turned off.
- **D (18)** — duplicate a `mattpocock-skills:` plugin skill that IS used → turned off; plugin copy remains.
- **B (30)** — never invoked but *mentioned* in Apr–May logs (`graphify`, `Agents`, `research`,
  `pp-zotero-research-library`, …) → **deliberately kept**. These sit in the blind spot.

**2. `pluginUsage` counters are untrustworthy on this machine.** They were reseeded at
migration. `playwright` reads 0 with 140 recorded MCP calls; `mattpocock-skills` reads 0
with 25 dispatches. Transcripts are the authority. Do not judge a plugin by its counter here.

**3. cwd is the home directory**, so `.claude/settings.json` IS `~/.claude/settings.json`.
Every "project-scope" edit on this box is global. This is why no permission rules were
added — a global `permissions.allow` would let one repo's steered denials pre-approve
commands everywhere.

**4. Compiler backlog was cleared by chaining runs, not by raising the guardrail.**
`MAX_TOKENS_PER_RUN = 600_000` in `scripts/guardrails.py` deliberately stops each run.
Re-running is the documented remedy; `state.json` makes it resumable. 7 runs, $34.53.

## Files created or modified

**Modified:**
- `~/.claude/settings.json` — added `skillOverrides` (72 entries = "off"); set 12 plugins
  to `false` in `enabledPlugins`. Merged via `jq -s '.[0] * .[1]'`; 126 allow rules,
  6 hook events, `env` block and `defaultMode: auto` all preserved.
- `~/.claude/settings.local.json` — repaired 2 impeccable hooks. Were PowerShell syntax
  pointing at `C:/Users/eric_rash/...` (dead since migration). Now POSIX + `$HOME`,
  `"shell": "powershell"` key dropped.
- `~/.claude/CLAUDE.md` — Tier A memory pointer pointed at
  `~/.claude/projects/C--Users-eric-rash/memory/MEMORY.md` (Windows key). Now uses `<slug>`.
- `~/.claude/global-memory/MEMORY.md` — added Mac-migration thread; removed the
  Python/WinGet line (stale on macOS, and duplicated by CLAUDE.md).

**Created:**
- `~/.claude/global-memory/.gitignore` — untracks `transcripts/.memsearch-index.lock`
  and `.memsearch-index.log`. Both were rewritten every index run and churned every
  backup commit. `.errors.log` deliberately still tracked.
- `~/.claude/global-memory/transcripts/.errors-archive-2026-08-07.log` — the 3 resolved
  entries; live `.errors.log` now empty.
- `~/.claude/doctor-backup-20260807-135924/` — pre-change copies of `settings.json`,
  `settings.local.json`, `CLAUDE.md`. Full revert = `cp` these back.

**Commits pushed:**
- `claude-global-memory` → `04bf01b`, then `a0e58c9` (transcript + .gitignore)
- `claude-skills` → `459c9ba`

## Next actions, most important first

1. **Fix the `.Codex` path bug in `~/.agents/skills`** (see below). 29 files broken.
2. **Restart Claude Code**, then `/context` — the skill/plugin changes load at session
   start and are NOT active in the session that made them. Verify the skill listing is
   no longer truncated.
3. Review and commit the 79 uncommitted files in `~/.agents/skills` (migration work,
   not authored by this session).
4. If any Tier B skill turns out to be needed, delete its name from `skillOverrides`
   in `~/.claude/settings.json`. Re-enabling a plugin = flip to `true`.

## Mid-flight / open questions

**The `.Codex` bug.** A Windows→Mac path rewrite across `~/.agents/skills` replaced
`C:\Users\eric_rash\.claude\skills\_shared\config.json` with
`/Users/kristinarash/.Codex/skills/_shared/config.json`. That path does not exist —
the config lives at `~/.claude/skills/_shared/config.json` and
`~/.agents/skills/_shared/config.json`. 29 `SKILL.md` files affected. Git history
confirms the original said `.claude`, so the intended target is unambiguous.

Not fixed here on purpose: those 29 files sit inside 79 files of uncommitted migration
work that this session did not author, and mixing edits in would have made that diff
unreviewable. Suggested fix, to run after reviewing the existing diff:

    cd ~/.agents/skills && grep -rl '\.Codex/skills' --include='SKILL.md' . \
      | xargs sed -i '' 's#\.Codex/skills#.claude/skills#g'

Note macOS is case-insensitive, so `~/.Codex` and `~/.codex` resolve to the same real
directory — which is why this failed silently rather than erroring loudly.

**Ambiguity left unresolved:** 4 bare `code-review` dispatches on 2026-07-18 could be
the symlinked personal skill or a built-in. It was kept rather than guessed at.
