# Work Plan — Tezino Summer Ramp: Retrospective, Live Monitor, Prescriptive

> Project shape resolved 2026-06-09 (see `CONTEXT.md` and `docs/adr/0001`). This file is
> the build order. The original framing ("tell the two-ramp narrative") is now absorbed
> into a three-layer model: **retrospective** (reconstruct the total stress that preceded
> the foot injury) feeds **live monitor** (track the 2026 ramp) feeds **prescriptive**
> (SPC guardrails for summer 2026). The retrospective is the evidence base, not the
> deliverable. Exposure is charted as ramp rates under a two-tier stress model (systemic /
> foot-specific mechanical) and anchored on BOTH camp report date and the two July-10
> injuries; response metrics (CMJ, asymmetry, body weight) are charted directly. The
> monitoring frame is SPC / XmR process behavior charts (ADR-0001), using Mark Graban /
> Donald J. Wheeler language to separate routine noise from meaningful process signals.

Goal: give performance staff an explainable account of the stress Tezino accumulated in
his prior summer ramps (what preceded the 2024-07-10 foot fracture and the 2025-07-10 hip
strain), a live SPC monitor for the 2026 ramp, and guardrails so the foot does not become
an in-season problem again.

## The narrative skeleton (each ramp told the same way)

For each year, answer four questions in order:

1. **What did he weigh coming out of spring, and where did summer take him?**
   Body weight trajectory May → camp report date. Slope, variability (weigh-in scatter),
   and the camp-entry number vs the position target.
2. **What was his neuromuscular state through summer?**
   Force plate: mRSI trend, asymmetry trend, tier (gold/purple) movement, prescription history.
   The 2023 → 2024 asymmetry story (-19% → near 0) suggests there is a real arc here.
3. **What did camp do to him?**
   Camp-block body weight response (2025: dropped to 284 mid-camp, finished 298 — that swing
   is a storyline), plus force plate readiness flags during camp, plus Catapult camp load if available.
4. **Did the summer prepare him for the camp he actually got?**
   The synthesis question. Cross-reference camp load shock (Catapult ACWR at camp start)
   against where his summer left him.

Then the comparison layer: 2024 ramp vs 2025 ramp side by side, and the "so what" for 2026
(he is at 292 now, asymmetry resolved as of late 2024, current force plate status unknown).

## Work plan

**Phase 1 — Close the data gaps** (prereq for everything)
- [x] Backfill force plate 2025-2026 — summer 2025 backfill done 2026-06-10; June 2026
      VALD resync done 2026-06-12. Tezino now has current CMJ tests on 2026-06-03 and
      2026-06-08, plus IMTP through 2026-06-10.
- [x] ~~Extract DEXA scan history~~ — dropped: export is demographics-only and the scan
      system is not accessible (confirmed 2026-06-10)
- [x] Catapult: auth/sync/pull done 2026-06-12 → `data/tezino_gps_sessions.csv` (546
      sessions 2022-2026 via `scripts/extract_tezino_gps.py`). **FC24 has ZERO GPS for
      him** (dark 7/11/24 to 9/10/24 — missed the whole camp); FC25 has 18 sessions but
      with a mid-camp absence P4-P9 (8/2-8/9). Summers are well covered (SUM24 26,
      SUM25 31 sessions), and SUM26 is live (8 sessions so far).
- [x] **Perch set-level ingest** — done 2026-06-11. `scripts/extract_tezino_perch.py`
      pulls all 2,946 of Tezino's tracked sets (2022-2026) to `data/tezino_perch_sets.csv`
      (reps, weight_lbs, pct_1rm, tonnage, velocity, exercise, timestamp). `/v3/sets`
      supports a server-side `user_id` filter, so the whole history comes in one stream.
      Validated against both injury windows (see `docs/DATA-INVENTORY.md` section 5).
      Still to do in Phase 3: fold these sets into the day-aligned ramp datasets.

