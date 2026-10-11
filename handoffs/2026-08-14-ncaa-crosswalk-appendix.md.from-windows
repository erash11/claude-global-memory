# Handoff — ATH Technology Framework: NCAA crosswalk appendix + document consolidation

**Date:** 2026-08-14
**Owner:** Eric Rash (Applied Performance, Baylor Athletics)
**Predecessor:** `2026-08-13-ath-tech-routing-and-inventory.md`
**Status:** 08-14 document set shipped and internally consistent. Two user-owned
threads in flight (Micah meeting, inventory email). No blockers.

---

## What happened

Kenny Boyd emailed the morning of 8/14 (screenshot in the OneDrive folder). Three asks:

1. Make sure the five NCAA Performance Technologies recommendations are "spoken for"
   in the framework.
2. Build an appendix that shows where — reusing the existing 3-column chart from
   `NCAA_PerformanceTech_v3.docx` with a fourth column carrying the policy reference.
3. Context: Jon felt the 8/13 discussion had veered away from NCAA "required"
   compliance. Kenny's position to Jon is that the ATH/ITS solution must be
   **complementary to the existing ITS/institutional workflow, not a separate one**.
   Kenny wants to be kept updated on Micah comms and pushed toward a version 1.

All three were addressed. The document set was then consolidated to remove
duplicate/stale versions.

---

## Coverage finding (the substantive answer to Kenny)

Verified against the actual text, not recalled:

| NCAA rec | State in the framework |
|---|---|
| 4. Tech Selection | **Fully carried** — §6 review levels, §7 exceptions, §8 Phase 1.2–1.6 incl. Scorecard, both control points |
| 5. Continuous Improvement | **Carried per-technology** — Phase 3.1–3.4 maps ~1:1 onto NCAA's continuation/modification/discontinuation. Annual SA survey + annual plan review absent |
| 3. Data Management | **Largely carried** — §1.1, §2.4, §5 (ITS, OGC/Privacy, Procurement), §6 Level 3. **Transfer student-athletes absent entirely**; no consent/release template |
| 1. Policy | Written plan = the document. **No standing MDT/Working Group; no clause committing the framework to periodic review** |
| 2. Education | **Thinnest** — only "routine education" (§1.1) and "complete required training" (§5). No section, no cadence, no audience tailoring |

Every gap is written into Appendix A as **"planned for Version 1"** — forward-looking,
no blame framing, and **no fabricated section numbers** (a reference that points at
nothing costs a full review cycle with Kenny).

---

## Decisions made (and the reasoning, which would otherwise be lost)

- **Wrote a new dated file rather than editing the 08-12 in place.** The 08-12 was
  presented in the 8/13 meeting and is the copy everyone has. It is byte-for-byte
  untouched (758,981 bytes, Aug 13 16:55).
- **Did NOT name the institutional ITS intake mechanism.** A first draft asserted
  requests "enter ITS through the existing institutional ITS request path." That is
  unverified — nobody has confirmed whether that is ServiceNow, a form, or Micah's team
  directly. Eric explicitly said not to address the mechanism yet. Both the framework
  (Phase 1.4) and Appendix A.2 now state only the *principle* (Athletics steps feed
  that review; they do not create a separate ITS workflow). **Restore the concrete
  mechanism after the Micah meeting.**
- **Rewrote §3.** It previously said NCAA guidance "is high-level by design." With Jon
  already reaching for the word "required," that clause was the one line that reads as
  downgrading NCAA guidance. Now: the guidance "sets the expectations each institution
  is to meet and leaves the method of implementation to the institution," plus a pointer
  to Appendix A. Deliberately makes **no claim about required vs. recommended** — that
  is a factual question about NCAA status that could not be settled from the source docs.
- **The executive summary carried the same "high-level by design" sentence.** Fixed
  there too — fixing it only in the framework would have left it in the 2-page document
  people are most likely to actually read.
- **Kept the exec summary and workflow handout at top level, not archived.** Both are
  dated 08-12 but are the only copy of their respective deliverable; content overlap
  with the framework is 1–3%. Archiving them would have hidden live documents.
- **Preserved the first 08-14 build** in `_Archive/2026-08-14_as-sent/` because Eric had
  already replied to Kenny and may have attached it. That copy still contains the
  "high-level by design" wording.

