# Codex SessionEnd Memory Compiler Hook

Date: 2026-07-28

## Goal

Give Codex the same durable-extraction opportunity Claude Code has at the end of
a session, while preserving the ownership boundaries between Codex raw
transcripts, the Claude memory compiler, compiled memory, and reviewed
SecondBrain knowledge.

## Confirmed Codex contract

Codex supports a main-thread `SessionEnd` lifecycle event. The command receives
JSON on stdin containing:

- `session_id`
- `transcript_path`
- `cwd`
- `hook_event_name`
- `reason`

`SessionEnd` has a maximum supported timeout of three seconds. The hook output is
advisory and cannot keep the thread open.

## Design

### Foreground launcher

`scripts/codex-hooks/session-end.ps1` must:

1. read and validate the hook JSON;
2. write a KeystoneOS event breadcrumb;
3. create a small job JSON under Codex state;
4. start a hidden background PowerShell worker; and
5. exit silently within the three-second Codex budget.

The launcher performs no LLM, compiler, or transcript parsing work.

### Background worker

`scripts/codex-hooks/session-end-memory-worker.ps1` must:

1. read the pending job;
2. acquire a per-session lock;
3. read only transcript lines not processed by an earlier successful flush;
4. extract user messages and final assistant answers;
5. exclude developer/system instructions, tool traffic, reasoning, and assistant
   commentary;
6. cap the reviewed context at approximately 15,000 characters;
7. write that context to a disposable file;
8. invoke the installed Claude memory compiler `scripts/flush.py`;
9. record the processed transcript line only after success; and
10. log failures without affecting Codex shutdown.

The worker may call the Claude compiler, but it must not directly edit compiled
knowledge articles or SecondBrain.

### Idempotency

Each session stores its last successfully processed transcript line. A repeated
`SessionEnd` with no new conversational messages is a no-op. A reopened thread
can flush only the newly appended conversation.

### Failure behavior

- Missing or malformed hook input: exit silently.
- Missing transcript, compiler, or `uv`: record a bounded error and exit.
- Existing fresh per-session lock: skip the duplicate worker.
- Compiler failure: leave the processed-line marker unchanged so a later
  `SessionEnd` can retry.
- No useful new messages: advance the marker without invoking the compiler.

## Configuration

The idempotent installer adds:

```json
"SessionEnd": [
  {
    "matcher": "other",
    "hooks": [
      {
        "type": "command",
        "command": "powershell.exe ... session-end.ps1",
        "timeout": 3
      }
    ]
  }
]
```

Existing non-Keystone hooks must be preserved. The installer must continue
backing up `~/.codex/hooks.json` before applying changes.

## Verification

Automated:

- launcher accepts the official input shape and emits no stdout;
- launcher produces one event breadcrumb and one pending job;
- dry-run worker extracts user/final-assistant text only;
- developer text, tool traffic, reasoning, and commentary are excluded;
- installer adds one `SessionEnd` hook with a timeout no greater than three
  seconds;
- repeated installer runs remain idempotent; and
- existing Codex hook tests continue to pass.

Live:

- install into `C:\Users\eric_rash\.codex\hooks.json`;
- confirm the generated JSON parses;
- run the worker against a disposable synthetic transcript;
- do not close or archive the active user thread merely to test the real event;
- report that a restart/new Codex process may be required before the updated
  hook configuration is loaded.

## Deliberate boundary

This hook automates compiler extraction, not SecondBrain promotion. SecondBrain
remains a reviewed human-synthesis layer and must be updated explicitly at a
meaningful project checkpoint.
