# Handoff — RTP Constraints Course, Gray book acquired + Joe interview ready

**Date:** 2026-09-03 · **Workspace:** `/Users/kristinarash/DEV/RTP_Constraints_Course/`
**Location warning:** this file is in `$TMPDIR`, which macOS clears. **It is not durable.**
The durable handoff home for this project is `docs/handoffs/`. Copy it there if it still matters:
`cp "$TMPDIR/handoff-rtp-constraints-course-20260903.md" ~/DEV/RTP_Constraints_Course/docs/handoffs/`

**Reads on, does not repeat:** `docs/handoffs/2026-09-02-research-phase-complete.md`.
Read that first. It holds the research decisions, the lesson-0001 candidates, and the trust note.
This file only records what changed on 2026-09-03.

---

## What this session did

Two asks: pull Rob Gray's book down from Zotero, and get ready to meet Joe this afternoon.

### 1. The book — done

Rob Gray replied to `email-rob-gray.md` and sent the full PDF. Eric put it in Zotero.

**Local copy now at:**
`/Users/kristinarash/DEV/RTP_Constraints_Course/sources/Gray-2024-Learning-to-be-an-Ecological-Coach.pdf`

- *Learning to be an "Ecological" Coach: Developing Attuned & Adaptable Coaching Skills* (2024,
  Perception Action Consulting & Education LLC). **342 pages.** SHA-256 begins `1f0da786`.
- **Born-digital text layer, confirmed to the last page.** Verified by extracting text at p300
  (1,746 chars) and p335 (1,766 chars, the reference list). **OCR is not needed for this book.**
  The `brew install ocrmypdf` from 2026-09-02 stays unused for it.
- **Author-supplied. Do not redistribute.** Do not commit it, do not paste it into an artifact
  or an external service.
- Copied, not moved. Zotero still links to the Drive original.

### 2. Joe — ready, nothing was changed

Verified against files, not memory:

- `INTERVIEW.md` (149 lines, 6 parts, ~45 min) is complete and is the artifact for the meeting.
- `MISSION.md` (38 lines) still carries its **DRAFT** banner. That is correct — this meeting is
  what removes it.
- `lessons/`, `reference/`, `scans/` are all still empty. Correct and deliberate.
- **No prior meeting note for Joe exists anywhere in `~/SecondBrain`.** Treat the 2026-09-03
  meeting as the **first** conversation with him.
- Eric's personal Google Calendar has **no event today**. The Baylor work calendar is not
  connected to this harness, so calendar checks cannot confirm or deny the meeting.

---

## Files changed this session

| File | Change |
|---|---|
| `sources/` | **NEW directory.** Holds the Gray PDF. |
| `sources/Gray-2024-…-Coach.pdf` | **NEW.** 4,888,421 bytes. |
| `RESOURCES.md` | Book 3 in the Gray book-stack list now marked `✅ IN HAND … Verified 2026-09-03`, with local path, page count, OCR finding, Zotero keys, and the redistribution warning. **516 → 526 lines. Nothing else in the file was touched** — the consolidation pass is still a separate open decision. |
| `CLAUDE.md` | Added a `sources/` row to the Layout table (workspace router rule: update in the same turn). |

`RTP_Constraints_Course` is **not a git repository** (`git rev-parse` fails). There is nothing to
commit and no `.gitignore` to write. If it is ever `git init`-ed, **`sources/` must be ignored.**

---

## Open — carried forward, most important first

1. **Run `INTERVIEW.md` with Joe.** Part 1 first; do not skip it. It tests whether Joe wants this
   niche at all. Everything else is still blocked behind it.
2. **Rewrite `MISSION.md` in Joe's words and delete the DRAFT banner.**
3. **Pick lesson 0001** from the four candidates in `NOTES.md`, using interview Q7 and Q10.
4. **`/model` → Fable 5.1**, `cd` to the workspace, then **`/teach`**. A human must type it —
   `disable-model-invocation: true`.
5. **Gray's certification** — $1,995, 2027 sessions full, **waitlist only**. If wanted, this is a
   this-week action. Interview Part 4/6 should establish whether Joe's development budget is real.
6. Everything under "Mid-flight / open" in the 2026-09-02 handoff is still open. Gap 3 (no
   American-football positional demand profile) especially.

