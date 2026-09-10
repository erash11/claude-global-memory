# Fall Camp Mode — Plan 1: Calibration Foundation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the calibration-domain abstraction (registry + Fall Camp library + domain-aware load math + structure helper) so later plans can wire Fall Camp data, sync, and UI without scattering season checks — and prove Spring math is unchanged.

**Architecture:** One `lib/calibration.ts` registry maps a season string to a `CalibrationDomain` (baselines, load thresholds, optional structure thresholds). Spring's domain reuses the existing `PERIOD_DEFAULTS`/thresholds in `loadCalc.ts`; Fall Camp's domain imports a generated constants file built from the FC24/FC25 calibration CSVs. The pure load-math functions in `loadCalc.ts` gain optional `baselines`/`thresholds` parameters that default to the current Spring constants, so every existing call site behaves identically. `loadCalc.ts` never imports `calibration.ts` (avoids a circular import); the registry depends on `loadCalc`, not the reverse.

**Tech Stack:** TypeScript, Next.js 16, Vitest, Node CSV read via `node:fs`. This plan adds no DB or UI changes.

**Scope guardrails (this plan only):**
- No changes to `periodMap.ts`, `syncPractice.ts`, any API route, any component, or any page.
- No DB writes. No seeding.
- Spring behavior must be byte-for-byte identical when functions are called with no domain args.

---

### Task 1: Pure unit-conversion + structure helpers in `lib/calibration.ts`

This task adds only the pure helpers and types (no FC data import yet) so they can be unit-tested before the generated file exists.

**Files:**
- Create: `simulator/lib/calibration.ts`
- Test: `simulator/tests/calibration.test.ts`

- [ ] **Step 1: Write the failing test**

Create `simulator/tests/calibration.test.ts`:

```ts
import { describe, expect, it } from 'vitest'
import {
  playerLoadToTeamBaseline,
  computeStructure,
  type CalibrationDomain,
} from '@/lib/calibration'

describe('playerLoadToTeamBaseline', () => {
  it('converts per-player PL to composite team-scale by dividing by RATIO (not multiplying)', () => {
    // RUN THRU FC avg_pl_player = 59.4 -> 59.4 / 0.09772 ≈ 607.86 -> 608
    expect(playerLoadToTeamBaseline(59.4)).toBe(608)
  })

  it('round-trips: team baseline * RATIO ≈ original per-player value', () => {
    const team = playerLoadToTeamBaseline(40)
    expect(Math.abs(team * 0.09772 - 40)).toBeLessThan(0.6)
  })
})

describe('computeStructure', () => {
  const fcLike: CalibrationDomain = {
    season: 'TEST FC',
    label: 'Test FC',
    baselines: {},
    loadThresholds: { greenMax: 405, yellowMax: 459 },
    structureThresholds: { greenMax: 11, yellowMax: 13 },
  }
  const springLike: CalibrationDomain = {
    season: 'TEST SPRING',
    label: 'Test Spring',
    baselines: {},
    loadThresholds: { greenMax: 420, yellowMax: 470 },
  }

  it('returns null for a domain without structure thresholds', () => {
    expect(computeStructure([{ name: 'TEAM STRETCH' }, { name: 'TEAM' }], springLike)).toBeNull()
  })

  it('counts non-break periods after stretch and classifies (12 -> YELLOW)', () => {
    const periods = [
      { name: 'RUN THRU' },
      { name: 'TEAM STRETCH' },
      ...Array.from({ length: 12 }, (_, i) => ({ name: `PERIOD ${i + 1}` })),
    ]
    expect(computeStructure(periods, fcLike)).toEqual({ countedPeriods: 12, classification: 'YELLOW' })
  })

  it('classifies <=11 counted periods as GREEN and >13 as RED', () => {
    const after = (n: number) => [
      { name: 'TEAM STRETCH' },
      ...Array.from({ length: n }, (_, i) => ({ name: `P${i}` })),
    ]
    expect(computeStructure(after(11), fcLike)!.classification).toBe('GREEN')
    expect(computeStructure(after(14), fcLike)!.classification).toBe('RED')
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd simulator && npx vitest run tests/calibration.test.ts`
Expected: FAIL — cannot resolve `@/lib/calibration`.

