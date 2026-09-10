# Handoff — Myszka book scanning, Joe interview ingest, Gray infographics

**Date:** 2026-09-03 (evening) · **Workspace:** `/Users/kristinarash/DEV/RTP_Constraints_Course/`

**Reads on, does not repeat:** `2026-09-03-gray-book-and-joe-prep.md` (morning) and
`2026-09-03-lesson-0001-shipped.md` (the `/teach` session). This file covers the work
either side of those.

**Next session starts here: more book pages get scanned tomorrow (2026-09-04).**

---

## 1. Joe's mission interview — ingested

Ran 2026-09-03, 47.8 min, via `INTERVIEW.md`. Pulled from Fireflies
(`Joe_CLA_CourseDesign`, id `01M1MASS572WKYQ07ZSDDB45EA`).

- **`interviews/2026-09-03-joe-smith-mission-interview.md`** — 617 sentences condensed to
  161 speaker turns, plus a key-answers digest with timestamps. **Names athletes and their
  injuries. Never commit, never paste into an artifact or external service.**
- Also exported to the vault: `~/SecondBrain/Inbox/meetings/2026-09-03_Joe_CLA_CourseDesign.md`
  — **summary only, 2.5 KB, no dialogue.** The workspace file is the real record.

**The decision that changed the course:** Joe rejected the post-clearance scope. The work
starts at the back end of rehab, *before* clearance, and covers acute cases. His own
sentence is now the mission: *"I'm least confident in the ability to rationalize a very
subjective process to objectively oriented people."*

`MISSION.md` was rewritten from this and the DRAFT banner removed.

## 2. Book scans — the live thread

**88 pages in hand, printed pages 14–101, contiguous.** Roughly the front third.

**Location:** `~/Downloads/vFlat/iPhone 15/` — named **`p014.jpg` … `p101.jpg`**.
**Reversible map:** `sources/myszka-scan-manifest.csv` (old name → new name, per page).
**Superseded duplicate** kept, not deleted: `~/Downloads/vFlat/iPhone 15/_superseded/`.

Scanned with **vFlat Scan** on iPhone. ~2000×3200 px, ~360 DPI. Median OCR confidence
**95.0**; 76 of 88 pages clean or better after the bad ones were re-shot.

### Traps found the hard way — read before touching the next batch

1. **Do not trust OCR for the folio.** Three tuning passes; one made things *worse*
   (80/88 unread). The bottom strip catches body text and citation years, and tesseract
   confuses 5 with 9 — it read page **50 as 90** with 8/8 unanimous votes.
   **What works:** crop a tight band around the centred folio
   (`x 0.36–0.64`, `y 0.900–0.952`), tile them into a contact sheet, and **read them
   visually.** Two sheets of 44 covered all 88 and were unambiguous.
2. **Sort by mtime, never by filename.** macOS appends ` (1)` on download collisions, and
   `…17-35-17 (1).jpg` sorts *before* `…17-35-17.jpg` while the timestamps say the
   opposite.
3. **Same-second captures land out of page order.** Pages 21/20 and 27/26 were swapped
   for this reason. Page 67 was shot before 66.
4. **A "failed" OCR page may just be blank.** `18-02-59.jpg` returned zero words. It is
   **page 62, genuinely blank in the book** — but it *does* carry a printed folio.
5. **The folder is live.** A new page-66 re-shoot appeared mid-analysis and broke an
   `assert`. Any script must re-verify the folio map rather than assume a file count.
6. **Bad stretches cluster in time.** All 7 originally-poor pages fell in one two-minute
   window (18:00–18:03) — a lighting or angle change, not random.

### Route once scanning finishes

```
img2pdf (page order)  →  ocrmypdf --force-ocr --rotate-pages --deskew  →  /ingest-book
```
All installed: `img2pdf`, `ocrmypdf`, `tesseract`, `qpdf` (`/opt/homebrew/bin/`).
`ingest-book` would take this at **full-text tier**, its highest confidence level.

**Do not build the PDF until the book is done.** Ingesting a third now means paying for
atomization twice, and atomization is the expensive step.

## 3. Shawn Myszka email — SENT 2026-09-03

**`email-shawn-myszka.md`** → `shawn@emergentmvmt.com`.

