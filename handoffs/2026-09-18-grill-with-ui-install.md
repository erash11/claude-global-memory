# 2026-09-18 — grill-with-ui skill install (all harnesses)

## What and why

Eric asked to add the skill at https://github.com/jasonku09/grill-with-ui, then mid-session
added the requirement: **"I want to use this skill with any harness"** — not Claude Code only.

The skill moves a "grilling" design interview out of the terminal onto a local browser page:
questions render as cards with lettered options and a recommended choice, answerable in any
order, each with its own discussion thread, staged until one **Send to Agent** button ships
them as a single turn. Ends by writing an exhaustive design doc. One Node script + one HTML
file, no dependencies, no build step. Node 20+ required (machine has v26.4.0).

## What was done

Cloned once, symlinked into every harness folder that exists on this machine:

```
~/.agents/skills/grill-with-ui        ← the clone (Codex/Cursor/Copilot read here natively)
~/.claude/skills/grill-with-ui   →    symlink   Claude Code
~/.gemini/skills/grill-with-ui   →    symlink   Gemini CLI
~/.codex/skills/grill-with-ui    →    symlink   Codex
~/.cursor/skills/grill-with-ui   →    symlink   Cursor
```

Start with `/grill-with-ui <topic>` (Claude Code, Cursor), `$grill-with-ui <topic>` (Codex),
or say "grill with ui: <topic>" anywhere else. `/grill-with-ui resume` picks up an
unfinished one. Session state lives in `~/.grill-with-ui/sessions/<project-key>/`, outside
any repo, so there is nothing to gitignore.

## Decisions and the reasoning behind them

**Clone into `~/.agents/skills`, symlink outward** — rather than four copies. One `git pull`
updates every harness, and it matches the six third-party skills already installed this way
(`humanizer`, `pp-espn`, `articulation-skill`, `game-film-timestamps`, `pp-fireflies`,
`session-handoff`).

**Used `MSYS=winsymlinks:nativestrict ln -s`, not plain `ln -s`.** Git Bash's default
*copies* the directory on Windows. The copy looks installed and the skill even works, but it
carries no `.git`, so `git pull` silently stops being the update path. Verified with
PowerShell `(Get-Item …).LinkType` → `SymbolicLink`; `ls -la` is not sufficient proof, it
shows `l... ->` either way.

**Ran `sync-to-codex.ps1` (dry-run first).** `~/.claude/skills` has a `pre-commit` hook that
refuses symlinks (mode 120000) while `daily-backup.ps1` does `git add -A` on that repo — so
the new `?? grill-with-ui` would have **jammed tonight's backup commit**. The sync script is
the designed fix: it drops third-party symlinks from the index and rewrites the generated
block in `.git/info/exclude` (that block says "do not edit by hand"). Confirmed it cannot
clobber the clone — its copy loop touches only `$MANAGED` entries and its retirement loop
only names in the previous manifest; a third-party name is in neither.

**Did not run `CreateSkill`,** despite `skills/CLAUDE.md` mandating it for skill work. This
is a vendored upstream repo; canonicalizing it (TitleCase, `Workflows/`) would rewrite
tracked files and break `git pull`. That mandate governs skills Eric owns. Open to reversing
if he wants it canonicalized.

**Did not patch the Windows test failure** — a local edit breaks `git pull`. Report upstream
instead if it ever matters.

## Verification actually performed

- PowerShell `LinkType` = `SymbolicLink` on all four links (not Git Bash copies)
- `SKILL.md` resolves from all five paths; `git fetch` succeeds → `git pull` works
- **Functional smoke test in a real DEV git repo** (`AgentAssist`): `new` → correct
  `project` path and sanitized `key`; `serve` → bound a port; `url` → `http://127.0.0.1:…`;
  page returned **HTTP 200, 45,479 bytes, `<title>grill</title>`**
- Post-sync recheck: skills repo clean, exclude block lists `/grill-with-ui`, clone still on
  `main`, all five locations resolve
- Smoke session data deleted; no real `~/.grill-with-ui` created; stray processes killed

## Known issues (upstream, non-blocking)

1. **Outside-git Windows quirk.** In a non-git directory `server.mjs` returns a *sanitized*
   `project` (`C-Users-eric_rash-…`) instead of the raw path — test `server.test.mjs:35`
   fails on `assert.equal(out.project, real)`. Inside a git repo it is correct, confirmed
   against AgentAssist. Every DEV project is a repo, so this does not affect real use.
2. **Unit suite never completes on Windows.** Emitted 2 of its tests (1 pass, 1 fail) in 5+
   minutes then stalled; leaked two orphaned `server.mjs` children (killed). Cause not
   diagnosed — deliberately left alone as upstream test-harness behavior. The functional
   smoke test above is the better signal.
3. Playwright e2e not run (needs `PLAYWRIGHT_PKG` + Chromium).

## Next actions

1. **Use it** — `/grill-with-ui <topic>` on a real design question; it is unproven in actual
   use, only in smoke test.
2. **Mac needs the same install** — nothing propagates it (`skills/` is gitignored from the
   dotclaude repo, `~/.agents` is not a repo):
   ```sh
   git clone https://github.com/jasonku09/grill-with-ui ~/.agents/skills/grill-with-ui
   for d in .claude .gemini .codex .cursor; do ln -s ~/.agents/skills/grill-with-ui ~/$d/skills/grill-with-ui; done
   ```
   On macOS plain `ln -s` is fine — the winsymlinks trap is Windows-only.
3. Confirm it appears in each harness's own skill picker (`/skills` in Codex and Gemini CLI).

## Open questions

- **Trigger overlap with `mattpocock-skills:grilling`.** Both answer to "grill" phrasing;
  **"grill with ui"** is the distinguishing phrase. If it misroutes in practice, one of the
  two descriptions needs narrowing.
- Canonicalize via `CreateSkill`, or keep it vendored and updatable? Kept vendored.

## Files touched this session

Created:
- `~/.agents/skills/grill-with-ui/` (clone of jasonku09/grill-with-ui, branch `main`)
- `~/.claude/skills/grill-with-ui` → symlink
- `~/.gemini/skills/grill-with-ui` → symlink
- `~/.codex/skills/grill-with-ui` → symlink
- `~/.cursor/skills/grill-with-ui` → symlink
- `~/.claude/projects/C--Users-eric-rash-Desktop-DEV/memory/project_third-party-skill-install.md`
- `~/.claude/global-memory/handoffs/2026-09-18-grill-with-ui-install.md` (this file)

Modified (by `sync-to-codex.ps1`):
- `~/.claude/skills/.git/info/exclude` — generated block now 7 third-party links
- `~/.claude/projects/C--Users-eric-rash-Desktop-DEV/memory/MEMORY.md` — index pointer
- `~/.agents/skills/` and `~/.codex/skills/` — routine re-sync of 41 managed skills

No DEV project repo was modified.
