# Scrimmage vs Regular Period Comparison — Design Note

**Status:** prep / not yet built. Likely revisit when fall camp begins (more scrimmages incoming → more data → more value).
**Drafted:** 2026-05-12

## Why

The simulator now preserves `(SCRIM)` parenthetical tags on period names so scrimmage-day load lives in a different bucket from regular-practice load. That preserves the data, but doesn't yet surface the calibration question coaches will ask:

> "How does SPT 1 (SCRIM) typically run vs. our regular SPT 1?"

Fall camp will have substantially more scrimmage days than spring (camp blocks tend to include 3-4 full scrimmages plus shorter scrimmage segments). By August/September the season-level data will be rich enough that side-by-side scrimmage-vs-regular comparison stops being anecdotal and becomes useful for:

- **Tempo calibration** — do our SCRIM SPECIAL TEAMS periods run hotter or colder than the model projects relative to regular SPT?
- **Practice planning** — when designing a high-stakes scrimmage segment, how should we expect player load to differ vs. the same drill in a Tuesday teach?
- **Recovery planning** — scrimmage days are heavier; quantifying *how much* heavier helps decide the next-day plan.

## Data model — what we have

After the May 2026 sync work:

- Regular periods: `SPECIAL TEAMS`, `TEAM`, `1 ON 1` etc. (canonical names from PERIOD_DEFAULTS).
- Scrimmage variants: `SPT 1 (SCRIM)`, `TEAM 1 (SCRIM)` etc. — preserved exactly as Catapult labels them. Auto-create as new DB rows on scrimmage practices.
- Both kinds carry the same fields: `minutes`, `pl_team_projected`, `pl_team_actual`, `pl_per_min_actual`.
- The `practices.tempo` and `practices.emphasis` fields can also signal scrimmage context but aren't used to pair scrim/regular periods today.

What we *don't* yet have:

- A canonical "regular-equivalent" mapping for each scrim period. `SPT 1 (SCRIM)` likely corresponds to `SPECIAL TEAMS` for comparison purposes, but the system doesn't encode that link.
- A flag on practices that says "this was a scrimmage." Inferable today by checking whether any period name contains `(SCRIM)`, but that's a derived signal.

Both are addressable in the implementation without schema changes.

## Comparison shapes — ordered by usefulness

### 1. Per-drill scrim-vs-regular averages (the headline)

For each drill family (SPT, TEAM, etc.), show:

| | Regular avg PL/p | Scrim avg PL/p | Delta | % heavier |
|---|---|---|---|---|
| SPT periods | 27.4 | 33.1 | +5.7 | +20.8% |
| TEAM periods | 41.8 | 52.4 | +10.6 | +25.4% |
| ... | | | | |

Computed across the season. Numerator: average per-period PL/p across all matched periods. Pairing rule: a scrim period named `SPT 1 (SCRIM)` is grouped with regular periods whose canonical is `SPECIAL TEAMS` — using the same prefix logic `findBaselineForUnknown` already employs.

This is the "is the simulator's projection systematically off for scrimmage days?" answer.

### 2. Per-practice contribution to total load

For a scrimmage practice, what fraction of total per-player load came from scrim periods vs. regular periods? A 1-bar stacked horizontal chart per scrimmage practice would convey this. Useful for spotting "we said this was a scrimmage but ran 30 min of teach periods" kinds of patterns.

### 3. Cross-practice trend

Over a fall camp block (e.g., 14 days), plot total per-player load per practice with markers for scrimmage days. Coaches can eyeball whether scrim spikes show up where expected.

## Three open design questions before building

1. **How do we pair scrim periods with their regular counterparts?** Three options:
   - **Prefix match** (recommended for v1): `SPT 1 (SCRIM)` → strip the `(SCRIM)` and trailing digits → look up canonical `SPECIAL TEAMS`. Reuses existing `canonicalize` logic minus the SCRIM preservation. Zero schema cost.
   - **Explicit mapping table**: hand-maintain a `scrim_to_regular` map. More flexible (could pair `LIVE SCRIMMAGE` → `TEAM`) but more upkeep.
   - **User-tagged**: let the user manually pair on first observation. Most accurate, most friction.

2. **Where does this view live?**
   - Inside the existing `/practices/[id]/compare` view? Per-practice context is too narrow — comparison only makes sense across many practices.
   - New top-level route `/calibration/scrim-vs-regular`? Cleaner home for season-level rollups. Probably the right answer.
   - Side-panel on `/admin`? Mixes admin/data-quality with calibration. Wrong place.

3. **What level of statistical rigor?**
   - v1: simple averages, with sample-size disclaimer chips ("n=3"). Good enough for in-season directional decisions.
   - v2: include standard deviation, maybe a t-test or confidence interval. Worth it once n>10 per bucket. Probably defer.

## Build sketch (when we're ready)

1. **Helper**: `pairScrimToRegular(canonical: string): string | null` in `lib/periodMap.ts`. Returns the regular canonical for a scrim-tagged name, or null if no match.
2. **Query**: `getScrimVsRegularStats(season: string)` — server-side, walks all periods, groups by `(pairedCanonical, isScrim)`, returns avg PL/p and count per group.
3. **New page**: `app/calibration/scrim-vs-regular/page.tsx` — server component, renders a table + the per-drill cards.
4. **Reuse**: `formatPracticeDate`, color tiering from existing comparison view, the same `loadCalc` math helpers.
5. **Tests**: pairing logic, average computation, edge cases (no scrim data, no regular data, mismatched units).
6. **Link**: top-level nav adds "Calibration" entry once at least one scrim practice is synced.

Estimated 60-90 min once enough fall-camp data exists to make the view non-empty.

## What this isn't

- Not a forecasting tool. Pure retrospective: "how have these run, historically?"
- Not per-position (yet — same constraint as the projected-vs-actual view; would need a new schema table).
- Not a scrim-detection mechanism — relies on the existing `(SCRIM)` naming convention. If Catapult naming changes or coaches start using a different tag, the pairing logic needs updating in lockstep.
- Not a replacement for in-the-moment coaching judgment about scrimmage intensity. It's a feedback loop on what already happened.

## Trigger to revisit

- **First fall-camp scrimmage with synced data** — gives us our first real scrim/regular comparison point. Probably late July / early August 2026.
- **After ~3 scrimmages of any kind** — sample size becomes meaningful enough to surface as a feature, not a curiosity.

## Adjacent work that should land first

- `(SCRIM)` parenthetical preservation in `canonicalize` (done, May 2026, commit `9cf802f`).
- Practice-face seed cleanup for scrimmage days — currently scrimmage practices have generic `SPECIAL TEAMS` / `TEAM` rows that get left empty because the practice ran SCRIM variants instead. Worth fixing the seed so scrimmage practices have the right period rows pre-loaded, OR leaving the empty rows and using the simulator's per-period remove to clean them up post-sync. Either path makes the data cleaner before this calibration feature reads from it.
