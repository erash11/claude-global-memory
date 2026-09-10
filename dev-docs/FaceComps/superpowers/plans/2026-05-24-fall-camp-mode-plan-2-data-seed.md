# Fall Camp Mode — Plan 2: Data Seed + Season-Scoped Reads

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Seed the 18 defensive 2026 Fall Camp practice faces into the existing `practices`/`periods` tables under `season = '2026 Fall Camp'`, after making the read path season-aware so the live Spring app is unaffected.

**Architecture:** A Python generator parses the 2026 Fall Camp workbook DEF sheets into a committed JSON artifact (`simulator/scripts/fall_camp_faces.json`). A Node seed script reads that JSON and inserts rows, looking up `pl_team_projected` from the Fall Camp library (Plan 1's `FALL_CAMP_BASELINES`) for load drills and storing `0` for non-load periods (transitions/breaks). Read queries gain an optional `season` parameter defaulting to `'2026 Spring'`, so existing Spring views are byte-identical and Fall Camp rows are invisible until the Plan 4 switcher passes a season.

**Tech Stack:** Python 3 + openpyxl (generator, dev-only), TypeScript + @neondatabase/serverless (seed), Next.js 16 server components.

**Validated during research (2026-05-24):**
- Period names, order, and structure count match the snapshot for all 18 practices.
- Per-period minutes recovered via merged-cell overlap; only pure transitions have no minutes (correct).
- Decision (user-confirmed): **fuller/more-accurate load model** — count every drill instance (including repeats) and alias workbook shorthand to FC library names. `9 ON 7 1 ON 1`→`9 ON 7 + 1 ON 1`, `PODS 1 ON 1`→`PODS`, `PERIMETER RUN PLAY ACTION PASS`→`PERIMETER RUN + PAP`, `SCRIMMAGE`→`TEAM` (conservative proxy; revisitable).
- Decision (user-confirmed): non-library periods (transitions/breaks) are seeded with `pl_team_projected = 0` so the structure count is exact while load is not inflated. `computeSessionLoad` already yields 0 for a 0-projected period.

---

### Task 1: Commit the validated dataset + generator

The generator and JSON were produced and validated during research. This task lands them in the repo.

**Files:**
- Create: `simulator/scripts/generate-fall-camp-faces.py` (the validated generator, paths relative to repo)
- Create: `simulator/scripts/fall_camp_faces.json` (generated artifact, 18 practices)

- [ ] **Step 1:** Ensure `generate-fall-camp-faces.py` uses repo-relative paths (resolve from `__file__`), reads `SourceFaces/2026 Fall Camp - Practice Faces .xlsx` and `docs/fall-camp/*.csv`, and writes `fall_camp_faces.json` next to itself. Includes the validation print (structure count vs snapshot) and the `FACE_ALIASES` map with the SCRIMMAGE→TEAM comment.

- [ ] **Step 2:** Run it and confirm: 18 practices, all structure counts match snapshot, only true transitions remain non-library.

Run: `cd simulator/scripts && python generate-fall-camp-faces.py`
Expected: table with no `COUNT MISMATCH`; unresolved list contains only `TRANSISTION ...` entries.

- [ ] **Step 3:** Commit.

```bash
git add simulator/scripts/generate-fall-camp-faces.py simulator/scripts/fall_camp_faces.json
git commit -m "feat(fall-camp): add validated 2026 Fall Camp face dataset + generator"
```

---

### Task 2: Season-scope the read path (default Spring)

Make practice-list reads accept an optional season, defaulting to `'2026 Spring'`. This keeps the live app on Spring and makes Fall Camp rows invisible until the switcher exists.

**Files:**
- Modify: `simulator/app/simulator/page.tsx`
- Modify: `simulator/app/api/practices/route.ts`
- Modify: `simulator/app/admin/page.tsx`

- [ ] **Step 1: `app/simulator/page.tsx`** — read `searchParams.season` (Next 16: `searchParams` is a Promise), default `'2026 Spring'`, filter the query.

```tsx
import { getDb } from '@/lib/db'
import type { Practice } from '@/lib/types'
import { SimulatorClient } from './SimulatorClient'

export default async function SimulatorPage({
  searchParams,
}: {
  searchParams: Promise<{ season?: string }>
}) {
  const { season } = await searchParams
  const activeSeason = season ?? '2026 Spring'
  const sql = getDb()
  const practices = JSON.parse(JSON.stringify(
    await sql`SELECT * FROM practices WHERE season = ${activeSeason} ORDER BY practice_num ASC`
  )) as Practice[]

  return <SimulatorClient practices={practices} />
}
```

- [ ] **Step 2: `app/api/practices/route.ts`** — accept `?season=` query param, default `'2026 Spring'`.

Read the current file first, then change the list query from
`SELECT * FROM practices ORDER BY practice_num ASC`
to read the season from the request URL:

```ts
const season = new URL(req.url).searchParams.get('season') ?? '2026 Spring'
const rows = await sql`SELECT * FROM practices WHERE season = ${season} ORDER BY practice_num ASC`
```

(Adjust to the handler's existing signature — ensure the handler accepts the `Request`.)

- [ ] **Step 3: `app/admin/page.tsx`** — same default-Spring filter on its `SELECT * FROM practices` query, reading `searchParams.season` like Step 1.

- [ ] **Step 4: Build + manual check.**

Run: `cd simulator && npm run build`
Expected: build succeeds.
Manual: `/simulator` (no query) shows only the 15 Spring practices (unchanged).

- [ ] **Step 5: Commit.**

```bash
git add simulator/app/simulator/page.tsx simulator/app/api/practices/route.ts simulator/app/admin/page.tsx
git commit -m "feat(fall-camp): season-scope practice reads, default to Spring"
```

---

### Task 3: Fall Camp seed script (with dry-run)

**Files:**
- Create: `simulator/scripts/seed-fall-camp.ts`

- [ ] **Step 1: Write the seed script.**

Reads `fall_camp_faces.json`, inserts practices/periods under `season = '2026 Fall Camp'`. Load periods get `pl_team_projected = FALL_CAMP_BASELINES[name].plTeam`; non-load periods get `0`. Idempotent via `ON CONFLICT (season, practice_num) DO NOTHING`. Supports `--dry-run` (prints per-practice period counts + projected load, no DB writes).

```ts
import { neon } from '@neondatabase/serverless'
import * as dotenv from 'dotenv'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { FALL_CAMP_BASELINES } from '../lib/fallCampLibrary.generated'

dotenv.config({ path: '.env.local' })

const SEASON = '2026 Fall Camp'
const DRY = process.argv.includes('--dry-run')

interface FacePeriod { name: string; minutes: number; load: boolean }
interface Face {
  practice_num: number
  date: string
  day_of_week: string
  dress: string
  tempo: string
  emphasis: string
  periods: FacePeriod[]
}

function plTeamFor(p: FacePeriod): number {
  if (!p.load) return 0
  return FALL_CAMP_BASELINES[p.name]?.plTeam ?? 0
}

async function main() {
  const faces = JSON.parse(
    readFileSync(resolve(__dirname, 'fall_camp_faces.json'), 'utf8'),
  ) as Record<string, Face>
  const list = Object.values(faces).sort((a, b) => a.practice_num - b.practice_num)

  if (DRY) {
    for (const f of list) {
      const loadPeriods = f.periods.filter((p) => p.load).length
      const totalMin = f.periods.reduce((s, p) => s + p.minutes, 0)
      console.log(`P${f.practice_num} ${f.date} ${f.tempo}: ${f.periods.length} periods (${loadPeriods} load), ${totalMin} min`)
    }
    console.log(`\n[dry-run] ${list.length} practices, no DB writes.`)
    return
  }

  const sql = neon(process.env.DATABASE_URL!)
  for (const f of list) {
    const rows = await sql`
      INSERT INTO practices (season, practice_num, practice_date, day_of_week, dress, tempo, emphasis, total_duration_min)
      VALUES (${SEASON}, ${f.practice_num}, ${f.date}, ${f.day_of_week}, ${f.dress}, ${f.tempo}, ${f.emphasis},
              ${f.periods.reduce((s, p) => s + p.minutes, 0)})
      ON CONFLICT (season, practice_num) DO NOTHING
      RETURNING id
    `
    const practice = (rows as { id: number }[])[0]
    if (!practice) {
      console.log(`  Skipped P${f.practice_num} (already exists)`)
      continue
    }
    for (let i = 0; i < f.periods.length; i++) {
      const p = f.periods[i]
      await sql`
        INSERT INTO periods (practice_id, name, order_index, minutes, pl_team_projected)
        VALUES (${practice.id}, ${p.name}, ${i}, ${p.minutes}, ${plTeamFor(p)})
      `
    }
    console.log(`  Seeded P${f.practice_num} with ${f.periods.length} periods`)
  }
  console.log('Fall Camp seed complete.')
}

main().catch((err) => { console.error(err); process.exit(1) })
```

- [ ] **Step 2: Dry-run.**

Run: `cd simulator && npx ts-node --project tsconfig.json --compiler-options '{"module":"CommonJS"}' scripts/seed-fall-camp.ts --dry-run`
Expected: 18 lines (P1..P18) with period counts; "no DB writes".

- [ ] **Step 3: Commit the script (before any live write).**

```bash
git add simulator/scripts/seed-fall-camp.ts
git commit -m "feat(fall-camp): add Fall Camp seed script with dry-run"
```

---

### Task 4: Live seed + verification (USER CONFIRMATION REQUIRED)

**This task writes to the production Neon DB backing the deployed app. Pause for explicit user go-ahead before Step 1.**

- [ ] **Step 1:** Run the live seed.

Run: `cd simulator && npx ts-node --project tsconfig.json --compiler-options '{"module":"CommonJS"}' scripts/seed-fall-camp.ts`
Expected: "Seeded P1..P18", "Fall Camp seed complete."

- [ ] **Step 2:** Verify Fall Camp rows exist and Spring is untouched.

Run a quick check script or query:
- `SELECT season, COUNT(*) FROM practices GROUP BY season` → `2026 Spring`=15, `2026 Fall Camp`=18.
- Load `/simulator` (no query) → still only the 15 Spring practices.
- Load `/simulator?season=2026%20Fall%20Camp` → 18 Fall Camp practices appear.

- [ ] **Step 3:** Final commit / branch state note. No code change in this task; record completion.

---

## Self-Review

**Spec coverage:** seed 18 DEF faces under a distinct season (Tasks 1,3,4); Spring untouched via season-scoped reads (Task 2); load math reuses Plan 1 baselines (Task 3 `plTeamFor`). ✓
**Decisions baked in:** fuller load model + aliases (Task 1 generator); zero-load non-drills (Task 3 `plTeamFor` returns 0). ✓
**Out of scope:** season switcher UI + structure gauge (Plan 4); sync (Plan 3). The `?season=` param added in Task 2 is the seam the Plan 4 switcher will drive.
**Risk:** live DB write gated behind explicit confirmation (Task 4).
