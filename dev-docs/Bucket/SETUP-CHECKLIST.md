# The Setup Checklist — one ordered path to the full workflow

Every step you personally need to do, in order, to get one workflow that works across
**frontier models** (Claude Code, Codex, Gemini) and **every device** (Mac, Windows,
phone, browser). Each phase says *where* you do it, *what* you do, and *how you know
it worked*. Deep reasoning lives in the other docs — this is just the path.

Legend: 🖥️ Mac · 🪟 Windows machine · ☁️ VPS · 📱 Phone · ⏱ rough time

---

## Phase 0 — Repair the foundation (do first) — 🖥️ then 🪟, ⏱ ~1 hr total

Your migration left the backup/memory system unhealthy; everything else builds on it.

- [ ] **0.1** 🖥️ Open Claude Code on the Mac and paste **Prompt 1** from
      [`AGENT-FIX-PROMPT.md`](AGENT-FIX-PROMPT.md). It fixes the failed pushes
      (`global-memory`, `skills`), reconciles SecondBrain, patches the rsync
      false-OK bug, fills the manifest gaps, and repairs the memory index.
- [ ] **0.2** 🖥️ Plug the **CRASHBOX SSD** into the Mac and leave it attached —
      until then, gitignored data (forceplate.db etc.) has no backup.
- [ ] **0.3** 🪟 On the Windows machine, paste **Prompt 2** from the same doc:
      final sync of its 2 stranded memory files, then disable the scheduled tasks
      so only the Mac writes.
- [ ] ✅ **Check:** next morning, the newest `daily-backup-*.out.log` in Drive ends
      `end: OK (0 errors)`; the Windows log folder stops getting new files.

## Phase 1 — One brain for every model — 🖥️, ⏱ ~15 min

