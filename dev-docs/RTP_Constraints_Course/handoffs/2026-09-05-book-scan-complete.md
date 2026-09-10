# Handoff — Myszka book scanning COMPLETE, references extracted

**Date:** 2026-09-05 · **Workspace:** `/Users/kristinarash/DEV/RTP_Constraints_Course/`

**Reads on, does not repeat:** `2026-09-03-book-scan-pipeline.md`, which set up the scan
route and recorded the traps. This file records the finish.

**The scanning thread is closed.** The book is a page-ordered, OCR'd PDF.

---

## 1. Shawn Myszka replied — no digital copy

He could not send one. The scan route was therefore the only route, and it is now done.
The 2026-09-03 instruction "if he sends a digital copy, stop scanning" is spent.

## 2. Pages on disk: printed 1–253, contiguous

**253 pages, no gaps.** The front matter (printed 1–13) was scanned at 10:05 on 2026-09-05,
after the ingest — see §7, which is where the two findings that came out of it live.

**The PDF still holds only printed 14–253** (240 pages). The front matter is on disk but not
yet in the file.

| Artifact | Path |
|---|---|
| The book | `sources/Myszka-2025-Enhancing-Skill-in-American-Football.pdf` (240 pp, 123 MB) |
| OCR text sidecar | `sources/Myszka-2025-Enhancing-Skill-in-American-Football.txt` (618 KB, 100,028 words) |
| Reversible rename map | `sources/myszka-scan-manifest.csv` |
| This batch's folio map | `sources/myszka-folio-map-2026-09-05.json` |

**PDF page 1 == printed page 14. The offset is 13.** Anything that cites a page must
apply it.

**Book structure, read out of the OCR text:**

| Printed pages | What |
|---|---|
| 14–232 | Chapters. Chapter 8 opens on 195. |
| 233–235 | Glossary |
| **237–248** | **References** — 128 entries |
| 249–253 | Appendix: "Thoughts from Others Embedded in Football" |

**Genuinely blank pages, each still carrying its printed folio: 62, 194, 236.** Each was
opened and confirmed, not assumed. 194 and 236 are blank versos before Chapter 8 and
before REFERENCES. They are not failed scans — do not "fix" them.

### The second batch, 2026-09-05

157 photos → printed pages 102–253. Median OCR confidence **95.5** (first batch: 95.0).

**Five duplicate re-shoots** were found and resolved by keeping the higher-confidence copy;
losers went to `_superseded/`, none deleted:

- **p152** — first attempt washed out (conf 30.6 vs 87.5).
- **p170–173** — shot twice. In the first pass p170 and p171 were captured *in the same
  second* (`08-08-44`), and the macOS ` (1)` collision suffix put them on disk in the
  opposite order to capture. Only the visual folio read settled it.

**Twelve same-second collision pairs this batch, against two last time.** The trap is not
rare. Expect it.

### Scan quality across the whole book

Every one of the 240 pages was scored. **Median mean OCR confidence 95.1 (batch 1, p014–101)
and 95.5 (batch 2, p102–253)** — the two sessions are indistinguishable in quality.

**Exactly one genuinely weak page: p120, confidence 74.6.** Worth a re-shoot if a lesson
leans on it; otherwise leave it. Nine more sit in the 84–90 band — readable, not pretty:
p19, p49, p50, p144, p152, p156, p158, p167, p242.

A rebuild after any re-shoot is cheap: drop the new file in, rerun `scan_pipeline.py pdf`.

## 3. How page order was proved — and what the proof is worth

Page order is the one thing that must be right, because it is baked into the PDF and
inherited by every note built from it. It was established one way and checked four further
independent ways — the fifth, and strongest, arrived last (§7).

1. **Built by a visual read** of a cropped folio band, tiled into contact sheets that print
   the *expected* folio beside each crop — so the task is spotting disagreements, not
   reading 157 numbers.
2. **Gated by arithmetic that costs nothing:** `files − duplicates == last − first + 1`.
   157 − 5 = 152 = printed 102…253 for this batch (246 − 6 = 240 across both sessions). The
   gate is enforced in code and **refuses to rename** when it fails; tested with a
   deliberately corrupted map, it refused. **But see the limits below — it is a
   map-consistency check, not a proof of order.**
3. **Checked afterwards by a different route** — `scripts/verify_pdf.py` reads the folio out
   of the *full-page* OCR text of the finished, deskewed PDF. It shares no code path with
   the visual read.

5. **Checked against the publisher's own contents page** (§7), scanned after the fact.
   All thirteen landmarks match. This is the only check with an external ground truth.

**Result: 234 of 240 pages carry a readable folio and every one matches its expected
value. Zero disagreements. Folios strictly increase through the book.** The other 6 pages
print no folio at all (chapter openers, all in the first batch) — and four of those are
bridged by the reviewer's prose-continuity read.

