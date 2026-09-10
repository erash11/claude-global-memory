# Durability Contract, Process Ownership, and Data Boundaries

Date: 2026-08-02
Status: proposed
Supersedes in scope: `2026-07-27-scheduled-job-durability-design.md` (that design stands; this
extends it from "scheduled jobs" to "every job, hook, and backup in the stack")

## Why this revision exists

An earlier plan for this work started at the symptoms — backpressure, a watchdog, idle shutdown —
before ownership, recovery, and data safety were proven. Five independent adversarial reviews
converged on the same verdict: directionally right, too broad, wrong order. Symptom controls added
on top of an unproven ownership model produce a system that fails in new ways and hides the old
ones.

The correction is sequencing, not scope reduction. Everything below still gets built; the resource
controls just stop being first.

## 1. Safety contract (the SLOs)

These are the numbers everything else is measured against. They are commitments, not aspirations —
a change that violates one is a regression regardless of what else it improves.

| Property | Target |
|---|---|
| Hook latency | p95 < 500 ms; never blocks session startup or exit |
| Search freshness | new material searchable within 15 min while a session is active |
| Startup context | 1–2 KB typical, 8 KB hard ceiling |
| Job state | always one of the seven states below, always readable |
| Kill switch | one global switch disables all background work |

### Job state model

```
queued -> active -> succeeded
              |
              +--> deferred    (resource or lease contention; will retry)
              +--> failed      (attempt failed; retry budget remains)
              +--> quarantined (retry budget exhausted; needs a human)
              +--> cancelled   (kill switch, or superseded by a newer generation)
```

`deferred` and `failed` are distinct on purpose. The current wrapper collapses "someone else holds
the lock" and "the job broke" into the same observable, which is why contention currently looks
like breakage.

## 2. Data boundaries and authorization

Three operations that are currently entangled get separated: **backup**, **index**, and
**verify-backup**. Each gets its own entry point, its own state, and its own authorization.

Backup content is an **allowlist manifest keyed by data class and destination** — not a directory
sweep with exclusions. Excluded by default and never allowlisted without an explicit decision entry:
raw transcripts, credentials, browser session state, and any file whose class is unknown.

Failure direction is per-operation, and it is the part most easily gotten wrong:

- **Fail closed** — cloud export, destructive actions, promotion, untrusted paths. If authorization
  or classification is ambiguous, do nothing.
- **Fail open** — session startup and shutdown. A broken hook must never make a session unusable.
  It must still leave a durable error where the next session start will read it.

## 3. One process owner

Every launch path — scheduled, reconciled, manual, nightly — goes through the same managed-job
contract. Today they do not, which is why "did it run?" has more than one answer.

`scripts/run-job.ps1` is the single owner, hardened with:

- A unique run ID per attempt, and a per-attempt log (not a per-day log that attempts overwrite).
- Distinct `busy` / `deferred` / `failed` results (see the state model above).
- **Windows Job Objects** for descendant containment. `taskkill /T` is the fallback only; it misses
  processes that have been re-parented, which is exactly how orphaned indexers survive today.
- A cross-session lease containing PID, **process start time**, **boot identity**, and a **random
  owner token**. PID alone is not identity — PID reuse across a reboot is the failure this closes.
- **No silent fallback from a global lock to a session-local lock.** If the global lock cannot be
  acquired, the job is `deferred`. It does not quietly downgrade to a weaker guarantee.

## 4. Durable coalesced capture (replacing direct hook indexing)

Hooks stop indexing. A hook writes an **atomic dirty-generation / path-set record** and returns —
that is the whole hook, and it is what makes the 500 ms p95 achievable.

The drain side is an **ephemeral drain worker**, not a permanent daemon. It starts when there is
work, drains, and exits. Properties:

- At-least-once delivery with idempotent indexing. Not exactly-once — see deferred list.
- Bounded retries, then quarantine. Periodic reconciliation against the source of truth catches
  anything the queue lost.
- Transcript progress is tracked as **fingerprint + committed byte offset**. The offset never
  advances past an incomplete trailing record — a half-written JSONL line is not consumed.
- Canonical transcript roots are validated; reparse-point and path-mismatch inputs are rejected.
- An entry is acknowledged **only after a unique sentinel is actually searchable**. Not after the
  indexer exits zero.

## 5. Verifiable backups

The current backup proves it ran. It does not prove it worked.

- Stage, verify manifest and hashes, then **atomically promote**.
- **Versioned/immutable snapshots**, not a mirror that propagates deletions. A mirror faithfully
  replicates the deletion you are trying to recover from.
- Completion is a **run-specific receipt**. Not exit code, not a timestamp, not matching log text —
  all three of which can be produced by a run that did nothing.
- **Periodic restore tests into a disposable profile.** A backup that has never been restored is a
  hypothesis.

## 6. Session and resume behavior

- One compiler invocation, one bounded startup packet.
- Memory and handoffs scope to the canonical current workspace.
- Replace "session older than X" with a **resume fingerprint**: workspace, branch/HEAD, dirty state,
  harness version, hook generation, pending work. Age was always a proxy for drift and a bad one.
  - Old but unchanged → still usable, no warning.
  - Recent but drifted → warn, or block mutation.
- Structured compaction checkpoints that name the processes which were *not* restored.

## 7. Resource controls — measure first

No watermark is chosen before the numbers exist. First measure indexing **peak RAM, CPU, disk, and
cold-start cost**. Then, and only then:

high/low watermarks with hysteresis, queue-age limits, maximum deferral, backoff, circuit breakers.

Two hard rules that survive regardless of what the measurements say:

- **Never kill by executable name.** `pwsh.exe` is not an identity; killing by name is how you kill
  the user's own shell.
- **Idle shutdown stays deferred** until it demonstrates net savings, and it must respect active
  leases, remote sessions, and drain state.

## 8. Fault-injection tests

`tests/memsearch-concurrency.ps1` is currently five `Contains()` assertions against source strings.
It verifies that certain literals appear in certain files. It spawns no processes and exercises no
concurrency, so it cannot fail for any reason related to concurrency. It gets replaced.

Real cases:

- 20–100 simultaneous producers.
- Worker death **before**, **during**, and **after** indexing.
- Wrapper timeout with child *and grandchild* processes.
- Reboot, sleep, PID reuse, clock rollback, disk full, ACL denial, missing PATH.
- Milvus / index unavailability, and the retry storm that follows recovery.
- Scheduled / manual / reconciler collisions.
- Partial JSONL records that later complete.
- Backup corruption and restore.
- Remote-control activity and same-worktree collisions.

## Explicitly deferred

Not built now. Listed so they are deferred decisions rather than oversights:

- A new permanent watchdog.
- Aggressive CPU/RAM backpressure.
- Idle shutdown.
- Broad unattended automation.
- "Exactly once" guarantees.

## Implementation sequence

1. Policy matrix, SLOs, state model, baseline tests.
2. Process ownership: run IDs, receipts, Job Object containment, lease identity.
3. Separate backup from indexing.
4. Durable coalesced worker.
5. Observability and fault-injection tests.
6. *Only then* consider backpressure, watchdogs, idle shutdown, unattended execution.

## Provenance

Five independent adversarial reviews (2026-08-02). No files were changed by the review agents; this
document is the first artifact of the revision.
