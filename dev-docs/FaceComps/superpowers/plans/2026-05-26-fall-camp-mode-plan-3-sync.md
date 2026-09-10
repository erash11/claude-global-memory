# Fall Camp Mode — Plan 3: Sync Parameterization

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Catapult sync pipeline season-aware so syncing a `'2026 Fall Camp'` practice uses Fall Camp baselines, the Fall Camp activity-name prefix (`FC26`), and an idempotency wipe that does not destroy Fall Camp seed rows — while keeping Spring sync byte-identical.

**Architecture:** All season-awareness localizes to `syncPractice()`. It already loads the practice row (which carries `season`), so it derives `const domain = getDomain(practice.season)` once and threads `domain.baselines`, `domain.activityPrefix`, and a `knownNames` set through the three Spring-hardcoded spots: (1) Catapult activity selection, (2) the idempotency wipe's "which rows are auto-created" decision, (3) canonicalization + `findBaselineForUnknown` at auto-create time. **Because the season is read from the DB row, `/api/sync`, `/api/sync/bulk`, and `/admin` need no changes** — they pass practice IDs and `syncPractice` does the rest. The two non-pure decisions (activity selection, auto-created-row classification) are extracted into exported pure functions so they can be unit-tested without the network or DB (the same pattern `computeChronologicalOrder` already follows).

**Tech Stack:** TypeScript, Next.js 16 route handlers, `@neondatabase/serverless`, Vitest. No DB schema change.

**Decisions baked in (from this session):**
- **Idempotency wipe = code-only heuristic (no schema migration).** A row is "auto-created" iff its `name` is NOT in the practice domain's baselines AND `pl_team_projected > 0`. This spares Fall Camp's zero-load transition/break rows (projected `0`) and Fall Camp library rows (in baselines), while staying byte-identical for Spring (Spring auto-created rows are exactly the names not in `PERIOD_DEFAULTS`, all with `pl_team_projected > 0`). Chosen over an explicit `auto_created` column because Fall Camp 2026 GPS won't exist until ~August 2026, Spring works today, and a prod schema migration is unjustified blast radius for the gain. Known latent limitation (pre-existing in Spring, unchanged here): an auto-created row whose canonical name happens to match a baseline name won't be re-wiped on the next sync. Acceptable.
- **Activity selection narrows by `domain.activityPrefix` with a Spring-safe fallback.** Prefer activities whose name contains the season prefix (`SP26` / `FC26`); if none match the prefix, fall back to the date+`P#` set. Since Spring and Fall Camp run on disjoint calendar dates and `parseActivityDate` already pins the exact date, the prefix is disambiguation insurance, and the fallback guarantees Spring never regresses if a Spring activity is named without `SP26`.
- **Canonicalization is parameterized by `knownNames` now; Fall Camp aliases are deferred (YAGNI).** Passing the Fall Camp baseline keys as `knownNames` already handles direct hits and trailing-digit stripping against the FC library (`PODS 1`→`PODS`, `TEAM 1`→`TEAM`). Genuinely different FC short-forms (if any) can't be known until real FC Catapult names arrive in August; `canonicalize` accepts an optional `aliases` arg as the seam for that, defaulting to the Spring alias map.

---

### Task 1: Add `activityPrefix` to the calibration domain

**Files:**
- Modify: `simulator/lib/calibration.ts`
- Test: `simulator/tests/calibration.test.ts`

- [ ] **Step 1: Write the failing test.** Append to the existing `describe('calibration registry', ...)` block in `simulator/tests/calibration.test.ts`:

```ts
  it('carries the Catapult activity-name prefix per season', () => {
    expect(getDomain('2026 Spring').activityPrefix).toBe('SP26')
    expect(getDomain('2026 Fall Camp').activityPrefix).toBe('FC26')
  })
```

- [ ] **Step 2: Run it to verify it fails.**

Run: `cd simulator && npx vitest run tests/calibration.test.ts`
Expected: FAIL — `activityPrefix` is `undefined` on both domains.

