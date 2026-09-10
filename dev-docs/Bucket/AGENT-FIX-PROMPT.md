# Agent Fix Prompts — paste these into Claude Code (or Codex)

> **Status 2026-08-14: Prompt 1 (Mac) has been executed — do not re-run it.**
> See [`FIX-STATUS-2026-08-14.md`](FIX-STATUS-2026-08-14.md) for what was applied and
> what's left. **Prompt 2 (Windows) is still outstanding** and remains the fix that stops
> the divergence recurring.
>
> Corrections made to this doc after that run:
> - Item 4 pointed at `~/Desktop/DEV`, which does not exist — DEV is at `~/DEV`.
> - Item 4's "2 unmanaged dirs" was stale; the list grows over time. Read the live log.
> - Item 6's Milvus prerequisite is obsolete — see the note on that item.

Companion to [`SYSTEM-HEALTH-FINDINGS.md`](SYSTEM-HEALTH-FINDINGS.md) (evidence and
reasoning live there). That doc was written for you; this one is written to be **pasted
verbatim into an agent session** on each machine. Two prompts: Mac first, then Windows.

Run them in that order — the Mac prompt un-strands your working memory; the Windows
prompt does the final sync and shuts off the second writer.

---

## Prompt 1 — run in Claude Code on the MAC (from `~`)

Copy everything inside the fence:

```text
Fix my backup/sync system. Context: I migrated from Windows to this Mac on 2026-08-05.
My nightly backup (~/.claude/scripts/daily-backup.ps1, run by launchd, manifest at
~/.claude/scripts/backup-manifest.json, log at ~/.claude/scripts/logs/daily-backup.log)
ends "ERROR (5 errors)" every night. Diagnosis was done from the logs on 2026-08-13;
verify each item against current state before acting, and fix in this order:

1. PUSH FAILURES. ~/.claude/global-memory and ~/.claude/skills both log "PUSH FAILED".
   Run `gh auth status` and `git push` in each repo to see the real error.
   - If auth is expired: tell me the exact `gh auth login` step to run, wait for me,
     then push.
   - If non-fast-forward: `git pull --rebase origin main` then push. If the rebase
     conflicts, STOP and show me the conflicting hunks — do not resolve on your own.

2. SECONDBRAIN DIVERGED. ~/Desktop/SecondBrain logs
   "DIVERGED (behind=2 ahead=0 dirty=2)". Show me `git status` and a diff of the dirty
   files first. Then: commit the dirty files, `git pull --rebase origin main`, push.
   Same rule — conflicts stop and come to me.

3. RSYNC FALSE-OK BUG. In ~/.claude/scripts/daily-backup.ps1, function Invoke-Rsync
   returns ($LASTEXITCODE -eq 0), but if /usr/bin/rsync fails to LAUNCH,
   $LASTEXITCODE is stale from an earlier command and a copy that moved zero bytes
   logs "SNAP OK". Patch it: verify the rsync binary exists (add error
   'rsync-missing' and return $false if not) and set $global:LASTEXITCODE = 0
   immediately before invoking rsync. Commit to the dotclaude repo (~/.claude is the
   repo) with a clear message and push.

4. MANIFEST GAPS. The log lists unmanaged DEV dir(s) — re-read the current log for
   the live list, it grows as new project folders appear. Look at those
   directories under ~/DEV, then add entries for them to backup-manifest.json
   following the existing schema. Ask me one question each: personal or
   institutional class? (Class drives destinations: institutional -> ssd+baylor,
   personal -> ssd; add github for either when the dir is a repo. Athlete data
   must never be classed personal.) Commit and push with the same commit as item
   3 or a follow-up.

5. CODEX SESSIONS SNAPSHOT. The log shows "codex/sessions : FAILED (rsync exit 1)".
   Re-run that one rsync manually with full output visible, identify the offending
   file (likely a live lock/sqlite temp), and add a targeted --exclude to the
   snapshot call for it. Also verify whether ~/.codex/memories is genuinely absent
   on this Mac (log says "SNAP skip (missing)") — if Codex stores memories at a
   different path now, update the manifest/snapshot source accordingly.

6. MEMORY INDEX. Nightly log shows "INDEX full set: Indexed 0 chunks" from 9 paths.
   Read ~/.claude/global-memory/transcripts/.errors.log. Known failure mode (see
   ~/.claude/RESTORE.md): the memsearch local flush patch must be re-applied after
   any pip install. Re-apply the patch per the notes in
   ~/.claude/claude-memory-compiler, reindex, and confirm a nonzero chunk count.
   NOTE (2026-08-14): ignore the Milvus prerequisite this item used to carry.
   Indexing works with port 19530 closed and Docker not installed, so Milvus is
   not in the path. Do not set it up.

7. VERIFY. Run `pwsh -NoProfile -File ~/.claude/scripts/daily-backup.ps1 -DryRun`
   and show me the output. Success criteria: no DIVERGED, no PUSH FAILED, no
   snapshot FAILED, manifest reports 0 unmanaged dirs. Remind me to plug in the
   CRASHBOX SSD — until it's attached overnight, gitignored data and working-tree
   captures are not happening (that's a physical step you can't do).

HARD RULES for this whole session: never force-push; never `git reset --hard`;
never delete files; never auto-resolve merge/rebase conflicts — show me instead;
do not touch anything under secrets/, .env files, or credentials; if a repo's
state doesn't match the diagnosis above, stop and tell me what you see instead.
Update ~/.claude/RESTORE.md in the same session if anything you fix contradicts
what it documents (that's its maintenance rule).
```

