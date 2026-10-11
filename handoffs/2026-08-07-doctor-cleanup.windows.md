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

1. **Get the 73 unversioned skill files into version control** — the one real remaining
   exposure. See "The `~/.agents/skills` structure" below. Needs a design decision;
   nothing else is blocking.
2. **Restart Claude Code**, then `/context` — the skill/plugin changes load at session
   start and are NOT active in the session that made them. Verify the skill listing is
   no longer truncated.
3. If any Tier B skill turns out to be needed, delete its name from `skillOverrides`
   in `~/.claude/settings.json`. Re-enabling a plugin = flip to `true`.

## Mid-flight / open questions

**The `.Codex` bug — FIXED 2026-08-07. The underlying divergence is NOT.**

A Windows→Mac path rewrite across `~/.agents/skills` replaced the `.claude` path
segment with `.Codex` — **235 occurrences across 73 `.md` files**, not the 29 first
counted (that count only caught the `.Codex/skills` shape). Other shapes affected:
`.Codex/LIFEOS/...`, `.Codex/global-memory/MEMORY.md`,
`.Codex/projects/<slug>/memory/`, and `~\.Codex\scripts\daily-backup.ps1`.

Ground truth came from `origin/main`, which **already had correct macOS paths** — zero
`.Codex`, zero Windows `C:\` paths. Every `.Codex` shape maps to `.claude` there, and
all rewritten targets exist on disk (`~/.claude/LIFEOS`,
`~/.claude/skills/_shared/config.json`, `~/.claude/scripts/daily-backup.ps1`, …).

Fix applied: `LC_ALL=C sed -i '' 's#\.Codex#.claude#g'` over the 73 files.
Case-sensitive on purpose — 13 legitimate lowercase `~/.codex` references (real Codex
CLI paths in `impeccable/`, `watch/`, `claude-stack-doctor/`) were left untouched,
verified by diffing per-file counts before and after.

Result: 235 → 0. Files differing from `origin/main` dropped 45 → 27, meaning 18
converged exactly with upstream. None of the remaining 27 contain `.Codex` — they
differ because the checkout is stale. Zero `.Codex` remains reachable through the 21
symlinks in `~/.claude/skills` that Claude Code actually loads.

Backup taken first:
`~/.claude/doctor-backup-20260807-135924/agents-skills-before-codex-fix.tar.gz`

Note macOS is case-insensitive, so `~/.Codex` and `~/.codex` resolve to the same real
directory — which is why this failed silently rather than erroring loudly.

## The `~/.agents/skills` structure — CORRECTED 2026-08-08

Three claims in the 8/07 version of this handoff were **wrong**. Superseded:

- ~~"`~/.agents/skills` is 5 commits behind, missing 933 files"~~ — false. Both
  checkouts sat at `459c9ba` with an **identical 1,203-file tracked list**. Nothing
  was behind, and there was nothing to reconcile.
- ~~"the committed symlinks are self-referential garbage"~~ — false. The blob target
  `../../.agents/skills/<name>` is **correct** when checked out at `~/.claude/skills`
  (→ `~/.agents/skills/<name>`). It is a self-loop **only** at `~/.agents/skills`.
  The repo assumes one checkout path; `~/.agents/skills` was the wrong one.
- ~~"`daily-backup` auto-commits `~/.agents/skills`"~~ — false. `daily-backup.ps1`
  lines 199–201 sync `~/.claude/global-memory`, `~/.claude`, `~/.claude/skills` only.

**What actually happened on 8/07.** `git reset --hard origin/main` on
`~/.agents/skills` destroyed 73 of 76 local files. Recovered in full from
`agents-skills-before-reset.tar.gz`.

**Root cause — and it is NOT `core.symlinks`.** The **content** of the 21 mattpocock
skills is tracked in **no git repo at all**: `git ls-tree -r origin/main` returns 0
files beneath those paths; only the symlink blobs are tracked. The 73 files existed
solely on disk plus the tarballs. `core.symlinks=false` only changed what the wreckage
looked like (29-byte text files); with it `true`, the reset would have written real
self-looping symlinks over the same directories and destroyed the same 73 files.
Verified both ways with throwaway clones.

**Fixes applied 2026-08-08:**
- **A** — `~/.agents/skills/.git` moved to
  `~/.claude/doctor-backup-20260807-135924/agents-skills-dotgit` (5.9M, moved not
  deleted). That path is now a **plain content directory**: no `checkout`/`reset`/
  `stash` can ever clobber it again. All 1,257 files preserved.
- **B** — `git config core.symlinks true` on `~/.claude/skills`, the canonical
  checkout. It had inherited `false` from Windows; a fresh clone there materialized
  all 21 symlinks as 29-byte text files, which would have broken every mattpocock
  skill from the *canonical* side. Tree stayed clean through the flip.

Verified after: 21/21 symlinks resolve, 154 `SKILL.md` reachable, 0 `.Codex`,
`~/.claude/skills` clean at `459c9ba`.

**Still open (the only real exposure):** those 73 files remain unversioned. Fixing it
forks three ways — a new repo; commit the content at a non-colliding path in
`claude-skills` and repoint the symlinks; or drop the symlink indirection entirely and
collapse to a single checkout. Deferred pending a decision.

**Ambiguity left unresolved:** 4 bare `code-review` dispatches on 2026-07-18 could be
the symlinked personal skill or a built-in. It was kept rather than guessed at.