- [ ] **Step 3: Write minimal implementation**

Create `simulator/lib/calibration.ts`:

```ts
import { RATIO } from './loadCalc'
import { countPeriodsAfterStretch, classifyByThresholds } from './fallCampCalibration'

export interface PeriodBaseline {
  plTeam: number
  defaultMinutes: number
}

export interface ZoneThresholds {
  greenMax: number
  yellowMax: number
}

export interface CalibrationDomain {
  season: string
  label: string
  baselines: Record<string, PeriodBaseline>
  loadThresholds: ZoneThresholds
  structureThresholds?: ZoneThresholds
}

// Convert a per-player average PL value (the scale Catapult and the FC library
// report) into the composite team-scale baseline used by PERIOD_DEFAULTS.
// This is the conversion most likely to introduce a ~10x bug: DIVIDE by RATIO
// to go per-player -> team-scale. Multiplying would be wrong.
export function playerLoadToTeamBaseline(avgPlPlayer: number): number {
  return Math.round(avgPlPlayer / RATIO)
}

export interface StructureResult {
  countedPeriods: number
  classification: 'GREEN' | 'YELLOW' | 'RED'
}

// Period-count structure zone. Only meaningful for domains that track it
// (Fall Camp). Returns null for domains without structureThresholds (Spring).
export function computeStructure(
  periods: Array<{ name: string }>,
  domain: CalibrationDomain,
): StructureResult | null {
  if (!domain.structureThresholds) return null
  const countedPeriods = countPeriodsAfterStretch(periods)
  const classification = classifyByThresholds(countedPeriods, domain.structureThresholds)
  return { countedPeriods, classification }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd simulator && npx vitest run tests/calibration.test.ts`
Expected: PASS (5 tests).

- [ ] **Step 5: Commit**

```bash
git add simulator/lib/calibration.ts simulator/tests/calibration.test.ts
git commit -m "feat(fall-camp): add calibration domain types + pure helpers"
```

---

### Task 2: Fall Camp library codegen script + generated constants

Generates `lib/fallCampLibrary.generated.ts` from the calibration CSVs. The script is deterministic; we unit-test the pure row-mapping helper, then run the script to emit the artifact.

**Files:**
- Modify: `simulator/lib/calibration.ts` (add exported `csvRowToBaseline` helper)
- Create: `simulator/scripts/generate-fall-camp-library.ts`
- Create (generated by running the script): `simulator/lib/fallCampLibrary.generated.ts`
- Test: `simulator/tests/calibration.test.ts` (extend)

- [ ] **Step 1: Write the failing test (extend calibration.test.ts)**

Append to `simulator/tests/calibration.test.ts`:

```ts
import { csvRowToBaseline } from '@/lib/calibration'

describe('csvRowToBaseline', () => {
  it('maps an FC library CSV row to a team-scale baseline keyed by canonical name', () => {
    // period,intensity,occurrences,avg_pl_player,median_pl_player,avg_pl_per_min,typical_minutes,...
    expect(csvRowToBaseline({
      period: 'RUN THRU',
      avg_pl_player: '59.4',
      typical_minutes: '34',
    })).toEqual({
      name: 'RUN THRU',
      baseline: { plTeam: 608, defaultMinutes: 34 },
    })
  })

  it('rounds typical_minutes to a whole number and clamps to >=1', () => {
    expect(csvRowToBaseline({ period: 'X', avg_pl_player: '20', typical_minutes: '0.4' }).baseline.defaultMinutes).toBe(1)
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd simulator && npx vitest run tests/calibration.test.ts`
Expected: FAIL — `csvRowToBaseline` is not exported.

- [ ] **Step 3: Add `csvRowToBaseline` to `lib/calibration.ts`**

Append to `simulator/lib/calibration.ts`:

```ts
export interface FallCampLibraryCsvRow {
  period: string
  avg_pl_player: string
  typical_minutes: string
}

// Map one row of fall_camp_period_library.csv to a named team-scale baseline.
export function csvRowToBaseline(row: FallCampLibraryCsvRow): {
  name: string
  baseline: PeriodBaseline
} {
  const plTeam = playerLoadToTeamBaseline(Number(row.avg_pl_player))
  const defaultMinutes = Math.max(1, Math.round(Number(row.typical_minutes)))
  return { name: row.period, baseline: { plTeam, defaultMinutes } }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd simulator && npx vitest run tests/calibration.test.ts`
