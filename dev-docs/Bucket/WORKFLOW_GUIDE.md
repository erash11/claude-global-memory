# Cross-Platform Claude Code Workflow Guide

**For:** Eric Rash, Director of Applied Performance, Baylor University
**Goal:** pick up any piece of work from any device — personal Mac, work Windows machine,
phone, or a browser — with the same context, skills, hooks, and memory everywhere,
without tripping a wire with Baylor IT.

**Grounded in your real system.** This guide was written after reading your Drive backup
tree, both machines' backup logs, and the `dotclaude` repo (RESTORE.md,
MIGRATION-MACOS.md, `daily-backup.ps1`, `backup-manifest.json`). You already built most
of the hard parts — the repos, the manifest-driven backup contract, the restore docs.
What's missing is (a) fixing the post-migration breakage, (b) an always-on hub so
sessions survive device switches, and (c) clean rules for which machine writes what.

> **Do the fixes first.** [`SYSTEM-HEALTH-FINDINGS.md`](SYSTEM-HEALTH-FINDINGS.md) is the
> dated diagnosis and runbook: the Windows machine is still fighting the Mac for the same
> repos, the Mac can't push `global-memory`/`claude-skills`, SecondBrain is diverged, the
> SSD capture layer hasn't run since migration, and the memory index writes 0 chunks.
> Nothing below matters much until that list is green.

---

## 1. The architecture

Your existing repo set is already the portable second brain. Nothing new to invent —
the system just gains one node (the VPS) and one rule (single writer per store):

```
                 GitHub erash11/* (source of truth, ~19 private repos)
                 ├── dotclaude              → ~/.claude (settings, hooks, agents,
                 │                            RESTORE.md, backup scripts)
                 ├── claude-skills          → ~/.claude/skills
                 ├── claude-global-memory   → ~/.claude/global-memory (working memory)
                 ├── claude-memory-compiler → ~/.claude/claude-memory-compiler
                 ├── SecondBrain            → notes vault
                 ├── KeystoneOS             → orchestration + scheduled jobs
                 └── one repo per project (own CLAUDE.md each)
                               │
     ┌─────────────────────────┼──────────────────────────────┐
     │                         │                              │
┌────▼──────────┐   ┌──────────▼───────────┐   ┌──────────────▼────────────┐
│ Mac (primary) │   │ VPS (always-on hub)  │   │ Work Windows (Baylor)     │
│ full system + │◄──┤ Claude Code in tmux, │   │ BROWSER ONLY:             │
│ nightly backup│SSH│ reachable anywhere   │   │ claude.ai/code            │
│ + CRASHBOX SSD│   │ via Tailscale        │   │ nothing installed         │
└───────────────┘   └──────────▲───────────┘   └───────────────────────────┘
                               │
                    Phone: Claude app (Code tab / Remote Control),
                           Termius over Tailscale
   Google Drive  = snapshot safety net (claude-projects, codex, gemini) — Mac writes it
   CRASHBOX SSD  = gitignored data + working-tree capture — Mac writes it
```

**The one structural rule this adds: single writer per store.** The 8/13 logs show the
Windows and Mac machines both auto-committing and pushing the same repos nightly, which
manufactured the current divergences. After the fixes: the **Mac** owns the nightly
backup job, the Drive snapshots, and the SSD capture. The **VPS** and any other machine
are ordinary git clients — they push their own commits when you work there, but exactly
one machine runs the automation that sweeps and snapshots.

## 2. Security ground rules (the part that keeps IT happy)

| | Personal world | Baylor world |
|---|---|---|
| Machines | Mac, VPS, phone | Work Windows machine |
| Accounts | GitHub `erash11`, personal Claude, gmail | Baylor SSO, Baylor-licensed tools |
| Data | Code, config, skills, memory, **synthetic data with real schemas** | Real athlete data (VALD, Catapult, Kinexon, DEXA), Baylor credentials |

- **Nothing installed on the work Windows machine.** No CLI, no Tailscale, no SSH keys
  to the VPS. A personal mesh VPN on a managed endpoint is the single most likely thing
  to get flagged. There you use **claude.ai/code in the browser** — sanctioned SaaS,
  zero footprint, and genuinely capable (this guide was produced in one).
