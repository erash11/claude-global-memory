# 2026-10-08 (Mac): Cloudroom install, global-memory backup fix

## What and why
1. Installed Cloudroom (desktop app that runs Claude Code / Codex locally or in cloud sandboxes), per https://www.cloudroom.dev/setup.md, installer `gui-v96-beta/Cloudroom-v96-arm64.dmg`.
2. Fixed the `daily-backup` error `repo-behind-blocked:global-memory` (2026-10-08 05:30 UTC).

## Decisions
- Cloudroom: the setup's `rm -rf /Applications/Cloudroom.app` step was blocked by dcg; skipped it because the app was not installed yet. App is notarized (Developer ID: David Ondrejek, 4AJ9HF33Z5). Eric finished the in-app setup; `~/.local/bin/room-cli status --json` answers (server `http://127.0.0.1:39886`, data dir `~/.gui-cloudroom`).
- Backup fix: the Mac had uncommitted transcript edits while Windows had pushed 4 commits touching the same files. Committed Mac edits, merged origin. Conflicts: `transcripts/2026-10-07.md` kept both machines' sections (Mac first); `transcripts/.memsearch-last-run` kept the newer Mac stamp.
- Closeout: new `~/.claude/projects/*/*.jsonl` session files NOT committed tonight — keyword scan hit health-data terms in several (precedent 10-07: TOS session held back). Needs a review before push.
- Cloudroom dropped a `room-cli` skill into `~/.claude/skills/room-cli/`. Not committed: it would sync to the Windows laptop, which has no Cloudroom, and the skill-bloat rule wants new skills to replace old ones.

## Files
- `/Applications/Cloudroom.app` (new)
- `~/.local/bin/room-cli` (created by Cloudroom)
- `~/.gui-cloudroom/` (Cloudroom data)
- `~/.claude/skills/room-cli/` (created by Cloudroom, uncommitted)
- `~/.claude/global-memory/transcripts/2026-10-07.md`, `transcripts/.memsearch-last-run` (merge)

## Next
1. Check `~/.claude/scripts/logs/daily-backup.log` on 10/9 for no `global-memory` error.
2. Decide: keep `room-cli` skill Mac-only (add to `~/.claude/skills/.gitignore`) or commit it.
3. Review the uncommitted `~/.claude/projects/*.jsonl` sessions for health data, then commit.
4. Still-open hook errors: memsearch-sync ETIMEDOUT, nightly-digest 10/6 send fail, gps-pull exit 4 (10/8).
