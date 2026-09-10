# Scheduled Job Durability — Run Ledger + Reconciler

Date: 2026-07-27
Status: implemented

## Problem

On 2026-07-27 the morning cadence did not run. Three independent causes stacked:

1. The machine shut down unexpectedly at 22:03 on 2026-07-26 and stayed down overnight, so the
   06:00 and 06:15 triggers were missed entirely.
2. `StartWhenAvailable` fired all catch-up runs at 07:54:28, ~8 minutes after boot, directly into
   the first-boot maintenance storm (Windows Update, Defender, Secure Boot key update, WER crash
   uploads).
3. At 07:57:07 a `winget upgrade --id Microsoft.PowerShell` began. The PowerShell 7.6.4 MSI's
   Restart Manager identified `pwsh.exe` pid 9864 — the running cadence — and shut it down at
   07:57:46. Exit code `0xC000013A` (STATUS_CONTROL_C_EXIT). `KeystoneOS-DailyBackup` died the same
   way 50 seconds earlier.

Nothing noticed. `cadence.log` had no entry for the day at all, and the failure was found only
because a human happened to ask.

`StartWhenAvailable` was already added (see `install-morning-cadence-task.ps1`) as the fix for an
earlier instance of this same class — "machine asleep at trigger time". It correctly handles
*missed trigger*. It does not handle *run started but died*, and it schedules catch-up at the
single worst moment in the boot cycle.

## Root cause

The scheduler is trusted as the record of what happened. Nothing records whether a job actually
*succeeded*, and nothing re-runs one that didn't. Every failure is therefore silent, and every
distinct cause (shutdown, crash, kill, transient error) needs its own bespoke mitigation.

Contributing: all KeystoneOS tasks had `RestartCount = 0`, so a single kill lost the whole day.
`KeystoneOS-StackDoctor` — the watchdog — was itself scheduled Mondays 06:40, inside the same blast
radius.

## Design

Two pieces, one idea: **make success an observable fact, then reconcile against it.**

### Run ledger — `outputs/run-ledger.json`

Append-only-ish record, newest first, capped at 60 entries per job:

```json
{ "version": 1,
  "jobs": {
    "morning-cadence": [
      { "date": "2026-07-27", "status": "ok", "exitCode": 0,
        "startedAt": "...", "finishedAt": "...", "durationSec": 128,
        "trigger": "reconcile", "madeUp": true }
    ] } }
```

`status` is one of `ok` | `failed` | `timeout` | `killed`. Writes are serialised by a named mutex
so the scheduled task and the reconciler cannot corrupt it.

### Job registry — `data/jobs.json`

Machine-readable, per repo convention that `data/*.json` beats prose. Each job declares its
schedule, grace period, timeout, attempt cap, and — critically — an optional `successProbe`.

The probe lets the reconciler detect success from a job's *own existing log*, not just from the
ledger. This means the reconciler is correct even for jobs that are not routed through `run-job.ps1`
(e.g. `MorningBriefing`, which is owned by another repo and already has its own retry policy). It is
what prevents a made-up run from sending a duplicate briefing email.

Probe kinds: `fileContains` (with `{DATE}` expansion in the path and pattern) and
`fileModifiedToday`.

### Wrapper — `scripts/run-job.ps1`

Acquires a per-job named mutex, runs the job as a child process with a timeout, records the outcome
to the ledger, and tees child output to `outputs/jobs/<job>-<date>.log`. The mutex is the mechanism
that makes a scheduled run and a reconciler run mutually exclusive — abandoned mutexes (holder was
killed) are detected and reclaimed, which is exactly the 2026-07-27 scenario.

### Reconciler — `scripts/keystone-reconcile.ps1`

Runs at logon (+5m) and hourly 07:00–19:00. For each job with `reconcile: true`:

```
scheduled today?  ->  no: skip
past scheduled time + graceMinutes?  ->  no: skip (not due yet)
succeeded today (ledger OR probe)?  ->  yes: skip
failed attempts today >= maxAttemptsPerDay?  ->  yes: skip, record give-up
inside makeupWindow?  ->  no: skip
mutex free?  ->  no: skip (already running)
-> run it via run-job.ps1 -Trigger reconcile
```

Idempotent and cheap: the common case is a handful of file reads and no work.

## What this buys

A single mechanism covers every cause, because it asks about *outcome* rather than *cause*:

| Failure | Before | After |
|---|---|---|
| Laptop off overnight | silently skipped | runs at logon +5m |
| Killed by PowerShell upgrade | silently lost | re-runs within the hour |
| Crash mid-run | silently lost | re-runs within the hour |
| Transient error | lost until next weekday | re-runs within the hour |
| Job genuinely broken | silent | capped attempts, recorded in ledger |

The failure mode becomes **"ran late"** instead of **"never ran, nobody knew"**.

## Supporting changes

- `RestartCount = 2`, `RestartInterval = 15m` on the pwsh tasks — cheap first line of defence that
  handles a Restart Manager kill without waiting for the next reconciler tick.
- Trigger `Delay = PT10M` so boot catch-up lands after the first-boot storm rather than inside it.
- `KeystoneOS-StackDoctor` moved from Mon 06:40 to Mon 10:30 — out of the blast radius of the thing
  it watches.
- Outlook auth freshness: the briefing degrades to an empty brief when its Playwright session
  expires, while still reporting success. The reconciler surfaces this to `.errors.log` (which is
  read at every session start) so it is visible before the next empty brief, not after.

## Non-goals

- Switching tasks to stored-credential (`Password`) logon so they run without an interactive
  session. Rejected: on a Baylor-managed device the password rotates, and every rotation would
  silently break every task — trading a rare failure for a recurring one.
- Preventing the Restart Manager kill itself. Not worth the machinery; being re-run is sufficient.

## Verification

- `tests/keystone-reconcile.ps1` — schedule matching, probe evaluation, ledger round-trip, mutual
  exclusion, attempt capping, decision table.
- Live: run the reconciler with the ledger cleared and confirm it makes up the missed job exactly
  once; run it again and confirm it does nothing.