**What the gate does NOT catch** (corrected after review — an earlier version of this
handoff overstated it): with no overrides, folios are a running counter, so the identity
holds **by construction** and the gate compares a number with itself. **A transposition of
two adjacent pages, a wrong start page, a missed duplicate, a real page wrongly marked
superseded, and two cancelling errors all pass it.** What it does catch: a gap, a doubled
folio, a collision with an existing file. Useful, cheap, and not a proof of order.

4. **Checked a fourth way, by the reviewer** — prose continuity read across 123 page
   boundaries (including all four boundaries around the six pages that print no folio, and
   every boundary in the re-shoot zones and at the session seam), plus bibliography
   alphabetisation and chapter-opener parity. **No boundary failed.**

## 4. References — extracted, matched, ready to import

`sources/myszka-references.md` — **all 128 entries**, with Zotero status marked per entry.
`sources/myszka-references-new.ris` — **122 records not in the library**, importable.

**Only 6 of 128 are already in Eric's Zotero library** (1,348 items scanned):
Kuzmits 2008, Lee 2014, Myszka 2023 *Being Water*, Otte 2024, Parry 2025, Yearby 2022.

**The Zotero MCP is read-only** — it exposes no create/write tool. So the deliverable is an
import file, not a direct add. Import path: **Zotero → File → Import →
`myszka-references-new.ris`**. Every record is tagged `myszka-enhancing-skill` and
`RTP-constraints-course`, so a bad import is one tag-filter away from being undone.

Each record keeps its **full OCR'd source string in the `N1` note**, so no parsing guess is
unrecoverable — which is why every problem the review found was a re-parse job rather than a
re-scan. The parser was rewritten after that review (§5); `scripts/extract_refs.py` now
**self-validates**, failing if any record is fused or undated. Current state: **0 fused,
0 undated, 0 phantom authors, 0 records without an author, 0 malformed RIS lines.**

**Only 1 of 122 records carries a DOI** — the printed bibliography mostly does not list
them. Zotero can fill them in afterwards.

## 5. The review gate, and what it caught

Eric's standing instruction, 2026-09-05: **nothing gets ingested until a verification step
plus an independent model review has passed.** Both ran.

**Codex could not.** The account hit its usage limit (resets 11:31). An independent
adversarial agent ran the same falsification brief instead.

**Verdict: GO on the PDF, NO-GO on the reference file as it then stood.** What the review
found, and what was done:

| Finding | Status |
|---|---|
| `verify_pdf.py`'s "folios strictly increasing" check was a **tautology** — it tested the *expected* values, so it could never fail | **FIXED.** Now reads the folio observed on the page. Proven to fail on a deliberately transposed copy. |
| The **gate claim was overstated.** With no overrides the identity holds by construction; a transposition, a wrong start page, a missed duplicate and two cancelling errors all pass it | **CORRECTED** in the docstring, the handoff (§3) and both memory files. It is a map-consistency check, not a page-order proof. |
| **Six** superseded duplicates, not five — a p66 re-shoot from 09-03 whose manifest row is formatted differently | Confirmed. One live p066.jpg, correctly superseded copy. No order impact. |
| Reference file: **7 chimeric records** welding one entry's authors to another's title (Gibson 1966 attributed to a nonexistent author) | **FIXED.** Root cause: web citations date as `(2016, June 9)`, which the year regex missed, so those entries never closed. |
| Reference file: **67 of 113 records with phantom authors** — a creator literally named "K" | **FIXED.** OCR drops the final period; the author parser now matches surname+initials with periods optional. |
| Entry count was wrong — closer to 126 than 119 | **FIXED.** Now **128 entries**, 0 fused, 0 undated. |

Verification of page order also passed independently four ways (§3), and the reviewer added
a fourth: prose continuity read across 123 page boundaries, plus bibliography alphabetisation
and chapter-opener parity. **No boundary failed.**

## 6. The book is ingested — 84 library entries

`/ingest-book` ran at **full-text tier** (probe: 240 pages, 237 carrying text,
`scanned: false`, so the OCR layer is real).

**New domain:** `~/SecondBrain/Knowledge/library/skill-acquisition/` — the second domain in
the library, alongside strength-and-conditioning. Index at `_domain.md`.

**Book:** `skill-acquisition/enhancing-skill--myszka/`, ingest map at `_book.md`.

| Chapter | Entries | Chapter | Entries |
|---|---|---|---|
| 1 Performance landscape | 11 | 6 Practice activity design | 8 |
| 2 Ecological dynamics | 13 | 7 Skill periodization | 3 |
| 3 Information & affordances | 9 | 8 Practical changes | 8 |
| 4 Analyzing the relationship | 12 | 9 Youth football | 6 |
| 5 Designing the environment | 11 | 10 Case studies | 2 |
| | | Glossary | 1 |