---

## Prompt 2 — run on the WINDOWS machine (after Prompt 1 succeeds)

If Claude Code still runs there, paste this; otherwise see the manual PowerShell
fallback below it.

```text
This Windows machine was migrated to a Mac on 2026-08-05, but its scheduled tasks
still run nightly and are fighting the Mac over shared git repos — that second
writer is manufacturing repo divergence on the Mac every night. This machine's
~/.claude/scripts/daily-backup.ps1 is now the macOS port, which fails on Windows
(/usr/bin/rsync, wrong DEV path) while logging false "SNAP OK" receipts. Goal:
one final sync, then make this machine a read-only client. Steps:

1. FINAL SYNC of four repos:
     $env:USERPROFILE\.claude                  (dotclaude)
     $env:USERPROFILE\.claude\global-memory
     $env:USERPROFILE\.claude\skills
     $env:USERPROFILE\Desktop\SecondBrain
   For EACH, in this order:
   a. Run `git status` and show me the output before changing anything.
   b. If there are dirty or untracked files, show me `git diff` (and for untracked
      files, their first ~30 lines) so I can see what's local-only. Some of these
      exist nowhere else — that's the whole point of this step.
   c. Commit them with a clear message, then `git pull --rebase origin main`,
      then push.
   Expect the "behind" count to be large — the Mac has been the active writer
   since 2026-08-05, so this machine is many commits behind on all four. That is
   normal, not a problem. Rebase conflicts are NOT normal: stop and show me the
   conflicting hunks instead of resolving them.
   Note: plain `git stash` does not pick up UNTRACKED files. If you need to stash
   to pull, use `git stash -u`, or rename the local file aside first.

2. DISABLE THE AUTOMATION (disable, do NOT unregister — RESTORE.md documents
   re-registration if it's ever wanted):
   Get-ScheduledTask | Where-Object {$_.TaskName -like 'KeystoneOS*' -or
     $_.TaskName -eq 'MorningBriefing'} | Disable-ScheduledTask
   Disabling MorningBriefing here is intended — that job was retired by decision
   on 2026-08-14 and is already shut off on the Mac. Not collateral damage.

3. VERIFY. Show me `Get-ScheduledTask | Where-Object {$_.State -ne 'Disabled'} |
   Select-Object TaskName,State` filtered to KeystoneOS*/MorningBriefing — the
   result should be empty. Then confirm all four repos above report clean and
   up to date with origin. From here this machine can still be used normally for
   reading and git work; it just runs no scheduled writers.

HARD RULES: never force-push; never `git reset --hard`; never delete files;
conflicts and surprises come to me before you act; do not touch secrets/, .env
files, or credentials.
```

### Manual fallback (if Claude Code is not installed on that machine)

Run in PowerShell, one repo at a time. Do **not** batch it — read each `git status`
before acting on it.

```powershell
foreach ($r in @("$env:USERPROFILE\.claude",
                 "$env:USERPROFILE\.claude\global-memory",
                 "$env:USERPROFILE\.claude\skills",
                 "$env:USERPROFILE\Desktop\SecondBrain")) {
    Write-Host "`n===== $r ====="
    git -C $r status --short --branch
}
```

For each repo that shows dirty or untracked files, inspect them, then:

```powershell
git -C <repo> add -A
git -C <repo> commit -m "final windows-machine sync before retirement"
git -C <repo> pull --rebase origin main    # STOP if this conflicts
git -C <repo> push origin main
```

Then shut off the writers:

```powershell
Get-ScheduledTask | Where-Object {$_.TaskName -like 'KeystoneOS*' -or
  $_.TaskName -eq 'MorningBriefing'} | Disable-ScheduledTask

# verify — should print nothing
Get-ScheduledTask | Where-Object {($_.TaskName -like 'KeystoneOS*' -or
  $_.TaskName -eq 'MorningBriefing') -and $_.State -ne 'Disabled'} |
  Select-Object TaskName,State
```

---

## After both prompts

The next Mac morning log (`daily-backup-*.out.log` in Drive) should end
`end: OK (0 errors)` with a verified receipt — that's the acceptance test. The
Windows log folder in Drive should simply stop growing.
