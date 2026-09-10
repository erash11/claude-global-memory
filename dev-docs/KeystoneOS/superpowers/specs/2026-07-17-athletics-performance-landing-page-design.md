# Baylor Athletics Performance — Landing Page Spec / PRD

**Date:** 2026-07-17
**Author:** Eric Rash (with Claude), grounded in Fireflies meeting `AthleticsPerformance_Website_Planning` (2026-07-16, Eric Rash + Silas Newby)
**Purpose:** Hand-off document for Claude Design to build a proof-of-concept landing page for the Athletics Performance department.
**Status:** Approved design, placeholder content (real text incoming from Silas Newby)

---

## 1. Overview

A single scrolling, public-facing landing page for the Baylor Athletics Performance department, covering **all sports** (football, basketball, olympic sports). The page presents the department's mission, five standards, staff, facilities, technology, and integrated-care model.

**Positioning / differentiator:** "Nobody's giving that level of access through a website." The page should feel like an intimate, guided look inside the department — the kind of access a recruit normally only gets on an official visit.

**This is a proof of concept.** It exists to be shown to department leadership for a green-light ("build a proof of concept and let them shoot it down or not"). It is not the production site.

## 2. Audiences (ranked)

1. **Prospective athletes and their families (primary).** Tone: aspirational, development-focused, caring. They should leave thinking: *these people will develop me, and this place is world-class.*
2. **Prospective staff (secondary).** The technology stack, interdisciplinary model, and facility depth double as an employer pitch.
3. Current athletes, campus partners, general public (tertiary — served incidentally).

## 3. Hard Constraints