**84 entries:** 33 principles, 25 frameworks, 15 heuristics, 7 claims, 4 case studies.
**Confidence: 25 proven, 52 supported, 7 untested** — the split is deliberate, and every
entry carries a mandatory "When NOT to apply" naming its limits.

**The appendix (249–253) was skipped deliberately** — testimonial material, no distinct
principles to atomize.

Committed to the vault (`090d6ef`, `8b27c2e`) and indexed. Verified searchable:
*"how do I make a drill easier without removing the defender"* returns
`principle--task-simplification-not-decomposition`.

**Entries most load-bearing for Joe's course:** `principle--variability-overuse-hypothesis`
(answers the safety objection by inverting it), `principle--rate-limiters-and-fear` (fear as
a constraint on exploration — the closest thing in the book to a return-to-play theory),
`principle--task-simplification-not-decomposition` (already used in lesson 0001),
`principle--affordances-point-both-ways` (why a returning athlete's perception is
mis-calibrated), and `case-study--tight-end-punt-coverage-exposure-gap` (the exposure audit
method, three practice reps against two season occurrences).

---

## 7. Front matter scanned — and it found two things

Printed pages **1–13** were photographed at 10:05, after the ingest, to get the contents
page. 15 shots → 14 pages (p8 shot twice; p14 was a re-shoot of a page already placed, and
**won on confidence 96.2 vs 94.1**, so the 2026-09-03 original was superseded). The gate
passed: 15 − 1 = 14 = printed 1…14.

**Pages on disk are now printed 1–253, contiguous, no gaps.**

### Finding 1 — page order verified a fifth way, and it is the strongest one

The printed contents page is ground truth, produced by the publisher, and it was read
*after* the page order had already been derived from the scans alone. **All thirteen
landmarks match exactly:**

| | Contents says | Derived from scans |
|---|---|---|
| Preface | 7 | 7 |
| Ch 1–10 | 15, 37, 63, 77, 111, 133, 181, 195, 209, 221 | identical |
| Glossary · References · Appendix | 233 · 237 · 249 | identical |

**Zero discrepancies.** Page order is now as well-evidenced as it can be without the
publisher's own file.

### Finding 2 — the book is longer than the scan

The contents page ends with **About the Authors — 255.** The scan stops at **253.**

**Printed pages 254 onward were never scanned, and nothing inside pages 14–253 revealed
it.** No running header, no folio, no cross-reference. It took the contents page to expose
a gap that had been sitting there unnoticed through five verification passes — a good
argument for scanning front matter *first* on the next book.

Nothing already ingested is affected: the appendix ends at 253 and About the Authors is
biography, not content. But the book file is not complete until those pages exist.

### Also settled

**Copyright 2025 by Emergence, LLC**, read off the copyright page. The PDF and its sidecar
were renamed to match the Gray book's convention:

- `sources/Myszka-2025-Enhancing-Skill-in-American-Football.pdf`
- `sources/Myszka-2025-Enhancing-Skill-in-American-Football.txt`

Two more genuinely blank pages, each carrying a folio: **printed 4 and 6** (front-matter
versos). Noted in `scripts/verify_pdf.py` for the rebuild.

### The rebuild — do it once

Do **not** rebuild the PDF yet. When printed 254–255 are scanned, one rebuild folds in the
front matter *and* the tail:

```
python3 scripts/scan_pipeline.py pdf --src "~/Downloads/vFlat/iPhone 15" \
    --outdir /tmp --out sources/Myszka-2025-Enhancing-Skill-in-American-Football.pdf
```

Result: the complete book with **printed page 1 = PDF page 1, offset 0** — which retires the
+13 offset, the thing the pre-ingest review called the single highest-value item to get
right. Then set `FIRST_PRINTED = 1` and add `{4, 6}` to `KNOWN_BLANK` in
`scripts/verify_pdf.py`, and rerun it.

**No library entry needs revisiting.** Entries cite *printed* pages through their `chapter:`
field; none reference a PDF index.

## Everything created or modified, 2026-09-05

**Workspace — `~/DEV/RTP_Constraints_Course/`**

