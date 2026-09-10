# Tooling Optimization — Terminal & Claude × Codex Integration

Opinionated picks for your specific setup (Mac primary at `/Users/kristinarash`, VPS
hub with tmux, work Windows browser-only, Claude Code + Codex CLI both in daily use).
Researched 2026-08-14.

---

## 1. Terminal: what to actually run

The terminal is a client; **tmux on the VPS stays the backbone** regardless of what
renders it. Pick by device:

### Mac — Ghostty (primary recommendation)

Fastest terminal on macOS (~3x iTerm2 throughput), truly native UI, zero-config, and
specifically good at the heavy TUI redraw load that Claude Code and Codex CLI generate.
Install: `brew install --cask ghostty`. It deliberately does nothing fancy — your
multiplexing lives in tmux on the VPS, which is exactly the division you want.

### Mac alternative — iTerm2, for one killer feature

`ssh vps` then `tmux -CC attach` renders your **remote tmux sessions as native macOS
tabs and splits** — no tmux keybindings to remember, close a tab and the session just
detaches. No other terminal has this. If you find yourself fighting `Ctrl-b` muscle
memory, this is the ergonomic escape hatch. Keep whichever of the two sticks after a
week; both are free.

### Cross-platform option — WezTerm

If you ever want one terminal with one config file on a personal Windows box and the
Mac, WezTerm (Lua config, built-in ssh domains and multiplexing) has the best
cross-platform parity. Not worth switching to for the Mac alone.

### Skip: Warp

Its pitch is built-in AI — natural-language command suggestions and its own agent mode.
You already run two frontier coding agents in the terminal; Warp's AI layer is
redundant, it requires an account, and it adds a third AI vendor surface to a workflow
you're deliberately keeping clean for IT. Fast, pretty, but solves a problem you don't
have.

### Keep: VS Code + Remote-SSH

Editing stays in VS Code attached to the VPS. The integrated terminal is fine for quick
commands; run the *agents* in Ghostty/iTerm2 full-screen where the TUIs get room and
VS Code reload/restarts can't kill a foreground agent session. (They survive in tmux
anyway — this is about ergonomics, not safety.)

---

## 2. Claude × Codex: the integration that actually pays

The 2026 consensus pattern matches your instinct: don't pick one agent — assign lanes
and make them check each other. Complementary strengths: **Claude Code for deep
reasoning across large codebases and architecture; Codex for autonomous execution,
background tasks, and independent review.**

### 2.1 Shared brain: one context file, two agents (do this first — 20 min)

Codex reads `AGENTS.md`; Claude Code reads `CLAUDE.md`. Right now every project where
you use both has either duplicated or divergent context. Unify:

```bash
# in each project repo — CLAUDE.md stays canonical
ln -s CLAUDE.md AGENTS.md
git add AGENTS.md && git commit -m "share agent context: AGENTS.md -> CLAUDE.md"
```

Same trick globally: `~/.codex/AGENTS.md → ~/.claude/CLAUDE.md`. Now every schema note,
gotcha, and convention you've written (the ForcePlate CLAUDE.md is 17 KB of hard-won
context) feeds both agents, and there is exactly one file to maintain. This is the
highest-leverage 20 minutes in this document.

Both `.claude/` and `.codex/` state are already covered by your backup manifest, so
nothing new to protect.

### 2.2 Cross-provider review loop (the quality multiplier)

Same-model review is sycophancy-prone — a model grades its own homework generously. A
different provider reviewing is measurably harder to fool. Two ways in, in order of
effort:

- **Official Codex plugin for Claude Code** — wraps your local Codex CLI through your
  existing Codex auth; you get `/codex:review`-style commands inline in a Claude Code
  session. Zero infrastructure.
- **Automated loop** — [hamelsmu/claude-review-loop](https://github.com/hamelsmu/claude-review-loop)
  runs Claude-implements → Codex-reviews → Claude-fixes until the review passes, state
  tracked in `.claude/review-loop.local.md`.

Practical default: Claude implements; before you push anything nontrivial, Codex
reviews the diff. Scriptable one-shot version (works in hooks, no plugin needed):

```bash
git diff main | codex exec "Review this diff for bugs, edge cases, and unjustified complexity. Be adversarial."
```

And the reverse when Codex wrote it: `git diff main | claude -p "Review this diff…"`.

### 2.3 Parallel lanes: worktrees + tmux (you already half-do this)

Your Windows backups are full of `.claude/worktrees/*` — you already run parallel
Claude agents in worktrees. Extend the same pattern to mixed agents on the VPS:

```bash
tmux new -s cmj
# pane 1: claude in the main worktree        (architecture / feature work)
# pane 2: codex in a worktree                (autonomous background task, e.g. test backfill)
git worktree add ../cmj-tests fix/test-coverage && cd ../cmj-tests && codex
```

Isolated worktrees mean zero file conflicts; the shared AGENTS.md/CLAUDE.md means both
agents follow the same rules; git is the merge point. Dedicated multi-agent managers
exist (Vibe Kanban, claude-squad, Conductor-style apps) but they add a layer you don't
need yet — tmux + worktrees on an always-on box covers the same ground with tools
already in your stack. Revisit if you're routinely running 4+ simultaneous agents.

### 2.4 Division-of-labor defaults

| Task shape | Send it to |
|---|---|
| Architecture, multi-file refactors, "why is this wrong", pipeline design | Claude Code |
| Long autonomous runs (test suites, migrations, scripted chores), background tasks | Codex |
| Review of the other one's diff | Always the *other* agent |
| Quick one-shot in a script or hook | `claude -p` / `codex exec` |

### 2.5 What NOT to add

- **An orchestrator platform** (OmniAgent/Merlin-class) — built for teams coordinating
  many operators; solo, it's overhead over `tmux ls`.
- **A third agent** for its own sake — two providers already give you the adversarial
  pair; more models means more auth to rot and more context files to sync.
- **MCP bridges between the agents** — the plugin/CLI-wrap pattern (each tool calling
  the other's local CLI through existing auth) does the same job with nothing to host.

---

## 3. Order of adoption

1. `AGENTS.md → CLAUDE.md` symlinks, global + active projects (§2.1) — today.
2. `brew install --cask ghostty`, run it for a week (§1) — today.
3. Codex plugin for Claude Code; adopt the review-before-push habit (§2.2) — this week.
4. Mixed-agent worktree lanes on the VPS once it exists (§2.3).
5. Reassess managers/orchestrators only when tmux stops scaling (§2.5).

Sources: [Best Terminal for Mac 2026](https://dev.to/vibehackers/best-terminal-for-mac-in-2026-ghostty-kitty-wezterm-alacritty-warp-more-4pe6) ·
[Terminal comparison 2026](https://blog.luminoid.dev/Terminal-Emulator-Comparison-2026/) ·
[Codex CLI + Claude Code together](https://codex.danielvaughan.com/2026/04/18/codex-cli-claude-code-working-together/) ·
[Run Claude Code and Codex together](https://agi-labo.com/en/guides/run-claude-code-and-codex-together) ·
[Codex plugin cross-provider review](https://www.tarekalaaddin.com/blog/codex-plugin-claude-code-cross-provider-review) ·
[claude-review-loop](https://github.com/hamelsmu/claude-review-loop)
