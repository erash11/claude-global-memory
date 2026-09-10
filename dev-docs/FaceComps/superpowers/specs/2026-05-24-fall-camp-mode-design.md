# Fall Camp Mode — Design Spec

**Date:** 2026-05-24
**Status:** Approved (design phase)
**Author:** Eric Rash + Claude

## Goal

Add a **Fall Camp mode** to the existing Practice Load Simulator so coaches can plan the 2026
Fall Camp practice faces against the FC24/FC25 calibration (period library + load and structure
thresholds), with the same full interactivity as the Spring simulator. The Spring experience must
remain functionally and visually unchanged.

Fall Camp differs from Spring in two ways that drive this design:

1. It has a **separate calibration domain** — its own period baselines and load thresholds, derived
   from FC24/FC25 (GREEN <= 405 PL/player, YELLOW 406-459, RED > 459).
2. It tracks a **second, independent zone**: period-count structure (counted periods after stretch;
   GREEN-count <= 11, YELLOW 12-13, RED > 13). Spring has no structure zone.

## Decisions (locked during brainstorming)

- **Interactivity:** Full simulator — drag-reorder, add/remove/swap periods, live recompute of both
  zones, and Catapult GPS sync. Mirrors Spring `/simulator`.
- **Dual zones:** Load zone and structure zone shown as **two separate gauges**, both first-class.
- **Navigation:** A **season switcher** at the top of the simulator (and admin) that swaps the
  dataset and calibration domain within the same page. Not separate routes, not a landing picker.
- **Storage:** Reuse the existing `practices` / `periods` tables, scoped by `season`. No new tables.
- **Seeding scope:** Defensive practice faces only; numbered `P#` practices only (Walk Thru / break
  days are excluded, consistent with the FC24/FC25 calibration).

## Architecture: Approach A — Season-scoped schema + calibration registry

All "how does Spring differ from Fall Camp" logic is isolated into one registry module. Everywhere
else in the app calls `getDomain(season)` and stays domain-agnostic.

### Schema

No schema change. `practices.season` already exists.

- Spring practices keep `season = '2026 Spring'` (existing literal in `scripts/seed.ts`).
- Fall Camp practices get `season = '2026 Fall Camp'`.

Structure-zone math is computed on the fly from a practice's periods, so it needs no new column.

### Calibration registry — `lib/calibration.ts` (new)

```ts
interface PeriodBaseline {
  canonicalName: string
  plTeam: number          // composite team-scale baseline (see unit convention)
  plPerMin: number
  defaultMinutes: number
}

interface ZoneThresholds { greenMax: number; yellowMax: number }

interface CalibrationDomain {
  season: string
  label: string                       // "Fall Camp 2026" / "Spring 2026" — drives the switcher
  periodBaselines: PeriodBaseline[]
  loadThresholds: ZoneThresholds       // PL/player
  structure?: {                        // present only for domains that track structure
    thresholds: ZoneThresholds          // counted-periods-after-stretch
  }
}

function getDomain(season: string): CalibrationDomain
function listDomains(): CalibrationDomain[]   // for the season switcher
```

- **Spring domain** = today's `PERIOD_DEFAULTS` (from `lib/periodMap.ts`) mapped into
  `PeriodBaseline[]`, plus the existing per-player load thresholds; `structure` undefined.
- **Fall Camp domain** = imports from `lib/fallCampLibrary.generated.ts` (see codegen below):
  baselines from the FC period library, `loadThresholds = { greenMax: 405, yellowMax: 459 }`,
  `structure.thresholds = { greenMax: 11, yellowMax: 13 }`.

`getDomain` defaults to the Spring domain for an unknown/missing season so existing call sites that
pass nothing keep working.

### loadCalc changes — `lib/loadCalc.ts`

Existing helpers gain an **optional** domain/baselines argument, defaulting to Spring so current
call sites are unaffected:

- `computeSessionLoad(periods, tempo, domain?)`
- `projectedPlTeam(period, tempo, domain?)`
- `findBaselineForUnknown(canonical, domain?)`

New helper:

- `computeStructure(periods, domain): { countedPeriods: number; classification: Zone } | null`
  — returns `null` when the domain has no `structure`. Uses the already-tested
  `countPeriodsAfterStretch` from `lib/fallCampCalibration.ts` and classifies via
  `classifyByThresholds`.

## Sync pipeline parameterization

`syncPractice(id)` (`lib/syncPractice.ts`) currently hard-codes Spring assumptions. Changes:

- Read the practice's `season`, call `getDomain(season)`, and use that domain's `periodBaselines`
  for auto-create and `findBaselineForUnknown`.
- Match Catapult activities by the domain's activity-name pattern. Add the Fall Camp pattern
  `FC26 - P{N} - MM.DD.YY` alongside Spring's `SP26 - P{N} - MM.DD.YY`. Parsing already exists in
  `lib/fallCampCalibration.ts` (`parseFallCampPracticeActivity`, `parseActivityDate`) — this is
  wiring, not new parsing.
- Validation bounds and idempotency behavior are unchanged (domain-agnostic).
- `/admin` sync panel and `/api/sync/bulk` become season-aware: they list/operate on practices for
  the active season only.

**Timing note:** Fall Camp 2026 has not happened yet (camp is ~August 2026). Until then, sync
returns no matching activities and leaves actuals null; the compare page shows its existing
"Not yet synced" stub. The pipeline is ready for August with no further work.

## UI

### Season switcher

- A small segmented control / dropdown at the top of `/simulator` and `/admin`, populated from
  `listDomains()`.
- Sets a `season` URL search param (`?season=2026%20Fall%20Camp`); default = Spring.
- Server queries gain a `WHERE season = $1` filter:
  `SELECT * FROM practices WHERE season = ${season} ORDER BY practice_num ASC`.
  Spring behaves identically because it selects the Spring season.

### Gauges

- **Spring:** unchanged — single load gauge.
- **Fall Camp:** two gauges side by side —
  1. Load gauge (PL/player vs FC load thresholds), same component as today.
  2. New **Structure gauge** (counted periods after stretch vs structure thresholds), its own
     GREEN/YELLOW/RED.

### Reused as-is

- `PracticeFlowChart`, period list, drag-to-reorder, add/remove/swap — all operate on whatever
  periods the page holds. Swap suggestions pull from the active domain's baselines, so Fall Camp
  suggestions come from the FC library.
- Compare page — projected values come from FC baselines via the domain-aware `projectedPlTeam`.

## Data generation (scripts in `simulator/scripts/`)

### 1. `generate-fall-camp-library.ts` (build-time codegen)

Reads `docs/fall-camp/fall_camp_period_library.csv` and the threshold CSVs; writes
`lib/fallCampLibrary.generated.ts` (baselines + load/structure thresholds the registry imports).
Keeps the calibration snapshot as the single source of truth; re-run on recalibration. No CSV
parsing ships to Vercel.

Note: the FC library CSV reports `avg_pl_player` (per-player scale). The generator converts to the
composite team-scale baseline (`/ RATIO`, RATIO = 0.09772) so Fall Camp baselines live on the same
scale as Spring's `PERIOD_DEFAULTS`, per the project's unit convention.

### 2. `seed-fall-camp.ts`

Reads `SourceFaces/2026 Fall Camp - Practice Faces .xlsx`, extracts the numbered DEF practice faces
only, and inserts into `practices` / `periods` with `season = '2026 Fall Camp'`. Each period's
`pl_team_projected` is computed from FC baselines at seed time. Idempotent via existing
`ON CONFLICT (season, practice_num) DO NOTHING`. Spring rows are never touched (different season).

**Open item resolved during planning:** confirm the FC workbook's sheet/row layout against the
Spring parser (title row, metadata rows, period rows, DEF-sheet naming). The unmatched-periods audit
CSV indicates the structure is parseable; the seed needs the exact column map.

## Testing

- **Unit:** registry returns correct domain per season; `computeStructure` matches known FC24/FC25
  counts; domain-aware `projectedPlTeam` / `findBaselineForUnknown` pick FC baselines for FC periods
  and Spring baselines for Spring. Extend existing `tests/fallCampCalibration.test.ts` patterns.
- **Regression (Spring untouched):** snapshot Spring session load + classifications for a couple of
  practices before/after the season-scoping refactor; assert identical.
- **Build:** `npm test` (currently 8 files / 92 tests) and `npm run build` (Next 16.2.3) must pass
  before commit.
- **Manual:** load `/simulator`, switch to Fall Camp, confirm 18 numbered DEF faces appear with both
  gauges; switch back to Spring and confirm it is visually identical to today.

## Out of scope (this sprint)

- Actual GPS sync results for Fall Camp 2026 (no data until ~August 2026; pipeline is ready).
- Offensive practice faces.
- Walk Thru / break-day practices.
- Any change to Spring math or layout.
