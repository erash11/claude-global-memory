# Software and Technology Management Framework — Design

**Date:** 2026-08-04
**Owner:** Eric Rash, Director of Applied Performance (DAPP)
**Sponsor:** Kenny Boyd
**Due:** Draft complete Friday 2026-08-07; presented Monday 2026-08-10
**Audience for Monday:** Kenny Boyd, John Allen, Micah, and the broader stakeholder group

---

## 1. Origin and mandate

This design derives from three sources:

1. **Fireflies meeting `Technology_Framwork`, 2026-08-03** (54m, Kenny Boyd + Eric Rash) —
   a whiteboard working session. Kenny's action item to Eric: *"Develop and finalize the
   draft Software and Technology Management Framework and workflow document by the end of
   the week for review and presentation at the scheduled meeting on Monday, the 10th."*
2. **Whiteboard photo `ProposalApproval.jpg`** — three phases, the Phase 1 workflow, the
   physiologic-data action item, and four open questions.
3. **Reference library in `DEV/Sport_Tech_Vetting/`** — STRN Quality Framework materials
   and the Eversheds Sutherland athlete-data one-pager.

Kenny's explicit instruction on finish level: get it **80% there and let the key
stakeholders take it the last 20%**. This design targets exactly that.

### Naming (settled in the meeting)

**"Software and Technology Management Framework."** Kenny worked through this on the
record. "Technology" alone risks staff thinking software is out of scope; "software"
alone risks the reverse. "Performance" is deliberately excluded so the framework is not
pigeonholed as a performance-only process — it is intended to cover all athletics units.

---

## 2. The strategic spine: NCAA SSI alignment

The single most important design decision.

`ES - Harnessing athlete performance data.pdf` is the Eversheds Sutherland one-pager
Kenny referred to in the meeting ("that system that Lisa was sharing" / the ATT PDF from
May), and told Eric to test the framework against: *"I would test the framework against
that... what other questions do we have to answer... if we're going to do an internal
audit on what we're doing in our performance technology management."*

It cites the **NCAA Sports Science Institute guidance on the Responsible Use of
Performance Technologies in College Athletics**, whose five recommendations map almost
one-to-one onto Kenny's whiteboard:

| NCAA SSI recommendation | Framework component |
|---|---|
| Implement written policies | The framework document itself |
| Educate student-athletes (informed consent) | Data appendix — consent section |
| Manage data rights (ownership, storage, access authority, permitted use) | Data appendix — categorization and ownership |
| Establish process for implementing new technologies (cross-disciplinary) | Phase 1 — Proposal, Approval, Purchase |
| Develop system for continual improvement | Phase 3 — Product Review, Renewal Decision |

**Why this matters for Monday.** Kenny's own stated risk is that the group reads this as
overreach — *"the will of the group is like, this is overkill, Kenny."* Anchoring the
framework to published NCAA guidance reframes it from a preference to a documented
compliance gap Baylor is closing. That is the argument that carries John Allen and Micah.

**Constraint from the user:** the NCAA framing stays, but it is presented as alignment
and rationale, not as an accusation that Baylor is currently non-compliant.

### Legal grounding available from the same source

- **FERPA** — student records; consent, retention, and disclosure obligations when
  releasing records to third parties, explicitly including AI vendors analyzing athlete data.
- **HIPAA** — where evaluation tools touch medical and injury records.
- **State privacy laws** — increasing scrutiny of wearable-derived heart rate, sleep, and
  stress metrics.

These are cited as *considerations that the framework is designed to surface early*, not
as legal advice. Legal review belongs to the group.

---

## 3. Framework structure

### Purpose statement

Kenny's own words, tightened: *to increase the efficiency and timeliness of requests for
software and technology purchase and implementation across Baylor Athletics.*

### Stated outcomes

Three named by Kenny in the meeting, plus one from Eric:

1. A consistent, shared understanding of **the entire inventory of software and
   technology in use** across the department.
2. **Improved utilization** of what is already owned — surfaced by the Phase 3 usage review.
3. **Coordinated renewal and term review**, so the department stops discovering it is in
   the final year of an agreement with no time to act.
4. **Increased staff fluency** (Eric) — so SPAs and administrators can speak to technology
   questions rather than defaulting to whatever a coach asks for in the moment.

### The three phases

**Phase 1 — Proposal, Approval, Purchase**
- Initiated by DAPP, Head Coach, or Admin Unit Director.
- **Business Office is the filter for all requests** — the first control point / quality
  control gate.
- Completed **Idea Form** and internal **ATH Form** submitted to ITS.
- Request is disseminated only after clearing **both** control points (BO, then ITS).
- **DAPP holds a weekly standing meeting with the ITS representative** to review the
  status of all open requests.

**Phase 2 — Implementation and Product Use**
- Individual project management **may sit with administrative staff other than DAPP**.
- Status updates flow from the ITS standing meeting through DAPP to the assigned project
  manager and stakeholders.