Tone constraints applied throughout (see Tier A memory
`project_kenny-boyd-doc-review-preferences.md`): no language implying past
incompetence, no ranking-flavored labels, Baylor branding and draft status on every
page.

---

## Files created or modified

All under
`/Users/kristinarash/Library/CloudStorage/OneDrive-BaylorUniversity/00_Primary_Storage_Drive/XXXX_Transfer/SoftwareTechDocs/`

**Current set (all created 8/14):**
- `Software_and_Tech_Management_ER_2026-08-14.docx` — framework, 10 pp, Appendix A
- `Software_and_Tech_Management_ER_2026-08-14.pdf`
- `Software_and_Tech_Management_WORKFLOW_ER_2026-08-14.docx` — handout, 3 pp
- `Software_and_Tech_Management_WORKFLOW_ER_2026-08-14.pdf`
- `Software_and_Tech_Management_EXEC_SUMMARY_ER_2026-08-14.docx` — summary, 2 pp
- `Software_and_Tech_Management_EXEC_SUMMARY_ER_2026-08-14.pdf`

**Archive (created 8/14):**
- `_Archive/README.txt` — describes all three groups
- `_Archive/2026-08-12/` — 8 superseded files, each MD5-verified before and after the
  move. Includes `MERGED_ER_2026-08-12.docx`, confirmed byte-identical in text to
  `ER_2026-08-12__.docx` (pure duplicate).
- `_Archive/2026-08-14_as-sent/` — 2 files, the first 08-14 build

**Also:** `Software_and_Tech_Management_ER_2026-08-12__.pdf` was cloud-only (zero blocks
allocated) and was hydrated to local disk. Everything in the tree is now materialized.

**Build scripts:** `~/.claude/global-memory/handoffs/2026-08-14-ath-tech-scripts/`
(`build_appendix.py`, `build_companions.py`, `docx_full.py`, `topdf_any.scpt`).
These regenerate the 08-14 set from the archived 08-12 source. **They become stale the
moment anyone edits a .docx directly in Word** — re-running would discard that edit.

---

## Folder convention now in force

Current documents live at the top level of `SoftwareTechDocs/`, all sharing one date
suffix. Superseded versions go to `_Archive/<YYYY-MM-DD>/`. `_Archive/README.txt` is
kept current so the folder reads correctly on the Windows side without this
conversation. Do not leave two dates live at the top level.

---

## Next actions, most important first

1. **Micah meeting (Tue or Wed next week)** — Eric reached out 8/14, awaiting a reply.
   Get: (a) the institutional intake path for a software/tech request — this is the
   fact that restores the concrete sentence in Phase 1.4 of *both* the framework and
   the workflow handout; (b) whether ITS already maintains a software/contract
   inventory Athletics can inherit; (c) who at supervisory level attends the weekly
   standing meeting named in §5.
2. **Inventory email to admin unit leaders — Monday 8/17.** Drafted, not sent. Two
   flags raised: (a) tone — an inventory request reads very easily as "you've been
   buying software without oversight," which is exactly the register Kenny cuts; a
   review pass against that was offered; (b) add a line saying the list will be
   cross-referenced with ITS records, so nobody agonizes over completeness and two
   conflicting inventories don't have to be reconciled later.
3. **Form the Working Group before drafting the remaining v1 sections.** Four of the
   five v1 gaps (education content, consent template, transfer protocol, annual
   survey) are things the Working Group is supposed to produce. Drafting them first
   inverts NCAA Recommendation 1 and yields documents with no owner. Forming the group
   is an organizational decision only Eric and Kenny can unblock.
4. **v1 sections, once the group exists:** Education and Training (annual cadence,
   audience-specific), the Working Group charter, transfer-SA data protocol, data
   rights/release consent template, annual SA survey + annual framework review.
   Transfer protocol and consent template need Legal/Privacy input.

---

## Mid-flight / open questions

- Did the reply to Kenny include the first 08-14 PDF? If so, his copy still says
  "high-level by design." Not worth resending on its own — but anything going to **Jon
  or Micah** should be the current build, since that wording is what Jon reacted to.
- Whether NCAA calls this guidance *required* or *recommended* is unresolved and was
  deliberately not asserted anywhere in the documents.
- Uploading ~0.9 MB PDFs to the Claude thread times out when batched; sending them one
  at a time works.
