# Morning Briefing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python system that fetches the last 7 days of mail from Outlook Web (via Playwright) and Gmail (via API), synthesizes a structured digest via Claude API, and emails it to the user's work Outlook inbox at ~07:30 each weekday.

**Architecture:** Single-machine Python project, scheduled by Windows Task Scheduler. Five isolated components — three source adapters, a carryover parser, a synthesizer, and a deliverer — communicate through a normalized `Thread` shape. Each component is independently testable; system degrades gracefully when any single piece fails so the user is never left without a 07:30 briefing.

**Tech Stack:** Python 3.11+, Playwright (Chromium with persistent profile), `google-api-python-client` (Gmail), `anthropic` SDK (Claude API), `smtplib` (Gmail SMTP), `tomllib` (config), `pytest` (tests).

**Working Directory:** `C:\Users\eric_rash\Desktop\DEV\morning-briefing\`

---

## Task 1: Project scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `morning_briefing/__init__.py`
- Create: `morning_briefing/sources/__init__.py`
- Create: `tests/__init__.py`
- Create: `README.md`

- [ ] **Step 1: Initialize project structure**

Create `pyproject.toml`:

```toml
[project]
name = "morning-briefing"
version = "0.1.0"
description = "Daily 07:30 a.m. email briefing from Outlook + Gmail"
requires-python = ">=3.11"
dependencies = [
    "playwright>=1.45",
    "google-api-python-client>=2.130",
    "google-auth-oauthlib>=1.2",
    "anthropic>=0.40",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-asyncio>=0.23"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

- [ ] **Step 2: Create .gitignore**

```
__pycache__/
*.pyc
.venv/
secrets/
logs/
*.log
.briefing-inbox.txt
.env
```

- [ ] **Step 3: Empty package files**

`morning_briefing/__init__.py`:
```python
"""Morning Briefing — daily email digest of outstanding work."""
__version__ = "0.1.0"
```

`morning_briefing/sources/__init__.py`:
```python
"""Source adapters: outlook_web, gmail_api, manual_paste."""
```

`tests/__init__.py`: empty file.

- [ ] **Step 4: Minimal README**

`README.md`:
```markdown
# Morning Briefing

Daily 07:30 a.m. email briefing of outstanding work, drawn from Outlook Web + Gmail.

See `docs/2026-05-21-morning-briefing-design.md` for the design spec.
```

- [ ] **Step 5: Initialize git + first commit**

```bash
cd C:\Users\eric_rash\Desktop\DEV\morning-briefing
git init
git add .
git commit -m "chore: project scaffold"
```

---

## Task 2: Thread type + filter primitives

**Files:**
- Create: `morning_briefing/types.py`
- Create: `morning_briefing/filters.py`
- Test: `tests/test_filters.py`

- [ ] **Step 1: Write the failing tests**

`tests/test_filters.py`:
```python
from datetime import datetime, timezone
from morning_briefing.types import Thread
from morning_briefing.filters import apply_filters

def _thread(**overrides) -> Thread:
    base: Thread = {
        "source": "gmail",
        "id": "t1",
        "from_name": "Sarah",
        "from_addr": "sarah@example.com",
        "subject": "Q2 budget",
        "snippet": "can you review?",
        "last_message_at": datetime(2026, 5, 19, tzinfo=timezone.utc),
        "my_last_reply_at": None,
        "unread": True,
    }
    base.update(overrides)
    return base

def test_hard_drop_noreply():
    threads = [_thread(from_addr="noreply@svc.com")]
    kept = apply_filters(threads, allowlist=[], mute_list=[])
    assert kept == []

def test_hard_drop_mute_list():
    threads = [_thread(from_addr="newsletter@vendor.com")]
    kept = apply_filters(threads, allowlist=[], mute_list=["newsletter@vendor.com"])
    assert kept == []

def test_hard_drop_user_replied_last():
    threads = [_thread(
        last_message_at=datetime(2026, 5, 19, 10, tzinfo=timezone.utc),
        my_last_reply_at=datetime(2026, 5, 19, 11, tzinfo=timezone.utc),
    )]
    kept = apply_filters(threads, allowlist=[], mute_list=[])
    assert kept == []

def test_allowlist_overrides_mute():
    t = _thread(from_addr="boss@company.com")
    kept = apply_filters([t], allowlist=["boss@company.com"], mute_list=["boss@company.com"])
    assert kept == [t]

def test_default_keep():
    t = _thread()
    kept = apply_filters([t], allowlist=[], mute_list=[])
    assert kept == [t]
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/test_filters.py -v`
Expected: FAIL — `morning_briefing.types` / `morning_briefing.filters` not found.

- [ ] **Step 3: Implement types**

`morning_briefing/types.py`:
```python
from datetime import datetime
from typing import Literal, TypedDict, NotRequired

Source = Literal["outlook", "gmail", "manual"]

class Thread(TypedDict):
    source: Source
    id: str
    from_name: str
    from_addr: str
    subject: str
    snippet: str
    last_message_at: datetime
    my_last_reply_at: NotRequired[datetime | None]
    unread: bool
```

- [ ] **Step 4: Implement filters**

`morning_briefing/filters.py`:
```python
import re
from .types import Thread

_AUTOMATED = re.compile(r"^(noreply|no-reply|donotreply|do-not-reply|notifications?)@", re.I)

def apply_filters(
    threads: list[Thread],
    allowlist: list[str],
    mute_list: list[str],
) -> list[Thread]:
    allow = {a.lower() for a in allowlist}
    mute = {m.lower() for m in mute_list}
    kept: list[Thread] = []
    for t in threads:
        addr = t["from_addr"].lower()
        if addr in allow:
            kept.append(t)
            continue
        if _AUTOMATED.match(addr):
            continue
        if addr in mute:
            continue
        my_reply = t.get("my_last_reply_at")
        if my_reply and my_reply >= t["last_message_at"]:
            continue
        kept.append(t)
    return kept
```

- [ ] **Step 5: Run tests to verify pass + commit**

Run: `pytest tests/test_filters.py -v`
Expected: 5 PASS.

```bash
git add morning_briefing/types.py morning_briefing/filters.py tests/test_filters.py
git commit -m "feat: Thread type + apply_filters with TDD coverage"
```

---

## Task 3: Config loading

**Files:**
- Create: `config.toml`
- Create: `morning_briefing/config.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: Write the failing test**

`tests/test_config.py`:
```python
from pathlib import Path
from morning_briefing.config import load_config

def test_load_config(tmp_path: Path):
    cfg_file = tmp_path / "config.toml"
    cfg_file.write_text("""
[delivery]
work_email = "eric@work.example"
gmail_user = "eric.rash11@gmail.com"
smtp_app_password_env = "GMAIL_APP_PASSWORD"

[schedule]
trigger_local = "07:20"
days = ["Mon","Tue","Wed","Thu","Fri"]
lookback_days = 7

[filtering]
allowlist = ["boss@company.com"]
mute_list = []

[paths]
archive_dir = "/tmp/archive"
manual_paste_file = "/tmp/paste.txt"
playwright_profile = "/tmp/profile"
log_dir = "/tmp/logs"

[claude]
model = "claude-opus-4-7"
api_key_env = "ANTHROPIC_API_KEY"
""")
    cfg = load_config(cfg_file)
    assert cfg.delivery.work_email == "eric@work.example"
    assert cfg.filtering.allowlist == ["boss@company.com"]
    assert cfg.schedule.lookback_days == 7
    assert cfg.claude.model == "claude-opus-4-7"
```

- [ ] **Step 2: Run test to verify failure**

Run: `pytest tests/test_config.py -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Implement config loader**

`morning_briefing/config.py`:
```python
import tomllib
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class DeliveryCfg:
    work_email: str
    gmail_user: str
    smtp_app_password_env: str

@dataclass(frozen=True)
class ScheduleCfg:
    trigger_local: str
    days: list[str]
    lookback_days: int

@dataclass(frozen=True)
class FilteringCfg:
    allowlist: list[str]
    mute_list: list[str]

@dataclass(frozen=True)
class PathsCfg:
    archive_dir: Path
    manual_paste_file: Path
    playwright_profile: Path
    log_dir: Path

@dataclass(frozen=True)
class ClaudeCfg:
    model: str
    api_key_env: str

@dataclass(frozen=True)
class Config:
    delivery: DeliveryCfg
    schedule: ScheduleCfg
    filtering: FilteringCfg
    paths: PathsCfg
    claude: ClaudeCfg

def load_config(path: Path) -> Config:
    raw = tomllib.loads(path.read_text())
    p = raw["paths"]
    return Config(
        delivery=DeliveryCfg(**raw["delivery"]),
        schedule=ScheduleCfg(**raw["schedule"]),
        filtering=FilteringCfg(**raw["filtering"]),
        paths=PathsCfg(
            archive_dir=Path(p["archive_dir"]),
            manual_paste_file=Path(p["manual_paste_file"]),
            playwright_profile=Path(p["playwright_profile"]),
            log_dir=Path(p["log_dir"]),
        ),
        claude=ClaudeCfg(**raw["claude"]),
    )
```

- [ ] **Step 4: Create real `config.toml` template**

`config.toml`:
```toml
[delivery]
work_email = "REPLACE_ME@company.example"
gmail_user = "eric.rash11@gmail.com"
smtp_app_password_env = "GMAIL_APP_PASSWORD"

[schedule]
trigger_local = "07:20"
days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
lookback_days = 7

[filtering]
allowlist = []
mute_list = []

[paths]
archive_dir = "C:/Users/eric_rash/Desktop/SecondBrain/morning-briefings"
manual_paste_file = "C:/Users/eric_rash/.briefing-inbox.txt"
playwright_profile = "./secrets/owa-profile"
log_dir = "./logs"

[claude]
model = "claude-opus-4-7"
api_key_env = "ANTHROPIC_API_KEY"
```

- [ ] **Step 5: Run tests + commit**

Run: `pytest tests/test_config.py -v`
Expected: PASS.

```bash
git add config.toml morning_briefing/config.py tests/test_config.py
git commit -m "feat: typed config loading from TOML"
```

---

## Task 4: Manual paste source (simplest source)

**Files:**
- Create: `morning_briefing/sources/manual_paste.py`
- Test: `tests/test_manual_paste.py`
- Test fixture: `tests/fixtures/paste_sample.txt`

The manual-paste file uses a deliberately simple format the user can produce by hand: blocks separated by `---`, each block has `From:`, `Subject:`, `Date:`, and a body.

- [ ] **Step 1: Create test fixture**

`tests/fixtures/paste_sample.txt`:
```
From: Marcus Wells <marcus.wells@vendor.com>
Subject: Re: contract renewal
Date: 2026-05-19T14:22:00-04:00
Unread: yes

Hey — bumping this. Still need your sign-off on section 4.
---
From: HR Bot <hr@company.example>
Subject: W-9 reminder
Date: 2026-05-18T09:00:00-04:00
Unread: no

Quarterly tax form due Friday.
```

- [ ] **Step 2: Write the failing test**

`tests/test_manual_paste.py`:
```python
from pathlib import Path
from morning_briefing.sources.manual_paste import read_paste_file

FIXTURE = Path(__file__).parent / "fixtures" / "paste_sample.txt"

def test_read_paste_file_returns_threads():
    threads = read_paste_file(FIXTURE)
    assert len(threads) == 2
    assert threads[0]["from_name"] == "Marcus Wells"
    assert threads[0]["from_addr"] == "marcus.wells@vendor.com"
    assert threads[0]["subject"] == "Re: contract renewal"
    assert threads[0]["unread"] is True
    assert "section 4" in threads[0]["snippet"]
    assert threads[1]["unread"] is False

def test_missing_file_returns_empty(tmp_path: Path):
    assert read_paste_file(tmp_path / "missing.txt") == []
```

- [ ] **Step 3: Run test to verify failure**

Run: `pytest tests/test_manual_paste.py -v`
Expected: FAIL — module not found.

- [ ] **Step 4: Implement manual paste parser**

`morning_briefing/sources/manual_paste.py`:
```python
import hashlib
import re
from datetime import datetime
from pathlib import Path
from ..types import Thread

_FROM_RE = re.compile(r"^From:\s*(.+?)\s*<(.+?)>\s*$", re.M)
_SUBJ_RE = re.compile(r"^Subject:\s*(.+)$", re.M)
_DATE_RE = re.compile(r"^Date:\s*(.+)$", re.M)
_UNREAD_RE = re.compile(r"^Unread:\s*(yes|no)\s*$", re.M | re.I)

def read_paste_file(path: Path) -> list[Thread]:
    if not path.exists() or not path.read_text().strip():
        return []
    blocks = [b.strip() for b in path.read_text().split("---") if b.strip()]
    threads: list[Thread] = []
    for block in blocks:
        fm = _FROM_RE.search(block)
        sm = _SUBJ_RE.search(block)
        dm = _DATE_RE.search(block)
        um = _UNREAD_RE.search(block)
        if not (fm and sm and dm):
            continue
        body_start = max(m.end() for m in (fm, sm, dm, um) if m)
        body = block[body_start:].strip()
        addr = fm.group(2).strip()
        subj = sm.group(1).strip()
        thread_id = "manual:" + hashlib.sha1(f"{addr}|{subj}".encode()).hexdigest()[:16]
        threads.append({
            "source": "manual",
            "id": thread_id,
            "from_name": fm.group(1).strip(),
            "from_addr": addr,
            "subject": subj,
            "snippet": body[:400],
            "last_message_at": datetime.fromisoformat(dm.group(1).strip()),
            "my_last_reply_at": None,
            "unread": bool(um and um.group(1).lower() == "yes"),
        })
    return threads
```

- [ ] **Step 5: Run tests + commit**

Run: `pytest tests/test_manual_paste.py -v`
Expected: 2 PASS.

```bash
git add morning_briefing/sources/manual_paste.py tests/test_manual_paste.py tests/fixtures/paste_sample.txt
git commit -m "feat: manual paste source adapter"
```

---

## Task 5: Gmail source (auth + fetch)

**Files:**
- Create: `morning_briefing/sources/gmail_api.py`
- Create: `scripts/gmail_auth.py` (one-time interactive auth)
- Test: `tests/test_gmail_api.py`

Gmail OAuth credentials must be provisioned out-of-band: download `credentials.json` from Google Cloud Console (Gmail API enabled, OAuth client type = Desktop). Place at `secrets/gmail_credentials.json`. The auth script produces `secrets/gmail_token.json`.

- [ ] **Step 1: One-time auth helper script**

`scripts/gmail_auth.py`:
```python
"""Run once: python scripts/gmail_auth.py — produces secrets/gmail_token.json."""
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
SECRETS = Path(__file__).resolve().parent.parent / "secrets"

def main():
    SECRETS.mkdir(exist_ok=True)
    flow = InstalledAppFlow.from_client_secrets_file(
        str(SECRETS / "gmail_credentials.json"), SCOPES
    )
    creds = flow.run_local_server(port=0)
    (SECRETS / "gmail_token.json").write_text(creds.to_json())
    print("Saved token to secrets/gmail_token.json")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Write the failing test (mock-based)**

`tests/test_gmail_api.py`:
```python
from datetime import datetime, timezone
from unittest.mock import MagicMock
from morning_briefing.sources.gmail_api import threads_from_messages

def _msg(message_id, thread_id, sender, subject, snippet, date_ms, labels):
    return {
        "id": message_id,
        "threadId": thread_id,
        "snippet": snippet,
        "internalDate": str(date_ms),
        "labelIds": labels,
        "payload": {"headers": [
            {"name": "From", "value": sender},
            {"name": "Subject", "value": subject},
        ]},
    }

def test_threads_from_messages_groups_by_thread():
    me = "eric.rash11@gmail.com"
    msgs = [
        _msg("m1", "t1", "Sarah K <sarah@x.com>", "Re: budget", "snippet1",
             1747756800000, ["UNREAD", "INBOX"]),
        _msg("m2", "t1", f"Eric <{me}>", "Re: budget", "my reply",
             1747843200000, ["SENT"]),
        _msg("m3", "t2", "Marcus <marcus@y.com>", "Contract",
             "still waiting", 1747670400000, ["UNREAD", "INBOX"]),
    ]
    threads = threads_from_messages(msgs, me)
    assert len(threads) == 2
    by_id = {t["id"]: t for t in threads}
    t1 = by_id["gmail:t1"]
    assert t1["my_last_reply_at"] is not None
    assert t1["my_last_reply_at"] >= t1["last_message_at"] - \
        (t1["my_last_reply_at"] - t1["my_last_reply_at"])  # sanity
    t2 = by_id["gmail:t2"]
    assert t2["my_last_reply_at"] is None
    assert t2["unread"] is True
```

- [ ] **Step 3: Run test to verify failure**

Run: `pytest tests/test_gmail_api.py -v`
Expected: FAIL — module not found.

- [ ] **Step 4: Implement Gmail source**

`morning_briefing/sources/gmail_api.py`:
```python
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from ..types import Thread

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
_FROM_RE = re.compile(r"(?:(.*?)\s*<)?([^<>\s]+@[^<>\s]+)>?")

def _parse_from(value: str) -> tuple[str, str]:
    m = _FROM_RE.search(value or "")
    if not m:
        return ("", "")
    name = (m.group(1) or "").strip().strip('"')
    return (name, m.group(2).strip())

def _header(payload: dict, name: str) -> str:
    for h in payload.get("headers", []):
        if h.get("name", "").lower() == name.lower():
            return h.get("value", "")
    return ""

def threads_from_messages(messages: list[dict[str, Any]], me_addr: str) -> list[Thread]:
    by_thread: dict[str, list[dict]] = {}
    for m in messages:
        by_thread.setdefault(m["threadId"], []).append(m)
    threads: list[Thread] = []
    for tid, msgs in by_thread.items():
        msgs.sort(key=lambda m: int(m["internalDate"]))
        latest = msgs[-1]
        last_dt = datetime.fromtimestamp(int(latest["internalDate"]) / 1000, tz=timezone.utc)
        from_name, from_addr = _parse_from(_header(latest["payload"], "From"))
        subject = _header(latest["payload"], "Subject")
        unread = "UNREAD" in latest.get("labelIds", [])
        my_last: datetime | None = None
        for m in msgs:
            _, addr = _parse_from(_header(m["payload"], "From"))
            if addr.lower() == me_addr.lower():
                dt = datetime.fromtimestamp(int(m["internalDate"]) / 1000, tz=timezone.utc)
                if my_last is None or dt > my_last:
                    my_last = dt
        threads.append({
            "source": "gmail",
            "id": f"gmail:{tid}",
            "from_name": from_name,
            "from_addr": from_addr,
            "subject": subject,
            "snippet": latest.get("snippet", "")[:400],
            "last_message_at": last_dt,
            "my_last_reply_at": my_last,
            "unread": unread,
        })
    return threads

def fetch_recent_threads(token_path: Path, me_addr: str, days: int = 7) -> list[Thread]:
    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    svc = build("gmail", "v1", credentials=creds, cache_discovery=False)
    after = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y/%m/%d")
    listing = svc.users().messages().list(
        userId="me", q=f"after:{after}", maxResults=500
    ).execute()
    ids = [m["id"] for m in listing.get("messages", [])]
    msgs = []
    for mid in ids:
        msgs.append(svc.users().messages().get(
            userId="me", id=mid, format="metadata",
            metadataHeaders=["From", "Subject"]
        ).execute())
    return threads_from_messages(msgs, me_addr)
```

- [ ] **Step 5: Run tests + commit**

Run: `pytest tests/test_gmail_api.py -v`
Expected: PASS.

```bash
git add morning_briefing/sources/gmail_api.py scripts/gmail_auth.py tests/test_gmail_api.py
git commit -m "feat: Gmail source adapter with OAuth + tests"
```

---

## Task 6: Outlook Web source (Playwright + persistent profile)

**Files:**
- Create: `morning_briefing/sources/outlook_web.py`
- Create: `scripts/seed_outlook_profile.py` (one-time interactive sign-in)
- Test: `tests/test_outlook_web.py`

OWA's frontend calls a JSON endpoint (typically under `/owa/service.svc?action=FindItem` or `/mail/...`) to populate the inbox. The script intercepts the *response* via Playwright's `page.on("response", ...)`, captures the JSON, and never scrapes the DOM. Exact endpoint URL varies by tenant and is discovered during the seeding step.

- [ ] **Step 1: One-time profile seeding script**

`scripts/seed_outlook_profile.py`:
```python
"""Run once: opens a real Chromium window so you can sign in to Outlook Web.
Saved session sits at the profile path configured in config.toml.
Check 'stay signed in' / 'trust this device' when prompted."""
import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

async def main(profile_dir: Path):
    profile_dir.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir), headless=False
        )
        page = await ctx.new_page()
        await page.goto("https://outlook.office.com/mail/")
        print("Sign in, then close the window when the inbox is visible.")
        await page.wait_for_event("close", timeout=0)
        await ctx.close()