| # | Constraint | Why |
|---|-----------|-----|
| C1 | **Sidearm-portable.** Static HTML/CSS/light-JS only. No backend, no build-time frameworks, no exotic dependencies. Cody will hand the concept to Sidearm to recreate on their platform — nothing may rely on infrastructure Sidearm can't reproduce. | Baylor will not self-host; production lives on Sidearm. |
| C2 | **All media are placeholders** in the POC. Every slot documents its aspect ratio and target resolution so real assets drop in later. | Real photo/video shoots (headshots, gimbal facility tours) happen after concept approval. |
| C3 | **All text is placeholder** until Silas Newby delivers real content (mission statement, five standards, staff roster, facility details). Placeholder copy must be realistic in length and tone, and every slot has a defined owner and size limit (§7). | Per meeting agreement: Silas supplies "all factual and text-based content." |
| C4 | **Visual tokens are abstract.** An existing Claude Design design system will be applied. This spec defines structure, hierarchy, content slots, and interaction; it notes light/dark *rhythm intent* per section but does not hard-code colors, type, or spacing. Baylor green/gold is assumed at the system level. | Design system supersedes ad-hoc styling. |
| C5 | **Single file / single page.** One long scrolling page; no routing. | Easiest to demo and to port. |
| C6 | **Responsive + accessible.** Works on phone (recruits' parents will open this on mobile); flip/carousel interactions must be keyboard- and touch-operable; all media slots carry alt text slots. | Public-facing university page. |

## 4. Page Structure (top to bottom)

Section rhythm intent: **dark → light → light → dark → light → light → dark → dark** (hybrid — dark for cinematic sections [hero, facilities, close], light for readable/informational sections [staff, technology]). The design system decides the actual treatments.

### S1. Hero *(dark, cinematic)*
- Full-bleed background media slot: **16:9 video loop placeholder** (fallback: still image).
- Department name: "Baylor Athletics Performance" (placeholder — confirm official name).
- Mission one-liner (pull-quote from the mission statement, ≤120 chars).
- Scroll cue.

### S2. Mission & Five Standards *(light)*
- Mission statement block (≤80 words).
- **Five standard cards**, equal weight, one row on desktop / stacked on mobile. Each: standard title (≤30 chars) + one-sentence description (≤140 chars).
- These are the same mission and standards used department-wide — consistency across sports is the point; do not editorialize per-sport.

### S3. Staff *(light)*
- Responsive grid of **flip cards** (target: 12–16 placeholder staff; grid must gracefully handle 8–25).
- **Front:** headshot (3:4 portrait), name, actual title, primary sport assignment.
- **Back (on click/tap/Enter):** hometown, education, years at Baylor, previous stops (≤3 institutions, most recent first), secondary sport assignment (optional — omit gracefully when absent).
- Flip is the meeting's signature interaction ("click it, spins around"). Must also work with keyboard focus and be announced to screen readers.
- Optional (nice-to-have, not required for POC): filter chips by sport.

### S4. Facilities *(dark, cinematic)*
- **Carousel of 6 large cards** — one per facility. Placeholder facility names (real names from Silas; known set includes Williams, Allison, Foster practice gyms/courts, indoor facility, soccer facility, Ferrell Center courts/weight room — final list is Silas's call; include any facility athletes train in or out of).
- Each card combines **carousel + flip** (per meeting: "it's a carousel with a card"):
  - Face: photo mini-carousel (3–4 slots, 16:9), facility name, primary sports served.
  - Flip/expand: brief history (built date, ≤60 words), room features list (4–6 bullets), **video-tour slot** (16:9) — reserved for the gimbal walkthrough of an active room (athletes training, coach-athlete conversations, room alive). Placeholder in POC.
- Carousel: swipe on touch, arrows + dots on desktop, keyboard-operable.

### S5. Performance Technology *(light)*
- Tile row (4–6 tiles): technology photo placeholder (athlete-using-it context shot, 4:3) + technology name + **one line** on what it does for the athlete (≤120 chars).
- Placeholder set: Perch, VALD ForceDecks, VALD NordBord, Catapult GPS (+2 open slots).
- Tone: *advertise, don't explain.* Per Silas: "not necessarily in depth — a great tool that helps us collaborate across departments and prescribe training." No methodology deep-dives.

### S6. One Integrated Department *(light)*
- Collaboration section: Athletics Performance shown as connected with **athletic medicine, nutrition, and mental health** — one care model, not silos.
- Short intro blurb (≤60 words) + a simple connected visual (4 nodes around the athlete; CSS/SVG, no library).
- Message: technology and data are shared across these departments in service of the athlete ("group effort").

### S7. Beyond the Weight Room *(dark)*
- Intangibles blurb (≤80 words): habits, discipline, consistency, developing well-rounded people — the athletic-development and education mission beyond sets and reps.
- One open slot for initiatives (e.g., the performance clinic) — placeholder card, hidden if unused.

### S8. Footer *(dark)*
- Department contact, location, link slot to official athletics site (baylorbears.com), university boilerplate slot.

## 5. Interactions Summary

| Interaction | Where | Behavior | Notes |
|---|---|---|---|
| Card flip | S3 staff, S4 facilities | Click/tap/Enter toggles front↔back; 3D flip or crossfade per design system | Must degrade to show-all if JS unavailable |
| Carousel | S4 facilities (outer + photo mini-carousels) | Swipe / arrows / dots; no autoplay on the outer carousel | Simple, dependency-free JS |
| Video slots | S1 hero, S4 tours | POC: poster-frame placeholder with play affordance (non-functional or stock loop) | Document target specs (§7) |
| Smooth scroll | Global | Scroll cue and any anchor links scroll smoothly | Respect `prefers-reduced-motion` |

## 6. Out of Scope (POC)

- Real photography, videography, headshots (placeholders only).
- CMS/backend, forms, search, analytics.
- Per-sport sub-pages or sport-specific content variants.
- In-depth technology methodology content.
- Recruiting-compliance review (needed before production, not for POC).
- Sidearm implementation itself (Cody's phase).

## 7. Content Slot Inventory

Owner for all text content: **Silas Newby**. Media owner: TBD (post-approval shoot). Placeholder discipline: realistic length/tone, clearly fake names (no real staff names until roster is supplied).

| Slot | Section | Type | Spec / Limit | Qty |
|---|---|---|---|---|
| Hero media | S1 | Video (loop) or image | 16:9, 1920×1080 | 1 |
| Department name | S1 | Text | ≤40 chars | 1 |
| Mission one-liner | S1 | Text | ≤120 chars | 1 |
| Mission statement | S2 | Text | ≤80 words | 1 |
| Standard title | S2 | Text | ≤30 chars | 5 |
| Standard description | S2 | Text | ≤140 chars | 5 |
| Staff headshot | S3 | Image | 3:4, 600×800 | 12–16 |
| Staff name / title / primary sport | S3 | Text | name ≤30, title ≤50, sport ≤30 chars | per staff |
| Staff back fields | S3 | Text | hometown ≤40; education ≤60; years at Baylor (int); previous stops ≤3 × ≤40 chars; secondary sport ≤30 (optional) | per staff |
| Facility name | S4 | Text | ≤40 chars | 6 |
| Facility photos | S4 | Image | 16:9, 1600×900 | 3–4 per facility |
| Facility history | S4 | Text | ≤60 words | 6 |
| Facility primary sports | S4 | Text list | ≤5 items | 6 |
| Facility features | S4 | Text list | 4–6 bullets, ≤60 chars each | 6 |
| Facility video tour | S4 | Video | 16:9, 60–90s target | 6 |
| Technology tile (image + name + line) | S5 | Image + text | 4:3 800×600; name ≤30; line ≤120 chars | 4–6 |
| Integration intro | S6 | Text | ≤60 words | 1 |
| Intangibles blurb | S7 | Text | ≤80 words | 1 |
| Initiative card | S7 | Text | title ≤40, blurb ≤50 words | 0–1 |
| Footer contact/links | S8 | Text | standard | 1 set |

## 8. Success Criteria

1. Department leadership approves the concept (or gives concrete revision direction) from a single scroll-through demo.
2. Cody confirms every element is reproducible on Sidearm without redesign.
3. Silas's real content drops into the defined slots with no layout rework.
4. The page communicates the differentiator: a recruit's parent scrolling on a phone gets a genuine inside look — faces, rooms, tools, and care model — within 90 seconds.

## 9. Build Notes for Claude Design

- Single HTML file preferred (inline CSS/JS acceptable) to keep the hand-off to Sidearm trivial.
- Apply the existing Claude Design design system for all visual tokens; this spec's light/dark rhythm (§4) is intent, not law.
- Use `prefers-reduced-motion` guards on flips, carousels, and smooth scroll.
- Every image slot renders a labeled placeholder (slot name + dimensions) so reviewers can see exactly what media is owed.
- Keep JS < ~150 lines: flip toggles, carousel, scroll cue. Nothing else.

## 10. Open Items

| Item | Owner | Blocking? |
|---|---|---|
| Mission statement + five standards text | Silas Newby | No (placeholders) |
| Staff roster + bio fields | Silas Newby | No (placeholders) |
| Final facility list (6) + details | Silas Newby | No (placeholders) |
| Official department display name | Eric | No |
| Media production plan (tours, headshots) | Post-approval | No |
| Sidearm feasibility check | Cody | Post-POC |