Expected: PASS (7 tests).

- [ ] **Step 5: Write the codegen script**

Create `simulator/scripts/generate-fall-camp-library.ts`:

```ts
import { readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { csvRowToBaseline } from '../lib/calibration'

const DOCS = resolve(__dirname, '../../docs/fall-camp')
const OUT = resolve(__dirname, '../lib/fallCampLibrary.generated.ts')

// Minimal CSV parser: header row + comma split. The FC CSVs contain no quoted
// commas in the columns we read (period, avg_pl_player, typical_minutes).
function parseCsv(text: string): Record<string, string>[] {
  const lines = text.trim().split(/\r?\n/)
  const headers = lines[0].split(',')
  return lines.slice(1).map((line) => {
    const cells = line.split(',')
    const row: Record<string, string> = {}
    headers.forEach((h, i) => { row[h] = cells[i] ?? '' })
    return row
  })
}

function loadThresholds(): { greenMax: number; yellowMax: number } {
  // GREEN <= 405, YELLOW 406-459, RED > 459 (FC24/FC25 daily PL/player terciles).
  return { greenMax: 405, yellowMax: 459 }
}

function structureThresholds(): { greenMax: number; yellowMax: number } {
  // GREEN-count <= 11, YELLOW 12-13, RED > 13 counted periods after stretch.
  return { greenMax: 11, yellowMax: 13 }
}

function main() {
  const libCsv = parseCsv(readFileSync(resolve(DOCS, 'fall_camp_period_library.csv'), 'utf8'))
  const baselines: Record<string, { plTeam: number; defaultMinutes: number }> = {}
  for (const row of libCsv) {
    if (!row.period) continue
    const { name, baseline } = csvRowToBaseline(row as never)
    baselines[name] = baseline
  }

  const banner = '// AUTO-GENERATED by scripts/generate-fall-camp-library.ts. Do not edit by hand.\n'
    + '// Source: docs/fall-camp/fall_camp_period_library.csv + threshold CSVs.\n'
    + `// Regenerate after recalibration. Generated ${new Date().toISOString().slice(0, 10)}.\n\n`

  const body =
    `import type { PeriodBaseline, ZoneThresholds } from './calibration'\n\n` +
    `export const FALL_CAMP_BASELINES: Record<string, PeriodBaseline> = ${JSON.stringify(baselines, null, 2)}\n\n` +
    `export const FALL_CAMP_LOAD_THRESHOLDS: ZoneThresholds = ${JSON.stringify(loadThresholds(), null, 2)}\n\n` +
    `export const FALL_CAMP_STRUCTURE_THRESHOLDS: ZoneThresholds = ${JSON.stringify(structureThresholds(), null, 2)}\n`

  writeFileSync(OUT, banner + body)
  console.log(`Wrote ${OUT} with ${Object.keys(baselines).length} baselines.`)
}

main()
```

- [ ] **Step 6: Run the codegen script to emit the generated file**

Run: `cd simulator && npx ts-node --project tsconfig.json --compiler-options '{"module":"CommonJS"}' scripts/generate-fall-camp-library.ts`
Expected: prints `Wrote .../lib/fallCampLibrary.generated.ts with N baselines.` (N > 20). Open the file and confirm `RUN THRU` has `plTeam: 608, defaultMinutes: 34`.

- [ ] **Step 7: Commit**

```bash
git add simulator/lib/calibration.ts simulator/tests/calibration.test.ts simulator/scripts/generate-fall-camp-library.ts simulator/lib/fallCampLibrary.generated.ts
git commit -m "feat(fall-camp): generate Fall Camp period library constants from calibration CSVs"
```

---

### Task 3: Calibration registry (Spring + Fall Camp domains)

**Files:**
- Modify: `simulator/lib/calibration.ts` (add domains + `getDomain`/`listDomains`)
- Test: `simulator/tests/calibration.test.ts` (extend)

- [ ] **Step 1: Write the failing test**

Append to `simulator/tests/calibration.test.ts`:

```ts
import { getDomain, listDomains, SPRING_2026, FALL_CAMP_2026 } from '@/lib/calibration'