Merged and ready (dotclaude PR #2). Claude reads `CLAUDE.md`, Codex reads
`AGENTS.md`, Gemini reads `GEMINI.md` — after this phase they all read the *same file*.

- [ ] **1.1** 🖥️ Pull the merged config and run the linker:
      ```bash
      cd ~/.claude && git pull --ff-only
      bash ~/.claude/scripts/setup-agents-symlinks.sh --commit
      ```
      This creates `~/.codex/AGENTS.md → ~/.claude/CLAUDE.md` plus
      `AGENTS.md → CLAUDE.md` in every project repo, and commits the links.
- [ ] **1.2** 🖥️ Push each project repo it committed in (it prints the list), or:
      `for r in ~/Desktop/DEV/*/ ~/Desktop/SecondBrain; do git -C "$r" push 2>/dev/null; done`
- [ ] **1.3** 🖥️ Point **Gemini** at the same brain — add to `~/.gemini/settings.json`:
      ```json
      { "context": { "fileName": ["AGENTS.md", "CLAUDE.md", "GEMINI.md"] } }
      ```
      (Gemini CLI's `contextFileName` accepts a list; first match wins per directory.
      If your installed version uses the older flat key, set
      `"contextFileName": ["AGENTS.md", "CLAUDE.md", "GEMINI.md"]` at top level.)
- [ ] **1.4** 🖥️ If any repo printed `SKIP … real file`, merge that AGENTS.md's
      content into the repo's CLAUDE.md by hand, delete it, re-run 1.1.
- [ ] ✅ **Check:** `ls -la ~/.codex/AGENTS.md` shows the symlink; open Codex in any
      project and ask "what are this project's conventions?" — it should answer from
      your CLAUDE.md content.

## Phase 2 — The always-on hub — ☁️, ⏱ ~90 min once

A ~$9/mo VPS holds live agent sessions in tmux so any device can pick them up.

- [ ] **2.1** Buy: Hostinger KVM 2 *or* Hetzner CX32 (8 GB RAM matters), Ubuntu
      24.04 LTS, nearest US datacenter, add your Mac's SSH key at provisioning
      (create one first if needed: `ssh-keygen -t ed25519 -C "eric-mac"`).
- [ ] **2.2** Harden per [`WORKFLOW_GUIDE.md`](WORKFLOW_GUIDE.md) §3.2: non-root
      user, key-only SSH, ufw, fail2ban. Verify login from a 2nd terminal before
      closing root.
- [ ] **2.3** Install Tailscale on the VPS, then close public SSH
      (`sudo ufw delete allow OpenSSH && sudo ufw allow in on tailscale0`).
      **Never install Tailscale on the Baylor machine.**
- [ ] **2.4** Run [`../scripts/bootstrap-vps.sh`](../scripts/bootstrap-vps.sh)
      (Node, uv, R, DuckDB, git, tmux, Claude Code), then follow its printed
      "next steps": `gh auth login`, restore `~/.claude` from dotclaude, clone
      `claude-skills` + `claude-global-memory` — the same RESTORE.md procedure as
      any machine, so your full context arrives automatically.
- [ ] **2.5** Install the other CLIs so all three models live on the hub too:
      `npm i -g @openai/codex @google/gemini-cli` — sign in once each. Re-run
      `setup-agents-symlinks.sh` (it handles `~/projects`).
- [ ] **2.6** Add the nightly WIP push:
      `crontab -e` → `0 2 * * * ~/Bucket/scripts/nightly-push.sh >> ~/nightly-push.log 2>&1`
      (clone this Bucket repo to `~/Bucket` first). The VPS does **not** run
      daily-backup.ps1 — the Mac stays the single automation writer.
- [ ] ✅ **Check:** `tmux new -s test`, start `claude`, detach (`Ctrl-b d`), close
      the terminal, `ssh` back in, `tmux attach -t test` — session intact.

## Phase 3 — Wire up each device — ⏱ ~30 min

- [ ] **3.1** 🖥️ Terminal: `brew install --cask ghostty` (or keep iTerm2 and use
      `ssh vps` + `tmux -CC attach` for native tabs). Add to `~/.ssh/config`:
      ```
      Host vps
        HostName <machine>.<tailnet>.ts.net
        User eric
      ```
- [ ] **3.2** 🖥️ VS Code: install **Remote-SSH**, connect to `vps` — your editor,
      terminal, and extensions now run against the hub.
- [ ] **3.3** 📱 Install **Tailscale** (same account) and **Termius** (add host
      `vps` via its tailnet name) — full terminal from anywhere.
- [ ] **3.4** 📱 In the **Claude app → Code tab**: your claude.ai/code cloud
      sessions appear automatically; for the VPS sessions, type `/rc` inside a
      Claude Code session on the VPS once and the session shows up in the app
      (Remote Control). Approve permissions from your phone.
- [ ] **3.5** 🪟 Work machine: bookmark **claude.ai/code** (and chatgpt.com/codex
      if you use Codex cloud). Browser only — install nothing, ever, on this box.
- [ ] ✅ **Check:** start a session in a VPS tmux window from the Mac, reattach to
      the same conversation from Termius on the phone, and see it in the Claude app.

## Phase 4 — The multi-model habits (ongoing)

- [ ] **4.1** Adopt the lanes: **Claude Code** for architecture and multi-file
      reasoning; **Codex** for long autonomous runs; **Gemini** as a third opinion
      when you want one. All read the same context files now.
- [ ] **4.2** Cross-review before any nontrivial push (the other provider reviews):
      `git diff main | codex exec "Adversarial review: bugs, edge cases, complexity"`
      — or install the Codex plugin for Claude Code for inline `/review` commands
      ([`TOOLING-OPTIMIZATION.md`](TOOLING-OPTIMIZATION.md) §2.2).
- [ ] **4.3** Parallel work = one tmux session per project on the VPS; add a git
      worktree when a second agent works the same repo
      (`git worktree add ../proj-taskname branch && cd ../proj-taskname && codex`).
- [ ] **4.4** New project ritual: new repo → write CLAUDE.md → `ln -s CLAUDE.md
      AGENTS.md` → first commit. Every model onboards instantly, forever.
- [ ] **4.5** Weekly 30 seconds: newest `daily-backup-*.out.log` ends `OK (0
      errors)`; Monday stack doctor stays quiet.

---

## Where each piece of state lives (so nothing surprises you)

| State | Home | Reaches other devices via |
|---|---|---|
| Global context (all 3 models) | `~/.claude/CLAUDE.md` (dotclaude repo) | git pull + symlinks (Phase 1) |
| Per-project context (all 3 models) | `<repo>/CLAUDE.md` (+`AGENTS.md` link) | the project repo itself |
| Skills / hooks / agents | `claude-skills`, `dotclaude` | git |
| Working memory | `claude-global-memory` | git (nightly auto-commit on Mac) |
| Live sessions | VPS tmux | SSH / Remote Control from anything |
| Claude transcripts, Codex + Gemini state | per machine | Mac's nightly Drive snapshot |
| Credentials | password manager only | you, by hand — never synced |
| Real athlete data | Baylor systems only | never |
