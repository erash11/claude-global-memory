# Fall Camp Mode — Plan 4: UI (Season Switcher + Structure Gauge)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Make Fall Camp usable in the simulator: a season switcher that swaps the dataset + calibration domain, and a second "Structure" gauge (period count after stretch) shown alongside the load gauge for Fall Camp. Spring stays visually identical.

**Architecture:** The page already reads `?season=` (Plan 2) and queries the right practices. We pass the active season into `SimulatorClient`, which derives the `CalibrationDomain` via `getDomain(season)` and threads `domain.baselines` / `domain.loadThresholds` into all load math (`computeSessionLoad`, `generateSwaps`, add-period, swaps) — these params already exist from Plan 1. A `SeasonSwitcher` client component navigates between seasons. `LoadGauge` takes a `thresholds` prop so its zone markers reflect the domain. A new `StructureGauge` renders only when `domain.structureThresholds` is defined.

**Tech Stack:** Next.js 16 App Router, React client components, `next/navigation`, CSS modules. Hand-rolled markup matching existing components.

**Conventions:** Follow existing patterns — CSS modules per component, `var(--navy)`/`var(--green)` etc. tokens, no chart library. `getDomain`/`listDomains`/`computeStructure` from `@/lib/calibration` are client-safe (pure).

---

### Task 1: Pass active season into SimulatorClient and derive the domain

**Files:**
- Modify: `simulator/app/simulator/page.tsx`
- Modify: `simulator/app/simulator/SimulatorClient.tsx`

- [ ] **Step 1: `page.tsx`** — pass `season` and force remount on season change with `key`.

Change the render line:

```tsx
  return <SimulatorClient key={activeSeason} practices={practices} season={activeSeason} />
```

- [ ] **Step 2: `SimulatorClient.tsx`** — accept `season`, derive domain, thread baselines/thresholds.

Update imports and Props:

```tsx
import { PERIOD_DEFAULTS, TEMPO_MULT, computeSessionLoad, generateSwaps } from '@/lib/loadCalc'
import type { SwapSuggestion } from '@/lib/loadCalc'
import { getDomain, computeStructure } from '@/lib/calibration'
```

```tsx
interface Props {
  practices: Practice[]
  season: string
}

export function SimulatorClient({ practices, season }: Props) {
  const domain = getDomain(season)
```

Then replace the four Spring-coupled call sites:

- In `loadPractice`: `const load = computeSessionLoad(active, practice.tempo, domain.baselines, domain.loadThresholds)`
- Main render load: `const load = practice ? computeSessionLoad(periods, effectiveTempo, domain.baselines, domain.loadThresholds) : null`
- Swaps: `const swaps = load ? generateSwaps(periods, load.plPlayer, load.classification, tempoMult, domain.baselines, domain.loadThresholds) : []`
- `handleAdd`: `const defaults = domain.baselines[name]`
- `handleSwap`: both `PERIOD_DEFAULTS[swap.inn]` → `domain.baselines[swap.inn]`

(Leave the `PERIOD_DEFAULTS` import in place only if still referenced; if no longer used, remove it to avoid an unused-import error.)

- [ ] **Step 3: Build.**

Run: `cd simulator && npm run build`
Expected: succeeds. (Spring behavior unchanged: `getDomain('2026 Spring')` returns Spring baselines/thresholds, identical to the old constants.)

- [ ] **Step 4: Commit.**

```bash
git add simulator/app/simulator/page.tsx simulator/app/simulator/SimulatorClient.tsx
git commit -m "feat(fall-camp): thread calibration domain through SimulatorClient"
```

---

### Task 2: Season switcher component

**Files:**
- Create: `simulator/components/SeasonSwitcher.tsx`
- Create: `simulator/components/SeasonSwitcher.module.css`
- Modify: `simulator/app/simulator/SimulatorClient.tsx` (render it in the header)

- [ ] **Step 1: `SeasonSwitcher.tsx`.**

```tsx
'use client'

import { useRouter } from 'next/navigation'
import { listDomains } from '@/lib/calibration'
import styles from './SeasonSwitcher.module.css'

interface Props {
  season: string
}

export function SeasonSwitcher({ season }: Props) {
  const router = useRouter()
  const domains = listDomains()

  return (
    <div className={styles.switcher}>
      {domains.map((d) => (
        <button
          key={d.season}
          className={d.season === season ? styles.tabActive : styles.tab}
          onClick={() => router.push(`/simulator?season=${encodeURIComponent(d.season)}`)}
        >
          {d.label}
        </button>
      ))}
    </div>
  )
}
```

- [ ] **Step 2: `SeasonSwitcher.module.css`.**

```css
.switcher { display: inline-flex; gap: 4px; background: var(--gray-200); padding: 4px; border-radius: 8px; }
.tab {
  border: none; background: transparent; color: var(--gray-600);
  padding: 6px 14px; border-radius: 6px; font-size: 13px; font-weight: 700;
  cursor: pointer; white-space: nowrap;
}
.tabActive {
  border: none; background: #fff; color: var(--navy);
  padding: 6px 14px; border-radius: 6px; font-size: 13px; font-weight: 700;
  cursor: pointer; white-space: nowrap; box-shadow: 0 1px 3px rgba(0,0,0,0.12);
}
```