- **Real athlete data never lands on personal infrastructure.** Develop against
  synthetic data matching real schemas; your project CLAUDE.md files (the ForcePlate one
  especially) document schemas well enough for Claude to generate faithful test data.
  Real-data runs happen on Baylor machines with Baylor tooling.
- **Credentials live in the password manager only** — your backup system already
  enforces this (the cred deny-list in `daily-backup.ps1`, born of the 2026-08-04
  Outlook-profile incident, and `CREDENTIALS.md` as the inventory). The same rule
  applies verbatim on the VPS.
- **The manifest's `class: institutional` tag is your compliance story.** Institutional
  data stays identifiable and purgeable. If the workflow proves out and you want real
  data on sanctioned infrastructure, that tag plus the HECVAT worksheet is the
  conversation with IT — ask for it rather than working around it.

## 3. The VPS hub (the new piece — one-time, ~90 min)

A ~$9/month Linux box that never sleeps, holding live Claude Code sessions in tmux.
Start work on the Mac, detach, reattach from anything. Full command detail is in
[`../scripts/bootstrap-vps.sh`](../scripts/bootstrap-vps.sh); sequence:

1. **Buy:** Hostinger KVM 2 (2 vCPU / 8 GB / 100 GB NVMe, ~24-mo term, renewal jumps
   140–232%) or Hetzner CX32 (similar, flat, no contract). Ubuntu 24.04 LTS, closest US
   datacenter to Waco, add the Mac's SSH key at provisioning.
2. **Harden:** non-root user, key-only SSH, no root login, ufw, fail2ban,
   unattended-upgrades. Verify key login from a second terminal before closing root.
3. **Tailscale** on server + Mac + phone, then close public SSH entirely
   (`ufw delete allow OpenSSH; ufw allow in on tailscale0`). Never on the Baylor machine.
4. **Toolchain:** Node (nvm), uv, R + CRAN build libs, DuckDB, git, tmux, gh —
   scripted.
