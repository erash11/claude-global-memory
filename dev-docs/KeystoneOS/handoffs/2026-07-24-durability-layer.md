# Handoff — Durability layer complete (2026-07-23 → 07-24)

For any harness resuming this thread. Full detail: memory `backup-coverage-2026-07`, decision log entry 2026-07-23, and `~\.claude\RESTORE.md`.

## What happened

Full-system audit (7/23) found healthy capture but broken durability. Fixed in two phases, both live and verified:

- **Phase 1**: every knowledge store now has a private GitHub remote under erash11 — SecondBrain, `dotclaude` (~\.claude config), `claude-skills`, `claude-global-memory`, morning-briefing, ZoteroInjestion; claude-memory-compiler forked (origin=erash11, upstream=coleam00).
- **Phase 2**: scheduled task `KeystoneOS-DailyBackup` (daily 06:15) runs `~\.claude\scripts\daily-backup.ps1` — auto-commits+pushes the 4 memory repos, robocopy-snapshots personal context (Claude transcripts, Codex, Gemini) → **personal Google Drive** `G:\My Drive\Backups\Machine`, and non-repo DEV folders → Baylor OneDrive `Backups\DEV-NonRepo`. Personal OneDrive is NOT signed in on this machine — dead folder, never target it.
- **Verification**: stack doctor (`claude-skills` repo) gained `backup-*` codes including a Drive-API cloud heartbeat via the gws CLI (checks RESTORE.md's cloud modifiedTime). gws re-authed 7/24 with **full drive read/write** + calendar.readonly (Eric's request; write round-trip verified).
- **Runbook**: `~\.claude\RESTORE.md` (canonical: github.com/erash11/dotclaude) — human-facing new-machine + Windows→Mac recovery guide, mirrored daily to `G:\My Drive\Backups\RESTORE.md`.

## Key gotchas learned (also in stack-doctor SKILL.md)

- gws v0.22.5: `-s drive` grants NO scopes — use explicit full scope URLs; delete `~\.config\gws\token_cache.json` after re-auth; `--upload` only accepts files under cwd; login is interactive (Eric at machine, via `!`; open the printed URL with Start-Process — terminal copy/paste truncates at line-wrap).
- Milvus (memsearch's vector DB) runs inside WSL2/Docker Desktop (port 19530 via wslrelay). After a machine restart, if Docker Desktop doesn't auto-start, memsearch fails — this mimics the 6/25 misdiagnosed incident. Check Docker first.
- memsearch-sync hook ETIMEDOUT after heavy sessions = indexing backlog exceeding the 45s cap, self-heals; only re-tune if chronic.
- dotclaude uses a whitelist .gitignore — new config files under `~\.claude` must be whitelisted or they silently aren't backed up.

## Open items (most important first)

1. **PR #16 (KeystoneOS, draft)** — decision-log entry + this handoff. Eric merges (one click). Branch: `worktree-phase2-durability`.
2. **Phase 3 (not started)**: Baylor workdrive PDF/Office extraction (biggest knowledge-access gap); memory-system map page in KeystoneOS.
3. Machine restart pending (Eric, 7/24). Post-restart: verify Docker Desktop/Milvus up, `G:` mounted, then run stack doctor.
4. Optional: gws now has Drive write — could replace/augment DriveFS-dependent snapshots with direct API uploads if DriveFS proves flaky.
