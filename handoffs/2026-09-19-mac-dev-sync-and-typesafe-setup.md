# 2026-09-19 — Mac dev-sync, then TypeSafe key setup on both machines

Machine: Mac (`~/DEV`). Two sessions ran today; this handoff covers both.

## What was being worked on and why

1. `/dev-sync` on the Mac, to reconcile with GitHub after Windows work on 09/17–09/18.
2. Getting the TypeSafe System One API key working, first on Windows, then on the Mac,
   so `TypeSafe_Sandbox/smoke_test.py` passes on both boxes.

## Decisions made, with the reasoning

- **`TypeSafe_Sandbox` was authored on Windows, not the Mac.** An earlier claim in this
  session that it was built on the Mac was wrong. The check that produced it grepped
  `~/.claude/projects` for the originating session id, and matched the *current* session's
  own transcript, because the id had been printed into this session's tool output.
  Discriminate with `grep -rl "<session id>" ~/.claude/projects | grep -v <this job id>`.
- **The key does not sync between machines. Each machine holds its own copy.**
  - Mac: macOS Keychain, service `typesafe-api-key`, exported by `~/.zshenv`.
  - Windows: `~/.claude/typesafe.env`, one line. Auto-gitignored by the dotclaude
    whitelist, because that `.gitignore` starts with `/*`.
- **The key needs its `apikey_` prefix.** The console shows `apikey_<36>_<64>`, 108 chars.
  Dropping the prefix returns a clean `401 authentication_error`. A malformed body returns
  `422` instead, so 401 means the key is wrong and 422 means the request is wrong. That
  split is the fastest way to tell which end is at fault. This cost the first attempt.
- **Claude Code does not need a restart for the Mac Bash tool to see the key.** The Bash
  tool spawns a fresh zsh, which sources `~/.zshenv`. A restart only matters for things
  that inherit Claude Code's own environment, such as plugin and MCP processes.
- **`TypeSafe_Sandbox` classified `personal` in the backup manifest**, matching
  `sleep-scheduler`. Eric should change it to `institutional` if a Baylor workflow adopts it.
- Conflict on `global-memory/transcripts/2026-09-17.md` resolved by **union merge, keeping
  both sides** (80 + 80 lines → 82), per the dev-sync rule for append-heavy logs.

## Files created or modified

- `~/DEV/TypeSafe_Sandbox/setup_global_key.sh` — mode fixed 644 → 755. It had been
  committed non-executable, so `./setup_global_key.sh` failed with "permission denied".
- `~/DEV/TypeSafe_Sandbox/docs/STATUS.md` — rewritten across both sessions.
- `~/DEV/TypeSafe_Sandbox/.venv/` — built with `uv`, `typesafe-sdk==0.7.0`. Gitignored.
- `~/DEV/graphify-out/*` — nightly generated output, committed twice today.
- `~/.claude/scripts/backup-manifest.json` — added `DEV/TypeSafe_Sandbox`; now 139 paths.
- `~/.claude/global-memory/transcripts/2026-09-17.md` — union merged.
- `~/.claude/global-memory/transcripts/.errors.log` — cleared, all entries resolved.
- `~/DEV/CLAUDE.md` — router rows for TypeSafe_Sandbox (from the other session, PR #4).

## Verified, not assumed

- `.venv/bin/python smoke_test.py` exits 0 on the Mac and returns `billing = 0.98`.
- On Windows, Noul / Choice / Score all returned sane values against the live API.
- 143 DEV repos fetched and clean. Fetch freshness confirmed by counting `FETCH_HEAD`
  files touched in the last hour, not by trusting the walk's exit code. A `git fetch`
  failing silently under `xargs` is the main way "clean" becomes a lie.

## Next actions, most important first

1. Nothing is built on TypeSafe yet. Decide whether any real Baylor workflow wants
   System One judgments. Until then the sandbox is proof-of-life only.
2. TOS evidence brief: **do not send.** Codex found 3 numeric misquotes and a bad Poisson
   argument. See `handoffs/2026-09-18-tos-evidence-review-and-ri5-002.md`.
3. Research in 5 #002 is built but not sent (PR #8).
4. Status report #3 due 9/25.

## Mid-flight / open

- TypeSafe plugin (`typesafe@typesafe-ai` v0.5.7) is installed on **Windows only**. The Mac
  has no such plugin; confirmed absent from `~/.claude/plugins/installed_plugins.json`.
  The smoke test does not need it. Install on the Mac only if the `/typesafe` skill is wanted.
- Backup manifest class for `TypeSafe_Sandbox` is a guess (`personal`). Eric may override.
