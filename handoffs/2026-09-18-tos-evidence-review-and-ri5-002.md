# 2026-09-18 — TOS evidence review, Baylor-style documents, Research in 5 #002

## What this session was

Eric's softball S&C colleague is taking blame for a perceived cluster of thoracic
outlet syndrome cases. The head coach believes Baylor softball has a higher rate
than peer institutions. The ask was deep research into TOS causes in overhead
athletes, plus two specific questions from the athletic training staff:

1. Is there research behind "don't lift the pitchers before they throw"?
2. Can a muscular endurance or capacity deficit cause TOS?

## What was built

**1. Evidence review, 109 sources.** Five parallel research agents swept
epidemiology, mechanism, conservative care and capacity, softball workload, and the
lifting-timing question. Every citation was verified against PubMed or Europe PMC.
All 113 PMID references in the markdown were then batch-checked against NCBI
E-utilities: all resolve, zero transcription errors.

**2. Two Baylor house-style documents** built through `baylor_docstyle.py`, the real
Word pipeline used by the Tech Inventory deliverables (not a lookalike). Structured
on the Pyramid Principle after running `/anthropic-skills:articulation-skill`.

**3. Research in 5 #002** on Funakoshi et al. 2024, built from the same body of work.

## The headline answers

- **"No lifting before throwing" has no research support.** Three structured PubMed
  searches returned no baseball study on the question and no paper at all linking
  training timing to TOS. Adjacent evidence leans against the rule: heavy bench and
  row 15 min before throwing did nothing to water polo velocity or accuracy; 75% 1RM
  did nothing to tennis at 3 min, 24 h or 48 h; a morning lift improved afternoon
  throw distance. The one study showing a velocity drop used push-ups to failure and
  found lower-body fatigue dropped velocity just as much, which undercuts the
  protect-the-arm rationale.
- **The endurance hypothesis is coherent but unproven.** Daley 2021 found a 45%
  rotator endurance deficit in TOS patients, roughly double the strength deficit, but
  in 40-year-old non-athlete clinic patients, in the wrong muscle group, with causation
  unresolvable. Nobody has ever measured scapular endurance in a TOS population.
- **The peer comparison cannot be made.** TOS is not in any published NCAA
  surveillance output. The best collegiate figure is Talutis 2025: 15,609 D-I
  athletes, softball 1.3%, tennis 2.6%, all-sport 0.48%.

## CRITICAL — unresolved, blocks sending

Codex verification (task `task-mu74155w-xictvv`, session `01a0b51f-3af3-75a2-a924-97d28acac245`)
found real errors. **The documents were NOT corrected before the session ended.**

Full report: `~/.claude/plugins/data/codex-openai-codex/state/DEV-b7470cd4d260a467/jobs/task-mu74155w-xictvv.log`

Three numeric misquotes, each load-bearing:

1. **"About half of true pitch volume is uncounted" is wrong.** Kamarajugadda 2025
   measured the share of *outings exceeding a recommendation* (25.6% game-only vs
   51.2% including bullpen and warm-up), not the share of pitches that go uncounted.
   An exceedance rate was converted into a volume composition. It is also a **high
   school** study, not collegiate. This claim drives the "cheapest fix" recommendation
   and appears on the briefing note, the full review and both artifacts.
2. **"The cocked position roughly doubles scalene stiffness" is wrong.** Takaba 2022:
   14.4 vs 9.4 kPa is a **53% increase**. Near-doubling (18.1 kPa) needs ABER *plus*
   contralateral neck rotation. Two conditions were compressed into one claim.
3. **"Lower-body screening predicts about half the shoulder load" misattributes
   variance.** Ulman 2025: **body mass plus pitch velocity** explained 49.9%; hip
   rotation strength added **6.3 percentage points**. The whole 49.9% was credited to
   LE screening, inflating the strongest S&C recommendation in the document.

**The central statistical argument does not hold as written.** At the brief's own
assumed 4/100,000/year, lambda = 0.0014 for a 35-athlete season, so P(>=2 cases) is
about 0.0001%. Two cases is NOT "within chance" under that model. The Poisson
confidence intervals used answer a different question: the plausible underlying rate
*after* observing events, not the probability of observing them under the baseline.

**The fix:** the conclusion survives but needs the right denominator. Talutis gives
1.3% of softball athletes over seven years, which is athlete-specific and makes two
cases unremarkable. Rebuild the section on that, and drop the general-population rate
from the reassurance argument. Also: "four orders of magnitude" is ~2,143x, so 3.3.

Smaller: "109 sources each checked against PubMed" is imprecise (109 PMIDs plus
Devaney, Oliver and Freetly, which are DOI-verified). "TOS is not separately coded in
the NCAA ISP" is stated flatly on the one-pager when the full review concedes the
Datalys codebook was unreachable; "no published NCAA benchmark exists" is defensible.
"Venous TOS 5-10 fold over-represented" describes referral mix, not incidence.

Codex's own summary: *"The central concern is not fabricated literature. Most
citations are real and many study-level numbers are accurate. The risk comes from the
final inferential step."* That is a fair description. Descriptive findings were
over-converted into causal and actionable claims.

**Research in 5 #002 is unaffected** — its numbers come straight from Funakoshi's
tables and none were flagged.

## Files created or modified

**TOS evidence review** — `~/Desktop/DEV/TOS_Evidence_Brief/`
- `scripts/build_briefing_note.py` — one-page coach note. One page is a hard constraint.
- `scripts/build_full_brief.py` — 14-page evidence review, 11 sections, 25 tables.
- `scripts/export_pdfs.py` — drives Word by COM, reports Word's page count.
- `deliverables/TOS_BRIEFING_NOTE_ER_2026-09-18.docx` and `.pdf` (1 page)
- `deliverables/TOS_EVIDENCE_REVIEW_ER_2026-09-18.docx` and `.pdf` (14 pages)
- `artifacts/source-evidence-review.md` — long form with all 109 citations and PMIDs
- `artifacts/tos-brief-artifact.html`, `artifacts/tos-onepager-artifact.html`
- `README.md`, `.gitignore`