- DAPP's role is explicitly **facilitator, not owner** — Kenny's language: *"switchboard
  operator," "single throat to choke," "the weatherman."* Kenny also stated directly:
  *"The workflow has to acknowledge that you're not necessarily the subject matter expert.
  You're not the project manager."* This must be written into the document so DAPP does
  not inherit ownership of every departmental project.

**Phase 3 — Product Review, Renewal Decision**
- Trigger: **six months, or end of competitive season — whichever is longer.**
  Kenny initially said "whichever comes first" and corrected himself on the record to
  "whichever is longer," so that in-season tools are judged on in-season usage.
  The whiteboard records the corrected version.
- Review examines actual utilization against stated intent. Kenny's example: a coach with
  a tool available eight months at under 20% utilization gets a conversation, not an
  automatic cancellation — the review is diagnostic first (is the vendor failing? is the
  integration broken? is training missing?) and a renewal decision second.
- Feeds the renewal/term calendar so agreements are reviewed before the decision window
  closes.

---

## 4. Data appendix (inside the framework document)

Delivered as an **FAQ**, per Kenny: *"it's almost like FAQs. Here's the Q's, here's the
potential A's to the Q's. But it's like these are questions that we need to have answers
to. This is an attempt to answer some of those questions."*

### Categorization (Kenny's taxonomy, developed on the record)

| Category | Definition | Ownership posture |
|---|---|---|
| **Performance data** | External data *generated by* the athlete (GPS, velocity, tracking, box-score derivatives) | Institutional stewardship; athlete-generated |
| **Physiologic data** | Internal data *generated by* the athlete (sleep, HR, hydration, body composition, bloods) | Athlete-owned; highest scrutiny |
| **Business operations data** | Data not generated by athletic performance (ticket sales, attendance, social following) | Institutional |

Sub-distinction also raised: **individual vs. team** performance data. Team data is
aggregated from individual data but is treated as team/institutional.

### Recommendations to the group (NOT stated positions)

**Design constraint from the user:** these are presented as *recommendations for the
group to ratify*, not as decided policy. This is deliberate — the consent mechanism and
access rules require legal, compliance, and medical input that is not Eric's to assert.

1. **Physiologic data may warrant per-instance consent rather than blanket consent.**
   Kenny: *"I think you can blanket consent performance data, but physiologic data, you
   need to have a consent for that moment."*
2. **No single individual should be the sole holder of athlete physiologic data**, and
   medical staff should be in the routing path. Kenny: *"a coach can't be the single...
   if anything, that's got to be run through them [medical]."*
3. **Coaching staff may receive summary rather than raw physiologic data.** Precedent
   Eric raised: DEXA and body composition are already handled this way — coaches receive
   summary information, not raw output. Framing matters here and should be
   *unburdening*, not withholding: the specialist owns the interpretation.
   The document should note honestly that this will not be universally welcomed.
4. **External sharing of athlete data requires athlete consent.** Precedent: providing
   an athlete's GPS numbers to an outside scout.
5. **External contractors require an executed agreement with institutional privacy and
   data protection terms before access to sensitive information.** This is already live
   practice — Kenny is running Joe Reed and Courtney Benjamin through exactly this.

### Categorization at intake

A request must declare its data category on the Idea Form. Kenny: *"when you have a
request, part of the request is going to include how is this categorized?"* This is what
lets ITS reach a yes/no faster and routes the request to the correct review depth.

---

## 5. Answers to the four open whiteboard questions

The whiteboard lists four questions in red. Two are answered by Section 4
(*How are we categorizing data?* and *Who owns data?*). The other two:

**How do we handle "emergency" requests?**
An **expedited lane, not a bypass.** Same gates, compressed clock, plus a short risk
checklist. This is Kenny's own position: *"you're not getting an exception to this
workflow. We just need to make sure there aren't any landmines that we're not aware of."*
Eric's honest caveat is included in the document: most urgent requests are reactionary,
and **no process delivers same-week procurement** — the framework's answer to urgency is
to make routine requests predictable enough that fewer become emergencies.

**How do we handle "product trials"?**
**Provisional approval in a contained sandbox** with a hard end date, no physiologic or
identifiable athlete data until full approval, and a mandatory review at trial end that
converts to approval or termination. This is Eric's proposal from the meeting: *"Do they
have a way to provisionally approve something and keep it in a sandbox?... then put it
through the standard processes, and then okay, cool, it's approved and then you can
release all that information."*

---

## 6. Evaluation scorecard

### Starting point already exists

`Sport_Tech_Vetting/Sports Tech Evaluation Assessment Sheet.pdf` (May 2024) is **already
a Baylor Applied Performance–branded adaptation** of the STRN Quality Framework. It
carries 20 of STRN's 23 features, dropping **Safety**, **Environmental Sustainability**,
and **Accessibility**. This design extends that sheet rather than rebuilding it, and
retains the same 20 features and the same three-level STRN rating language.

### What is added: tiering

