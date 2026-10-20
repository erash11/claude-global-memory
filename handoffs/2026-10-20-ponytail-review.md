# 2026-10-20 — ponytail plugin review (Windows)

## What and why
Eric asked whether to install https://github.com/dietrichgebert/ponytail (v5.3.2, a
"lazy senior dev" Claude Code plugin). Reviewed the repo: core prompt
`skills/ponytail/SKILL.md` (~3.5 KB), three hooks (SessionStart injects rules plus a
2,000-char codebase map, SubagentStart, UserPromptSubmit), a "band" cost tracker that
writes CSV + board.html to `~/.config/ponytail/band/` (webhook off by default, no
outbound calls otherwise).

## Decision
Do NOT install the plugin. Reasons: it replaces nothing (overlaps
mattpocock code-review / codex-review, graphify, explain-usage), adds always-on
SessionStart weight after the 9/12 skill-bloat cut, its benchmarks are the author's own
on FastAPI + React, and its codebase map has no R support. Eric chose to adopt the rule
text instead.

## Files changed
- `~/.claude/CLAUDE.md` — Workflow Expectations: "Writing code: climb the reuse ladder"
  bullet plus 4 sub-bullets (scope, test for risky logic, `shortcut:` comments, closing
  skipped/risk line). dotclaude commit `7f60b0a`, pushed.

## Next
1. After a week of sessions, check whether coding replies end with the skipped/risk
   line and whether the ladder changes diffs; drop the bullet if it is a no-op.

## Mid-flight
None. Clone used for the review lives only in the session scratchpad (temporary).
