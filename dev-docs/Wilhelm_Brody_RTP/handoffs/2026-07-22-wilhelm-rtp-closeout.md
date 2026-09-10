# Handoff — Wilhelm RTP Clearance Report (closed 2026-07-22)

## What this was

One-page ACL return-to-play clearance report for Brody Wilhelm (TE, ACLR 2025-10-01),
built 7/21–7/22 for Eric's PT colleague's meeting with team physicians. Deliverables:
print PDF + private artifact link (https://claude.ai/code/artifact/7e175547-9175-4421-bdfa-3360775de173),
both rendered from the same HTML.

Final read: **4 of 7 criteria met** — sprint velocity 103%, CMJ symmetry 9.0%,
CMJ mRSI 92%, DynaMo quad LSI 92% met; weekly workload 83% approaching;
IMTP 83% and Bench e1RM 76% not met.

## How it works (resume points)

- `params.yaml` — the reuse seam: athlete ids (Catapult/VALD/Perch), position,
  surgery date, involved limb, strength exercise, thresholds. Next RTP case =
  edit this + rerun.
- `src/pull_data.py` — pulls Catapult (live CLI, athlete_id filter, client-side
  dates), VALD forceplate.db (DuckDB) **plus live ForceDecks top-up** for CMJ
  tests newer than the DB, VALD DynaMo (knee extension per-limb), Perch
  (perch.duckdb). `--skip-catapult` reuses cached GPS from data/report_data.json.
- `src/charts.py` — radar (attainment % of target) + knee/velocity/workload/CMJ
  SVG panels, Baylor DIN Pro fonts, dataviz palette.
- `src/build_report.py` — HTML shell → headless Edge one-page PDF
  (needs `--user-data-dir` scratch profile) + artifact body variant.
- Build: `python src/pull_data.py [--skip-catapult] && python src/charts.py && python src/build_report.py`

## Decisions with reasoning (would be lost otherwise)

- **Bench Press replaced Power Clean**: Perch Power Clean values were flat 275
  for months = carried-forward template values, not real lifts (Eric confirmed
  he hadn't resumed cleans). Bench = honest 76% NOT MET.
- **IMTP LSI not computable** — VALD IMTP export has no L/R split; limb symmetry
  is carried by CMJ Eccentric Braking Impulse Asymmetry + DynaMo knee-ext LSI.
- **Right limb assumed involved** (consistently weaker through rehab); flip
  `athlete.involved_limb` in params.yaml if wrong.
- **7/21 quad LSI jump (63%→92%) is partly the LEFT limb testing lower**
  (1045→796 N), not only right-side gain — charted per-limb deliberately.
- **CMJ asymmetry flipped sign and drifted to +9.0%** (was −3.7%) across the
  three topped-up June tests — inside the ±10% green zone but worth watching.
- Radar = snapshot only; trends kept for trajectory (radar can't show it).

## API gotchas (also in Tier A memory `project-wilhelm-rtp-report.md`)

- Catapult v6 /stats: filter by athlete_id only (athlete_name hangs; date
  filters silently ignored → client-side). Session max_vel is mph; profile
  velocity_max is m/s — never mix.
- DynaMo: `prd-use-api-extdynamo.valdperformance.com` (`ext` host; non-ext 401s),
  same Auth0 token as ForceDecks (ForcePlate_DecisionSystem/.env creds),
  `GET /v2022q2/teams/{teamId}/tests?athleteId=…&includeRepSummaries=true`;
  wide date ranges (>~13 mo) silently return 0.
- ForceDecks: trial RSI-modified is ×100 vs DB scale; asymmetry = metric
  "Eccentric Braking Impulse" with limb="Asym"; tests paged by
  `ModifiedFromUtc` → last `modifiedDateUtc` until HTTP 204.

## Files (all in DEV\SpecialRequests\Wilhelm_Brody_RTP, merged to main)

- out/Wilhelm_Brody_RTP_2026-07-21.pdf, out/report.html, out/report_artifact.html,
  data/report_data.json (copied from worktree; out/ and data/ are gitignored)
- src/pull_data.py, src/charts.py, src/build_report.py, params.yaml
- docs/superpowers/specs/2026-07-21-rtp-clearance-report-design.md (amended)
- docs/superpowers/plans/2026-07-21-rtp-clearance-report.md

## Open / next

1. memsearch indexing ETIMEDOUT regression (7/17→7/22) — run /claude-stack-doctor.
2. Repo is local-only (no remote). Push if a GitHub home is wanted.
3. If the physicians ask for a follow-up: re-test IMTP + Bench are the two
   blockers; Perch data ends 4/17 — re-ingest before any strength update.
