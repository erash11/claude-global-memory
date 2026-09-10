# Projected vs Actual GPS Comparison — Design Note

**Status:** prep / not yet built
**Drafted:** 2026-05-08

## Why

The simulator today uses GPS actuals silently — once a practice is synced, every period quietly switches from baseline projection to `pl_per_min_actual`, and the displayed PL/Player number becomes "what actually happened." This is correct for planning future practices but wastes information for past ones: coaches never see the gap between *what they projected* and *what GPS measured*.

Surfacing that gap is the highest-leverage UX win for the season:
- Builds intuition. Coaches learn which drills routinely run heavier or lighter than the model.
- Validates the planning tool. "Did our projection hold?" is the question that decides whether the simulator is trusted.
- Supports the head-coach conversation. The April meeting prep doc compared projected vs actual manually; this view automates that loop.

## Data already available

No schema changes needed. Every `Period` row has both:

- `pl_team_projected` — static baseline by period type (from `PERIOD_DEFAULTS`)
- `pl_team_actual` — populated by `/api/sync` after a Catapult pull
- `pl_per_min_actual` — also populated by sync

`practice.synced_at` indicates whether sync has run. The comparison view is only meaningful when `synced_at != null`.

## Three layers of comparison, ordered by coach value

### 1. Per-period (the strategic core)

For each period, show two numbers:
- **Projected**: `computePeriodPlTeam(plPerMinFromBaseline, period.minutes, tempo)` — what the model said
- **Actual**: `pl_team_actual` — what GPS measured

Plus delta and percent error. This is where intuition is built — coaches see "1 ON 1 ran 30% heavier than projected on March 24" and start adjusting their internal model.

UI: extra cells in `PeriodItem`, only rendered when `synced_at` is set. Can be a toggle ("Show vs actual") or always-on for synced practices.

### 2. Session-level accuracy

For the practice as a whole:
- Projected total PL/Player vs actual total PL/Player
- Mean absolute error across periods
- Single "model accuracy: X%" summary, e.g. "within 4% on this practice"

UI: a small panel under the LoadGauge when synced, or an inline note on the gauge itself.

### 3. Cross-practice trend (longer-term value)

Once 5+ practices are synced, plot projection vs actual over time. Coaches see "we underestimate THUD days by ~6%" — a season-level calibration insight.

UI: a `/calibration` page or a panel on `/admin`. Probably defer to v2.

## Key design decisions to settle before building

1. **Toggle or always-on?** When viewing a synced practice, do we show the comparison by default or behind a "Compare to GPS" button? Toggle keeps the planning view clean for future practices being adjusted on a synced template; always-on makes the calibration value harder to miss.

2. **What's "projected"?** Two reasonable definitions:
   - **Baseline projection**: use static `PERIOD_DEFAULTS` rates with the period's actual minutes and tempo. This is what the model would say *without* any GPS data.
   - **Pre-sync simulation snapshot**: what the simulator would have shown right before sync ran. We don't currently capture this, so it would require adding a `projected_at_sync` snapshot column or computing it on the fly from baselines anyway.

   Recommend baseline — same outcome, no schema change.

3. **Where does it live?** Three options:
   - Inline on the simulator page (existing route, conditional rendering)
   - New route: `/practices/[id]/compare` (cleaner separation, dedicated layout)
   - Side panel slide-out (compromise — simulator stays, comparison opens on demand)

   Recommend new route. The simulator page is for editing; comparison is for reviewing. Mixing them complicates state.

4. **Per-position breakdown?** Catapult exports per-position stats, but the current schema only stores period-level. If coaches want "STAR ran heavier than projected on this drill," that needs a `period_position_stats` table. Significant lift; defer.

## Build sequence (when we're ready)

1. **Add `projectedPlTeam(period, tempo)` helper to `loadCalc.ts`** that ignores `pl_per_min_actual`. Plus tests.
2. **New route `/practices/[id]/compare`** with a server component that fetches the practice + periods.
3. **`<PeriodComparisonRow>` component** — projected | actual | delta | % per period.
4. **`<SessionAccuracyPanel>`** — total projected vs actual, MAE, accuracy %.
5. **Link from `/simulator` to `/practices/[id]/compare`** when `synced_at != null`. Probably a small "View GPS comparison →" button under the gauge.
6. **Tests**: comparison math (projection deltas, accuracy %), edge cases (unsynced periods within a synced practice).
7. **Update CLAUDE.md** with the new route and the `projectedPlTeam` helper.

Estimated 60-90 minutes if scope holds. Most risk is in design decision #1 (toggle vs always-on) — wrong choice forces a rebuild.

## What to do *before* building

- Pick toggle vs always-on (probably always-on for the dedicated route; the question goes away if we're not embedding in `/simulator`).
- Pick baseline-projection vs snapshot (probably baseline).
- Decide whether v1 includes session-level accuracy or just per-period.

## What this is *not*

- Not a forecasting tool — it's purely retrospective.
- Not per-position. Period-level only in v1.
- Not cross-season. P1-P15 within a single season.
- Not a replacement for the Excel calibration sheet. That's still useful for offline analysis.
