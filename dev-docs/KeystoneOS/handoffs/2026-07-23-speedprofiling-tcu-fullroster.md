# SpeedProfiling — TCU full-roster correction shipped (2026-07-23)

**Repo:** `C:\Users\eric_rash\Desktop\DEV\Football\SpeedProfiling` (branch `tcu-fix-pull-retry`, pushed)
**Deliverable:** PR #9 — https://github.com/erash11/SpeedProfiling/pull/9 (OPEN, awaiting Eric's merge)

## What happened and why

The 2026-07-23 morning handoff's live work is DONE. The "TCU degraded game / half the
roster not miked" characterization is retracted: script 01 was silently dropping
athletes on the first transient Catapult API error. With per-athlete retry
(`PULL_MAX_ATTEMPTS=4`), the re-pull recovered **66/66 athletes, 0 failures**.

Commit `ad5bad2` (on `tcu-fix-pull-retry`, stacked on `tcu-2025-pull`) contains:
- `R/01_get_data.R` — retry loop (last_err reset per attempt; genuine empty pull not retried)
- `R/config.R` — `PULL_MAX_ATTEMPTS`/`PULL_RETRY_SLEEP_S`, `save_rds_atomic()`, corrected TCU comment
- `R/02_combine_data.R`, `R/03_velocity_profiling.R` — all `.rds` writes atomic

Verified before ship: suite **365 green** on the exact committed tree; subagent code
review clean (recorded as PR #9 comment); TCU cache 66 athletes / 10,144,831 rows;
pooled `data_10hz.rds` 28,586,140 rows (BYU 61 / TT 61 / TCU 66 athletes).

## Corrected numbers (already sent to Eric with refreshed velocity_profiles.html)

503 sprints / 73 athletes (TCU 155, was 58) · 71 profiled · 32 well-identified ≥20 yd ·
hier held-out RMSE **1.393** (v1 1.414) · understated 14. Offset −15
participation-confirmed on full roster (sweep peaks −15, 10.58 athl/play vs BYU 10.75);
TCU surge scan unreliable (pregame-warmup false cluster ~−152).

## Decisions / lessons (also in KeystoneOS project memory: project-speedprofiling-data-gotchas.md)

1. **One pipeline run at a time.** 15.6 GB machine; each 02/03 run peaks ~9 GB.
   Concurrent runs OOM-kill each other SILENTLY (process vanishes, no R error) —
   this, not interleaved writes, tore `data_tagged.rds` twice today. Check
   `Get-Process Rscript` before launching.
2. **Two parallel Claude sessions executed the same handoff today** and raced each
   other (R runs, config edits, the commit). Before redoing handoff work: check
   `git log`, `gh pr list`, and running processes.
3. Long R runs: launch detached (`Start-Process Rscript -RedirectStandardOutput/-Error`);
   child background jobs die ~10 min. R `message()` output goes to stderr.
4. Never `Rscript -e "..."` inside PowerShell double quotes — PS interpolates R's
   `$column` as empty PS variables and silently corrupts the code. Use a script file.
5. Don't edit an R script while an `Rscript` process is executing it — R evaluates
   the file incrementally and will parse your new bytes mid-token.

## Next actions

1. **Eric:** merge PR #9 (then `tcu-2025-pull`'s PR lineage is fully absorbed; branch
   cleanup after merge).
2. Optional follow-up (noted in morning handoff, not started): post-pull completeness
   assertion — every rostered athlete has data or a logged genuine-empty reason.
3. Deferred roadmap unchanged: ≥80%/≥90% sprint-selection refinements; more games;
   linemen testing-day protocol.

## Mid-flight / environment

- Nothing running: 0 Rscript processes at closeout; machine safe to restart.
- `~/.claude/global-memory/transcripts/.errors.log` had 2 entries (7/22 Milvus
  proxy not ready; 7/23 memsearch index ETIMEDOUT ×3 during today's RAM starvation).
  Surfaced to Eric and cleared. **Post-restart smoke test:** `memsearch search "TCU" --top-k 3`.
- Scratch/verify scripts live in the job tmp dir (`~/.claude/jobs/010026e9/tmp/`):
  `verify_pull.R`, `verify_then_03.R`, `final_stats.R`, `pr_body.md` — disposable.
- `data/` and `output/` in SpeedProfiling are gitignored (FERPA); fresh as of ~4:38 PM.
