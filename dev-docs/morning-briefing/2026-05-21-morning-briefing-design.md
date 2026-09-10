# Morning Briefing — Design Spec

**Date:** 2026-05-21
**Status:** Draft, awaiting user approval
**Author:** Eric Rash + Claude (brainstorming session)

## 1. Problem

Each weekday, items get lost in the shuffle across two inboxes (Gmail personal, Outlook work):
- emails owed a reply
- people who owe a reply and need a follow-up
- meetings that need scheduling
- forms or tasks that need returning
- general work that needs surfacing

A 7:30 a.m. email briefing should make these items unmissable, with stale items aging visibly so they get harder to ignore each day they remain unresolved.

## 2. Goals

- **G1.** A single email arrives in the user's work Outlook inbox at ~07:30 every weekday morning.
- **G2.** The email organizes outstanding work from both mailboxes into five buckets: Needs Reply, Follow Ups, Meetings to Schedule, Forms/Tasks Owed, Still Open From Prior Days, plus a brief FYI line.
- **G3.** Items unresolved from prior days carry forward with an age stamp (`[3d]`, `[5d]`) until acted on.
- **G4.** Each briefing is also archived as markdown in `Desktop/SecondBrain/morning-briefings/YYYY-MM-DD.md` for durable history.
- **G5.** The system degrades gracefully when any single component fails — partial briefings are produced rather than silence.

## 3. Non-goals

- Replying to emails on the user's behalf.
- Auto-learning the allowlist or priority signals — these are manually curated.
- Synthesizing weekend mail (system runs weekdays only).
- Replacing the user's existing `weekly-review` (Friday) or `interview-me` (end of day) skills — this complements them as a morning ritual.
- Multi-user / shared deployment. Single-user, local only.

## 4. Constraints

- **Work Outlook is "New Outlook"** (WebView2 wrapper around Outlook Web). No COM API. Reached via outlook.office.com in a browser.
- **Work device is MDM-locked.** Briefing system must run on the user's personal Windows machine (`C:\Users\eric_rash\...`), not the work laptop.
- **Conditional Access permits sign-in to outlook.office.com from this personal machine.** (Confirmed 2026-05-21.)
- **No Azure app registration assumed.** Microsoft Graph path is not anchored on; system uses browser-session-as-user approach.
- **Mailbox volume: 50–200 messages/week combined.** Filtering required; not every thread can go into the LLM prompt.

## 5. Architecture

A single Python project at `C:\Users\eric_rash\Desktop\DEV\morning-briefing\`, scheduled via Windows Task Scheduler.

```
morning-briefing/
├── sources/
│   ├── __init__.py
│   ├── outlook_web.py    # Playwright + persistent profile against OWA
│   ├── gmail_api.py      # Google API client for personal Gmail
│   └── manual_paste.py   # Fallback: reads ~/.briefing-inbox.txt
├── carryover.py          # Parses yesterday's briefing for open items
├── synthesize.py         # Claude API call: normalized inputs → structured digest
├── deliver.py            # Renders markdown + sends HTML email via Gmail SMTP
├── config.toml           # allowlist, mute_list, paths, work_email, schedule
├── secrets/              # gitignored: Playwright profile, Gmail OAuth tokens, SMTP app password
├── logs/                 # daily run logs, errors
├── run.py                # Orchestrator
└── docs/
    └── 2026-05-21-morning-briefing-design.md   (this file)
```

### Component contracts

Each source exposes a single function returning a normalized list:

```python
def fetch_recent_threads(days: int = 7) -> list[Thread]: ...

Thread = TypedDict({
    "source": Literal["outlook", "gmail", "manual"],
    "id": str,                # source-native thread id (stable across days)
    "from_name": str,
    "from_addr": str,
    "subject": str,
    "snippet": str,           # first ~400 chars of latest message
    "last_message_at": datetime,
    "my_last_reply_at": datetime | None,
    "unread": bool,
})
```

Downstream code knows nothing about which source a thread came from — strict isolation makes the synthesizer simpler and lets us swap `outlook_web.py` for a future `outlook_graph.py` without touching anything else.

## 6. Daily flow

```
07:20  Windows Task Scheduler fires run.py
07:20  Sources fetch in parallel (asyncio.gather):
         outlook_web   → headless Chromium, saved profile, capture OWA JSON
         gmail_api     → Gmail API last-7-days threads
         manual_paste  → reads ~/.briefing-inbox.txt if non-empty
07:24  carryover.py reads yesterday's briefing markdown,
       extracts "Open items" + "Still Open From Prior Days" sections,
       matches each to a current thread by thread-id (or sender+subject hash
       for cross-source matches)
07:25  synthesize.py builds prompt:
         - today's date
         - allowlist + mute_list from config
         - all filtered threads from all sources
         - carryover items with computed age
       Calls Claude API (claude-opus-4-7).
       Returns structured JSON: needs_reply, follow_ups, meetings_to_schedule,
       forms_owed, still_open, fyi.
07:27  deliver.py:
         - renders briefing markdown to Desktop/SecondBrain/morning-briefings/2026-05-21.md
         - renders HTML email body
         - sends via Gmail SMTP from eric.rash11@gmail.com to <work_email>
         - subject: "Morning Briefing — Thu May 21"