if __name__ == "__main__":
    profile = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("./secrets/owa-profile")
    asyncio.run(main(profile))
```

- [ ] **Step 2: Write the failing test (parser-only, no live browser)**

`tests/test_outlook_web.py`:
```python
from morning_briefing.sources.outlook_web import threads_from_owa_payload

SAMPLE_PAYLOAD = {
    "Body": {
        "ResponseMessages": {
            "Items": [{
                "RootFolder": {
                    "Items": [
                        {
                            "ItemId": {"Id": "AAA111"},
                            "ConversationId": {"Id": "CONV1"},
                            "From": {"Mailbox": {
                                "Name": "Sarah Klein",
                                "EmailAddress": "sarah.klein@company.example",
                            }},
                            "Subject": "Q2 budget review",
                            "Preview": "Need your sign-off on lines 4-7",
                            "DateTimeReceived": "2026-05-19T13:00:00Z",
                            "IsRead": False,
                            "LastModifiedTime": "2026-05-19T13:00:00Z",
                        },
                        {
                            "ItemId": {"Id": "BBB222"},
                            "ConversationId": {"Id": "CONV2"},
                            "From": {"Mailbox": {
                                "Name": "Notifier",
                                "EmailAddress": "noreply@svc.example",
                            }},
                            "Subject": "Build passed",
                            "Preview": "ok",
                            "DateTimeReceived": "2026-05-20T01:00:00Z",
                            "IsRead": True,
                            "LastModifiedTime": "2026-05-20T01:00:00Z",
                        },
                    ]
                }
            }]
        }
    }
}

