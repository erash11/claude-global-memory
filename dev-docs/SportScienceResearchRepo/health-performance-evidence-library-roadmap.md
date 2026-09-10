# Baylor Athletics Health & Performance Evidence Library Roadmap

**Adopted:** July 21, 2026
**Status:** Phase 3 implemented; Phase 4 Batches 01–12 published
**Product name:** Baylor Athletics Health & Performance Evidence Library

## Decision

Maintain one shared evidence library for Baylor Athletics Health & Performance staff. Football becomes a searchable context within the library rather than the product identity. Sport-specific exports or views can be added later without splitting the source of truth.

The canonical evidence from the original 433-row library and its football-specific translations is retained. New work broadens the interface and evidence coverage without erasing the context that produced the current collection.

## Product Principles

1. **One evidence base, multiple contexts.** Do not create separate paper stores for each sport or discipline.
2. **Evidence first.** Abstract, methods, findings, and limitations remain distinct from practitioner translation.
3. **Context is metadata.** Sport, population, domain, and audience become filters, not required prose in every summary.
4. **Application notes are optional.** Do not force performance, medical, nutrition, or sport-specific claims when a paper does not support them.
5. **Exports are downstream views.** Future sport- or discipline-specific exports read from the same normalized library.
6. **Verification before volume.** Source identity, schema validity, and link resolution gate each published batch.

## Pre-Cleanup Baseline

The July 21, 2026 read-only audit established:

- 433 published rows: 8 Baylor internal entries and 425 source-backed rows
- 396 distinct local source PDFs represented cleanly
- 1,759 of 2,155 local source PDFs not represented
- 16 duplicated source-file groups producing 27 additional rows
- 2 unresolved source references
- 1 blank return-to-sport value
- Public GitHub Pages deployment healthy with 433 rows loaded

These counts supersede the older filename-filter estimate in `session.md`.

## Trustworthy Baseline and Current State

The July 21 cleanup removed 26 verified duplicate rows, repaired the malformed source links, separated two records that had been assigned the wrong shared source, restored the previously unreadable workload paper from its PDF, corrected one DOI/citation, and completed the blank return-to-sport field.

The baseline began at 407 canonical rows. After 12 full-text-reviewed pilot batches, the reproducible manifest at `docs/library-coverage-manifest.json` now reports:

- 549 canonical published rows with 549 unique stable IDs
- 540 local source-backed rows, 8 Baylor internal rows, and 1 DOI-backed external row
- no repeated or unresolved local source references
- no missing required fields or schema mismatches
- 2,155 PDFs representing 2,125 unique file contents
- 536 unique local source contents represented and 1,589 unrepresented
- all five publication quality gates passing

Run `npm run audit` before publication and `npm run audit:manifest` whenever the corpus or published library changes.

## Target Module Shape

The UI should consume a normalized paper interface rather than knowing whether a record came from the legacy schema or a future schema.

### Normalization seam

Introduce one normalization module when the taxonomy is implemented:

```text
papers.json record
      |
      v
normalizePaper(record)
      |
      v
normalized evidence record
      |
      +--> search and filters
      +--> evidence table
      +--> CSV or future sport-specific exports
```

This seam keeps legacy keys such as `athleteDev` and `rtp` behind a small interface. The current UI should not accumulate conditional logic for each schema generation.

### Approved normalized evidence record

The runtime interface is implemented in `evidence-taxonomy.mjs`. The canonical 13-field `papers.json` schema remains unchanged; `normalizePaper(record, metadata)` maps legacy and future records into:

- identity: ID, citation, DOI, year, source URL
- evidence: abstract, TLDR, methods, findings, limitations
- translation: general practical implications plus optional audience-specific applications
- context: domains, audiences, sports, populations, and study design
- curation: source verification, review status, and taxonomy provenance

Precedence is future record metadata, then the legacy `paper-taxonomy.json` sidecar, then deterministic inference. This keeps `athleteDev` and `rtp` behind the adapter and prevents schema-version conditionals from spreading through the UI.