STRN's own follow-up paper (*Bringing the Framework to Life*, v1.0 Dec 2024) documents
several rating systems, including a **hurdle rating** — a minimum threshold / pass-fail
model in which technology must meet a minimum criteria set to be permitted for use.
That is precisely what a procurement gate needs, and the flat sheet does not currently
provide it.

- **Gate features (pass/fail):** Compliance, Privacy, Ownership, Transparency,
  Interoperability. A "weakness needing improvement" on any of these halts the request
  regardless of total score. These are the institutional-risk and lock-in features.
- **Scored — evidence quality:** Accuracy, Repeatability, Reproducibility,
  Specifications, Construct Validity, Concurrent Validity, Predictive Validity,
  Functionality.
- **Scored — operational fit:** Usability, Robustness, Data Representation, Customer
  Support & Training, Data Standardization, Maintainability, Scalability.

### Review depth scales to risk

Kenny's stated fear: *"we might be making more work for us than needed."* A flat
20-feature evaluation on every request would prove him right. Three request tiers:

| Tier | Trigger | Review depth |
|---|---|---|
| **Light** | No athlete data; single unit; low or one-time cost | Gate features only |
| **Standard** | Performance data, multi-team, or recurring cost | Full scorecard |
| **Elevated** | Physiologic/health data, external data sharing, or third-party/AI processing | Full scorecard + data protection review + medical sign-off |

Dollar thresholds are deliberately left blank — that is a Business Office decision and is
flagged as an open decision for the group.

---

## 7. Deliverables

All Word format (`.docx`), so the group can track-change. Sources retained for fast
revision after Monday.

| # | Artifact | Purpose |
|---|---|---|
| 1 | `Software_and_Technology_Management_Framework_DRAFT.docx` | The core document — purpose, outcomes, 3 phases, roles, data appendix FAQ, open decisions |
| 2 | `Workflow_Diagram.png` (embedded in #1, also standalone) | Visual of the request path through both control points and all three phases |
| 3 | `Form_1_Technology_Idea_Form.docx` | Phase 1 intake — includes data categorization and tier determination |
| 4 | `Form_2_Internal_ATH_Form.docx` | Internal athletics form submitted alongside the Idea Form to ITS |
| 5 | `Technology_Evaluation_Scorecard.docx` | Tiered 20-feature scorecard with gate/scored split |
| 6 | `Request_Tracker.xlsx` | The weekly ITS standing-meeting tracker |

### Tracker columns

From Kenny's description: *"here's the project, here's the item, and here's when you
submitted it, and here's when the desired implementation date is, and then what's holding
it up."* Plus unit grouping, since Kenny described requests reported by unit
(*"nine of them are from health and wellness, two of them are from fan engagement"*).

Columns: Request ID · Unit · Project/System · Item · Requester · Project Manager ·
Data Category · Tier · Date Submitted · Desired Implementation · Current Status ·
Blocker / What's Holding It Up · Last ITS Update · Next Review Date.

---

## 8. Open decisions flagged for the group

Explicitly marked in the document as belonging to the stakeholder group, not to DAPP:

1. Dollar thresholds separating Light / Standard / Elevated review tiers.
2. Named approver at each gate — who signs at the Business Office, who signs at ITS.
3. Consent mechanism and system of record for physiologic-data consent.
4. Whether coaching staff access to raw physiologic data is restricted, and by what rule.
5. Target service-level times for standard vs. expedited requests.
6. Where the software inventory register lives and who maintains it.
7. Whether this is issued as guidance/best practice or as departmental policy — the
   2026-07-30 meeting recorded a preference for flexible best-practice documents over
   rigid formal policy, aligned to NCAA guidance.

---

## 9. Scope boundary

**In scope now:** the six deliverables above.

**Deferred until the group approves the framework:** the software inventory register,
the renewal/term calendar, and any ticketing-system build. Eric raised the ticketing
option in the meeting (*"could probably build out a ticketing system for something like
that"*) and correctly identified the real constraint — *"it's just getting people to do
the process."* Tooling before buy-in is wasted effort.

---

## 10. Registry note

The portfolio registry already contains two related entries:

- `Sport_Tech_Vetting` (job, rank 3, **shipped**) — the 2024 assessment-sheet work whose
  output this design extends.
- `NCAA_BestPractices_Doc` (job, rank 2, **idea**) — from the 2026-07-30 Kenny meeting
  action item to draft best-practice processes aligned with NCAA guidance.

**Decision (Eric, 2026-08-04): `NCAA_BestPractices_Doc` stays a separate project.**
Related, but distinct scope — it is not folded into this one. An earlier draft of this
spec recommended merging them; that recommendation was considered and declined.

The useful boundary for whoever picks up `NCAA_BestPractices_Doc`: this framework already
implements two of the five NCAA SSI recommendations — *establish a process for
implementing new technologies* (Phase 1) and *develop a system for continual improvement*
(Phase 3) — and makes a first pass at *manage data rights* and *educate student-athletes*
in Appendix A. The best-practices document can therefore reference this framework for the
request/approval/review process rather than restate it, and spend its own length on the
wider performance-technology infrastructure questions the 2026-07-30 meeting raised.
