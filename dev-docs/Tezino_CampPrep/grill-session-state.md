# Grill Session State — paused 2026-06-09 evening

> STATUS 2026-06-11: historical snapshot of the 6/9 grilling session, kept as the record
> of how the project shape was decided. Several "not yet grilled" items below were
> resolved on 6/10 (camp report dates, IMTP coverage check, Catapult auth/sync, force
> plate backfill all DONE). Data gaps are now closed EXCEPT Perch set-level ingest.
> For current build order and live status, treat `AGENTS.md` and `docs/NARRATIVE-PLAN.md`
> as authoritative.

Resume by re-reading CONTEXT.md, docs/adr/0001, docs/INJURY-TIMELINE.md, then this file.

## Resolved (in order)
1. **Project shape**: retrospective → live monitor → prescriptive. Retrospective is the
   evidence base, not the deliverable. (CONTEXT.md)
2. **Injury timeline**: pulled from Risk_Stratification_Engine exports. Index injury =
   left 5th MT shaft fracture, 2024-07-10, mechanism Acceleration, during S&C — *inside*
   the study window. 2025-07-10 hip strain, also Acceleration. (docs/INJURY-TIMELINE.md)
3. **Perch access**: API client already exists at `PlayerProfiles_FB_03-28-2026/src/perch_ingest.py`
   (api.perch.fit, /v3/sets, creds in that project's .env). Existing cache is 1RM-only;
   this project needs a set-level ingest variant (reps, weight, velocity, exercise, timestamp).
   API reaches back through 2023 (Tezino 1RM rows span 2023-03-14 → 2026-04-27).
4. **Stress model**: two tiers — systemic (tier 1, soft eyes) + foot-specific mechanical
   (tier 2, hard eyes). Explainability is a hard requirement. (CONTEXT.md)
5. **Monitoring frame**: SPC / XmR charts, limits from healthy 2026 baseline, historical
   pre-injury zones as shaded warning bands, ramp rates (not raw load) for exposure metrics.
   Retrospective validation against both July 10ths; build live tool regardless; report
   validation result honestly on the artifact. (ADR-0001)
6. **PFF**: context layer only (snaps per season). Re-evaluate if a better plan emerges.
7. **Live monitor form** (resolved at pause): single regenerable HTML dashboard, one
   command refreshes all sources + recomputes charts + rewrites the file. Run weekly by
   Eric (Friday, current for Monday conversations). Staff-presentable tone from day one.
   No scheduling/automation until the manual loop proves itself 2-3 weeks.

## Not yet grilled (resume here)
- **Metric panel selection** — which specific Catapult params for tier 2 (accel bands,
  HSR threshold for a 290 lb DL — squad default thresholds may be wrong for him),
  which Perch lifts count as lower-body axial, the >=80% 1RM definition (true 1RM vs
  pct_1rm field)
- **Baseline window choice** — post-surgical spring vs first two weeks of June 2026
  (depends on when summer lifting actually starts and his clearance status)
- **Camp report dates FC24 / FC25 / FC26** — still needed from Eric (anchor dates)
- **Surgery date + current clearance status** — confirm with sports med
- **DEXA role** — scan history still locked in the Access .mdb
- **IMTP** — `imtp_tests` table exists in ForcePlate DB (per PlayerProfiles docs);
  Tezino coverage not yet checked
- **Catapult CLI** — auth/sync not yet verified; athlete lookup returned empty

## Build order once grilling completes
1. Close data gaps: force plate 2025-2026 backfill, set-level Perch ingest, Catapult sync,
   DEXA mdb extraction
2. Retrospective: aligned-timeline exposure reconstruction for summers 2024/2025
   (anchor: days to camp report / days to injury)
3. SPC validation on 2024 + 2025
4. Live dashboard with 2026 data