### Approved controlled vocabularies

- **Domain:** Training & Performance; Sports Medicine & Injury; Rehabilitation & Return to Sport; Recovery & Readiness; Nutrition & Hydration; Brain Health & Psychology; Athlete Wellbeing; Monitoring & Technology
- **Audience:** Performance; Athletic Training; Sports Medicine; Rehabilitation; Nutrition; Research & Analytics; Coaching
- **Sport context:** Mixed / General Sport; American Football; Soccer; Basketball; Baseball / Softball; Rugby; Volleyball; Track & Field; Swimming & Diving; Gymnastics; Tennis; Golf; Ice Hockey; Combat Sports; Endurance Sport; Other Sport
- **Population:** Professional / Elite; Collegiate; Youth / Adolescent; Adult / Recreational; Female Athletes; Male Athletes; Injured Athletes; Healthy Athletes; Mixed / Unspecified
- **Study design:** Systematic Review / Meta-analysis; Randomized Controlled Trial; Cohort Study; Cross-sectional Study; Case-control Study; Consensus / Position Statement; Narrative Review; Case Report / Case Series; Laboratory / Experimental Study; Qualitative Study; Methodological / Validation Study; Internal Evidence Synthesis; Other

The first legacy backfill is deterministic and marked `rules-v1-unreviewed`. It supports discovery but is not presented as expert-reviewed interpretation. Directly curated metadata can replace a sidecar row without changing the UI contract.

The UI applies OR logic within a filter dimension and AND logic across dimensions. Full-text search includes normalized evidence, translations, and taxonomy labels.

## Delivery Phases

### Phase 1 — Public Reframe

- Adopt the approved product name across the live UI, browser metadata, exports, and current documentation
- Replace football-only public labels with Performance Application and Return to Sport Application
- Preserve the current persisted schema and all existing content

**Exit condition:** the shared library no longer presents football as the umbrella identity and the existing app builds and loads the canonical dataset.

### Phase 2 — Trustworthy Baseline

- Generate a reproducible source-to-record manifest
- Resolve or document the two broken source references
- Review the 16 duplicated source groups and remove only verified redundant rows
- Complete the blank return-to-sport value or explicitly mark it not applicable
- Add automated checks for IDs, required fields, duplicate source identity, and link construction

**Exit condition:** processed and remaining counts can be reproduced from the repo, and every published row passes the agreed validation checks.

### Phase 3 — Taxonomy and Discovery

- [x] Approve the normalized evidence interface and controlled vocabularies
- [x] Add the normalization module at the data-loading seam
- [x] Backfill domain, audience, sport/population, and study-design metadata for all 407 existing records
- [x] Add multi-select filters without weakening current full-text search
- [x] Add taxonomy coverage and vocabulary auditing

**Exit condition:** staff can find evidence by professional need or population without knowing football terminology.

### Phase 4 — Balanced Expansion Pilot

