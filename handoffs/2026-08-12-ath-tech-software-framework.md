# Handoff — ATH Technology / Software Management Framework

**Date:** 2026-08-12
**Owner:** Eric Rash (Applied Performance, Baylor Athletics)
**Status:** Delivered. Meeting 2026-08-13, 4:15–4:45 PM Central, Microsoft Teams —
"INITIAL DISCUSSION: ATH Technology/Software Review". Email sent by Eric himself.

---

## What this was

Merge Eric's existing Software and Technology Management Framework draft with a
Baylor-format policy draft ("Responsible Use of Athlete Performance Technologies
and Data Policy", `JA_TechPolicy.pdf`, a 10-page scanned PDF with no text layer —
had to be OCR'd by rendering pages to PNG and reading them).

Then condense into an executive summary plus a standalone workflow document, for
distribution ahead of the 8/13 meeting.

## Merge specification (from Eric, after his meeting with Kenny Boyd)

- Eric's document is the **skeleton**; JA sections merge into it.
- JA sections **1, 2, 3, 4, 6, 8** come in. JA **5, 7, 9, 10, 11** and all
  appendices are **excluded**.
- JA §8 (Responsibilities) merges into **our §5 Roles** — this pinned Roles at §5,
  which forced JA 1–4 to fold *into* our existing §1–4 rather than sit ahead of them.
- The three-phase process moves to **last** (§8), followed by the workflow diagram (§9).
- Scope: **department-wide**, all Athletics technology, with athlete performance
  technology as the originating context and highest-risk category.
- Base file was the **Aug 11** draft (`..._DRAFT_ER_.docx`), which had §8.2
  trials/pilots deleted and a newer diagram. Eric confirmed §8.2 stays out.

**Trap that nearly caused an error:** three near-identical drafts existed in
`deliverables/`. The *newest* (Aug 11) had FEWER sections than the Aug 7 file Eric
originally pointed at. Always diff before choosing a base.

## Final section structure

| § | Section | Source |
|---|---|---|
| 1 | Purpose | Eric + JA 1 Policy Statement (1.1) + JA 2 Reason (1.2) |
| 2 | Scope and terminology | Eric + JA 3 (2.2) + JA 4 (2.3) + JA 6 Definitions (2.4) |
| 3 | Alignment with NCAA guidance | Eric, unchanged |
| 4 | Intended outcomes | Eric |
| 5 | Roles and responsibilities | Eric's 7 roles + JA's 6 = 13 |
| 6 | Levels of review | Eric, retitled + relabeled |
| 7 | Exceptions | Eric |
| 8 | The three phases | Eric, moved last |
| 9 | Workflow | diagram |

## Decisions made (and the reasoning that would otherwise be lost)

1. **Review tiers renamed.** Kenny rejected Light/Standard/Elevated. He floated
   Basic/Intermediate/Advanced; that was **declined** because it reads as
   sophistication of the *technology* rather than depth of *review*, and "Basic"
   sounds like a judgment on the requester. Shipped
   **Level 1 Standard / Level 2 Enhanced / Level 3 Comprehensive Review**, section
   retitled "Levels of review". **This is a proposal, not a settled decision.**

2. **ITS seniority framing.** Kenny wanted a supervisory-level IT person, not a line
   technician. Written as what the *request* demands ("ITS is represented at a
   supervisory level with the authority to commit ITS resources"), never as a
   competence judgment on staff.

3. **No blame-implying rationale.** "so the department stops discovering it is in
   the final year of an agreement with no time to act" → "advance visibility of
   contract end dates and the lead time to evaluate options". See Tier A memory
   `project_kenny-boyd-doc-review-preferences.md`.

4. **Urgency gate.** A request directed by an administrative lead enters the
   expedited lane on receipt — a documented gate instead of arguing case by case.

5. **Humanizer: narrow pass only.** Ran 9 edits on sentences Claude authored.
   Deliberately did NOT touch Eric's own language or JA's policy text, and ignored
   the skill's "add soul / use first person / let some mess in" half, which is blog
   advice that would damage a policy document headed to OGC.

6. **Diagram "tier" → "level".** The workflow PNG said "tier" twice, contradicting
   the new §6. Re-rendered both labels in the original Cascadia Code at matched size
   and centering (48px, 3× export scale, 10px padding — geometry recovered exactly
   from the .excalidraw JSON). Pixel-faithful. "level" survives whatever naming
   Kenny finally picks.

7. **Eric's own edit pass (8/12, in OneDrive)** — 9 changes, all honored:
   cut "No single unit can make that call alone"; "carries"→"handles the most
   sensitive data"; "depends on what it actually involves"→"the request's scope";
   **cut "The framework is department-wide … any single unit"**; "the deepest
   review"→"a review"; cut "defaulting on whatever is asked for"; cut the §6
   re-levelling sentences; cut "not a bypass" / "compressed clock" and reworded the
   urgency gate; tightened 1.7 and expanded "Dir App"→"Director of Applied".

## File locations

**Local — `/Users/kristinarash/DEV/SoftwareTech_Mgmt_Framework/deliverables/`**
- `Software_and_Tech_Management_MERGED_ER_2026-08-12.docx` / `.pdf` — framework (7pp)
- `Software_and_Tech_Management_EXEC_SUMMARY_ER_2026-08-12.docx` / `.pdf` (2pp)
- `Software_and_Tech_Management_WORKFLOW_ER_2026-08-12.docx` / `.pdf` (3pp)
- `Software_and_Tech_Management_MERGED_ER_2026-08-12_SUPERSEDED_pre-edit.docx` — old build, kept
- `Framework_level-language.excalidraw` — diagram source with "level" wording
- `Workflow_Diagram_level-language.png` — the corrected diagram
- `Framework.excalidraw` — ORIGINAL, untouched, still says "tier"
- 08-11 versions of all three documents also retained

**OneDrive — `/Users/kristinarash/Library/CloudStorage/OneDrive-BaylorUniversity/00_Primary_Storage_Drive/XXXX_Transfer/SoftwareTechDocs/`**
- Same five shared files, byte-identical (SHA-256 verified)
- Plus `Software_and_Tech_Management_2026-08-12.pdf` (Eric's own export; note the
  filename lacks the role token the others carry)

**Build scripts — `~/.claude/jobs/126c5de4/tmp/`** (ephemeral, dies with the job)
`baylordoc.py` (shared styling), `build_merged.py`, `build_exec.py`,
`build_workflow.py`, `patch_diagram.py`, `extract_full.py`, `topdf4.scpt`.
`build_merged.py` now writes to `..._MERGED_ER_REBUILD_DO-NOT-SEND.docx` so a rerun
cannot overwrite Eric's edited framework. **If these scripts matter beyond this job,
copy them somewhere durable.**

## Gotchas for whoever picks this up

- **OneDrive is the source of truth.** Eric edits there. The local copy is a
  snapshot and goes stale silently — nothing keeps them in sync.
- **Never rerun `build_merged.py` against the canonical filename.** It would wipe
  Eric's edits with no warning.
- **Word automation is flaky.** `active document` returns empty right after `open`;
  needs a wait loop (`topdf4.scpt`). When it wedges, a full quit + relaunch fixes it —
  killing it is safe only when `count of documents` is 0.
- No LibreOffice / Pages / pandoc on this machine. Word is the only DOCX→PDF path.
- The `gws` CLI is authed to **personal** Gmail (eric.rash11@gmail.com), not Baylor.
  Contacts API returns 403 (missing scope). Calendar work events come from a
  read-only subscribed feed that strips attendees.

## Next actions

1. **8/13 meeting** — two open questions to land: the Level 1/2/3 naming, and the
   scope wording. Eric's edit removed "department-wide" from §2.1, which was the
   specific thing Kenny asked to strengthen; §1.2 still carries the idea
   ("the department's general approach to all technology") but that §2.1 sentence is
   where a challenge will land.
2. **After naming is settled** — update `Framework_level-language.excalidraw` and
   re-export the PNG, then rebuild the workflow doc.
3. Consider archiving the 08-11 document set to cut folder clutter.