def test_threads_from_owa_payload():
    threads = threads_from_owa_payload(SAMPLE_PAYLOAD)
    assert len(threads) == 2
    by_subj = {t["subject"]: t for t in threads}
    assert by_subj["Q2 budget review"]["from_addr"] == "sarah.klein@company.example"
    assert by_subj["Q2 budget review"]["unread"] is True
    assert by_subj["Q2 budget review"]["id"].startswith("outlook:")
    assert by_subj["Build passed"]["unread"] is False
```

- [ ] **Step 3: Run test to verify failure**

Run: `pytest tests/test_outlook_web.py -v`
Expected: FAIL — module not found.

- [ ] **Step 4: Implement OWA source**

`morning_briefing/sources/outlook_web.py`:
```python
"""Outlook Web source via Playwright persistent profile.

Strategy: launch headless Chromium with a saved user-data-dir, navigate to
outlook.office.com/mail, intercept the inbox-listing JSON response, return
parsed Threads. DOM is never scraped.
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from playwright.async_api import async_playwright, TimeoutError as PWTimeout
from ..types import Thread

class OutlookAuthError(RuntimeError):
    """Raised when OWA returns the login redirect, meaning the profile auth lapsed."""

def _items_from_payload(payload: dict[str, Any]) -> list[dict]:
    """Walk known OWA response shape to the message list."""
    items: list[dict] = []
    try:
        for resp in payload["Body"]["ResponseMessages"]["Items"]:
            items.extend(resp["RootFolder"]["Items"])
    except (KeyError, TypeError):
        pass
    return items

def threads_from_owa_payload(payload: dict[str, Any]) -> list[Thread]:
    items = _items_from_payload(payload)
    threads: list[Thread] = []
    for it in items:
        mailbox = it.get("From", {}).get("Mailbox", {})
        addr = mailbox.get("EmailAddress", "")
        if not addr:
            continue
        threads.append({
            "source": "outlook",
            "id": f"outlook:{it.get('ConversationId', {}).get('Id', it.get('ItemId', {}).get('Id', ''))}",
            "from_name": mailbox.get("Name", ""),
            "from_addr": addr,
            "subject": it.get("Subject", ""),
            "snippet": (it.get("Preview", "") or "")[:400],
            "last_message_at": datetime.fromisoformat(
                it["DateTimeReceived"].replace("Z", "+00:00")
            ),
            "my_last_reply_at": None,
            "unread": not it.get("IsRead", False),
        })
    return threads

async def fetch_recent_threads(profile_dir: Path, timeout_s: int = 45) -> list[Thread]:
    captured: list[dict] = []

    async def on_response(resp):
        url = resp.url
        if "outlook.office.com" not in url:
            return
        # Heuristic: any JSON response that looks like an inbox listing
        if any(k in url for k in ("FindItem", "MessageList", "/mail/v9/")):
            try:
                if "application/json" in (resp.headers.get("content-type") or ""):
                    captured.append(await resp.json())
            except Exception:
                pass

    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir), headless=True
        )
        page = await ctx.new_page()
        page.on("response", lambda r: asyncio.create_task(on_response(r)))
        try:
            await page.goto("https://outlook.office.com/mail/", timeout=timeout_s * 1000)
            if "login.microsoftonline.com" in page.url:
                await ctx.close()
                raise OutlookAuthError("Outlook profile auth has lapsed.")
            # give frontend time to issue the listing call
            await page.wait_for_load_state("networkidle", timeout=timeout_s * 1000)
        except PWTimeout:
            pass
        finally:
            await ctx.close()

    threads: list[Thread] = []
    for payload in captured:
        threads.extend(threads_from_owa_payload(payload))
    # de-dup by id
    seen, unique = set(), []
    for t in threads:
        if t["id"] in seen:
            continue
        seen.add(t["id"])
        unique.append(t)
    return unique
```

- [ ] **Step 5: Run tests + commit**

Run: `pytest tests/test_outlook_web.py -v`
Expected: PASS.

```bash
git add morning_briefing/sources/outlook_web.py scripts/seed_outlook_profile.py tests/test_outlook_web.py
git commit -m "feat: Outlook Web source via Playwright + persistent profile"
```

> **Note for execution:** the exact `FindItem` / `MessageList` endpoint substrings above are heuristics. After running `seed_outlook_profile.py` for the first time, run `outlook_web.fetch_recent_threads` once with `headless=False` and Chromium DevTools open to confirm which URLs return the inbox JSON in your tenant, then adjust the `any(k in url for k in ...)` heuristic if needed. This is the only build-time discovery step.

---

## Task 7: Carryover parser + resolver

**Files:**
- Create: `morning_briefing/carryover.py`
- Test: `tests/test_carryover.py`
- Test fixture: `tests/fixtures/yesterday.md`

Three concerns: parse yesterday's markdown into `OpenItem`s, age them by date delta, and check today's *unfiltered* source data for evidence the user has acted (so resolved items drop instead of being carried forward forever).

- [ ] **Step 1: Create test fixture**

`tests/fixtures/yesterday.md`:
```markdown
# Morning Briefing — Wed May 20

▸ NEEDS REPLY (1)
- Sarah Klein — re: Q2 budget review (outlook, 2d old)
    She's waiting on your sign-off.

▸ FOLLOW UPS (1)
- You pinged Devin about the GPS contract on May 14 — 6 days, no reply.

▸ STILL OPEN FROM PRIOR DAYS (1)
- [4d] Reply to Marcus re: vendor renewal — original May 16
```

- [ ] **Step 2: Write the failing test**

`tests/test_carryover.py`:
```python
from datetime import date
from pathlib import Path
from morning_briefing.carryover import parse_open_items, age_carried

FIXTURE = Path(__file__).parent / "fixtures" / "yesterday.md"

def test_parse_open_items():
    items = parse_open_items(FIXTURE.read_text())
    descs = [i.description for i in items]
    assert "Sarah Klein" in descs[0]
    assert any("Marcus" in d for d in descs)
    assert any("Devin" in d for d in descs)
    assert len(items) == 3

def test_age_carried_increments():
    items = parse_open_items(FIXTURE.read_text())
    aged = age_carried(items, yesterday=date(2026, 5, 20), today=date(2026, 5, 21))
    marcus = next(i for i in aged if "Marcus" in i.description)
    assert marcus.age_days == 5  # was [4d], +1

def test_drop_resolved_items_by_user_reply():
    from datetime import datetime, timezone
    from morning_briefing.carryover import drop_resolved
    items = parse_open_items(FIXTURE.read_text())
    # Marcus thread now has the user's reply as the latest message → resolved
    threads = [{
        "source": "outlook", "id": "outlook:marcus-vendor",
        "from_name": "Marcus", "from_addr": "marcus@vendor.com",
        "subject": "Re: vendor renewal", "snippet": "...",
        "last_message_at": datetime(2026, 5, 20, 10, tzinfo=timezone.utc),
        "my_last_reply_at": datetime(2026, 5, 20, 11, tzinfo=timezone.utc),
        "unread": False,
    }]
    surviving = drop_resolved(items, threads)
    assert all("Marcus" not in i.description for i in surviving)
    # Sarah and Devin items remain (no matching thread or no reply)
    assert any("Sarah" in i.description for i in surviving)
    assert any("Devin" in i.description for i in surviving)
```

- [ ] **Step 3: Run test to verify failure**

Run: `pytest tests/test_carryover.py -v`
Expected: FAIL — module not found.

- [ ] **Step 4: Implement carryover parser**

`morning_briefing/carryover.py`:
```python
import re
from dataclasses import dataclass, replace
from datetime import date

@dataclass(frozen=True)
class OpenItem:
    bucket: str           # NEEDS REPLY / FOLLOW UPS / STILL OPEN / ...
    description: str      # full bullet text minus age tag
    age_days: int         # 0 if not previously aged

_SECTION_RE = re.compile(r"^▸\s+([A-Z /]+?)\s*(?:\(\d+\))?\s*$", re.M)
_AGE_RE = re.compile(r"\[(\d+)d\]\s*")
_BULLET_RE = re.compile(r"^[\-•]\s+(.*)$")

def parse_open_items(markdown: str) -> list[OpenItem]:
    sections = list(_SECTION_RE.finditer(markdown))
    items: list[OpenItem] = []
    for i, sec in enumerate(sections):
        bucket = sec.group(1).strip()
        if bucket == "FYI":
            continue
        start = sec.end()
        end = sections[i + 1].start() if i + 1 < len(sections) else len(markdown)
        body = markdown[start:end]
        for line in body.splitlines():
            m = _BULLET_RE.match(line.strip())
            if not m:
                continue
            text = m.group(1).strip()
            age_match = _AGE_RE.search(text)
            age_days = int(age_match.group(1)) if age_match else 0
            description = _AGE_RE.sub("", text).strip()
            items.append(OpenItem(bucket=bucket, description=description, age_days=age_days))
    return items

def age_carried(items: list[OpenItem], yesterday: date, today: date) -> list[OpenItem]:
    delta = (today - yesterday).days
    return [replace(i, age_days=i.age_days + delta) for i in items]

def _normalize(s: str) -> str:
    return "".join(ch.lower() for ch in s if ch.isalnum())

def drop_resolved(items: list[OpenItem], threads: list[dict]) -> list[OpenItem]:
    """Drop items where today's source data shows the user has now replied.

    Matching is fuzzy because carryover items are free-form strings (sender name,
    short topic) rather than thread ids. For each item, find any thread where
    (a) the sender name OR address appears in the item description, and
    (b) the user's reply is the most recent message in that thread.
    """
    resolved_signals = []
    for t in threads:
        my_reply = t.get("my_last_reply_at")
        if my_reply and my_reply >= t["last_message_at"]:
            resolved_signals.append({
                "name_key": _normalize(t.get("from_name", "")),
                "addr_local": (t.get("from_addr", "").split("@", 1)[0] or "").lower(),
                "subject_key": _normalize(t.get("subject", "")),
            })
    if not resolved_signals:
        return items

    surviving: list[OpenItem] = []
    for item in items:
        desc_norm = _normalize(item.description)
        desc_lower = item.description.lower()
        is_resolved = False
        for sig in resolved_signals:
            if sig["name_key"] and sig["name_key"] in desc_norm:
                is_resolved = True
                break
            if sig["addr_local"] and sig["addr_local"] in desc_lower:
                is_resolved = True
                break
        if not is_resolved:
            surviving.append(item)
    return surviving
```

- [ ] **Step 5: Run tests + commit**

Run: `pytest tests/test_carryover.py -v`
Expected: 3 PASS.

```bash
git add morning_briefing/carryover.py tests/test_carryover.py tests/fixtures/yesterday.md
git commit -m "feat: carryover parser + resolver for prior-day briefing"
```

---

## Task 8: Synthesizer (Claude API call)

**Files:**
- Create: `morning_briefing/synthesize.py`
- Test: `tests/test_synthesize.py`

- [ ] **Step 1: Write the failing test**

`tests/test_synthesize.py`:
```python
from morning_briefing.synthesize import build_prompt
from morning_briefing.carryover import OpenItem
from datetime import datetime, timezone, date

def _t(addr, subj):
    return {
        "source": "gmail", "id": f"gmail:{addr}",
        "from_name": "X", "from_addr": addr,
        "subject": subj, "snippet": "...",
        "last_message_at": datetime(2026, 5, 19, tzinfo=timezone.utc),
        "my_last_reply_at": None, "unread": True,
    }

def test_build_prompt_includes_threads_and_carryover():
    threads = [_t("a@x.com", "hello"), _t("b@x.com", "form")]
    carry = [OpenItem(bucket="STILL OPEN", description="Reply to Marcus", age_days=5)]
    prompt = build_prompt(
        today=date(2026, 5, 21),
        threads=threads,
        carryover=carry,
        allowlist=["boss@company.com"],
    )
    assert "2026-05-21" in prompt
    assert "a@x.com" in prompt
    assert "Reply to Marcus" in prompt
    assert "[5d]" in prompt
    assert "boss@company.com" in prompt
    # contract reminder for the model:
    assert "needs_reply" in prompt
    assert "follow_ups" in prompt
```

- [ ] **Step 2: Run test to verify failure**

Run: `pytest tests/test_synthesize.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement synthesizer**

`morning_briefing/synthesize.py`:
```python
import json
import os
from dataclasses import dataclass, asdict
from datetime import date
from anthropic import Anthropic
from .types import Thread
from .carryover import OpenItem

@dataclass(frozen=True)
class Digest:
    needs_reply: list[dict]
    follow_ups: list[dict]
    meetings_to_schedule: list[dict]
    forms_owed: list[dict]
    still_open: list[dict]
    fyi: list[dict]

SYSTEM = """You are a personal email triage assistant.