**Phase 2 — Build the per-ramp datasets** (done 2026-06-10)
- [x] `data/ramps/ramp_{2023,2024,2025}.csv` + `ramps_all.csv` — long tidy format
      (ramp, date, day, source, metric, value, detail), day -90 to +25 around camp P1,
      all four modalities (bodyweight, cmj, imtp, gps). Built by
      `scripts/build_ramp_datasets.py` (re-runnable, pure file transform).
- [x] `data/ramps/ramp_kpis.csv` — the Phase 3 summary-table KPIs per ramp
      (camp load KPIs use padded practices only; walk-thrus excluded for
      cross-year comparability since 2023 has no tracked walk-thrus)
- [x] Camp anchor dates resolved from Catapult activity names: FC23 P01 = 8/3/2023,
      FC24 P1 = 8/1/2024, FC25 P1 = 7/30/2025
- Note from the build: he has body-weight entries DURING FC24 (Aug 2024, ~300 lb)
  despite zero GPS — present at the facility, not practicing. Sharpens the
  injury/availability hypothesis for the FC24 hole.
- [x] `ramp_2026.csv` added (2026-06-10): the in-progress ramp, anchored to an
      ESTIMATED FC26 P1 of 7/29/2026 (P1 trended 8/3 → 8/1 → 7/30; update the
      anchor in `build_ramp_datasets.py` when the camp calendar is published).
      Early read at day -49 (same relative point each year, cumulative GPS PL):
      2023: 2229 | 2024: 2003 | 2025: 1294 | **2026: 1022** — the softest summer
      start of the four, and avg PL/session is also lowest (170 vs 216-279).
      Caveats: estimated anchor, group-assignment differences. No 2026 weigh-ins in
      window yet (last 4/20, day -100). Current force plate is now present: latest
      current-ramp CMJ is 2026-06-08 (mRSI 0.5637, purple, green readiness), and IMTP
      extends through 2026-06-10.

**Phase 3 — Retrospective exposure reconstruction** (the evidence base, built 2026-06-11)
Reconstruct total stress per summer ramp across all extracted surfaces, anchored on BOTH
days-to-camp and days-to-injury. Two tiers, both explainable (no composite scores):
- [x] Tier 1 (systemic, soft eyes): weekly tonnage / total reps / reps >=80% 1RM (Perch);
      total player load, total distance, session count (Catapult). Output:
      `data/retrospective/weekly_exposure.csv`, with week-over-week and vs-28-day-average
      ramp-rate fields.
- [x] Tier 2 (foot-specific mechanical, hard eyes): lower-body axial Perch metrics are
      built; available Catapult impact/high-IMA rows are included as explicitly flagged
      `proxy_pending_thresholds` rows until acceleration/HSR thresholds are locked.
- [x] Response panel: CMJ mRSI + asymmetry (tier detail retained), IMTP, body weight,
      charted directly in `data/retrospective/response_panel.csv`.
- [x] Zoom on the injury weeks: `data/retrospective/injury_week_zoom.csv` covers -14..+14
      days around 2024-07-10 and 2025-07-10.
- [x] KPI summary table extended with Perch tier-1/tier-2 KPIs in
      `data/ramps/ramp_kpis.csv`.

**Phase 3b — SPC validation on 2024 + 2025** (built 2026-06-11)
- [x] Rebuild XmR charts on 2024 and 2025 and check whether out-of-control signals
      preceded each July-10 injury. Output: `data/spc_validation/spc_points.csv`,
      `spc_validation_summary.csv`, and `spc_validation_notes.md`, built by
      `scripts/build_spc_validation.py`.
- [x] Report the validation honestly: using 2023 as the retrospective healthy baseline,
      11 series had early-warning signals before the July-10 injuries and 43 series had no
      pre-injury signal. This supports change detection, not a strong injury-prediction
      claim. See `docs/SPC-VALIDATION.md`.
- [x] Extend the signal engine beyond points outside natural process limits to include
      sustained-shift, sustained-trend, and moving-range rules before staff-facing launch.