- [x] Prepare a 96-paper title-screened queue: 12 unrepresented, content-deduplicated candidates per controlled domain
- [x] Full-text screen and audit Batch 01: 12 INCLUDE, 0 EXCLUDE, 0 DEGRADED
- [x] Publish Batch 01 as stable IDs 434–445
- [x] Full-text screen and audit Batch 02: 12 INCLUDE, 0 EXCLUDE, 0 DEGRADED
- [x] Publish Batch 02 as stable IDs 446–457
- [x] Full-text screen and audit Batch 03: 11 INCLUDE, 1 EXCLUDE, 0 DEGRADED
- [x] Publish Batch 03 as stable IDs 458–468
- [x] Full-text screen and audit Batch 04: 12 INCLUDE, 0 EXCLUDE, 0 DEGRADED
- [x] Publish Batch 04 as stable IDs 469–480
- [x] Full-text screen and audit Batch 05: 11 INCLUDE, 1 EXCLUDE, 0 DEGRADED
- [x] Publish Batch 05 as stable IDs 481–491
- [x] Full-text screen and audit Batch 06: 12 INCLUDE, 0 EXCLUDE, 0 DEGRADED
- [x] Publish Batch 06 as stable IDs 492–503
- [x] Full-text screen and audit Batch 07: 12 INCLUDE, 0 EXCLUDE, 0 DEGRADED
- [x] Publish Batch 07 as stable IDs 504–515
- [x] Full-text screen and audit Batch 08: 12 INCLUDE, 0 EXCLUDE, 0 DEGRADED
- [x] Publish Batch 08 as stable IDs 516–527
- [x] Full-text screen and audit Batch 09: 12 INCLUDE, 0 EXCLUDE, 0 DEGRADED
- [x] Publish Batch 09 as stable IDs 528–539
- [x] Full-text screen and audit Batch 10: 12 INCLUDE, 0 EXCLUDE, 0 DEGRADED
- [x] Publish Batch 10 as stable IDs 540–551
- [x] Full-text screen and audit Batch 11: 12 INCLUDE, 0 EXCLUDE, 0 DEGRADED
- [x] Publish Batch 11 as stable IDs 552–563
- [x] Full-text screen and audit Batch 12: 12 INCLUDE, 0 EXCLUDE, 0 DEGRADED
- [x] Publish Batch 12 as stable IDs 564–575
- Include cross-sport and underrepresented population evidence intentionally; do not rely only on the existing backlog's distribution
- Process in small audited batches with source, extraction, synthesis, and verification gates
- Publish only after duplicate and schema checks pass

The active queue is stored in `docs/pilot-expansion-shortlist.md` and `docs/pilot-expansion-shortlist.json`; durable batch decisions live under `docs/pilot-screening/`, and publication-ready records live under `docs/pilot-synthesis/`. Batches 01–12 verified and published 142 readable, eligible local sources, with two mislabeled sources excluded. Their reviewed primary-domain distribution is 37 Training & Performance, 30 Monitoring & Technology, 24 Sports Medicine & Injury, 17 Recovery & Readiness, 14 Rehabilitation & Return to Sport, 11 Nutrition & Hydration, 6 Athlete Wellbeing, and 3 Brain Health & Psychology.

After Batch 12 publication, the active queue contains 96 unrepresented title-screened candidates with 12 per pilot domain and no previously screened INCLUDE records awaiting synthesis. Primary-domain matches fill each domain first. Athlete Wellbeing currently requires seven explicitly labeled secondary-title matches because only five unrepresented candidates have it as their strongest title signal. Generic physical `stress` wording is excluded from the Wellbeing rule to prevent heat-stress and bone-stress false positives.

**Exit condition:** met. The library contains 540 distinct local source files plus nine internal or external records and now demonstrates reviewed breadth across all eight controlled domains.

### Phase 5 — Backfill and Operating Cadence

- Prioritize the remaining corpus by domain relevance and evidence value rather than alphabetic order or a football filename filter
- Separate the one-time backlog burn-down from the ongoing new-research cadence
- Pilot with representatives from performance, athletic training/sports medicine, rehabilitation, and nutrition
- Add downstream sport- or discipline-specific exports only when a real staff workflow requires them

**Exit condition:** the library has a repeatable intake, verification, publishing, and review cadence with named ownership.

## Pilot Allocation Decision

Use an evenly balanced first pilot—12 candidates in each of the eight domains—to correct the current football and injury/performance concentration and test usefulness across staff groups. After this breadth pilot and staff review, weight the monthly intake cadence toward Baylor's highest-priority Health & Performance questions.

## Next Gate

Full-text screen Batch 13 from the replenished balanced queue, then convert only INCLUDE decisions into the next structured synthesis batch. A candidate enters synthesis only after source identity, eligibility, study-design, domain, sport/population, and duplicate-content checks pass. The next unused stable ID is 576. Run `npm run audit:screening` after recording a batch, `npm run synthesis:apply` to publish reviewed synthesis records, and `npm run pilot:shortlist` to replenish the queue.