You receive a date, a list of recent email threads from the user's Outlook and Gmail
mailboxes, an allowlist of senders that always matter, and a list of items still open
from prior days.

Categorize each relevant thread into exactly one bucket:
- needs_reply: someone is waiting on the user to respond
- follow_ups: the user is waiting on someone else; flag if >3 days
- meetings_to_schedule: someone wants a meeting that isn't yet on the calendar
- forms_owed: a form, signature, acknowledgment, or task the user must complete
- still_open: ongoing carryover items that have not been resolved
- fyi: informational only, no action needed

Return ONLY valid JSON matching this schema, no prose:
{
  "needs_reply": [{"who": str, "subject": str, "source": str, "age_days": int, "context": str}],
  "follow_ups": [{"who": str, "topic": str, "pinged_on": str, "days_since": int}],
  "meetings_to_schedule": [{"who": str, "topic": str, "suggested_window": str}],
  "forms_owed": [{"description": str, "due": str}],
  "still_open": [{"age_days": int, "description": str, "original_date": str}],
  "fyi": [{"who": str, "subject": str}]
}

Keep each context/description under 140 chars. Be terse. Be honest about uncertainty.
"""

def build_prompt(
    today: date,
    threads: list[Thread],
    carryover: list[OpenItem],
    allowlist: list[str],
) -> str:
    thread_json = [
        {
            "id": t["id"], "source": t["source"],
            "from_name": t["from_name"], "from_addr": t["from_addr"],
            "subject": t["subject"], "snippet": t["snippet"],
            "last_message_at": t["last_message_at"].isoformat(),
            "my_last_reply_at": t["my_last_reply_at"].isoformat() if t.get("my_last_reply_at") else None,
            "unread": t["unread"],
        }
        for t in threads
    ]
    carry_json = [
        {"bucket": c.bucket, "description": c.description, "age_days": c.age_days,
         "tag": f"[{c.age_days}d]"}
        for c in carryover
    ]
    return (
        f"Today is {today.isoformat()}.\n\n"
        f"Allowlist (always surface): {json.dumps(allowlist)}\n\n"
        f"Threads (last 7 days, filtered):\n{json.dumps(thread_json, indent=2)}\n\n"
        f"Carryover from prior days:\n{json.dumps(carry_json, indent=2)}\n\n"
        f"Return the JSON digest now. Buckets: needs_reply, follow_ups, "
        f"meetings_to_schedule, forms_owed, still_open, fyi."
    )

def synthesize(
    today: date,
    threads: list[Thread],
    carryover: list[OpenItem],
    allowlist: list[str],
    model: str,
    api_key_env: str,
) -> Digest:
    prompt = build_prompt(today, threads, carryover, allowlist)
    client = Anthropic(api_key=os.environ[api_key_env])
    resp = client.messages.create(
        model=model, max_tokens=4000, system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    data = json.loads(text)
    return Digest(**{k: data.get(k, []) for k in Digest.__dataclass_fields__})
```

- [ ] **Step 4: Run tests + commit**

Run: `pytest tests/test_synthesize.py -v`
Expected: PASS.

```bash
git add morning_briefing/synthesize.py tests/test_synthesize.py
git commit -m "feat: Claude-backed synthesizer with prompt unit-test"
```

---

## Task 9: Renderer + delivery

**Files:**
- Create: `morning_briefing/deliver.py`
- Test: `tests/test_deliver.py`

- [ ] **Step 1: Write the failing test**

`tests/test_deliver.py`:
```python
from datetime import date
from morning_briefing.deliver import render_markdown
from morning_briefing.synthesize import Digest

def test_render_markdown_sections():
    d = Digest(
        needs_reply=[{"who": "Sarah", "subject": "budget", "source": "outlook",
                      "age_days": 2, "context": "needs sign-off"}],
        follow_ups=[{"who": "Devin", "topic": "GPS contract",
                     "pinged_on": "May 14", "days_since": 7}],
        meetings_to_schedule=[],
        forms_owed=[{"description": "W-9 form", "due": "May 23"}],
        still_open=[{"age_days": 5, "description": "Reply to Marcus",
                     "original_date": "May 16"}],
        fyi=[{"who": "Spencer", "subject": "ops update"}],
    )
    md = render_markdown(d, today=date(2026, 5, 21))
    assert "Morning Briefing — Thu May 21" in md
    assert "▸ NEEDS REPLY" in md
    assert "Sarah" in md and "needs sign-off" in md
    assert "▸ MEETINGS TO SCHEDULE (0)" not in md  # empty buckets are skipped
    assert "[5d]" in md
    assert "Spencer" in md
```

- [ ] **Step 2: Run test to verify failure**

Run: `pytest tests/test_deliver.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement renderer + delivery**

`morning_briefing/deliver.py`:
```python
import os
import smtplib
from datetime import date
from email.message import EmailMessage
from pathlib import Path
from .synthesize import Digest

def render_markdown(d: Digest, today: date, banner: str | None = None) -> str:
    lines: list[str] = [f"# Morning Briefing — {today.strftime('%a %b %d')}", ""]
    if banner:
        lines.append(f"> {banner}")
        lines.append("")

    def section(title: str, items: list[dict], render_one):
        if not items:
            return
        lines.append(f"▸ {title} ({len(items)})")
        for item in items:
            lines.append(f"- {render_one(item)}")
        lines.append("")

    section("NEEDS REPLY", d.needs_reply,
        lambda i: f"{i['who']} — re: {i['subject']} ({i['source']}, {i['age_days']}d old)\n    {i['context']}")
    section("FOLLOW UPS", d.follow_ups,
        lambda i: f"You pinged {i['who']} about {i['topic']} on {i['pinged_on']} — {i['days_since']} days, no reply.")
    section("MEETINGS TO SCHEDULE", d.meetings_to_schedule,
        lambda i: f"{i['who']} wants {i.get('topic','time')} — {i['suggested_window']}")
    section("FORMS / TASKS OWED", d.forms_owed,
        lambda i: f"{i['description']} — due {i['due']}.")
    section("STILL OPEN FROM PRIOR DAYS", d.still_open,
        lambda i: f"[{i['age_days']}d] {i['description']} — original {i['original_date']}")
    if d.fyi:
        names = " / ".join(i.get("who", "?") for i in d.fyi)
        lines.append(f"▸ FYI ({len(d.fyi)} threads, no action needed)")
        lines.append(f"  Read in Outlook if curious: {names}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"

def write_archive(markdown: str, archive_dir: Path, today: date) -> Path:
    archive_dir.mkdir(parents=True, exist_ok=True)
    path = archive_dir / f"{today.isoformat()}.md"
    path.write_text(markdown, encoding="utf-8")
    return path

def send_email(
    markdown: str,
    today: date,
    gmail_user: str,
    smtp_password_env: str,
    to_addr: str,
) -> None:
    msg = EmailMessage()
    msg["Subject"] = f"Morning Briefing — {today.strftime('%a %b %d')}"
    msg["From"] = gmail_user
    msg["To"] = to_addr
    msg.set_content(markdown)  # plain-text body; clients will render the bullets readably
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(gmail_user, os.environ[smtp_password_env])
        s.send_message(msg)
```

- [ ] **Step 4: Run tests + commit**

Run: `pytest tests/test_deliver.py -v`
Expected: PASS.

```bash
git add morning_briefing/deliver.py tests/test_deliver.py
git commit -m "feat: markdown render + Gmail SMTP delivery"
```

---

## Task 10: Orchestrator (`run.py`)

**Files:**
- Create: `run.py`
- Create: `scripts/reauth.bat`

- [ ] **Step 1: Write the orchestrator**

`run.py`:
```python
"""Morning Briefing orchestrator. Run by Windows Task Scheduler at 07:20 weekdays."""
import argparse
import asyncio
import logging
import sys
import traceback
from datetime import date, timedelta
from pathlib import Path

from morning_briefing.config import load_config, Config
from morning_briefing.filters import apply_filters
from morning_briefing.sources import gmail_api, manual_paste, outlook_web
from morning_briefing.sources.outlook_web import OutlookAuthError
from morning_briefing.carryover import parse_open_items, age_carried, drop_resolved
from morning_briefing.synthesize import synthesize, Digest
from morning_briefing.deliver import render_markdown, write_archive, send_email

def setup_logging(log_dir: Path, today: date) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_dir / f"{today.isoformat()}.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

async def gather_sources(cfg: Config) -> tuple[list, str | None]:
    """Fetch from all sources concurrently. Returns (threads, banner_or_none)."""
    log = logging.getLogger("sources")
    banner: str | None = None
    gmail_threads, outlook_threads, manual_threads = [], [], []

    async def run_outlook():
        nonlocal outlook_threads, banner
        try:
            outlook_threads = await outlook_web.fetch_recent_threads(cfg.paths.playwright_profile)
        except OutlookAuthError:
            banner = "⚠ Outlook auth expired — run scripts/reauth.bat to refresh."
            log.warning("Outlook auth expired")
        except Exception as e:
            banner = f"⚠ Outlook fetch failed: {e}. See logs."
            log.exception("Outlook fetch failed")

    async def run_gmail():
        nonlocal gmail_threads
        try:
            token = Path("./secrets/gmail_token.json")
            gmail_threads = await asyncio.to_thread(
                gmail_api.fetch_recent_threads, token, cfg.delivery.gmail_user,
                cfg.schedule.lookback_days,
            )
        except Exception:
            log.exception("Gmail fetch failed")

    def run_manual():
        nonlocal manual_threads
        try:
            manual_threads = manual_paste.read_paste_file(cfg.paths.manual_paste_file)
        except Exception:
            log.exception("Manual paste read failed")

    run_manual()
    await asyncio.gather(run_outlook(), run_gmail())
    return gmail_threads + outlook_threads + manual_threads, banner

def load_carryover(archive_dir: Path, today: date):
    yesterday = today - timedelta(days=1)
    # walk back up to 3 days to handle weekends
    for back in range(1, 4):
        candidate = archive_dir / f"{(today - timedelta(days=back)).isoformat()}.md"
        if candidate.exists():
            items = parse_open_items(candidate.read_text(encoding="utf-8"))
            return age_carried(items, yesterday=today - timedelta(days=back), today=today)
    return []

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.toml", type=Path)
    parser.add_argument("--dry-run", action="store_true", help="Skip email send.")
    parser.add_argument("--force", action="store_true", help="Send even if today's archive exists.")
    args = parser.parse_args(argv)

    cfg = load_config(args.config)
    today = date.today()
    setup_logging(cfg.paths.log_dir, today)
    log = logging.getLogger("run")

    archive_path = cfg.paths.archive_dir / f"{today.isoformat()}.md"
    if archive_path.exists() and not args.force and not args.dry_run:
        log.info("Today's briefing already sent (%s exists). Use --force to override.", archive_path)
        return 0

    try:
        threads, banner = asyncio.run(gather_sources(cfg))
        # Resolve carryover BEFORE filtering — the filter drops threads where the
        # user has already replied, which is exactly the signal we need for
        # carryover resolution (spec §8).
        carry_raw = load_carryover(cfg.paths.archive_dir, today)
        carry = drop_resolved(carry_raw, threads)
        kept = apply_filters(threads, cfg.filtering.allowlist, cfg.filtering.mute_list)
        log.info("Fetched %d threads, %d after filter, %d carried (%d resolved).",
                 len(threads), len(kept), len(carry), len(carry_raw) - len(carry))

        try:
            digest = synthesize(today, kept, carry, cfg.filtering.allowlist,
                                cfg.claude.model, cfg.claude.api_key_env)
        except Exception:
            log.exception("Synthesizer failed; falling back to raw-list digest.")
            digest = Digest(
                needs_reply=[{"who": t["from_name"] or t["from_addr"], "subject": t["subject"],
                              "source": t["source"], "age_days": 0,
                              "context": t["snippet"][:140]} for t in kept],
                follow_ups=[], meetings_to_schedule=[], forms_owed=[],
                still_open=[{"age_days": c.age_days, "description": c.description,
                             "original_date": ""} for c in carry],
                fyi=[],
            )
            banner = (banner + " ") if banner else ""
            banner = banner + "⚠ Synthesizer offline — raw inbox below."

        markdown = render_markdown(digest, today, banner=banner)
        write_archive(markdown, cfg.paths.archive_dir, today)

        if args.dry_run:
            print(markdown)
            return 0

        send_email(markdown, today, cfg.delivery.gmail_user,
                   cfg.delivery.smtp_app_password_env, cfg.delivery.work_email)
        log.info("Briefing sent to %s.", cfg.delivery.work_email)
        return 0

    except Exception:
        log.exception("Total failure")
        try:
            send_email(
                f"Briefing failed.\n\nSee logs at {cfg.paths.log_dir / (today.isoformat() + '.log')}\n\n{traceback.format_exc()}",
                today, cfg.delivery.gmail_user,
                cfg.delivery.smtp_app_password_env, cfg.delivery.work_email,
            )
        except Exception:
            log.exception("Even the failure email failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Reauth helper**

`scripts/reauth.bat`:
```bat
@echo off
cd /d %~dp0..
python scripts/seed_outlook_profile.py secrets/owa-profile
pause
```

- [ ] **Step 3: Commit**

```bash
git add run.py scripts/reauth.bat
git commit -m "feat: run.py orchestrator with degraded-mode fallbacks"
```

---

## Task 11: One-time setup + first live run

This task is sequential and does NOT make code changes — it provisions credentials and runs the system end-to-end with `--dry-run`. No commits unless something breaks and you patch it.

- [ ] **Step 1: Install dependencies**

```bash
cd C:\Users\eric_rash\Desktop\DEV\morning-briefing
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
playwright install chromium
```

- [ ] **Step 2: Provision Gmail credentials**

1. Go to https://console.cloud.google.com → new project → enable Gmail API.
2. Create OAuth 2.0 Client ID, type **Desktop**, download as `secrets/gmail_credentials.json`.
3. Run: `python scripts/gmail_auth.py` — interactive browser sign-in produces `secrets/gmail_token.json`.

- [ ] **Step 3: Provision Gmail SMTP App Password**

1. Go to https://myaccount.google.com/apppasswords (requires 2FA on).
2. Generate one for "Mail" / "Windows Computer". Copy the 16-char password.
3. Set environment variable (PowerShell, persistent):
   ```powershell
   [Environment]::SetEnvironmentVariable("GMAIL_APP_PASSWORD", "<the-16-char-pw>", "User")
   ```

- [ ] **Step 4: Anthropic API key**

```powershell
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "<sk-ant-...>", "User")
```

- [ ] **Step 5: Seed Outlook profile**

```bash
python scripts/seed_outlook_profile.py secrets/owa-profile
```
- Sign in to outlook.office.com, check "stay signed in" / "trust this device."
- When inbox loads, close the window.

- [ ] **Step 6: Populate `work_email` in config.toml**

Edit `config.toml`, replace `REPLACE_ME@company.example` with the actual work email.

- [ ] **Step 7: Discover OWA JSON endpoint (if needed)**

```bash
python -c "import asyncio; from morning_briefing.sources.outlook_web import fetch_recent_threads; from pathlib import Path; print(len(asyncio.run(fetch_recent_threads(Path('./secrets/owa-profile')))))"
```

If this returns 0, the endpoint heuristic missed your tenant's URL.
- Re-run `seed_outlook_profile.py` with DevTools open.
- Filter Network tab for XHR/Fetch.
- Click the inbox; identify the request returning the message list.
- Edit `morning_briefing/sources/outlook_web.py` and add that URL substring to the `any(k in url for k in (...))` check.
- Commit that change: `git commit -am "fix: add tenant-specific OWA endpoint substring"`.

- [ ] **Step 8: End-to-end dry-run**

```bash
python run.py --dry-run
```

Expected: markdown briefing printed to stdout; archive file written to `Desktop/SecondBrain/morning-briefings/<today>.md`; no email sent.

Inspect the output. If anything looks off (wrong bucketing, missing senders, weird formatting), iterate.

- [ ] **Step 9: First live send**

```bash
python run.py --force
```

- Open work Outlook. Check inbox AND junk folder.
- If in junk: mark "Not Junk" and (if available in your tenant) add `eric.rash11@gmail.com` to safe senders.

---

## Task 12: Schedule for 07:20 weekdays

**Files:**
- Create: `scripts/install_task.ps1`

- [ ] **Step 1: PowerShell installer**

`scripts/install_task.ps1`:
```powershell
$projectRoot = (Resolve-Path "$PSScriptRoot\..").Path
$python      = Join-Path $projectRoot ".venv\Scripts\python.exe"
$runScript   = Join-Path $projectRoot "run.py"

$action  = New-ScheduledTaskAction -Execute $python -Argument """$runScript""" -WorkingDirectory $projectRoot
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 7:20am
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "MorningBriefing" -Action $action -Trigger $trigger -Settings $settings -Description "Daily 07:30 a.m. email briefing." -User $env:UserName -RunLevel Limited -Force
```

- [ ] **Step 2: Install the task**

In PowerShell (regular user, not admin):
```powershell
cd C:\Users\eric_rash\Desktop\DEV\morning-briefing
.\scripts\install_task.ps1
```

Verify: open Task Scheduler GUI → Task Scheduler Library → look for `MorningBriefing` with next-run timestamp matching tomorrow 07:20.

- [ ] **Step 3: Commit installer**

```bash
git add scripts/install_task.ps1
git commit -m "chore: Task Scheduler installer for 07:20 weekday trigger"
```

---

## Task 13: Stale-7d marker + final polish

**Files:**
- Modify: `morning_briefing/deliver.py` — render `⚠ stale` for `age_days >= 7`

- [ ] **Step 1: Write the failing test**

Add to `tests/test_deliver.py`:
```python
def test_render_marks_stale_items():
    from morning_briefing.deliver import render_markdown
    from morning_briefing.synthesize import Digest
    from datetime import date
    d = Digest(
        needs_reply=[], follow_ups=[], meetings_to_schedule=[], forms_owed=[],
        still_open=[
            {"age_days": 3, "description": "recent", "original_date": "May 18"},
            {"age_days": 8, "description": "old one", "original_date": "May 13"},
        ],
        fyi=[],
    )
    md = render_markdown(d, today=date(2026, 5, 21))
    assert "⚠ stale" in md
    assert md.count("⚠ stale") == 1
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/test_deliver.py::test_render_marks_stale_items -v`
Expected: FAIL.

- [ ] **Step 3: Update the still_open renderer**

In `morning_briefing/deliver.py`, change the STILL OPEN section:
```python
def _still_open_line(i: dict) -> str:
    stale = " ⚠ stale" if i["age_days"] >= 7 else ""
    return f"[{i['age_days']}d]{stale} {i['description']} — original {i['original_date']}"

section("STILL OPEN FROM PRIOR DAYS", d.still_open, _still_open_line)
```

- [ ] **Step 4: Run all tests + commit**

Run: `pytest -v`
Expected: ALL PASS.

```bash
git add morning_briefing/deliver.py tests/test_deliver.py
git commit -m "feat: stale marker for items carried 7+ days"
```

---

## Done

System runs automatically at 07:20 every weekday. To verify in 24 hours:
1. Confirm email arrived in work inbox at ~07:30.
2. Check `Desktop/SecondBrain/morning-briefings/<today>.md` has the same content.
3. Spot-check whether any item you'd want surfaced got dropped → add the sender to `allowlist` in `config.toml`.

After week 1, revisit `allowlist` and `mute_list` based on what the system missed or over-included.