Address verified from a **primary source**: corresponding author on the *Being Water*
accepted manuscript at [shura.shu.ac.uk/31552](https://shura.shu.ac.uk/31552/). Corroborated
by `tyler@emergentmvmt.com` on the Yearby paper (so Emergence uses `firstname@`).

**He is not a stranger** — Gmail shows four "Dear Eric" emails from
`shawn@optimizemovement.com`, Nov 2017 to Mar 2019, about the Sport Movement Skill
Conference. The draft opens on that.

Asks whether a digital edition exists and, if not, for a DRM-free copy. Rob Gray's PDF is
cited as a **trust precedent**, not as pressure on a co-author.

**Every superlative about Eric's own reading was cut** at his direction — the *Football
Beyond The Stats* paragraph and "the most directly useful thing I've read". Those verdicts
came from `RESOURCES.md`, which an agent wrote. **Standing rule for this workspace: never
put a reading history in Eric's mouth.**

**SENT 2026-09-03.** If Myszka replies with a digital copy, the remaining scanning is
unnecessary — stop and use his file.

## 4. Rob Gray's infographics — saved locally

**`reference/gray-infographics/`** (7.2 MB, 16 files). `NOTES.md` asked for this because
the site is one person's.

- Six infographics at **full resolution** (4000×2250, 300 DPI) — the WordPress
  `-1024x576` suffix was stripped to reach the originals.
- **`comparative-training-studies.md`** — the 21-study head-to-head table, extracted from
  HTML into a searchable table. **This is the page Joe hands a physician who pushes back.**
- **`two-approaches.md`** — transcribed from the image, because a picture is not quotable.
- Source `.html` pages kept so extractions can be re-checked.
- Its own `README.md` records provenance and two scraping traps (the site's calendar
  widget is a `<table>`; the Two Approaches graphic is easy to mislabel as a video thumb).

**Two rows back lesson 0001 directly:** the last row of Two Approaches (decomposition vs
coupling) and study 17, Caldeira 2023, where **task simplification beat task
decomposition** head to head. Studies 9 and 18 (Orangi) are the ACL-risk rows a physician
will care about.

---

## Files created or modified this session

| Path | What |
|---|---|
| `interviews/2026-09-03-joe-smith-mission-interview.md` | **NEW.** Transcript + digest. Sensitive. |
| `MISSION.md` | **REWRITTEN** from the interview. DRAFT banner removed; athlete names stripped. |
| `email-shawn-myszka.md` | **NEW.** **Sent 2026-09-03**, awaiting reply. |
| `reference/gray-infographics/` | **NEW DIRECTORY.** 16 files + README. |
| `sources/myszka-scan-manifest.csv` | **NEW.** Reversible scan rename map. |
| `CLAUDE.md` | Layout rows added for `interviews/` and `reference/gray-infographics/`. |
| `docs/handoffs/2026-09-03-gray-book-and-joe-prep.md` | Copied out of `$TMPDIR` before it was cleared. |
| `~/Downloads/vFlat/iPhone 15/p014.jpg … p101.jpg` | 88 scans renamed to page order. |
| `~/SecondBrain/Inbox/meetings/2026-09-03_Joe_CLA_CourseDesign.md` | Vault export (summary only). |
| `~/SecondBrain/Inbox/meetings/2026-09-03_Sep_03_0930_AM.md` | Vault export, **placeholder filename** — see open items. |

`RTP_Constraints_Course` is **still not a git repository.** Nothing was committed. If it is
ever `git init`-ed, **`sources/`, `interviews/` and `reference/gray-infographics/` must all
be ignored.**

---

## Open — most important first

1. **Scan the rest of the book (2026-09-04).** Resume at printed page **102**. New shots
   append to `~/Downloads/vFlat/iPhone 15/`; re-run the folio contact-sheet method to
   place them. Do not rely on filename order.
2. ~~Send the Myszka email.~~ **SENT 2026-09-03.** Awaiting reply at `shawn@emergentmvmt.com`.
   **If he sends a digital copy, stop scanning.** Nothing is blocked on him either way —
   the scan route continues in parallel.
3. **A Fireflies rename never landed.** The 09:30 staff meeting was renamed via GraphQL to
   *"Performance Staff — Facility Use, Team Updates & Hiring Standards"*; the API accepted
   it and it had not applied after ~10 minutes. The vault file is therefore
   `2026-09-03_Sep_03_0930_AM.md`. Fix with
   `fireflies-pp-cli sync --full --resources transcripts` then `/meeting-sync`, whose
   filename-drift audit catches it.
4. **Lesson 0002.** `lessons/0001-opposed-vs-unopposed.html` and
   `learning-records/0001-…md` exist from the `/teach` session. The infographic rows above
   are ready-made supporting material.
5. Everything under "Open" in the two earlier 2026-09-03 handoffs still stands, including
   **gap 3** — no American-football positional demand profile. Myszka is the best person
   alive to answer it; that is the *second* email, not the first.

## Trust note

`MISSION.md` and the interview digest were both checked line by line against the
transcript timestamps. The scan page map was verified two independent ways — arithmetic
from capture order, and visual folio reading — which agreed on all six re-shot pages.
`RESOURCES.md` was not re-verified this session; the 2026-09-02 trust note still stands.