### Decision put to Eric, not yet answered

Ingest the book now, or read it first.
- **A — read first (recommended, and what was recommended to him).** The interview comes before
  more input. More reading does not unblock the course.
- **B — run `/ingest-book` now** on the `sources/` path, splitting it into citable advisor entries.

**Do not run `/ingest-book` until Eric answers.**

---

## Zotero — broken, and deliberately left broken

The upload created **two items for one file**. The two PDFs are **byte-identical** (same SHA-256).

| Zotero key | What is wrong |
|---|---|
| `G3CCHWPJ` | itemType `book`, but **no title and no creator**. Child attachment `FFTIHFPP` = `_.pdf`. |
| `BJMBTJ8L` | itemType `journalArticle` (wrong), titled with only the **subtitle**. Creator Rob Gray is set. Child attachment `WLDP6JKJ`. |

Both attachments are **linked files**, not stored copies. They point into
`~/Library/CloudStorage/GoogleDrive-<user>@gmail.com/My Drive/Zotero_PDFs/`.
`~/Zotero/storage/<key>/` holds only a `.zotero-ft-cache`, no PDF.

**The fix is a 30-second job in the Zotero UI, for Eric, not for an agent:** keep one item, set
type **Book**, title *Learning to be an "Ecological" Coach*, author **Rob Gray**, year **2024**;
trash the other; delete `_.pdf` from the Drive folder.

**Why an agent did not do it — both routes are closed:**
- `~/Zotero/zotero.sqlite` returns **`database is locked (5)`** while the Zotero app is running.
  Reads work by copying the file first: `cp ~/Zotero/zotero.sqlite "$CLAUDE_JOB_DIR/tmp/z.sqlite"`
  then `sqlite3 -readonly` the copy. **Writes are not possible this way.**
- Zotero MCP: `sync` works, but **`search` and `sql` both return `MCP tenant gate is not
  configured`.** Assume every non-`sync` Zotero MCP tool is gated until proven otherwise.

---

## Gotchas worth keeping

- **`mcp__zotero__sync --since 7d` fails on `items` and `collections`** with HTTP 400
  `Invalid value for 'since' parameter`, but still exits 0 (non-critical-failure policy).
  `items-top` synced fine — 1,363 records, ~67 s. **Read the `sync_summary` event, not the exit code.**
- **`pypdf` is not installed system-wide.** Use `/Users/kristinarash/.local/bin/uv run --with pypdf`.
  `pdftotext` (poppler) is **not** on this machine either.
- **A `.zotero-ft-cache` proves nothing about a long PDF.** Zotero indexes only the first ~100
  pages by default. Both caches here were 150,290 bytes for a 342-page book. To claim a text layer
  exists, extract from a **late** page.
- Two Zotero items with identical `.zotero-ft-cache` sizes is a **duplicate-upload tell.**

---

## Suggested skills for the next session

| Skill | When to use it |
|---|---|
| `meeting-prep` | Before the next Joe session, or any coach/staff meeting. Verifies artifacts against decisions. Already run once for 2026-09-03. |
| `ingest-book` | **Only after Eric picks option B.** Target the `sources/` PDF. It is the right tool for turning the book into citable advisor entries. |
| `/teach` (mattpocock) | The owner of all lesson writing. **`disable-model-invocation: true` — an agent cannot call it. Ask Eric to type it.** Do not hand-roll lessons. |
| `library-advisor` | After ingestion only. Consults the grounded library instead of parametric knowledge. |
| `memory-write` | If the interview produces a durable fact about Joe or the course direction. Nothing from 2026-09-03 was written to memory; the workspace files hold it. |
| `sports-science-research-grounding` | Any substantive CLA / return-to-performance claim. **Workspace rule: ground in `RESOURCES.md`, never in parametric knowledge. This field has a lot of confident bad writing in it.** |
| `session-handoff` / `closeout` | End of the next working session. |

**Do not** invoke `/teach` or `/ingest-book` unasked.

---

## Trust note

Nothing in `RESOURCES.md` was re-verified this session beyond the Gray book entry. The 2026-09-02
trust note still stands: **treat `verified <date>` markers as solid; treat everything else as
citable only after a check.** The new book entry is marked `verified 2026-09-03` and every claim
in it (page count, text layer, hash, Zotero keys) was checked directly against the file.
