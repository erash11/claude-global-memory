# 2026-10-11 — /doctor cleanup and dcg fixes (Mac)

## What and why
Ran `/doctor` on the Claude Code setup, then fixed dcg (the Bash command guard hook)
blocking routine work and its duplicate hook that kept coming back.

## Decisions
- **dcg: allowlist the noisy rules, keep the hard stops.** Six rules made ~75% of blocks in
  30 days and are low risk. `rm-rf-*`, `branch-force-delete`, `checkout-discard`,
  `restore-worktree` stay on. Turning dcg off fully was rejected.
- A Claude Code `permissions.allow` rule cannot get past dcg: it is a hook, and hook blocks win.
- **Duplicate hook root cause:** dcg `self_heal_hook` (default true) re-adds the
  absolute-path `/Users/kristinarash/.local/bin/dcg` PreToolUse entry on every run. That is
  why commits f17531c / 7387e7e "removed" it and it came back. Set to false. Kept the guarded
  `if [ -x "$HOME/.local/bin/dcg" ]` entry (works on both machines).
- /doctor: owned skills go `name-only`, never `off` (per skill-bloat memory). Connectors
  disabled only for the ~/DEV project.

## Files changed
- `~/.config/dcg/config.toml` — `self_heal_hook = false` (Mac only, not in git)
- `~/Library/Application Support/dcg/allowlist.toml` — 6 rules: `core.git:git-alias-semantic-unverified`,
  `core.filesystem:redirect-truncate-root-home`, `core.filesystem:redirect-truncate-dynamic-path`,
  `core.filesystem:mv-sensitive-source-root-home`, `core.filesystem:mv-dynamic-path`,
  `heredoc.posix:pipeline-consumer` (Mac only, not in git)
- `~/.claude/settings.json` — removed hardcoded dcg hook; `skillOverrides.articulation-skill = "name-only"`
  (committed by the 21:00 auto backup, `ff6a02b`)
- `~/.claude.json` — `projects["/Users/kristinarash/DEV"].disabledMcpServers` += claude.ai Claude Docs,
  HyperFrames by HeyGen, Wispr Flow, Box
- `~/.agents/skills/persistent-localhost/SKILL.md` — description wrapped in `>-` (YAML was broken)
- `~/.claude/skills/design-taste-frontend-v1` — untracked symlink removed (target kept in `~/.agents/skills/`)
- `~/.claude/projects/-Users-kristinarash-DEV/memory/project_dcg-guard-blocks.md` — allowlist + self-heal notes
- `~/.claude/docs/STATUS.md` — today's entry

## Next
1. `git -C ~/.claude stash drop` (stash@{0} is redundant; grep check printed 1).
2. On Windows: `dcg config | grep -i self-heal`; if true and the duplicate appears, set it false there too.
   The allowlist and self-heal change are Mac-only; the Windows Tier A copy of the dcg note was not changed.

## Undo
- dcg rule: `dcg allowlist remove <rule>`
- connector: `/mcp enable <name>` in ~/DEV
- symlink: `ln -s ../../.agents/skills/design-taste-frontend-v1 ~/.claude/skills/design-taste-frontend-v1`
