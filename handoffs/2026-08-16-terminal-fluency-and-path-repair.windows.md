# Handoff — Terminal Fluency lessons 01–03 + PATH/secrets repair

**Session:** 2026-08-13 → 2026-08-16 (background job, resumed across days)
**Harness:** Claude Code (Opus 5, 1M context)
**Nothing is mid-flight.** Every deliverable is written and verified. Open items below are all
*his* decisions, not unfinished work.

---

## What this was

Eric asked to learn the command line via `/mattpocock-skills:teach`. The mission that came out of
the interview is narrower and more useful than "learn bash": **become fluent enough at the terminal
to drive Claude Code and Codex from it**, because the CLI gives control the desktop/web UIs don't.
His stated starting floor: *"I run commands, I don't read them."*

It turned into two things at once — a teaching workspace, and two rounds of real repair on his
machine that the lessons surfaced.

## Where everything lives

Teaching workspace: **`~/DEV/Terminal_Fluency`** (not a git repo)

```
MISSION.md                              the grounding for every lesson — read first
NOTES.md                                teaching prefs, verified env, lesson ledger, design notes
GLOSSARY.md                             4 terms promoted, 4 held pending evidence
RESOURCES.md                            verified sources + explicit verification status per link
assets/lesson.css                       shared stylesheet (all lessons link it)
assets/quiz.js                          reusable quiz widget, shuffles options, one attempt each
lessons/0001-reading-a-command.html     command anatomy, quoting, cwd, --help
lessons/0002-where-commands-come-from.html   npm/npx/uv/uvx, PATH, which -a
lessons/0003-pipes-and-redirection.html      | and > and stderr; claude -p as a pipeline component
reference/agent-cli-cheatsheet.html     Claude Code vs Codex flags, from real --help output
reference/package-tools.html            installer/runner map, PATH, what was repaired and why
learning-records/0001-starting-floor.md
learning-records/0002-lesson-01-completed-and-package-tool-gap.md
learning-records/0003-lesson-02-completed-and-first-real-repair.md
learning-records/0004-second-repair-and-the-composition-turn.md
```

Also modified outside the workspace:

```
~/.zshrc                                dedupe + Keychain lookup replacing plaintext key
~/.zprofile                             removed two unguarded brew shellenv calls
~/.claude/CLAUDE.md                     corrected env section (was the source of a misdiagnosis)
~/.claude/global-memory/MEMORY.md       added "CLI lessons (8/16)" active thread
~/.claude/projects/-Users-kristinarash-DEV/memory/project_terminal-fluency-workspace.md
~/.claude/projects/-Users-kristinarash-DEV/memory/project_path-shadowing-and-cleanup.md   (new)
~/.claude/projects/-Users-kristinarash-DEV/memory/MEMORY.md                               (index)
```

Backups (rollback for the shell edits): `~/.zshrc.bak-20260813-preflight`,
`~/.zshrc.bak-20260813-prekeychain`, `~/.zprofile.bak-20260813-preflight`. The two `.zshrc` ones
are `chmod 600` because they still contain the plaintext API key.

## Machine changes made

| Change | Before | After |
|---|---|---|
| `uv` version | 0.11.6 (Apr), shadowing Homebrew's 0.12.1 | 0.12.3, single copy at `~/.local/bin/uv` |
| PATH | 17 entries, `~/go/bin` + `~/.local/bin` twice | 15 entries, zero duplicates |
| `/usr/local` Node install | ~690 MB of pre-migration debris | removed; only Docker + kubectl remain |
| Fireflies API key | plaintext in `.zshrc` | macOS Keychain, `.zshrc` reads it (~10 ms) |

All verified in a scrubbed clean shell, not from a polluted tool shell.

## Decisions worth preserving (the reasoning would be lost otherwise)