- [ ] **Step 3: Render it in `SimulatorClient` header.** Add the import and place it in the `<header>` block:

```tsx
import { SeasonSwitcher } from '@/components/SeasonSwitcher'
```

```tsx
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>Avg Player Load Simulator</h1>
          <div className={styles.sub}>Adjust Drill Selection to Manipulate Per-Player Load</div>
        </div>
        <SeasonSwitcher season={season} />
      </header>
```

- [ ] **Step 4: Build + manual.** `npm run build`; then `/simulator` shows the switcher with Spring active; clicking Fall Camp navigates to `?season=2026 Fall Camp` and loads 18 practices.

- [ ] **Step 5: Commit.**

```bash
git add simulator/components/SeasonSwitcher.tsx simulator/components/SeasonSwitcher.module.css simulator/app/simulator/SimulatorClient.tsx
git commit -m "feat(fall-camp): add season switcher to simulator"
```

---

### Task 3: Domain-aware LoadGauge markers

**Files:**
- Modify: `simulator/components/LoadGauge.tsx`
- Modify: `simulator/app/simulator/SimulatorClient.tsx` (pass `thresholds`)

- [ ] **Step 1: `LoadGauge.tsx`** — accept optional `thresholds`, default Spring; derive markers from it.

Add to `Props`:

```tsx
  thresholds?: { greenMax: number; yellowMax: number }
```

In the component body, after destructuring `load`:

```tsx
  const t = thresholds ?? { greenMax: 420, yellowMax: 470 }
```

Replace the three hardcoded zone marker spans with:

```tsx
        <span style={{ color: 'var(--green)' }}>GRN &le;{t.greenMax}</span>
        <span style={{ color: 'var(--yellow)' }}>YEL {t.greenMax + 1}-{t.yellowMax}</span>
        <span style={{ color: 'var(--red)' }}>RED &gt;{t.yellowMax}</span>
```

(Leave the `200` / `550` end markers and the bar range as-is; they bracket both domains.)

- [ ] **Step 2:** In `SimulatorClient`, pass the prop:

```tsx
            <LoadGauge
              load={load}
              originalPP={originalPP}
              originalDuration={originalDuration}
              practiceId={practice.id}
              hasGpsData={hasGpsData}
              thresholds={domain.loadThresholds}
            />
```

- [ ] **Step 3: Build.** `npm run build` succeeds. Spring markers still read `GRN ≤420 / YEL 421-470 / RED >470`; Fall Camp reads `GRN ≤405 / YEL 406-459 / RED >459`.

- [ ] **Step 4: Commit.**

```bash
git add simulator/components/LoadGauge.tsx simulator/app/simulator/SimulatorClient.tsx
git commit -m "feat(fall-camp): domain-aware load gauge zone markers"
```

---

### Task 4: Structure gauge (Fall Camp only)

**Files:**
- Create: `simulator/components/StructureGauge.tsx`
- Create: `simulator/components/StructureGauge.module.css`
- Modify: `simulator/app/simulator/SimulatorClient.tsx`

- [ ] **Step 1: `StructureGauge.tsx`.**

```tsx
'use client'

import styles from './StructureGauge.module.css'

const CLASS_COLOR: Record<string, string> = {
  GREEN: 'var(--green)',
  YELLOW: 'var(--yellow)',
  RED: 'var(--red)',
}

interface Props {
  countedPeriods: number
  classification: 'GREEN' | 'YELLOW' | 'RED'
  thresholds: { greenMax: number; yellowMax: number }
}

export function StructureGauge({ countedPeriods, classification, thresholds }: Props) {
  const color = CLASS_COLOR[classification]
  return (
    <div className={styles.container}>
      <div className={styles.value} style={{ color }}>{countedPeriods}</div>
      <div className={styles.unit}>Periods After Stretch</div>
      <div className={styles.markers}>
        <span style={{ color: 'var(--green)' }}>GRN &le;{thresholds.greenMax}</span>
        <span style={{ color: 'var(--yellow)' }}>YEL {thresholds.greenMax + 1}-{thresholds.yellowMax}</span>
        <span style={{ color: 'var(--red)' }}>RED &gt;{thresholds.yellowMax}</span>
      </div>
      <span className={styles.badge} style={{ background: color }}>{classification}</span>
      <div className={styles.note}>Counts non-break periods after the team stretch.</div>
    </div>
  )
}
```

- [ ] **Step 2: `StructureGauge.module.css`.**