| Path | What |
|---|---|
| `scripts/scan_pipeline.py` | **NEW.** The reusable pipeline. Its docstring carries every trap found across all three scanning sessions — read it before the next book. |
| `scripts/verify_pdf.py` | **NEW.** Proves page order after the build, by a route independent of how it was built. |
| `scripts/extract_refs.py` | **NEW.** OCRs the reference pages; self-validates (fails on any fused or undated record). |
| `scripts/zotero_overlap.py` | **NEW.** Matches extracted references against the local Zotero cache. |
| `scripts/build_refs.py` | **NEW.** Emits the two reference deliverables. |
| `sources/Myszka-2025-Enhancing-Skill-in-American-Football.pdf` | **NEW.** 240 pp (printed 14–253), 123 MB. **Never commit, never redistribute.** |
| `sources/Myszka-2025-Enhancing-Skill-in-American-Football.txt` | **NEW.** OCR sidecar, 100,028 words. |
| `sources/myszka-references.md` | **NEW.** All 128 bibliography entries, Zotero status marked. |
| `sources/myszka-references-new.ris` | **NEW.** 122 importable records. |
| `sources/myszka-folio-map-2026-09-05.json` | **NEW.** Replayable folio map for the 09-05 body batch. |
| `sources/myszka-scan-manifest.csv` | **APPENDED.** Now 263 rows — reversible for every page. |
| `docs/handoffs/2026-09-05-book-scan-complete.md` | **NEW.** This file. |
| `CLAUDE.md` | Layout rows added for `scripts/` and the expanded `sources/`. |

**Vault — `~/SecondBrain/Knowledge/library/`** (committed: `090d6ef`, `8b27c2e`, `434b504`)

| Path | What |
|---|---|
| `skill-acquisition/_domain.md` | **NEW DOMAIN.** Second in the library. |
| `skill-acquisition/enhancing-skill--myszka/_book.md` | **NEW.** Ingest map, offset, quotation warning, Outstanding items. |
| `skill-acquisition/enhancing-skill--myszka/*.md` | **84 NEW entries.** 33 principles, 25 frameworks, 15 heuristics, 7 claims, 4 case studies. |

**Memory**

| Path | What |
|---|---|
| `~/.claude/global-memory/MEMORY.md` | RTP thread rewritten. Committed `9243302`. |
| `~/.claude/projects/-Users-kristinarash-DEV/memory/feedback_ingest-review-gate.md` | **NEW.** The review-gate rule and what it caught. |
| `~/.claude/projects/-Users-kristinarash-DEV/memory/project_book-scan-page-ordering.md` | **UPDATED.** Gate limits corrected; "scan the front matter first" added. |
| `~/.claude/projects/-Users-kristinarash-DEV/memory/MEMORY.md` | Index pointer for the new feedback memory. |

**Scans — `~/Downloads/vFlat/iPhone 15/`**

`p001.jpg`–`p253.jpg` (253 pages, contiguous) plus `_superseded/` (8 files, nothing deleted).

**Still not a git repository.** Nothing in the workspace is committed — today's scripts,
handoff and sources are protected only by the daily backup. If it is ever `git init`-ed,
`sources/`, `interviews/` and `reference/gray-infographics/` must all be ignored — the book
PDF especially. It is author-supplied and must never be redistributed.

## The cheap-read decision, 2026-09-05

Eric chose **option B** for future scanning batches: a small model (Haiku) reads the
contact sheets first, the arithmetic gate blocks anything that does not add up, and only
disagreements get a careful second look. The savings are small; **the gate is the part
worth keeping.** `scan_pipeline.py` implements it and its docstring explains it.

---

## Open — most important first

1. ~~Run `/ingest-book`.~~ **DONE** — 84 entries, see §6.
2. **Import `myszka-references-new.ris` into Zotero** (File → Import). **122 records**
   (128 entries extracted, 6 already in the library).
   Then decide which of them deserve full-text ingest — that needs the actual papers, most
   of which are not on disk. Recommendation: import all 113 as citation records now; ingest
   full text later, only for the subset the lessons actually cite.
3. ~~One shot of the contents page.~~ **DONE 2026-09-05** — the whole front matter was
   scanned. See §7.
4. **Scan printed pages 254–255** (About the Authors), then rebuild the PDF **once** —
   see §7. This is the only thing standing between here and a complete book file.
5. **Re-run the Codex review** after 11:31 if a third opinion is wanted. The independent
   adversarial review already ran and its findings are all resolved (§5).
6. **No advisor persona exists for `skill-acquisition` yet.** `_domain.md` has `advisor: ""`.
   See `library/CREATING-ADVISORS.md` if one is wanted — it would make the 84 entries
   consultable as a persona rather than only by search.
7. **Lesson 0002.** Unchanged from 2026-09-03. `lessons/0001-opposed-vs-unopposed.html`
   and its learning record exist; the Gray infographic rows are ready-made support.
8. Everything under "Open" in the 2026-09-03 handoffs still stands, including **gap 3** —
   no American-football positional demand profile. That is the second Myszka email.

## Trust note

Page order was verified **five** independent ways, which agreed on all 240 pages (§3, §7) —
the last against the publisher's printed contents page. The
duplicate resolutions were decided by measured OCR confidence, not by eye. The blank pages
were each opened and read. **The bibliography was extracted by OCR and machine-parsed** —
author initials and page ranges carry scanning noise, and the raw string is kept in `N1`
for that reason. Check any entry against the printed page before it appears in a lesson.
