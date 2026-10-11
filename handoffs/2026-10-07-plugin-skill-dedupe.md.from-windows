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

## Later the same evening (supersedes the review trim above)
Eric: "I want to default all the mattpocock skills." Pocock wins every overlap. Now "off" in
`~/.claude/settings.json` skillOverrides: built-in `code-review`; superpowers
`requesting-code-review`, `test-driven-development`, `systematic-debugging`, `brainstorming`,
`writing-skills`, `writing-plans`, `executing-plans`, `subagent-driven-development`,
`finishing-a-development-branch`; `anthropic-skills:skill-creator`, `anthropic-skills:deep-research`.
`mattpocock-skills:code-review` is ON. Owned skills `CreateSkill` and `session-handoff` left on
(never set an owned skill "off"). Commits `b035163`, `a82bf7a`, `f71ac9e`, `8527828`.
Mapping lives in `~/.claude/projects/-Users-kristinarash-DEV/memory/feedback_defer-to-mattpocock-skills.md`.

## Files
- `~/.claude/settings.json`
- `~/.claude/plugins/installed_plugins.json` (written by the `claude plugin` CLI)
- `~/.claude/projects/-Users-kristinarash-DEV/memory/project_skill-bloat-and-promotion.md`

## Next
1. Restart Claude Code on the Mac; confirm `mattpocock-skills:*` skills list at 1.3.1 and the
   12 overridden skills are gone. If built-in `/code-review` still lists, the override does not
   reach built-ins.
2. Run `/setup-matt-pocock-skills` once per repo before using `mattpocock-skills:code-review`.
3. On Windows, after `/dev-sync`: run `claude plugin install mattpocock-skills@mattpocock` if its
   skills are missing, then `claude plugin uninstall mattpocock-skills@claude-plugins-official`.
4. Unresolved hook failures: memsearch-sync (Milvus unreachable) and nightly-digest send failed
   2026-10-06. See `~/.claude/global-memory/transcripts/.errors.log`.
