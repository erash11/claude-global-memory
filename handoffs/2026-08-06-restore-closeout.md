# Handoff — 2026-08-06 — Machine-restore closeout (zotero/catapult publish + loose ends)

## What was worked on
Final day of the MacBook restore: drove both Printing Press publish PRs to green, closed every restore loose end (repo reconciliation, backup health, SSH, SSD, zotero install).

## State on sign-off
- **PR #1667 (catapult) + PR #1668 (zotero)** on `mvanhorn/printing-press-library`: all 7 CI checks green, 16 Greptile findings fixed on #1668, mergeable_state clean. Waiting solely on maintainer merge — user chose NOT to monitor (monitors stopped). No local impact either way; both CLIs installed and working.
- **Backup**: first full SSD baseline complete, `OK (0 errors)` at 21:25. SSD = 500GB exFAT, volume renamed to **CRASHBOX**; manifest at `~/.claude/scripts/backup-manifest.json` points to `/Volumes/CRASHBOX/AssistantBackup`.
- **All repos reconciled** post-outage: KeystoneOS, morning-briefing, project-triage, CFB_Victory_Model, global-memory, SecondBrain, publish clone. Clean everywhere.
- **SSH key** uploaded to GitHub (`MacBook (restored 2026-08)`), auth verified.
- **Zotero installed**: skill `~/.claude/skills/pp-zotero-research-library/SKILL.md` (updated from stale v0.1; catapult skill also refreshed), MCP server registered user-scope as `zotero` → `~/go/bin/zotero-research-library-pp-mcp`, bundle at `~/printing-press/library/zotero-research-library/zotero-research-library.mcpb`.

## Key decisions + reasoning
- **Git hangs in sandboxed shells were credential prompts, not the GitHub outage.** Fix recorded in Tier A memory `project_zsh-shell-traps.md`: `GIT_TERMINAL_PROMPT=0 git -c credential.helper= -c 'credential.helper=!gh auth git-credential' <cmd>`.
- **Memory-compiler backlog (54 logs)**: one catch-up run compiled 9 logs ($5.22) before its 600k-token budget tripped. Decision: let the nightly hook drain it (2/night, ~a month) rather than ~$25 more of manual runs. `.errors.log` entries about this are expected until drained.
- **Backup script fixes** (`~/.claude/scripts/daily-backup.ps1`): deprecated Baylor OneDrive destination skipped (dehydrated files broke rsync); missing SSD honors manifest `optional:true` as warning not error; Drive receipt read-back retries.
- **PR review traps** recorded in `~/.claude/projects/-Users-kristinarash-DEV/memory/project_printing-press-spec-traps.md`: SKILL verifier needs literal `cmd.AddCommand(newXxxCmd(...))` registration; Zotero `/deleted` returns a category map; tombstones must be applied, not just stored.

## Files touched (beyond the above)
- `~/printing-press/library/zotero-research-library/internal/{cli/sync.go, store/store.go, client/client.go, config/config.go, ...}` — review fixes, mirrored to working tree + PR branch
- `~/printing-press/.runstate/dev-289aa4de/runs/20260806-100315-0ed5c3e3/retro-candidates.md` — retro notes
- `~/.claude/global-memory/MEMORY.md` — active-thread updated

## Next actions
1. Nothing urgent. If maintainer merges the PRs, no action needed (library bots handle post-merge).
2. Compiler backlog drains automatically nightly; optional manual catch-up: `cd ~/.claude/claude-memory-compiler && uv run python scripts/compile.py`.
3. Parked by user (do not resume unprompted): GMAIL_APP_PASSWORD, Milvus, skill-tax.