**Lesson content is built from his own machine, never synthetic examples.** Established after two
sessions of the same pattern: learn a concept → find it applies to a real defect → fix it → ask for
more. Lesson 03's drill 2 deliberately re-runs lesson 02's diagnosis, which now returns nothing
*because he fixed it*. Keep doing this.

**`uv` was updated in place rather than deleting the older copy.** The tidy-looking fix —
`rm ~/.local/bin/uv`, let Homebrew win — would have silently broken three hooks in
`~/.claude/settings.json` (SessionStart / PreCompact / SessionEnd) that call the memory-compiler by
*absolute path*. PATH order only governs lookups by name.

**PATH was deliberately NOT reordered**, despite him asking for it. Once each tool has one owner and
duplicates are gone, reordering buys nothing and has the widest blast radius. Told him so rather
than silently skipping it; he can still ask.

**The stale Windows-path warning in `~/.claude/settings.json` is deliberately left unfixed.** Every
`claude -p` emits it. It is lesson 03's stderr demonstration — verified that the warning goes to
stderr and the answer to stdout, so `2>/dev/null` cleans it. Fixing it removes a real teaching
example on his own machine. The fix was offered in the lesson; do it only when he asks.

**Four glossary terms are held back.** *flag*, *value*, *argument*, *working directory* — he has
used them correctly for three lessons but never been asked to *name* them. Lesson 03's footer asks
directly. Promote when he answers; do not promote on continued correct usage alone.

## Traps hit — do not repeat these

1. **A PATH read from inside a tool shell is polluted** by that session's own `export PATH=…`. This
   produced a wrong claim (`~/.bun/bin` reported duplicated when it wasn't) that had to be
   retracted. Honest measurement:
   `env -i HOME="$HOME" USER="$USER" TERM=xterm SHELL=/bin/zsh /bin/zsh -lic 'echo $PATH'`
2. **Scheduled jobs are the blind spot.** Eight KeystoneOS launchd agents referenced `/usr/local`.
   Harmless (PATH entries only) but invisible from shell config. Check `~/Library/LaunchAgents`.
3. **`[ -e ]` and `find -type f` skip broken symlinks.** 92 npm man pages were symlinks into a
   just-deleted tree; the first pass removed 1 of 92 and reported success.
4. **Standalone HTML needs explicit `<meta charset="utf-8">`** or every em-dash becomes mojibake —
   and a linked `.js` file's own non-ASCII breaks *separately* from the HTML's.
5. **The `teach` skill has `disable-model-invocation: true`**, so it is absent from the registered
   skill list and the Skill tool cannot load it. Read its `SKILL.md` + four `*-FORMAT.md` siblings
   directly from `~/.claude/plugins/cache/mattpocock/mattpocock-skills/<ver>/skills/productivity/teach/`.

## Next actions, most important first

1. **Rotate the Fireflies API key** (his action — needs the Fireflies dashboard). The Keychain
   protects it going forward but retracts nothing: the literal value still sits in two `.zshrc`
   backups, this session's `.jsonl` transcript, two `~/.claude/file-history/` entries, and
   `~/.claude/global-memory/transcripts/2026-08-11.md`. Then:
   `security add-generic-password -s FIREFLIES_API_KEY -a "$USER" -w 'NEW' -U`
2. **He does lesson 03's drill** and reports back — including naming the parts of a command, which
   unblocks the glossary promotion. Do not build lesson 04 before that.
3. **Optional sudo cleanup:** `sudo rm -rf /usr/local/include/node` (62 MB) and
   `sudo rmdir /usr/local/lib/node_modules` (already empty).
4. **Lesson 04** is sessions / resuming / permission modes. Then 05 quoting+exit codes (ground it in
   his own recorded zsh traps), 06 `--output-format json` + `jq`.

## How to resume

```
cd ~/DEV/Terminal_Fluency
claude
```
Then: *"continue my CLI lessons."* Read `MISSION.md` → `NOTES.md` → newest `learning-records/`.
The workspace is self-describing; do not re-interview him about the mission.
