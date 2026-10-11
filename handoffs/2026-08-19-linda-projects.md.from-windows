# Handoff — Linda Projects (Applied Performance)

**Date:** 2026-08-19
**Working dir:** `/Users/kristinarash/DEV/Linda Projects` (deliberately **not** a git repo)

---

## What this was

Eric asked for a project plan for Linda Mungai, a new Applied Performance Specialist,
built from (a) a Fireflies conversation with Chris Ruf about what she'd work on and
(b) a PDF at `.../XXXX_Transfer/LindaICE.pdf`.

The PDF turned out to be her **ICE Form I-983 STEM OPT training plan** — a signed federal
document, not a project list. That reframed everything: the projects have to map to the
form, and each has to leave a written artifact she can cite in her periodic progress
evaluations. Ruf said the same on 2026-08-19: *"we'll just tailor her work to that."*

Then it grew: execution plan → meeting prep for a 2026-08-20 kickoff → humanizing pass →
Baylor house-style PDFs → flow diagrams.

---

## Decisions made (and the reasoning that would otherwise be lost)

1. **Two separate plans, not one.** The supervisor doc carries immigration detail
   disclosed in a closed meeting ("keep it in this room"), Ruf's read that the tennis
   coach will ignore the conditioning test, Kenny Boyd's note that coach authority comes
   from him and Chris *not* Eric, and which project Eric would cut. None of that can
   reach Linda. Doc `01` is the sanitized version. Verified by word-search, not by eye.
2. **The I-983 is the spine, not the meeting notes.** Every project is framed as
   objective → first step → tools → neuroscience tie → evidence artifact → how it gets
   presented. The evidence column is the whole point.
3. **Sequence was already settled by Ruf and Eric** — profiles → normative ranges →
   conditioning test → match profiles. Not re-derived.
4. **P3 framed as "complete either way."** Ruf expects the coach to ignore it, so the
   plan tells Linda up front that adoption is not the success condition. Said in August
   this lands; said in March it sounds like an excuse.
5. **Two hard gates written in:** lock the P1 test battery before testing anyone
   (one-way door), and establish the noise floor before interpreting anything.
6. **Multi-page PDFs use a charcoal header band + light body**, not the full dark ground
   of the printed card. Eric chose this. The execution plan has checkboxes she ticks by
   hand — a dark ground would burn toner and defeat that.
7. **Nothing uploaded externally.** No excalidraw.com export, no artifact publish. The
   folder sits next to confidential material.

---

## Files — everything created this session

Working folder `/Users/kristinarash/DEV/Linda Projects/`:

| Path | What |
|---|---|
| `README.md` | Folder index, confidentiality rules, rebuild commands, the render gotcha |
| `01_ExecutionPlan_LindaFacing.md` | Linda-facing plan. 4 projects × 3 phases, 27 milestones |
| `02_SupervisorPlan_I983_CONFIDENTIAL.md` | **Eric only.** I-983 mapping, his obligations, internal context |
| `03_MeetingAgenda_2026-08-20_EricOnly.md` | **Eric only.** Run sheet + do-not-say list |
| `04_Linda_OnePager.md` | Markdown source of the handout |
| `Linda_ProjectPlan_2026-27.pdf` | Handout. 1p portrait |
| `Linda_ExecutionPlan_2026-27.pdf` | Full plan. 7p portrait |
| `Linda_MeetingRunSheet_2026-08-20_EricOnly.pdf` | Run sheet. 3p portrait |
| `Linda_ProjectFlowDiagrams.pdf` | 3 flow diagrams. 3p **landscape** |
| `source/build.py` | Builds all four PDFs from markdown + HTML |
| `source/report.css` | Multi-page style (charcoal band, light body) |
| `source/onepager.html`, `source/diagrams.html` | Hand-authored pages |
| `source/baylor-brand.css` | Copy of the brand file (fonts + BU marks embedded) |
| `source/I983_page3.png`, `source/I983_page5.png` | Extracted form pages |
| `diagrams/README.md` | What each diagram shows |

Also written outside the folder:

- `~/Library/CloudStorage/OneDrive-BaylorUniversity/00_Primary_Storage_Drive/08_ADMIN/Personnel/README_LindaMungai_ProjectPlans.md` — pointer note
- `~/.claude/projects/-Users-kristinarash-DEV-AgentAssist/memory/` — `MEMORY.md`,
  `reference_baylor-house-style.md`, `project_chrome-pdf-font-gotcha.md`

Rebuild everything: `cd "/Users/kristinarash/DEV/Linda Projects" && uv run --with markdown python source/build.py`

---

## The trap that cost real time

Chrome `--print-to-pdf` does not wait for `@font-face` to load. With the 1.6 MB
`baylor-brand.css` it printed **four PDFs with zero text** — all rules and colors, no
words — and exited 0. Caught only because Eric opened them.

Fix is `--virtual-time-budget=20000`, now in `build.py` and both READMEs.
**Verify by rasterizing the PDF, never by screenshotting the HTML.** The HTML always
looked perfect; that is what hid it.

---

## Next actions, most important first

1. **Eric's meeting with Linda is Thursday 2026-08-20.** He needs to read
   `03_...EricOnly.md` before handing her anything. Print `Linda_ProjectPlan_2026-27.pdf`
   for her; email `Linda_ExecutionPlan_2026-27.pdf` after.
2. **Schedule the recurring supervision meeting.** Required by the I-983, still not booked.
   It's one of two decisions the run sheet says not to leave the room without.
3. **Ask Ruf two things:** is the Kinexon/volleyball analysis Linda's or Blair's, and who
   signs the I-983 progress evaluations — Eric or Kenny?
4. **Ask Linda for the complete I-983.** We only have pages 3 and 5 of 5.
5. **Confirm evaluation due dates** with the Baylor DSO / ISSS.
6. **Send the VALD normative data request** (milestone 2.1). Long lead time, blocks P2.

---

## Mid-flight / unresolved

- **No printer configured on this Mac.** `lpstat` reports no destinations. Eric asked
  twice to print; all four PDFs were opened in Preview instead. If he adds a printer,
  print with "Background graphics" enabled — and note the diagrams file is landscape
  while the other three are portrait.
- **Eric edited `04_Linda_OnePager.md` mid-session** and removed the ground-rules block
  (coach review + no athlete data in AI tools). Left removed as intended. Those rules are
  still in `01` and in his run sheet, so they get said aloud rather than handed over.
- He also corrected Connexon → **Kinexon** (my transcription error); propagated to `02`
  and `03`.