describe('calibration registry', () => {
  it('returns the Spring domain for its season string and it has no structure zone', () => {
    const d = getDomain('2026 Spring')
    expect(d).toBe(SPRING_2026)
    expect(d.structureThresholds).toBeUndefined()
    expect(d.loadThresholds).toEqual({ greenMax: 420, yellowMax: 470 })
  })

  it('returns the Fall Camp domain with a structure zone and FC load thresholds', () => {
    const d = getDomain('2026 Fall Camp')
    expect(d).toBe(FALL_CAMP_2026)
    expect(d.loadThresholds).toEqual({ greenMax: 405, yellowMax: 459 })
    expect(d.structureThresholds).toEqual({ greenMax: 11, yellowMax: 13 })
    expect(d.baselines['RUN THRU']).toEqual({ plTeam: 608, defaultMinutes: 34 })
  })

  it('defaults to Spring for an unknown season', () => {
    expect(getDomain('nonsense')).toBe(SPRING_2026)
  })

  it('lists both domains for the season switcher', () => {
    expect(listDomains().map((d) => d.season)).toEqual(['2026 Spring', '2026 Fall Camp'])
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd simulator && npx vitest run tests/calibration.test.ts`
Expected: FAIL — `getDomain`/`SPRING_2026`/`FALL_CAMP_2026` not exported.

- [ ] **Step 3: Add the registry to `lib/calibration.ts`**

Add imports at the top of `simulator/lib/calibration.ts` (alongside the existing `RATIO` import):

```ts
import { PERIOD_DEFAULTS, THRESH_GREEN, THRESH_YELLOW } from './loadCalc'
import {
  FALL_CAMP_BASELINES,
  FALL_CAMP_LOAD_THRESHOLDS,
  FALL_CAMP_STRUCTURE_THRESHOLDS,
} from './fallCampLibrary.generated'
```

Append to `simulator/lib/calibration.ts`:

```ts
export const SPRING_2026: CalibrationDomain = {
  season: '2026 Spring',
  label: 'Spring 2026',
  baselines: PERIOD_DEFAULTS,
  loadThresholds: { greenMax: THRESH_GREEN, yellowMax: THRESH_YELLOW },
}

export const FALL_CAMP_2026: CalibrationDomain = {
  season: '2026 Fall Camp',
  label: 'Fall Camp 2026',
  baselines: FALL_CAMP_BASELINES,
  loadThresholds: FALL_CAMP_LOAD_THRESHOLDS,
  structureThresholds: FALL_CAMP_STRUCTURE_THRESHOLDS,
}

const DOMAINS: CalibrationDomain[] = [SPRING_2026, FALL_CAMP_2026]

export function listDomains(): CalibrationDomain[] {
  return DOMAINS
}

export function getDomain(season: string): CalibrationDomain {
  return DOMAINS.find((d) => d.season === season) ?? SPRING_2026
}
```

Note: `PERIOD_DEFAULTS` is typed `Record<string, { plTeam: number; defaultMinutes: number }>`, which is structurally identical to `Record<string, PeriodBaseline>`, so it assigns cleanly to `baselines`.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd simulator && npx vitest run tests/calibration.test.ts`
Expected: PASS (11 tests).

- [ ] **Step 5: Commit**

```bash
git add simulator/lib/calibration.ts simulator/tests/calibration.test.ts
git commit -m "feat(fall-camp): add calibration registry with Spring and Fall Camp domains"
```

---

### Task 4: Parameterize `loadCalc` math by baselines + thresholds

Add optional `baselines`/`thresholds` parameters that default to the existing Spring constants. Existing call sites (which pass no extra args) must produce identical output — guarded by a regression test.

**Files:**
- Modify: `simulator/lib/loadCalc.ts`
- Test: `simulator/tests/loadCalc.domain.test.ts` (create)

- [ ] **Step 1: Write the failing test**

Create `simulator/tests/loadCalc.domain.test.ts`:

```ts
import { describe, expect, it } from 'vitest'
import {
  classify,
  findBaselineForUnknown,
  projectedPlTeam,
  computeSessionLoad,
  PERIOD_DEFAULTS,
  THRESH_GREEN,
  THRESH_YELLOW,
} from '@/lib/loadCalc'
import type { ActivePeriod, Period } from '@/lib/types'

const springThresholds = { greenMax: THRESH_GREEN, yellowMax: THRESH_YELLOW }

function period(name: string, minutes: number, overrides: Partial<Period> = {}): Period {
  return {
    id: 1, practice_id: 1, name, order_index: 0, minutes,
    pl_team_projected: PERIOD_DEFAULTS[name]?.plTeam ?? 300,
    pl_team_actual: null, pl_per_min_actual: null, ...overrides,
  }
}

describe('loadCalc regression: Spring defaults unchanged', () => {
  it('classify with no thresholds == classify with explicit Spring thresholds', () => {
    for (const v of [300, 420, 421, 470, 471, 600]) {
      expect(classify(v)).toBe(classify(v, springThresholds))
    }
  })

  it('findBaselineForUnknown with no baselines == with explicit PERIOD_DEFAULTS', () => {
    for (const n of ['TEAM PASS', 'STACKS N PACKS', 'TEAM']) {
      expect(findBaselineForUnknown(n)).toEqual(findBaselineForUnknown(n, PERIOD_DEFAULTS))
    }
  })

  it('projectedPlTeam with no baselines == with explicit PERIOD_DEFAULTS', () => {
    const p = period('TEAM', 12)
    expect(projectedPlTeam(p, 'THUD')).toBe(projectedPlTeam(p, 'THUD', PERIOD_DEFAULTS))
  })

  it('computeSessionLoad with no domain args == with explicit Spring args', () => {
    const periods: ActivePeriod[] = [
      { ...period('TEAM', 12), active: true, added: false },
      { ...period('STRETCH', 10), active: true, added: false },
    ]
    expect(computeSessionLoad(periods, 'THUD')).toEqual(
      computeSessionLoad(periods, 'THUD', PERIOD_DEFAULTS, springThresholds),
    )
  })
})

describe('loadCalc with a Fall-Camp-style baseline set', () => {
  const fcBaselines = { 'RUN THRU': { plTeam: 608, defaultMinutes: 34 } }
  const fcThresholds = { greenMax: 405, yellowMax: 459 }

  it('uses the supplied baseline for an unknown-in-Spring period', () => {
    expect(findBaselineForUnknown('RUN THRU', fcBaselines)).toEqual({ plTeam: 608, defaultMinutes: 34 })
  })

  it('classifies with Fall Camp thresholds (410 -> YELLOW, not GREEN)', () => {
    expect(classify(410, fcThresholds)).toBe('YELLOW')
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd simulator && npx vitest run tests/loadCalc.domain.test.ts`
Expected: FAIL — `classify`/`findBaselineForUnknown`/etc. do not accept the extra argument (TS error or assertion failure).

- [ ] **Step 3: Edit `lib/loadCalc.ts`**

Add a shared threshold type and default near the top, after the existing `THRESH_YELLOW` (line 36):

```ts
export interface LoadThresholds {
  greenMax: number
  yellowMax: number
}

const DEFAULT_THRESHOLDS: LoadThresholds = { greenMax: THRESH_GREEN, yellowMax: THRESH_YELLOW }

export type BaselineMap = Record<string, { plTeam: number; defaultMinutes: number }>
```

Replace `findBaselineForUnknown` (lines 49-58) with:

```ts
export function findBaselineForUnknown(
  canonical: string,
  baselines: BaselineMap = PERIOD_DEFAULTS,
): { plTeam: number; defaultMinutes: number } {
  if (baselines[canonical]) return baselines[canonical]
  const words = canonical.trim().split(/\s+/)
  while (words.length > 1) {
    words.pop()
    const candidate = words.join(' ')
    if (baselines[candidate]) return baselines[candidate]
  }
  return { plTeam: FALLBACK_PL_TEAM, defaultMinutes: FALLBACK_DEFAULT_MINUTES }
}
```

Replace `classify` (lines 114-118) with:

```ts
export function classify(
  ppLoad: number,
  thresholds: LoadThresholds = DEFAULT_THRESHOLDS,
): 'GREEN' | 'YELLOW' | 'RED' {
  if (ppLoad <= thresholds.greenMax) return 'GREEN'
  if (ppLoad <= thresholds.yellowMax) return 'YELLOW'
  return 'RED'
}
```

Replace `projectedPlTeam` (lines 127-139) with:

```ts
export function projectedPlTeam(
  period: Period,
  tempo: string,
  baselines: BaselineMap = PERIOD_DEFAULTS,
): number {
  const mult = TEMPO_MULT[tempo] ?? 1.0
  const baseline = baselines[period.name] ?? findBaselineForUnknown(period.name, baselines)
  const defaultMins = baseline.defaultMinutes
  const baselinePlTeam = period.pl_team_projected || baseline.plTeam
  const plPerMin = baselinePlTeam / defaultMins
  return computePeriodPlTeam(plPerMin, period.minutes, mult)
}
```

Replace the `computeSessionLoad` signature and the two lines inside it that look up baselines/classification. Change the signature (line 183) to:

```ts
export function computeSessionLoad(
  periods: ActivePeriod[],
  tempo: string,
  baselines: BaselineMap = PERIOD_DEFAULTS,
  thresholds: LoadThresholds = DEFAULT_THRESHOLDS,
): SessionLoad {
```

Inside `computeSessionLoad`, change the baseline lookup (line 192) from:

```ts
    const baseline = PERIOD_DEFAULTS[p.name] ?? findBaselineForUnknown(p.name)
```

to:

```ts
    const baseline = baselines[p.name] ?? findBaselineForUnknown(p.name, baselines)
```

and change the classification (line 207) from:

```ts
  const classification = classify(plPlayer)
```

to:

```ts
  const classification = classify(plPlayer, thresholds)
```

- [ ] **Step 4: Run the new test to verify it passes**

Run: `cd simulator && npx vitest run tests/loadCalc.domain.test.ts`
Expected: PASS (6 tests).

- [ ] **Step 5: Run the FULL suite to confirm no regression**

Run: `cd simulator && npm test`
Expected: all files pass (previously 8 files / 92 tests, now +2 new files; total tests increased, zero failures).

- [ ] **Step 6: Commit**

```bash
git add simulator/lib/loadCalc.ts simulator/tests/loadCalc.domain.test.ts
git commit -m "feat(fall-camp): parameterize loadCalc math by baselines and thresholds (Spring defaults preserved)"
```

---

### Task 5: Parameterize `generateSwaps` by baselines + thresholds

`generateSwaps` (loadCalc.ts:226-345) reads `PERIOD_DEFAULTS` and calls `classify` internally. Thread the domain's baselines/thresholds through it, defaulting to Spring. Swap option name lists (`LIGHT_OPTIONS`/`HEAVY_OPTIONS`) stay as optional params defaulting to the current Spring lists; a later plan can supply Fall Camp lists.

**Files:**
- Modify: `simulator/lib/loadCalc.ts`
- Test: `simulator/tests/loadCalc.domain.test.ts` (extend)

- [ ] **Step 1: Write the failing test**

Append to `simulator/tests/loadCalc.domain.test.ts`:

```ts
import { generateSwaps } from '@/lib/loadCalc'

describe('generateSwaps regression: Spring defaults unchanged', () => {
  const periods: ActivePeriod[] = [
    { ...period('TEAM', 12), active: true, added: false },
    { ...period('TEAM', 12), active: true, added: false },
    { ...period('REDZONE LOCKOUT', 10), active: true, added: false },
  ]
  it('no-arg call equals explicit Spring-args call', () => {
    const withDefaults = generateSwaps(periods, 500, 'RED', 1.0)
    const withExplicit = generateSwaps(
      periods, 500, 'RED', 1.0,
      PERIOD_DEFAULTS,
      { greenMax: THRESH_GREEN, yellowMax: THRESH_YELLOW },
    )
    expect(withDefaults).toEqual(withExplicit)
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd simulator && npx vitest run tests/loadCalc.domain.test.ts`
Expected: FAIL — `generateSwaps` does not accept the 5th/6th arguments.

- [ ] **Step 3: Edit `generateSwaps` in `lib/loadCalc.ts`**

Change the `generateSwaps` signature (lines 226-231) to add two trailing optional params:

```ts
export function generateSwaps(
  periods: ActivePeriod[],
  currentPP: number,
  currentClass: 'GREEN' | 'YELLOW' | 'RED',
  tempoMult: number,
  baselines: BaselineMap = PERIOD_DEFAULTS,
  thresholds: LoadThresholds = DEFAULT_THRESHOLDS,
): SwapSuggestion[] {
```

Inside `generateSwaps`, replace every `PERIOD_DEFAULTS[` with `baselines[` and every `classify(` call with `classify(` ... `, thresholds)`. Concretely:

- In `periodEffectivePL` (line 239): `const defaultMinutes = baselines[p.name]?.defaultMinutes ?? 10`
- Line 250: `(p) => (baselines[p.name]?.plTeam ?? 0) >= 300,`
- Lines 261-262: `const lightDefault = baselines[lightName]?.defaultMinutes ?? 10` and `const lightPLTeam = baselines[lightName]?.plTeam ?? 0`
- Line 267: `const newClass = classify(newPP, thresholds)`
- Line 283: `const newClass = classify(newPP, thresholds)`
- Line 294: `(p) => (baselines[p.name]?.plTeam ?? 999) < 250,`
- Lines 305-306: `const heavyDefault = baselines[heavyName]?.defaultMinutes ?? 10` and `const heavyPLTeam = baselines[heavyName]?.plTeam ?? 0`
- Line 311: `const newClass = classify(newPP, thresholds)`
- Lines 329-330: `const heavyDefault = baselines[heavyName]?.defaultMinutes ?? 10` and `const heavyPLTeam = baselines[heavyName]?.plTeam ?? 0`
- Line 334: `const newClass = classify(newPP, thresholds)`

Leave `LIGHT_OPTIONS` and `HEAVY_OPTIONS` (lines 223-224) unchanged for this plan.

- [ ] **Step 4: Run the new test to verify it passes**

Run: `cd simulator && npx vitest run tests/loadCalc.domain.test.ts`
Expected: PASS (7 tests in file).

- [ ] **Step 5: Run the FULL suite + build**

Run: `cd simulator && npm test && npm run build`
Expected: all tests pass; `npm run build` succeeds on Next 16.2.3.

- [ ] **Step 6: Commit**

```bash
git add simulator/lib/loadCalc.ts simulator/tests/loadCalc.domain.test.ts
git commit -m "feat(fall-camp): parameterize generateSwaps by baselines and thresholds"
```

---

## Self-Review (completed at authoring time)

**Spec coverage (Plan 1 portion):**
- Calibration registry (`lib/calibration.ts`, `getDomain`, domain descriptor) — Tasks 1, 3. ✓
- Spring domain reuses `PERIOD_DEFAULTS` + existing thresholds; Fall Camp from generated file — Tasks 2, 3. ✓
- `loadCalc` helpers gain optional domain args defaulting to Spring — Tasks 4, 5. ✓
- `computeStructure` using `countPeriodsAfterStretch` — Task 1. ✓
- Unit-conversion bug guard (divide by RATIO) — Task 1 test + `playerLoadToTeamBaseline`. ✓
- Codegen from CSV — Task 2. ✓
- Spring-untouched regression guard — Tasks 4, 5 tests. ✓

**Deferred to later plans (intentionally out of scope here):** seed script (Plan 2), `syncPractice`/`periodMap`/activity pattern (Plan 3), season switcher + season-scoped queries + structure gauge (Plan 4).

**Type consistency:** `PeriodBaseline` (calibration) and `BaselineMap`'s value type (loadCalc) are structurally identical `{ plTeam, defaultMinutes }`. `ZoneThresholds` (calibration) and `LoadThresholds` (loadCalc) are structurally identical `{ greenMax, yellowMax }`. `classifyByThresholds` and `countPeriodsAfterStretch` are imported from the existing `fallCampCalibration.ts` (already present and tested). The generated file imports `PeriodBaseline`/`ZoneThresholds` types from `./calibration`, which exist after Task 1.

**Placeholder scan:** none.