```css
.container { text-align: center; padding: 8px 0; }
.value { font-size: 36px; font-weight: 800; transition: color 0.3s ease; }
.unit { font-size: 14px; font-weight: 600; color: var(--gray-600); }
.markers {
  display: flex; justify-content: space-between;
  font-size: 9px; color: var(--gray-400); padding: 0 2px; margin-top: 8px;
}
.badge {
  display: inline-block; padding: 3px 12px; border-radius: 12px;
  font-size: 12px; font-weight: 700; color: #fff; margin-top: 6px;
}
.note { font-size: 10px; color: var(--gray-500); margin-top: 8px; }
```

- [ ] **Step 3: Render in `SimulatorClient`** — compute structure and show the card only for domains that track it. Add near the `load` computation:

```tsx
  const structure = practice ? computeStructure(periods.filter(p => p.active), domain) : null
```

After the "Avg Player Load" card, add:

```tsx
          {structure && (
            <div className={styles.card}>
              <div className={styles.cardTitle}>Practice Structure</div>
              <StructureGauge
                countedPeriods={structure.countedPeriods}
                classification={structure.classification}
                thresholds={domain.structureThresholds!}
              />
            </div>
          )}
```

Add the import:

```tsx
import { StructureGauge } from '@/components/StructureGauge'
```

- [ ] **Step 4: Build + manual.** `npm run build`. On `/simulator?season=2026 Fall Camp`, the Structure card appears with the count (e.g. P1 = 11, GREEN) and updates as periods are toggled. On Spring, no Structure card appears.

- [ ] **Step 5: Commit.**

```bash
git add simulator/components/StructureGauge.tsx simulator/components/StructureGauge.module.css simulator/app/simulator/SimulatorClient.tsx
git commit -m "feat(fall-camp): add period-count structure gauge for Fall Camp"
```

---

### Task 5: Domain-aware AddPeriod drill list

**Files:**
- Modify: `simulator/components/AddPeriod.tsx`
- Modify: `simulator/app/simulator/SimulatorClient.tsx`

- [ ] **Step 1: `AddPeriod.tsx`** — accept a `baselines` map instead of importing Spring `PERIOD_DEFAULTS`.

```tsx
'use client'

import { useState } from 'react'
import type { BaselineMap } from '@/lib/loadCalc'
import styles from './PracticeSelector.module.css'

interface Props {
  onAdd: (name: string, minutes: number) => void
  baselines: BaselineMap
}

export function AddPeriod({ onAdd, baselines }: Props) {
  const [selected, setSelected] = useState('')
  const drills = Object.keys(baselines).sort()
  // ...unchanged markup, but replace PERIOD_DEFAULTS[selected] with baselines[selected]
```

In the add handler: `const defaultMins = baselines[selected]?.defaultMinutes ?? 10`.

- [ ] **Step 2:** In `SimulatorClient`, pass it: `<AddPeriod onAdd={handleAdd} baselines={domain.baselines} />`.

- [ ] **Step 3: Build + manual.** `npm run build`. On Fall Camp, the Add-drill dropdown lists FC library drills (e.g. `9 ON 7 + 1 ON 1`, `PODS`, `TEAM (SCRIM)` variants); on Spring, the original Spring drills.

- [ ] **Step 4: Commit.**

```bash
git add simulator/components/AddPeriod.tsx simulator/app/simulator/SimulatorClient.tsx
git commit -m "feat(fall-camp): domain-aware add-period drill list"
```

---

### Task 6: Full verification

- [ ] **Step 1: Tests + build.** `cd simulator && npm test && npm run build` — 110 tests pass, build clean.

- [ ] **Step 2: Manual (dev server).** `npm run dev`, then in a browser:
  - `/simulator` → Spring: switcher present (Spring active), single load gauge, markers `≤420/421-470/>470`, 15 practices, behaves as before.
  - Click **Fall Camp 2026** → 18 practices, **two gauges** (load with `≤405/406-459/>459`, plus Structure with count + zone), add-drill list shows FC drills.
  - Toggle a period off on a Fall Camp practice → structure count decrements and may change zone; load updates.
  - Switch back to Spring → Structure card gone, identical to original.

- [ ] **Step 3:** Report results. If all pass, hand off to finishing-a-development-branch.

---

## Self-Review

**Spec coverage:** season switcher swapping dataset + domain (Tasks 1,2); two separate gauges, load + structure (Tasks 3,4); Spring untouched via `getDomain` defaults (all tasks); domain-aware swaps/add reuse Plan 1 params (Tasks 1,5). ✓
**Type consistency:** `domain.baselines` is `Record<string, PeriodBaseline>`, structurally identical to `BaselineMap` in loadCalc — passes to `computeSessionLoad`/`generateSwaps`/`AddPeriod`. `domain.loadThresholds`/`structureThresholds` are `{greenMax,yellowMax}`, matching `LoadThresholds` and the gauge props. `computeStructure` returns `{countedPeriods, classification}` consumed by `StructureGauge`. ✓
**Placeholder scan:** none — every step has concrete code.
**Out of scope:** Plan 3 (sync). Compare-page projection markers are unchanged (no FC actuals exist yet).
**Risk:** UI-only; no DB writes. Manual browser verification in Task 6 is the real gate (type/test checks don't prove feature correctness).