07:30  Email lands in work Outlook inbox.
```

10-minute head start on the 07:30 target absorbs latency in any single step.

## 7. Filtering rules

Sources pre-filter before threads reach the synthesizer:

**Hard drop (never reach Claude):**
- Accepted calendar invites with no follow-up text
- Senders in `mute_list` (configured per-user)
- Any `noreply@*`, `donotreply@*`, `notifications@*`
- Threads where the user's last reply is the most recent message AND `last_message_at` < user's reply

**Always surface (skip all other filters):**
- Senders in `allowlist`
- Threads flagged in OWA (use OWA's own importance/flag signal where available)

**Default (sent to Claude):**
- Everything else from the last 7 days

The allowlist starts empty. The user manually adds senders to `config.toml` as patterns of "the system should have flagged this" emerge over the first week or two.

## 8. Carryover logic

After the synthesizer produces today's structured digest, `carryover.py` walks yesterday's `.md` file:

1. Parse `▸ STILL OPEN FROM PRIOR DAYS` and the action sections (`NEEDS REPLY`, `FOLLOW UPS`, etc.) for items present yesterday.
2. For each yesterday-item, check: is there a matching thread in today's source data AND has the user's `my_last_reply_at` advanced past yesterday's `last_message_at`?
   - **Yes** → consider resolved; drop from carryover.
   - **No** → carry forward to today's `STILL OPEN` section with age incremented by 1 day.
3. Anything that has been carried forward 7+ days emits an additional `⚠ stale` marker.

Matching strategy:
- **Primary key:** source + thread-id (stable across the OWA/Gmail APIs)
- **Fallback key:** lowercase sender-address + first 60 chars of subject (handles thread-id drift, especially in manual-paste mode)

## 9. Briefing format

Email body (HTML rendering of the same content saved as markdown):

```
Subject: Morning Briefing — Thu May 21

▸ NEEDS REPLY (n)
  • <Name> — re: <subject> (<source>, <age>d old)
      <one-line context of what they're waiting for>
  ...

▸ FOLLOW UPS (n)
  • You pinged <name> about <topic> on <date> — <n> days, no reply.
  ...

▸ MEETINGS TO SCHEDULE (n)
  • <Name> wants <duration> to discuss <topic>.
    <suggested-window>
  ...

▸ FORMS / TASKS OWED (n)
  • <description> — due <date>.
  ...

▸ STILL OPEN FROM PRIOR DAYS (n)
  • [<age>d] <terse description> — original <date>
  ...

▸ FYI (<n> threads, no action needed)
  Read in Outlook if curious: <name1> / <name2> / <name3> ...
```

Each bullet capped at one or two lines. Whole briefing scannable in under 90 seconds.

## 10. Configuration

`config.toml`:

```toml
[delivery]
work_email = "<populated by user>"          # destination address
gmail_user = "eric.rash11@gmail.com"        # from-address
smtp_app_password_env = "GMAIL_APP_PASSWORD"  # read from env, never committed

[schedule]
trigger_local = "07:20"
days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
lookback_days = 7

[filtering]
allowlist = []                              # senders that always surface
mute_list = []                              # senders that never reach Claude

[paths]
archive_dir = "C:/Users/eric_rash/Desktop/SecondBrain/morning-briefings"
manual_paste_file = "C:/Users/eric_rash/.briefing-inbox.txt"
playwright_profile = "./secrets/owa-profile"
log_dir = "./logs"

[claude]
model = "claude-opus-4-7"
api_key_env = "ANTHROPIC_API_KEY"
```

## 11. Degraded modes

| Failure | Behavior |
|---|---|
| Outlook auth lapsed (Playwright sees login redirect) | Send Gmail-only briefing with top banner: `⚠ Outlook auth expired — run reauth.bat to refresh`. |
| Outlook fetch errors entirely | Same Gmail-only path. Manual paste file checked as tertiary input. |
| Gmail API errors | Outlook-only briefing with banner. |
| Claude API errors | Email still sends with banner `⚠ Synthesizer offline — raw inbox below` and the filtered raw thread list. |
| Total failure | Minimal "Briefing failed — see `logs/<date>.log`" email. **Never silence.** |
| Briefing already sent today (Task Scheduler retry / manual rerun) | Detect by archive file existence; skip email send unless `--force` flag passed. |

## 12. Testing strategy

- **Source unit tests:** golden-file inputs (cached OWA JSON, Gmail API responses, sample paste files) → asserted normalized `Thread` lists.
- **Carryover unit tests:** synthetic prior-day briefing markdown + synthetic today's threads → asserted carry-forward decisions.
- **Synthesizer integration test:** small fixed set of threads, real Claude API call, assert output JSON shape and that critical items appear. Loose content asserts (no exact-string match against an LLM response).
- **Delivery dry-run mode:** `run.py --dry-run` writes markdown + prints email body but does not SMTP.
- **End-to-end smoke:** weekly manual run with `--dry-run` to confirm nothing has rotted.

## 13. Setup checklist (deferred to implementation plan)

1. Project scaffolding + `pyproject.toml`
2. Playwright install + one-time interactive sign-in to outlook.office.com to seed the profile
3. Gmail API OAuth dance for `eric.rash11@gmail.com` (read scope)
4. Gmail App Password for SMTP (separate from OAuth, used for sending)
5. Anthropic API key in environment
6. `config.toml` populated (work_email, allowlist seed)
7. Manual end-to-end run to validate
8. Windows Task Scheduler entry: trigger 07:20 weekdays, action = `python C:\...\morning-briefing\run.py`
9. Send one test briefing, mark "Not Junk" in Outlook, optionally add Gmail to safe senders

## 14. Open questions for implementation phase

- Exact OWA JSON endpoints to intercept (need to inspect via Playwright first run).
- Whether Outlook Web's "trusted device" grace period in the user's tenant supports unattended runs for ≥7 days or requires more frequent re-auth.
- Email rendering: plain markdown-style text vs. light HTML styling for the email body.
- Whether the "FYI" line should include unread counts per sender or remain a flat name list.

These are answered during build, not blocking the spec.