- [ ] **Step 3: Add the field to the interface and both domains.** In `simulator/lib/calibration.ts`, add `activityPrefix` to the `CalibrationDomain` interface (after `season`):

```ts
export interface CalibrationDomain {
  season: string
  label: string
  // Prefix Catapult uses in activity names for this season, e.g. "SP26 - P3 - 03.20.26".
  // Used by syncPractice to disambiguate which activity belongs to a practice.
  activityPrefix: string
  baselines: Record<string, PeriodBaseline>
  loadThresholds: ZoneThresholds
  structureThresholds?: ZoneThresholds
}
```

Then set it on each domain object:

```ts
export const SPRING_2026: CalibrationDomain = {
  season: '2026 Spring',
  label: 'Spring 2026',
  activityPrefix: 'SP26',
  baselines: PERIOD_DEFAULTS,
  loadThresholds: { greenMax: THRESH_GREEN, yellowMax: THRESH_YELLOW },
}

export const FALL_CAMP_2026: CalibrationDomain = {
  season: '2026 Fall Camp',
  label: 'Fall Camp 2026',
  activityPrefix: 'FC26',
  baselines: FALL_CAMP_BASELINES,
  loadThresholds: FALL_CAMP_LOAD_THRESHOLDS,
  structureThresholds: FALL_CAMP_STRUCTURE_THRESHOLDS,
}
```

Note: `simulator/tests/calibration.test.ts` also constructs inline `CalibrationDomain` literals (`fcLike`, `springLike` in the `computeStructure` block). Add `activityPrefix: 'TEST'` to each so they satisfy the now-required field.

- [ ] **Step 4: Run the test to verify it passes.**

Run: `cd simulator && npx vitest run tests/calibration.test.ts`
Expected: PASS (all assertions, including the two inline-domain blocks).

- [ ] **Step 5: Commit.**

```bash
git add simulator/lib/calibration.ts simulator/tests/calibration.test.ts
git commit -m "feat(fall-camp): add activityPrefix to calibration domain"
```

---

### Task 2: Parameterize `canonicalize` by `knownNames`

`canonicalize` currently closes over a module-level `KNOWN_PERIOD_NAMES = new Set(Object.keys(PERIOD_DEFAULTS))` (Spring). Make the known-name set and alias map optional parameters defaulting to Spring, so Fall Camp can pass its own library names. Existing single-argument callers and tests stay green.

**Files:**
- Modify: `simulator/lib/periodMap.ts`
- Test: `simulator/tests/periodMap.test.ts`

- [ ] **Step 1: Write the failing test.** Append a new `describe` block to `simulator/tests/periodMap.test.ts`:

```ts
describe('canonicalize with a custom known-name set (Fall Camp)', () => {
  // Fall Camp library names are uppercase, like Spring's.
  const FC_KNOWN = new Set(['TEAM', 'RUN THRU', '9 ON 7 + 1 ON 1', 'PODS', 'PERIMETER RUN + PAP'])

  it('passes an FC library name through unchanged', () => {
    expect(canonicalize('9 ON 7 + 1 ON 1', FC_KNOWN)).toBe('9 ON 7 + 1 ON 1')
  })

  it('strips a trailing sub-period digit against the FC set: "PODS 1" -> "PODS"', () => {
    expect(canonicalize('PODS 1', FC_KNOWN)).toBe('PODS')
  })

  it('does NOT resolve a Spring-only name when given the FC set: "1 ON 1" is unknown -> passes through', () => {
    // "1 ON 1" is in Spring PERIOD_DEFAULTS but not in FC_KNOWN; with the FC set
    // it is not a known name, and trailing-digit stripping yields "1 ON" (also
    // unknown), so it passes through uppercased rather than resolving.
    expect(canonicalize('1 ON 1', FC_KNOWN)).toBe('1 ON 1')
  })

  it('still defaults to the Spring set when no set is passed', () => {
    expect(canonicalize('TEAM 1')).toBe('TEAM')
    expect(canonicalize('INDY 1')).toBe('INDIVIDUAL')
  })
})
```

