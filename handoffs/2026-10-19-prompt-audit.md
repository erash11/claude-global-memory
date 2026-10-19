# 2026-10-19 — Prompt audit of ~/.claude (Windows)

## What and why
Ran `/claude-api prompt-audit` over the user-level Claude Code setup (CLAUDE.md, AGENTS.md,
machine.md, skills/CLAUDE.md, 38 live skills, 4 agents), checked against claude-opus-5-5. The goal
was to find instructions written for older models, plus files that contradict each other or the repo.

## Result
- Group 1 (dated prompt text) was nearly clean: no thinking scaffolds, no retired model names, no
  update suppressors. Only one passage shouted without a reason (graphify).
- One real error: `memory-write` described slugs as "/ and . become -", which contradicts AGENTS.md
  and the actual slug folders (every non-alphanumeric character becomes "-").
- Full report: `~/.claude/audits/2026-10-19-prompt-audit.md`.

## Changes (claude-skills `6213750`, pushed)
- `~/.claude/skills/memory-write/SKILL.md` — slug rule matches AGENTS.md.
- `~/.claude/skills/graphify/SKILL.md` — Agent-tool line stated plainly with its reason.
- `~/.claude/skills/CLAUDE.md` — CreateSkill deletion note removed.
- Views re-synced with `sync-to-codex.ps1` (44 entries to `~/.agents/skills` and `~/.codex/skills`).

## Other state changes
- `~/.claude` (dotclaude) was 55 commits behind and could not fast-forward. Stashed `settings.json`,
  restored 209 transcript files removed by Claude Code's auto-cleanup (all in commit `d16bf58`),
  pulled, then popped the stash. Settings merged cleanly: Mac's `opus[1m]` default, modelSettings and
  session-autopush hook, plus the local plugin toggles (playwright, commit-commands, github,
  claude-mem-cowork). Live `projects/` transcripts left uncommitted, per the 2026-10-16 STATUS rule.

## Open (decisions for Eric)
- G-2: graphify requires subagent fan-out; USER.md says few subagents unless asked. Is `/graphify` an exception?
- G-3: impeccable and graphify are upstream skills installed as real folders; skills/CLAUDE.md says vendored skills are symlinks. Symlink them, or list them as exceptions?
- G-4: MEMORY.md says the Windows laptop has no automation since 10/8, but claude-stack-doctor lists `\Eric\memsearch-drain-weekly` as active. Which is current?
- The GitHub plugin is enabled but its MCP server returned 401 this session (token rejected).

## Next
1. On the Mac: `git -C ~/.claude/skills pull`, then `bash ~/.claude/skills/sync-to-codex.sh`.
