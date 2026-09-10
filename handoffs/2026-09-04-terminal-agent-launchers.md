# Handoff — 2026-09-04 — Terminal + agent launcher setup

## What this session was

Eric wanted one-keystroke launchers for his two coding agents, then kept pulling
the thread: tmux as the VS Code terminal, side-by-side panes so Claude Code and
Codex are visible at once, and a written reference in the vault. Prompted by
David Ondrej's video "My Agentic Engineering Workflow (after 6,775 sessions)"
(YouTube `c9nRxEy1kUY`, 54:20) — specifically the 25:41 mark, where he
recommends exactly the `cc` / `cx` aliases.

## What changed

| Path | Change |
|---|---|
| `~/.zshrc` (lines 54–55) | `cc` → `claude --dangerously-skip-permissions`; `cx` → `codex --dangerously-bypass-approvals-and-sandbox`. **Pre-existed** this session under an "agent launchers (added 2026-09-04)" block — verified working, not re-added. |
| `~/Library/Application Support/Code/User/settings.json` | Added `terminal.integrated.profiles.osx` (a `tmux` profile running `/opt/homebrew/bin/tmux new-session`, plus a `zsh` escape-hatch profile) and `terminal.integrated.defaultProfile.osx: "tmux"`. Backup at `settings.json.bak` in the same folder. |
| `~/.tmux.conf` | **Created.** `mouse on`, `history-limit 50000`, `base-index 1` + `renumber-windows on`, splits/new-windows inherit `pane_current_path`, `prefix r` reloads. Prefix deliberately left at stock `Ctrl+b`. |
| `~/SecondBrain/Knowledge/tooling/tmux-cheat-sheet.md` | **Created**, plus a new `Knowledge/tooling/` subfolder. 4 commits: `87bbb52`, `136b712`, `c543a73`, `9d859a3`. |

## Decisions and the reasoning behind them

- **`Knowledge/tooling/` is a new vault subfolder.** None of the existing ones
  (faith, sport-science, career-strategy, library, frameworks,
  coaching-frameworks) fit a CLI reference, and the vault's `CLAUDE.md` says to
  add a subfolder rather than drop a file at `Knowledge/` root.
- **tmux prefix stays `Ctrl+b`.** No clash was found — `terminal.integrated.commandsToSkipShell`
  in the VS Code settings already carries `-workbench.action.toggleSidebarVisibility`,
  which hands `Ctrl+b` back to the shell. Changing the prefix would have made
  every tutorial and the cheat sheet wrong for no gain.
- **The VS Code profile runs bare `tmux new-session`, not `new-session -A -s main`.**
  `-A` would have made every VS Code terminal attach to one shared session, and
  multiple clients on one session *mirror* each other — confusing. The cost is
  that the `+` button spawns a fresh session each time, which is documented in
  the cheat sheet with the instruction to split inside one session instead.
- **Did not push the vault.** Standing rule: only KeystoneOS is push-authorized.

## Two real bugs found and fixed

1. **"`Ctrl+b c` doesn't work."** Root cause: he had **7 stray tmux sessions**,
   each with one pane, because every `+` click ran `tmux new-session`. Splits
   were working; he was making new sessions instead of splitting.
2. **"I couldn't click back into the other panel."** Root cause: stock tmux
   ignores the mouse entirely. Fixed by `set -g mouse on` in the new
   `~/.tmux.conf`. Documented tradeoff: with mouse on, hold **Option** while
   dragging to get a selection macOS `Cmd+C` can copy.

## Video triage (so nobody re-watches 54 minutes)

Full deduped transcript was pulled but lives in job-temp and will not survive.
The filtered verdict:

- **Already had:** the `cc`/`cx` aliases (25:41) and the guardrail pre-tool hook
  (34:36, which the video calls non-negotiable) — that is `dcg`, and it fired
  correctly during this session, blocking a truncating redirect into `$HOME`.
  Voice dictation (14:04) — Eric confirmed he already has it.
- **Worth stealing:** text snippets for repeated prompts (27:36); "ask before
  build" — make the agent surface 3–5 decisions before a big change (30:14);
  review once with a *different* model, never recursively (42:33); tell models
  explicitly to stop adding tests (48:37).
- **Ignore:** the 10:00–20:00 VPS section is a **paid Hostinger ad**, and cloud
  servers are blocked for Eric's work anyway (no cloud without Baylor IT
  approval). Worktrees — the video itself says they only pay off past ~15
  parallel agents. Buying four AI subscriptions. The tool-of-the-week names
  (BB, cmux, herder, Pi); the presenter says the video is stale in a month.

## Next actions

1. **Push the vault** — 4 commits sit unpushed on `~/SecondBrain` (`erash11/SecondBrain`).
   Not done because only KeystoneOS is push-authorized.
2. **Clean up stray tmux sessions.** `tmux ls` showed 7. Sessions 1, 4, 6 were
   idle and empty: `tmux kill-session -t 1; tmux kill-session -t 4; tmux kill-session -t 6`.
   2, 3, 5 showed as attached — check before killing.
3. **Close the demo pane** left in session `0:0` — `Ctrl+b` then `x`. It was
   created deliberately to prove splitting worked.

## Mid-flight / open

Nothing blocking. Eric said "I'm not sure this is the best setup, still trying
to figure a lot of this out" — the honest read given to him was that his local
stack (aliases + guardrail hook + tmux + voice) already matches everything the
video actually recommends for someone not running 30 parallel agents, and the
remainder of the video is sponsorship or scale he does not have.