(The third assertion's expected value is `'1 ON 1'` because the input already equals its own uppercased trim; `stripTrailingDigits('1 ON 1')` returns `'1 ON'`, which is not in `FC_KNOWN`, so the function returns the original `upper`.)

- [ ] **Step 2: Run it to verify it fails.**

Run: `cd simulator && npx vitest run tests/periodMap.test.ts`
Expected: FAIL — `canonicalize` does not accept a second argument; the FC-set assertions resolve against Spring instead.

- [ ] **Step 3: Parameterize the function.** In `simulator/lib/periodMap.ts`, rename the module-level set to a Spring default and thread the params through:

```ts
const SPRING_KNOWN_NAMES = new Set(Object.keys(PERIOD_DEFAULTS))

export function canonicalize(
  rawName: string,
  knownNames: Set<string> = SPRING_KNOWN_NAMES,
  aliases: Record<string, string> = ALIASES,
): string {
  const upper = rawName.trim().toUpperCase()

  // 1) Already a recognized canonical name.
  if (knownNames.has(upper)) return upper

  // 2) Direct alias match.
  if (aliases[upper]) return aliases[upper]

  // 3) Strip a trailing " <digits>" suffix and retry.
  const stripped = stripTrailingDigits(upper)
  if (stripped && stripped !== upper) {
    if (knownNames.has(stripped)) return stripped
    if (aliases[stripped]) return aliases[stripped]
    // 3b) Two-level strip (defensive).
    const stripped2 = stripTrailingDigits(stripped)
    if (stripped2 && stripped2 !== stripped) {
      if (knownNames.has(stripped2)) return stripped2
      if (aliases[stripped2]) return aliases[stripped2]
    }
  }

  return upper
}
```

Delete the old `const KNOWN_PERIOD_NAMES = new Set(Object.keys(PERIOD_DEFAULTS))` line (replaced by `SPRING_KNOWN_NAMES`). Keep the `ALIASES` map and `stripTrailingDigits` as-is.

- [ ] **Step 4: Run periodMap tests to verify they pass (old + new).**

Run: `cd simulator && npx vitest run tests/periodMap.test.ts`
Expected: PASS — all original `canonicalize`/`parseActivityDate` tests plus the four new FC-set tests.

- [ ] **Step 5: Commit.**

```bash
git add simulator/lib/periodMap.ts simulator/tests/periodMap.test.ts
git commit -m "feat(fall-camp): parameterize canonicalize by known-name set"
```

---

### Task 3: Extract + test the two season-aware sync helpers

Two decisions inside `syncPractice` are currently Spring-hardcoded and untestable because they're inline in a network/DB function. Extract them as exported pure functions (mirroring `computeChronologicalOrder`).

**Files:**
- Modify: `simulator/lib/syncPractice.ts` (add the two exported helpers; body wiring is Task 4)
- Test: `simulator/tests/syncPractice.helpers.test.ts` (new)

- [ ] **Step 1: Write the failing test file.** Create `simulator/tests/syncPractice.helpers.test.ts`:

```ts
import { describe, it, expect } from 'vitest'
import { selectAutoCreatedIds, selectPracticeActivities } from '@/lib/syncPractice'

describe('selectAutoCreatedIds', () => {
  // Spring: known = PERIOD_DEFAULTS-style names; auto-created rows are names not
  // in that set, all with pl_team_projected > 0. Behavior must be unchanged.
  const springKnown = new Set(['TEAM', '1 ON 1', 'INDIVIDUAL'])

  it('flags a Spring auto-created row (unknown name, projected > 0)', () => {
    const rows = [
      { id: 1, name: 'TEAM', pl_team_projected: 432 },
      { id: 2, name: 'TEAM PASS', pl_team_projected: 432 }, // auto-created
    ]
    expect(selectAutoCreatedIds(rows, springKnown)).toEqual([2])
  })

  // Fall Camp: known = FC library names. Seed includes zero-load transition rows
  // (projected 0, name not in baselines) that MUST survive the wipe.
  const fcKnown = new Set(['TEAM', '9 ON 7 + 1 ON 1', 'PODS'])

  it('spares Fall Camp zero-load transition rows (name not in baselines but projected 0)', () => {
    const rows = [
      { id: 10, name: 'TEAM', pl_team_projected: 432 },           // FC library -> survive (known)
      { id: 11, name: 'TRANSISTION', pl_team_projected: 0 },      // transition -> survive (projected 0)
      { id: 12, name: 'BREAK', pl_team_projected: 0 },            // break -> survive (projected 0)
      { id: 13, name: 'MYSTERY DRILL', pl_team_projected: 300 },  // truly auto-created -> wipe
    ]
    expect(selectAutoCreatedIds(rows, fcKnown)).toEqual([13])
  })

  it('treats null pl_team_projected as 0 (survives)', () => {
    const rows = [{ id: 20, name: 'WALKTHRU', pl_team_projected: null }]
    expect(selectAutoCreatedIds(rows, new Set<string>())).toEqual([])
  })
})

describe('selectPracticeActivities', () => {
  const acts = (names: string[]) => names.map((name, i) => ({ id: i + 1, name }))

  it('narrows to the season prefix when prefixed activities exist', () => {
    const activities = acts([
      'SP26 - P3 - 03.20.26',
      'FC26 - P3 - 03.20.26', // same date, different season (hypothetical)
      'Walk Thru - 03.20.26',
    ])
    const { practiceActivities } = selectPracticeActivities(activities, '2026-03-20', 'FC26')
    expect(practiceActivities.map(a => a.name)).toEqual(['FC26 - P3 - 03.20.26'])
  })

  it('falls back to the date+P# set when no activity matches the prefix (Spring-safe)', () => {
    const activities = acts(['P3 - 03.20.26', 'Walk Thru - 03.20.26'])
    const { practiceActivities } = selectPracticeActivities(activities, '2026-03-20', 'SP26')
    expect(practiceActivities.map(a => a.name)).toEqual(['P3 - 03.20.26'])
  })

  it('excludes Walk Thru and activities whose encoded date does not match', () => {
    const activities = acts([
      'SP26 - P3 - 03.20.26',
      'SP26 - P4 - 03.21.26', // different date
      'SP26 - Walk Thru - 03.20.26',
    ])
    const { dateMatched, practiceActivities } = selectPracticeActivities(activities, '2026-03-20', 'SP26')
    expect(dateMatched.map(a => a.name)).toEqual(['SP26 - P3 - 03.20.26', 'SP26 - Walk Thru - 03.20.26'])
    expect(practiceActivities.map(a => a.name)).toEqual(['SP26 - P3 - 03.20.26'])
  })
})
```

- [ ] **Step 2: Run it to verify it fails.**

Run: `cd simulator && npx vitest run tests/syncPractice.helpers.test.ts`
Expected: FAIL — `selectAutoCreatedIds` and `selectPracticeActivities` are not exported.

- [ ] **Step 3: Add the two exported helpers to `simulator/lib/syncPractice.ts`.** Place them near `computeChronologicalOrder` (above `syncPractice`). They reference `parseActivityDate`, already imported from `./periodMap`.

```ts
// Pure: classify which period rows were auto-created by a previous sync (vs.
// seeded from the practice face). A row is auto-created iff its name is NOT in
// the season's baseline set AND it carries a positive projected load. Seed rows
// either have a known baseline name (load drills) or pl_team_projected = 0
// (Fall Camp transitions/breaks), so both survive the idempotency wipe. Spring
// behavior is unchanged: every Spring auto-created row has an unknown name and
// projected > 0; every Spring seed row has a known name.
export function selectAutoCreatedIds(
  rows: Array<{ id: number; name: string; pl_team_projected: number | null }>,
  knownNames: Set<string>,
): number[] {
  return rows
    .filter((r) => !knownNames.has(r.name) && (r.pl_team_projected ?? 0) > 0)
    .map((r) => r.id)
}

// Pure: from a Catapult activity list, select the activities that belong to the
// practice on `dateStr`. The Catapult API date filter is unreliable, so we match
// on the date encoded in the activity name, require a "P<n>" period token, and
// exclude Walk Thru. We then prefer activities carrying the season prefix
// (SP26 / FC26) to disambiguate cross-season collisions; if none carry it we
// fall back to the date+P# set so Spring never regresses on naming drift.
export function selectPracticeActivities(
  activities: Array<{ id: number; name: string }>,
  dateStr: string,
  activityPrefix: string,
): {
  dateMatched: Array<{ id: number; name: string }>
  practiceActivities: Array<{ id: number; name: string }>
} {
  const dateMatched = activities.filter((a) => parseActivityDate(a.name) === dateStr)
  const practiceish = dateMatched.filter(
    (a) => /\bP\d+\b/.test(a.name) && !a.name.includes('Walk Thru'),
  )
  const prefixed = practiceish.filter((a) => a.name.includes(activityPrefix))
  return {
    dateMatched,
    practiceActivities: prefixed.length > 0 ? prefixed : practiceish,
  }
}
```

- [ ] **Step 4: Run the helper tests to verify they pass.**

Run: `cd simulator && npx vitest run tests/syncPractice.helpers.test.ts`
Expected: PASS — all `selectAutoCreatedIds` and `selectPracticeActivities` cases.

- [ ] **Step 5: Commit.**

```bash
git add simulator/lib/syncPractice.ts simulator/tests/syncPractice.helpers.test.ts
git commit -m "feat(fall-camp): extract season-aware sync helpers with tests"
```

---

### Task 4: Wire the domain into `syncPractice`

Now thread the season through the live function: derive `domain`, build `knownNames`, and replace the three Spring-hardcoded spots with calls into Task 1-3 work.

**Files:**
- Modify: `simulator/lib/syncPractice.ts`

- [ ] **Step 1: Update imports.** At the top of `simulator/lib/syncPractice.ts`:
  - Add `getDomain` from calibration.
  - Drop `PERIOD_DEFAULTS` from the `./loadCalc` import (it was only used for the now-removed module-level `KNOWN_PERIOD_NAMES`). Keep `RATIO`, `findBaselineForUnknown`, `aggregatePeriodStats`.

```ts
import { getDb } from './db'
import { CatapultClient, CatapultAPIError, type CatapultPeriodStat } from './catapult'
import { canonicalize, parseActivityDate } from './periodMap'
import { normalizePeriod, normalizePractice } from './normalize'
import { RATIO, findBaselineForUnknown, aggregatePeriodStats } from './loadCalc'
import { getDomain } from './calibration'
```

- [ ] **Step 2: Delete the module-level `KNOWN_PERIOD_NAMES`.** Remove this line (it now lives per-call as `knownNames`):

```ts
const KNOWN_PERIOD_NAMES = new Set(Object.keys(PERIOD_DEFAULTS))
```

- [ ] **Step 3: Derive `domain` and `knownNames` right after the practice is normalized.** After the `const practice = normalizePractice(practiceRows[0])` / `practiceLabel` lines (currently ~line 109-110), insert:

```ts
  const domain = getDomain(practice.season)
  const knownNames = new Set(Object.keys(domain.baselines).map((k) => k.toUpperCase()))
```

(Seed names and FC library keys are already uppercase; `.map(toUpperCase)` is defensive so the `knownNames.has(...)` checks below can't miss on a casing slip.)

- [ ] **Step 4: Replace the activity-selection block** with a call to `selectPracticeActivities`. Replace the current lines (the `dateMatchedActivities` / `practiceActivities` filters through the `if (practiceActivities.length === 0)` error, currently ~127-141):

```ts
  const { dateMatched: dateMatchedActivities, practiceActivities } =
    selectPracticeActivities(activities, dateStr, domain.activityPrefix)
  if (practiceActivities.length === 0) {
    throw new SyncError(
      404,
      `No Catapult activity whose name encodes ${dateStr} (${domain.activityPrefix}) was returned. Catapult returned ${activities.length} activities total.`,
      {
        activities_found: activities.map(a => a.name),
        date_matched_activities: dateMatchedActivities.map(a => a.name),
      },
    )
  }
  const activity = practiceActivities[0]
```

- [ ] **Step 5: Make the idempotency wipe season-aware.** The `beforeWipe` query currently selects only `id, name`; it needs `pl_team_projected` for the heuristic. Replace the `beforeWipe` block (currently ~155-162):

```ts
  const beforeWipe = JSON.parse(JSON.stringify(
    await sql`SELECT id, name, pl_team_projected FROM periods WHERE practice_id = ${id}`
  )) as Array<{ id: number; name: string; pl_team_projected: number | null }>

  const autoCreatedIds = selectAutoCreatedIds(beforeWipe, knownNames)
  if (autoCreatedIds.length > 0) {
    await sql`DELETE FROM periods WHERE id = ANY(${autoCreatedIds})`
  }
```

(The `UPDATE periods SET pl_team_actual = NULL, pl_per_min_actual = NULL ...` clearing step that follows is unchanged.)

- [ ] **Step 6: Thread the domain into canonicalize + auto-create baseline.** Two edits in the grouping/matching section:
  - The grouping loop (currently ~177-182) — pass `knownNames`:

```ts
  const grouped = new Map<string, CatapultPeriodStat[]>()
  for (const stat of periodStats) {
    const canonical = canonicalize(stat.period_name, knownNames)
    const list = grouped.get(canonical) ?? []
    list.push(stat)
    grouped.set(canonical, list)
  }
```

  - The auto-create baseline lookup (currently ~234) — pass `domain.baselines`:

```ts
      const baseline = findBaselineForUnknown(canonical, domain.baselines)
```

- [ ] **Step 7: Run the full test suite + build.**

Run: `cd simulator && npm test`
Expected: all files pass — the pre-existing 110 tests plus the new calibration / periodMap / syncPractice.helpers assertions (≈118 total).

Run: `cd simulator && npm run build`
Expected: build succeeds on Next 16.2.3.

- [ ] **Step 8: Commit.**

```bash
git add simulator/lib/syncPractice.ts
git commit -m "feat(fall-camp): make syncPractice season-aware via calibration domain"
```

---

### Task 5: Confirm routes are untouched + update handoff docs

No code change to the API routes or admin page — confirm and document why, then mark Plan 3 complete in the handoff docs.

**Files:**
- Modify: `simulator/AGENTS.md`
- Modify: `CLAUDE.md` and `AGENTS.md` at the **repo root** (a pre-commit hook enforces that these two are byte-identical mirrors — edit one, copy into the other before committing)

- [ ] **Step 1: Verify the routes need no change.** Read `simulator/app/api/sync/route.ts` and `simulator/app/api/sync/bulk/route.ts`. Confirm both pass only `practice_id`(s) to `syncPractice`, and that `bulk`'s `all` / `only_unsynced` branches select IDs across all seasons (`SELECT id FROM practices ...` with no season filter). This is now correct: each practice resolves its own domain inside `syncPractice`, so a bulk "sync all" correctly syncs Spring practices with Spring calibration and Fall Camp practices with Fall Camp calibration. No edit required. (Record this confirmation in the commit message.)

- [ ] **Step 2: Update `simulator/AGENTS.md`.** In the "Remaining work" section, move Plan 3 from pending to done. Replace the `**Plan 3 — sync parameterization (NOT done).** ...` bullet with:

```markdown
- **Plan 3 — sync parameterization (DONE 2026-05-26).** `syncPractice` derives
  `getDomain(practice.season)` and threads it through: activity selection narrows by
  `domain.activityPrefix` (`SP26`/`FC26`) with a Spring-safe fallback; canonicalization uses
  the domain's baseline keys as `knownNames`; auto-create uses `findBaselineForUnknown(name, domain.baselines)`;
  the idempotency wipe classifies auto-created rows via `selectAutoCreatedIds` (name not in baselines
  AND `pl_team_projected > 0`), which spares Fall Camp's zero-load transition rows. `/api/sync`,
  `/api/sync/bulk`, and `/admin` are unchanged — season is read from the DB row. Cannot E2E against
  live Fall Camp GPS until ~August 2026; the season-routing logic is covered by unit tests
  (`tests/syncPractice.helpers.test.ts`, `tests/periodMap.test.ts`, `tests/calibration.test.ts`).
  When real FC Catapult period names arrive, add FC short-form aliases via `canonicalize`'s
  optional `aliases` arg (the seam is in place; YAGNI until then).
```

- [ ] **Step 3: Update the root `CLAUDE.md` Fall Camp section.** In the "### Fall Camp 2026 mode — BUILT & DEPLOYED" block, change the "Remaining — Plan 3 (sync), NOT done" bullet to reflect completion:

```markdown
- **Plan 3 (sync) — DONE 2026-05-26:** `syncPractice` is season-aware via `getDomain(practice.season)`
  (activity prefix `SP26`/`FC26` with fallback, domain baselines for canonicalize + auto-create,
  season-safe idempotency wipe). Sync routes + admin unchanged (season comes from the DB row).
  Not E2E-tested against live FC GPS (none until ~August 2026); covered by unit tests.
```

- [ ] **Step 4: Mirror root docs + commit.** The pre-commit hook requires root `CLAUDE.md` ≡ root `AGENTS.md`. Copy the edited root file over its mirror so they match exactly:

```bash
cp CLAUDE.md AGENTS.md   # or the reverse, whichever you edited — ensure they are byte-identical
git add simulator/AGENTS.md CLAUDE.md AGENTS.md
git commit -m "docs(fall-camp): mark Plan 3 sync parameterization complete"
```

(If the hook still blocks on a mirror mismatch, diff the two root files, reconcile, re-stage, and commit again — do not use `--no-verify`.)

---

## Self-Review

**Spec coverage** (handoff "Plan 3 — sync parameterization" + AGENTS.md "Remaining work"):
- `syncPractice` season-aware via `getDomain(practice.season)` → Task 4 Step 3. ✓
- Fall Camp activity pattern `FC26 - P# - MM.DD.YY` → `activityPrefix` (Task 1) used in `selectPracticeActivities` (Task 3) wired in Task 4 Step 4. ✓
- Spring baselines no longer assumed for auto-create → `findBaselineForUnknown(canonical, domain.baselines)` (Task 4 Step 6). ✓
- `/api/sync`, `/api/sync/bulk`, `/admin` made correct → confirmed no-change-needed because season is read from the DB row (Task 5 Step 1). ✓
- Idempotency wipe must not destroy FC seed rows → `selectAutoCreatedIds` heuristic (Task 3) wired in Task 4 Step 5. ✓

**Placeholder scan:** No TBD/TODO/"handle edge cases" — every code step shows complete code and exact commands. The only deferred item (FC aliases) is explicitly YAGNI with the seam (`canonicalize`'s `aliases` param) already built and documented, not a placeholder in the code path. ✓

**Type consistency:**
- `CalibrationDomain.activityPrefix: string` defined in Task 1, consumed as `domain.activityPrefix` in Tasks 3-4. ✓
- `selectAutoCreatedIds(rows, knownNames: Set<string>)` and `selectPracticeActivities(activities, dateStr, activityPrefix: string)` signatures defined in Task 3 match the call sites in Task 4 (Steps 4-5). ✓
- `canonicalize(rawName, knownNames?, aliases?)` defined in Task 2 matches the 2-arg call in Task 4 Step 6 and the 1-arg defaults used by existing callers/tests. ✓
- `beforeWipe` row type gains `pl_team_projected: number | null`, matching `selectAutoCreatedIds`'s parameter type. ✓

**Risk / known limitations (documented, accepted):**
- Code-only wipe heuristic leaves one pre-existing latent case (auto-created row sharing a baseline name won't be re-wiped) — unchanged from current Spring behavior, not a regression.
- No live Fall Camp GPS until ~August 2026, so this plan is verified by unit tests + build, not an end-to-end sync. The season-routing decisions are all pure-function tested.
- FC-specific canonicalization aliases are deferred until real FC Catapult period names exist; the parameter seam is in place.

**Out of scope:** Plans 1, 2, 4 (already shipped). No DB schema change. No UI change.
