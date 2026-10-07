# 2026-10-07 — Plugin and skill dedupe (Mac)

## What and why
Eric could not update mattpocock-skills from 1.2 to 1.3. Cause: two installs. The enabled one came
from `claude-plugins-official` (pins a commit, lagged at 1.2.3); the 1.3.1 copy from Matt's own
marketplace was installed but disabled.

## Done
- Enabled `mattpocock-skills@mattpocock` (1.3.1); uninstalled `mattpocock-skills@claude-plugins-official`.
- Removed 6 untracked symlinks in `~/.claude/skills/` (code-review, grilling, handoff, prototype,
  teach, watch) that duplicated plugin skills. Real folders remain in `~/.agents/skills/`.
- Description/body similarity scan of 148 active skills: no other duplicates. The 7 claude.ai synced
  duplicates were already "off" in skillOverrides.
- Trimmed review skills in `~/.claude/settings.json` skillOverrides:
  `mattpocock-skills:code-review` off, `superpowers:requesting-code-review` name-only, removed the
  stale bare `code-review` name-only line. dotclaude commit `b3641cc`.

## Files
- `~/.claude/settings.json`
- `~/.claude/plugins/installed_plugins.json` (written by the `claude plugin` CLI)
- `~/.claude/projects/-Users-kristinarash-DEV/memory/project_skill-bloat-and-promotion.md`

## Next
1. Restart Claude Code on the Mac; confirm `mattpocock-skills:*` skills list at 1.3.1.
2. On Windows, after `/dev-sync`: run `claude plugin install mattpocock-skills@mattpocock` if its
   skills are missing, then `claude plugin uninstall mattpocock-skills@claude-plugins-official`.
3. Unresolved hook failures: memsearch-sync (Milvus unreachable) and nightly-digest send failed
   2026-10-06. See `~/.claude/global-memory/transcripts/.errors.log`.