Not tracked by git: `~/DEV`'s `.gitignore` starts with `/*` (thin repo), so this
project is invisible to git. Nothing was committed. Adding a negation rule would
change that policy and was not done unasked.

**Also on Drive:** `G:\My Drive\00_Primary_Storage_Drive\04_RESEARCH\TOS_Evidence_Brief_2026-09\`
(same four docx/pdf files)

**Vault:** `~/Desktop/SecondBrain/Knowledge/sport-science/thoracic-outlet-syndrome-overhead-throwing-athletes.md`
(8,800 words, uncommitted)

**Web versions, private artifacts:**
- Full brief: https://claude.ai/artifact/BYngQJBiEpdKfP4y83FKSb
- One-pager: https://claude.ai/artifact/BFXvVvusPU2yJRxyWipiZ8 (v2, humanizer pass applied)
Both must be shared from each page's Share menu before anyone else can open them.

**Research in 5 #002** — `~/Desktop/DEV/Weekly_Research_Review/`
- `reviews/002_thoracic-outlet-overhead/review.json`, `notes.md`
- Branch `worktree-ri5-002-tos-overhead-athletes`, commit `da55bbd`, **PR #8 open**
- Drive: `G:\My Drive\00_Primary_Storage_Drive\07_EDUCATION\Research_in_5\002_thoracic-outlet-overhead\`
- QA PASS on all ten slide images, Agency FB embedded in both PDFs. **Published, not sent.**

**Skill repair** — `~/.agents/skills/articulation-skill/`
- Installed `SKILL.md` and `references/examples.md` from the synced copy. The symlink
  at `~/.claude/skills/articulation-skill` was fine; its target directory was empty,
  which is why the skill never loaded. It registered immediately after the copy.

## Decisions worth keeping

- **Paper choice for RI5 #002 was Funakoshi 2024, not Freetly 2024.** Freetly (softball
  pitcher utilization, 2.9x the innings on a third the staff) is more actionable, but
  it lands directly on the softball coaching staff during a live dispute. Funakoshi is
  on-topic for TOS and politically neutral. Eric chose this.
- **RI5 #002 graded Preliminary, not Moderate.** Retrospective single-centre series,
  everyone had surgery after conservative care failed, two thirds of the eligible pool
  excluded or lost to follow-up, only 3 of 79 athletes played softball.
- **The coach one-pager deliberately omits the lifting-timing question.** Raising it in
  front of the head coach would make the document read as a rebuttal rather than a
  briefing. It is an internal staff matter and lives in the full review.
- **A concession line was pulled from the coach one-pager** at Eric's instruction:
  "we will not claim it prevents TOS" on the scapular capacity row.
- **Three figures were deliberately excluded after tracing failed**, and the full
  review says so: the "3 to 80 per 1,000" incidence figure (traces to a journal not
  indexed in PubMed), "Roos described 14 types of congenital band" (no Roos primary
  says 14; it is seven in 1976 and nine in 1980), and "1,200 to 1,500 pitches per
  tournament weekend" (cited to a biomechanics paper reporting no tournament volume).

## Gotchas learned

- **Word inserts an empty paragraph after a table that ends the document body.** That
  phantom paragraph alone created a second page on the briefing note after the content
  already fit. `d.spacer(0)` at the end makes pagination deterministic.
- **Long table cells wrap to two lines and cost far more vertical space than the same
  words in a paragraph.** When a Baylor doc runs over, shorten table cells before prose.
- **`baylor_docstyle` validator limits are tighter than `docs/CONTENT_SPEC.md` says**
  in the RI5 repo: `trust.design` 45, `trust.sample` 60, chart row `label` 22.
  build.js is the authority; the spec text is stale. Noted in that repo's STATUS.
- **Europe PMC `fullTextXML` is the reliable way in when PMC blocks scripted PDF
  download.** It carries every table. Say in notes.md that pages are journal pages.
- **The worktree guard rejects Bash commands containing the substring "git"** even
  inside an unrelated identifier — `isdigit` tripped it. Rename the variable.
- **`~/DEV` thin-repo `.gitignore` starting `/*` means new project folders are
  invisible to git.** A worktree commit there will be empty.

## Next actions, most important first

1. **Correct the three misquotes and rebuild the statistical section** on the Talutis
   denominator. Then regenerate both docx/pdf pairs (`python scripts/build_*.py` then
   `scripts/export_pdfs.py`) and republish both artifacts. Roughly fifteen minutes.
   **Do not send either document until this is done.**
2. Review and merge PR #8 (Research in 5 #002). Then post `teams.md` and send
   `email.txt` with the dark PDF, if the timing is right given the softball dispute.
3. Share the two artifact links from each page's Share menu if the colleague is to
   read the web versions.
4. Decide whether `TOS_Evidence_Brief` should be tracked by git. It currently is not.
5. Optional: repair the two other broken skill symlinks, `humanizer` and
   `session-handoff`, both pointing at empty dirs under `~/.agents/skills/`. Recoverable
   copies exist in `~/.claude/skills/synced/`, `~/DEV/agent-skills/` and the June backup.
   The June humanizer copy has 5 files against the current 4, so diff before restoring.
   `humanizer` still works through the plugin path, so only `session-handoff` is truly lost.

## Open questions

- Should the corrected documents keep the same filenames, or get a `_v2` suffix? The
  originals are already on Drive and may have been opened.
- Is the Research in 5 #002 send timing right while the softball TOS question is live?
