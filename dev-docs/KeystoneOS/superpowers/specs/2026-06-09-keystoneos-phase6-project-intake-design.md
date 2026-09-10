# KeystoneOS Phase 6 Project Intake Design

## Purpose

KeystoneOS needs to capture all discovered work without treating every folder as a daily active project. The intake layer turns workspace inventory into an organized review packet so Eric can decide what belongs in daily rotation, what should stay visible, and what can remain archived.

## Approach

Add a `keystone intake` command that reads the generated workspace inventory, classifies each item into a bucket, and writes a dated markdown and JSON packet under `outputs/intake/`. The command is read-only: it never mutates `data/projects.json`, `projects/registry.md`, or active briefs. Promotion remains explicit through `keystone promote`.

## Buckets

- `active`: already present in `data/projects.json`.
- `daily_candidate`: high-signal unregistered code or repo folders that likely deserve active project briefs.
- `knowledge_candidate`: SecondBrain project notes or other project-note files that may deserve a project brief or link to an existing active project.
- `watch`: useful projects that should remain visible but do not need daily resume behavior yet.
- `review`: low-signal or nested candidates that should be checked manually before promotion.

## Output

The markdown packet should show counts by bucket and list the highest-value items first. For promotable items, it should include an exact command:

```powershell
.\scripts\keystone.ps1 promote "<path-or-name>" -Status "Active candidate"
```

The JSON packet should preserve the same bucket, score, signals, path, active key, and recommendation command for future dashboard or agent use.

## Constraints

- Keep the command local-first and dependency-free.
- Keep promotion explicit.
- Reuse the existing inventory scanner and scoring.
- Avoid requiring the user to answer questions before the packet can be generated.

## Verification

- A temp-fixture integration test should prove `intake` writes markdown and JSON outputs.
- The test should prove active projects stay in the `active` bucket.
- The test should prove a high-signal unregistered repo becomes a `daily_candidate`.
- The test should prove a SecondBrain-style project note becomes a `knowledge_candidate`.
- The test should prove `data/projects.json` is not changed by intake.