**Phase 4 — Live monitor** (the deliverable)
- [x] Dashboard data contract: `scripts/build_dashboard_data.py` writes
      `data/dashboard/dashboard_data.json` from the ramp KPIs, retrospective panels, and
      SPC validation outputs. This is the stable input for the dashboard UI.
- [x] Single regenerable HTML dashboard: `scripts/build_dashboard_html.py` writes
      `data/dashboard/index.html` from the JSON contract. The first staff-facing pass
      includes current 2026 KPI cards, the Current Force Plate panel, 2024/2025 warning
      references, SPC validation counts, early-warning series, and chart-ready SVG panels
      for weekly exposure, response, and signal points. Baseline policy is now selected as
      the first four weeks of June 2026, with staff review after three weeks and provisional
      live limits until the four-week window is complete. Historical warning references are
      context, not targets or safe limits.
- [x] Manual operating loop command: `python scripts\refresh_dashboard.py` runs all
      generated sources in dependency order and rewrites
      `data/dashboard/dashboard_data.json` + `data/dashboard/index.html`.
- [x] Pulse Check First redesign: the static dashboard now leads with selected process
      behavior chart panels for average player load per session, high-IMA/high-impact GPS
      exposure, Perch axial load, CMJ, and IMTP.
- [ ] Manual operating loop review: run the refresh each Friday so the dashboard is current
      for Monday, review caveats and current-response values, then decide whether any staff
      interpretation copy needs adjustment. No scheduling/automation until the manual loop
      proves itself 2-3 weeks.

**Phase 5 — Prescriptive guardrails**
- [ ] Translate the retrospective + validated SPC limits into summer-2026 ramp guardrails
      (rate caps, watch thresholds) so the foot does not become an in-season problem.

## Framing — RESOLVED (2026-06-09, sharpened by the injury timeline)

The old "2024 ramp vs 2025 ramp" framing is superseded. The injury timeline makes the
index event the anchor, not the camp: the 2024-07-10 foot fracture happened MID-RAMP
(inside the June/July window), so the 2024 retrospective question is "what stress
accumulated between the start of summer 2024 and July 10," not "what did his camp look
like." FC23 (full healthy camp) is the clean baseline; 2024 (mid-ramp fracture, lost camp)
and 2025 (mid-July hip strain, interrupted camp) are the two injury ramps. Charts anchor
on BOTH days-to-camp and days-to-injury. His worst pre-camp CMJ on record (0.407, white
tier, 7/14/25) sits right at the 2025 injury window, which sharpens the "did the summer
prepare him?" edge.

## Open questions for Eric

Resolved since this list was written:
- ~~Camp report dates~~ resolved (FC24 P1 = 8/1/24, FC25 P1 = 7/30/25, FC26 est. 7/29/26).
- ~~What happened in FC24?~~ resolved: left 5th metatarsal fracture 2024-07-10
  (`docs/INJURY-TIMELINE.md`). The GPS hole 7/11/24-9/10/24 is the post-fracture absence.
- ~~Framing option (1/2/3)?~~ resolved: injury-anchored three-ramp arc (see "Framing" above).
- ~~Asymmetry arc?~~ folded in: CMJ asymmetry is a response metric, charted directly.
- ~~SPC baseline-window choice~~ resolved 2026-06-12: first four weeks of June 2026,
  with a three-week review checkpoint and finalization after week four.

Still open (needed at the noted step, not blocking the Perch ingest):
- The FC25 P4-P9 gap (8/2-8/9, brackets the 284-lb nadir and weak 8/24 IMTP) is consistent
  with the 2025-07-10 hip strain lingering into camp; confirm the read with Eric.
- Position/DL target weight (is ~292 the number, or does staff want more/less?).
- Surgery date + procedure (early 2026) and current clearance status for summer 2026.
- Tier-2 metric-panel specifics: Catapult accel-band and HSR thresholds appropriate for a
  ~290 lb DL (squad defaults may be wrong), which Perch lifts count as lower-body axial,
  and the >=80% 1RM definition (true 1RM vs the pct_1rm field).
