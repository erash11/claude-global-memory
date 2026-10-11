# Handoff — CommandCentre `/os` verification + compiler commit

**Written** 2026-09-02 · **Working dir** `~/DEV` · **Machine** macOS

This session **verified** the `/os` board that the earlier session built. It wrote no
application code. It supersedes the open-items list in
`/var/folders/.../handoff-command-centre-os-2026-09-02.md` (OS temp dir, not durable —
do not rely on that file still existing).

---

## What was asked

"Review the command-centre handoff. Is our OS command center ready to go?"

## Answer: yes, verified live

| Check | Result |
|---|---|
| `http://localhost:7373/` (old status page) | 200, unchanged |
| `http://localhost:7373/os` | 200 |
| `http://localhost:7373/api/state.json` | 200, ~0.39s |
| launchd `com.keystone.commandcentre` | up, PID 90651 (exit shows `-15`, expected) |
| Renders with live data | yes — 17 active projects, 149 skills, 841 notes, 9 routines, 40 of 4,524 artifacts |
| CORS header on the API | none (correct) |
| `/open?path=/etc/hosts`, `../../etc/passwd`, `DexaProject` | all 404 (blocked) |
| SYSTEM HEALTH | **WARN**, not BAD — sole item "Graph: 1 file left", self-clears next 09:30 run |

## Two open items from the prior handoff are now CLOSED

1. **memsearch ETIMEDOUT — fixed**, by a different session today at 12:33. The SessionEnd
   hook now re-execs itself detached (`--worker`, `stdio: 'ignore'`, `.unref()`); measured
   42ms. Full write-up:
   `~/.claude/projects/-Users-kristinarash-DEV/memory/project_memsearch-hook-timeout-cap.md`
   - **Do not conflate two different symptoms.** The ETIMEDOUT was on the session-end
     *index* hook. A *search* still takes ~9.5s — that is the query path, a separate and
     un-investigated thing. Slow search is not evidence the index fix failed.
2. **`.errors.log` — legitimately empty**, cleared 2026-09-02 07:29. The prior handoff
   warned against clearing it to make the dashboard look green. That is not what happened:
   the underlying fault was really fixed. Leave it.

## Files created or modified this session

| Path | State |
|---|---|
| `~/.claude/projects/-Users-kristinarash-DEV/memory/project_command-centre.md` | **modified** — appended the headless-Chrome verification gotcha (7,150 → 8,022 chars) |
| `~/.claude/claude-memory-compiler` (branch `session-start-progressive-disclosure`) | **committed** `a078b1c` — `hooks/session-start.py`, `scripts/flush.py`, `uv.lock` |
| `~/.claude/global-memory/handoffs/2026-09-02-command-centre-os-verification.md` | **new** — this file |
| `~/.claude/jobs/e94e87f8/tmp/os-now.png`, `os-now2.png` | scratch renders, disposable |

No CommandCentre file was touched. `~/DEV/CommandCentre` is **not a git repo** — the only
safety net is `server.py.bak-2026-09-01`.

## The compiler commit — what and why

Three files had sat uncommitted since **2026-08-29** while running live in production.
They were another session's work, not this one's; this session only recorded them in git.

- `hooks/session-start.py` — pasted the whole ~48k-char knowledge index into every session,
  blowing the 20k cap and silently truncating the recent daily log off the end, the one
  part always relevant. Now a pointer, with the log always included (6k cap).
- `scripts/flush.py` — optional 3rd CLI arg sets `LOG_DATE_OVERRIDE` so a stranded context
  file lands in ITS day's log, not today's; those entries are labelled "backfilled".
- `uv.lock` — `claude-agent-sdk` 0.2.110 → 0.2.136.

Committed on a **branch, not `main`**, because this repo's history is PR merges
(`Merge pull request #9`). **Not pushed** — closeout only auto-pushes KeystoneOS.
`hooks/session-start.py.bak-2026-08-29` was deliberately left untracked.

## Next actions, most important first

1. **Decide the S2 ring question** (still unanswered from the prior session).
   `RING_EXCLUDE` in `~/DEV/CommandCentre/server.py` keeps `COG_S2_Position_Reports` off
   the artifact ring, because the ring renders filenames as labels and those filenames
   carry athlete names. Recommendation given: **keep them out**. One line to reverse.
2. **Push the compiler branch and open a PR**, or drop it:
   `cd ~/.claude/claude-memory-compiler && git push -u origin session-start-progressive-disclosure`
3. **Optional: investigate ~9.5s memsearch query latency.** Never measured before today, so
   there is no baseline saying this is a regression. Low priority.
4. Longer-term forks are unchanged and still documented in
   `~/DEV/CommandCentre/DESIGN.md`: making skills runnable from `/os` (breaks the read-only
   invariant — a real design decision), calendar/email via a cached JSON (Eric declined),
   ring cap tuning, pointing `/` at `/os`.

## Gotchas worth not rediscovering

- **The claude-in-chrome extension cannot open `localhost` pages.** It returns
  `Frame with ID 0 is showing error page` on both `localhost` and `127.0.0.1`, while `curl`
  gets 200. That is the extension's site-permission gate, **not** a server fault. Do not go
  hunting an IPv4/IPv6 bind bug — the server is IPv4-only by design (`server.py:878`) and
  that is not the cause. Verify with headless Chrome instead:

  ```
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
    --virtual-time-budget=6000 --screenshot=/tmp/os.png --window-size=1440,900 \
    http://127.0.0.1:7373/os
  ```

  `--virtual-time-budget` is **required**. Without it the shot fires before the
  `/api/state.json` fetch resolves, every panel reads `LOADING`, and a healthy board looks
  broken.
- `launchctl kickstart -k` leaves exit `-15` on the previous instance permanently. Judge the
  service on the live **PID** in `launchctl list`, never the exit code.
- `~/.claude/global-memory/MEMORY.md` is at **2,445 of its 2,500-char cap**. Consolidate
  before adding anything there; prefer a Tier A file.