5. **Restore your brain — same procedure as any machine** (RESTORE.md Scenario A step 2,
   which is platform-neutral):
   ```bash
   gh auth login    # erash11
   mkdir -p ~/.claude && cd ~/.claude
   git init -b main
   git remote add origin https://github.com/erash11/dotclaude.git
   git fetch origin && git checkout -f origin/main -b main
   git clone https://github.com/erash11/claude-skills.git        ~/.claude/skills
   git clone https://github.com/erash11/claude-global-memory.git ~/.claude/global-memory
   ```
   Skip the memory-compiler/Milvus stack on the VPS initially — get it working on the
   Mac first (it's currently indexing 0 chunks; see findings §5). The VPS works fine
   without it and can gain it later.
6. **Claude Code:** `npm install -g @anthropic-ai/claude-code`, then `claude` — first
   run walks through browser auth via a pasted code. Personal account, same as the Mac.
7. **tmux discipline:** one named session per project (`cmj`, `volleyball`,
   `progress-report`). `Ctrl-b d` detaches; everything keeps running.
8. **Nightly WIP push** (`scripts/nightly-push.sh` via cron, 2 AM): commits and pushes
   `~/projects/*` so nothing lives only on the box. The VPS deliberately does **not**
   run `daily-backup.ps1` — that's the Mac's job (single writer).
9. **Skills triage note:** your skills repo has Windows-born skills that MIGRATION
   flagged (`everything-search`, `claude-stack-doctor`, `html-to-pdf`, `.ps1` callers).
   `brew`-less Linux needs the same triage — install `pwsh` on the VPS
   (`snap install powershell --classic` or Microsoft's apt repo) if you want the `.ps1`
   scripts, or treat those skills as Mac-only. They fail safe (nuisance, not data loss).

## 4. Per-device setup

**Mac (primary + automation owner).** Already migrated. It runs: the launchd jobs
(daily-backup 00:30, morning-cadence, stack doctor, morning briefing), the Drive
snapshots, and the CRASHBOX SSD capture. For remote work it's a client of the VPS: add
to `~/.ssh/config`:
```
Host vps
  HostName <your-machine>.<tailnet>.ts.net
  User eric
```
Then `ssh vps`, `tmux attach`. **VS Code Remote-SSH** gives you your exact VS Code
experience (editor, terminal, Claude Code extension) running against the VPS — the
terminal you like, attached to the hub. Note: the Mac's home is `/Users/kristinarash` —
scripts and launchd plists must never assume `eric_rash` there.

**Work Windows machine.** Browser only: claude.ai/code against your GitHub repos. After
the findings §1 fix, its scheduled tasks are disabled and it no longer writes to the
shared stores. If the machine is ever reimaged or returned, nothing of yours is on it.

**Phone.**
- *Claude app → Code tab*: your claude.ai/code cloud sessions, plus **Remote Control**
  (`/rc` inside a session on the VPS) bridging into the live tmux sessions. On a VPS the
  classic Remote Control weaknesses (lid closed, wifi drop, ~10-min network timeout)
  disappear. One remote connection per session; permissions still approved manually.
- *Termius or Blink + Tailscale*: full terminal to the VPS when you need to drive tmux
  directly.

**Any future machine (or rebuilt VPS).** RESTORE.md is canonical and already covers it:
tools → `~/.claude` from dotclaude → state from Drive/SSD → repos → venvs → schedules.
Twenty minutes to functional.

## 5. Daily rhythm

- **Start work, any device:** `ssh vps && tmux attach -t <project>` (or VS Code
  Remote-SSH, or Claude app). New project → new repo, own CLAUDE.md, `docs/session.md`
  log — the ForcePlate repo is the reference pattern.
- **Leave the desk:** detach. That's the whole handoff.
- **From the phone:** check progress, approve permissions, queue next steps via the
  Claude app; real typing via Termius.
- **Work machine downtime:** claude.ai/code in the browser — cloud sessions on the same
  repos, so commits flow into the same git truth.
- **Nightly, automatic:** Mac's daily-backup sweeps memory repos, snapshots AI state to
  Drive, captures gitignored data + working trees to CRASHBOX, refreshes RESTORE.md
  mirrors, writes receipts. VPS pushes its own WIP. Failures surface at the start of
  your next Claude session (your hook already does this).
- **Weekly:** Monday stack doctor (already scheduled) + a 30-second glance at the
  latest `daily-backup-*.out.log` in Drive: it should end `OK (0 errors)`.

## 6. What goes where — quick reference

| Thing | Lives in | Writer |
|---|---|---|
| Settings, hooks, agents, RESTORE.md, backup scripts | `dotclaude` → `~/.claude` | any machine you edit on (git) |
| Skills | `claude-skills` → `~/.claude/skills` | any machine (git) |
| Working memory | `claude-global-memory` | auto-committed nightly by **Mac only**; others push as they work |
| Notes vault | `SecondBrain` | you, from anywhere (git) |
| Project code + CLAUDE.md | per-project repos | any machine (git) |
| Conversation transcripts (`~/.claude/projects`) | per machine | Mac's copy snapshotted to Drive nightly |
| Gitignored data (dbs, outputs) + uncommitted edits | Mac disk | **CRASHBOX SSD nightly (must be plugged in)** |
| Live sessions | VPS tmux | attach from anywhere |
| Credentials | password manager only | never in any backup, by design |
| Real athlete data | Baylor systems only | never on personal infra |

## 7. Build order

1. **Now:** work through [`SYSTEM-HEALTH-FINDINGS.md`](SYSTEM-HEALTH-FINDINGS.md) —
   restore single-writer, un-strand memory, reattach the SSD. Acceptance: a morning log
   ending `OK (0 errors)`.
2. **This week:** VPS (§3). Acceptance: start a session on the Mac, detach, reattach
   from the phone and from a browser.
3. **Ongoing:** work Windows machine stays browser-only; open the sanctioned-data
   conversation with IT when the workflow has proof behind it.
4. **Optimization layer:** terminal choice and running Claude Code + Codex as an
   adversarial pair — see [`TOOLING-OPTIMIZATION.md`](TOOLING-OPTIMIZATION.md).
