# Practice Load Simulator Rebuild Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild `Practice_Load_Simulator_v2.html` as a Next.js 14 app on Vercel with Neon PostgreSQL, Catapult API sync, duration-scaled load calculations, and a lightweight password gate.

**Architecture:** Next.js 14 App Router scaffolded in a `simulator/` subdirectory of the FaceComps repo. Vercel is configured to use `simulator/` as the root directory. Neon PostgreSQL stores practice and period data. Catapult GPS sync runs server-side via a Next.js API route using the existing JWT token pattern.

**Tech Stack:** Next.js 14, TypeScript, Neon Serverless Postgres (`@neondatabase/serverless`), `jose` (cookie signing), Vitest + React Testing Library, CSS Modules

---

## File Structure

```
simulator/
├── app/
│   ├── layout.tsx                              — root layout, global nav header, password gate wrapper
│   ├── page.tsx                                — redirect to /simulator
│   ├── globals.css                             — CSS custom properties (Baylor design tokens)
│   ├── login/
│   │   └── page.tsx                            — password entry form
│   ├── simulator/
│   │   └── page.tsx                            — main simulator (server component → client hydration)
│   ├── admin/
│   │   └── page.tsx                            — GPS sync panel
│   └── reference/
│       └── page.tsx                            — printable reference card
├── components/
│   ├── PracticeSelector.tsx                    — practice dropdown + metadata grid
│   ├── PracticeSelector.module.css
│   ├── LoadGauge.tsx                           — PL/player gauge, classification badge, delta row
│   ├── LoadGauge.module.css
│   ├── PeriodList.tsx                          — ordered list of period rows
│   ├── PeriodItem.tsx                          — single row: name | minutes (editable) | PL/player | PL/min | badges | remove btn
│   ├── PeriodItem.module.css
│   ├── AddPeriod.tsx                           — drill picker + Add button
│   ├── SwapSuggestions.tsx                     — contextual swap cards
│   └── SwapSuggestions.module.css
├── lib/
│   ├── db.ts                                   — Neon connection singleton
│   ├── types.ts                                — shared TypeScript interfaces
│   ├── periodMap.ts                            — Catapult period name → canonical name mapping
│   ├── loadCalc.ts                             — all load calculation pure functions
│   ├── catapult.ts                             — Catapult Connect v6 API client (TypeScript)
│   └── auth.ts                                 — cookie sign/verify helpers (jose)
├── middleware.ts                               — password gate: checks cookie, redirects to /login
├── app/api/
│   ├── login/route.ts                          — POST: verify password, set signed cookie
│   ├── practices/route.ts                      — GET: list all practices
│   ├── practices/[id]/route.ts                 — GET: single practice with periods
│   ├── practices/[id]/periods/[pid]/route.ts   — PATCH: update period minutes
│   └── sync/route.ts                           — POST: Catapult → Neon GPS sync
├── scripts/
│   └── seed.ts                                 — one-time seed: practice_defaults, practices, periods
├── tests/
│   ├── setup.ts                                — vitest global setup (@testing-library/jest-dom)
│   ├── loadCalc.test.ts
│   ├── periodMap.test.ts
│   └── catapult.test.ts
├── vitest.config.ts
├── next.config.ts
├── tsconfig.json
└── package.json
```

---

## Task 1: Project Scaffold

**Files:**
- Create: `simulator/` (all scaffold files via create-next-app)
- Create: `simulator/vitest.config.ts`
- Create: `simulator/tests/setup.ts`

- [ ] **Step 1: Scaffold the Next.js app**

Run from `C:/Users/eric_rash/Desktop/DEV/Football/FaceComps/`:
```bash
npx create-next-app@latest simulator --typescript --app --no-tailwind --no-eslint --no-src-dir --import-alias "@/*"
```
Select: No to all optional prompts (Turbopack, etc.) if not already defaulted.

- [ ] **Step 2: Install dependencies**

```bash
cd simulator
npm install @neondatabase/serverless jose
npm install --save-dev vitest @vitejs/plugin-react @testing-library/react @testing-library/jest-dom jsdom
```

- [ ] **Step 3: Create vitest config**

Create `simulator/vitest.config.ts`:
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./tests/setup.ts'],
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, '.'),
    },
  },
})
```

- [ ] **Step 4: Create test setup file**

Create `simulator/tests/setup.ts`:
```typescript
import '@testing-library/jest-dom'
```

- [ ] **Step 5: Add test script to package.json**

In `simulator/package.json`, add to the `"scripts"` block:
```json
"test": "vitest run",
"test:watch": "vitest"
```

- [ ] **Step 6: Verify scaffold runs**

```bash
npm run dev
```
Expected: Server starts at `http://localhost:3000` with default Next.js page. Stop with Ctrl+C.

- [ ] **Step 7: Commit**

```bash
cd ..
git add simulator/
git commit -m "feat: scaffold Next.js simulator app with Vitest"
```

---

## Task 2: Types and Database Layer

**Files:**
- Create: `simulator/lib/types.ts`
- Create: `simulator/lib/db.ts`

- [ ] **Step 1: Create shared types**

Create `simulator/lib/types.ts`:
```typescript
export interface PeriodDefault {
  name: string
  default_minutes: number
  pl_team_baseline: number
  pl_per_min_baseline: number
}

export interface Practice {
  id: number
  season: string
  practice_num: number
  practice_date: string        // ISO date string e.g. "2026-03-24"
  day_of_week: string
  dress: string
  tempo: string
  emphasis: string
  total_duration_min: number
  synced_at: string | null
}

export interface Period {
  id: number
  practice_id: number
  name: string
  order_index: number
  minutes: number
  pl_team_projected: number
  pl_team_actual: number | null
  pl_per_min_actual: number | null
}

export interface PracticeWithPeriods extends Practice {
  periods: Period[]
}

export interface SessionLoad {
  plTeam: number
  plPlayer: number
  totalMinutes: number
  classification: 'GREEN' | 'YELLOW' | 'RED'
  plPerMinSession: number
}

export interface ActivePeriod extends Period {
  active: boolean
  added: boolean            // true if added by coach in this session (not from DB)
}
```

- [ ] **Step 2: Create database connection**

Create `simulator/lib/db.ts`:
```typescript
import { neon } from '@neondatabase/serverless'

if (!process.env.DATABASE_URL) {
  throw new Error('DATABASE_URL environment variable is not set')
}

export const sql = neon(process.env.DATABASE_URL)
```

- [ ] **Step 3: Create the database schema in Neon**

Open the Neon console (neon.tech), create a new project named `baylor-load-sim`, then run this SQL in the Neon SQL editor:

```sql
CREATE TABLE IF NOT EXISTS period_defaults (
  name                 VARCHAR PRIMARY KEY,
  default_minutes      NUMERIC NOT NULL,
  pl_team_baseline     NUMERIC NOT NULL,
  pl_per_min_baseline  NUMERIC NOT NULL
);

CREATE TABLE IF NOT EXISTS practices (
  id                   SERIAL PRIMARY KEY,
  season               VARCHAR NOT NULL,
  practice_num         INTEGER NOT NULL,
  practice_date        DATE NOT NULL,
  day_of_week          VARCHAR NOT NULL,
  dress                VARCHAR NOT NULL,
  tempo                VARCHAR NOT NULL,
  emphasis             VARCHAR NOT NULL,
  total_duration_min   INTEGER NOT NULL,
  synced_at            TIMESTAMP
);

CREATE TABLE IF NOT EXISTS periods (
  id                   SERIAL PRIMARY KEY,
  practice_id          INTEGER NOT NULL REFERENCES practices(id) ON DELETE CASCADE,
  name                 VARCHAR NOT NULL,
  order_index          INTEGER NOT NULL,
  minutes              NUMERIC NOT NULL,
  pl_team_projected    NUMERIC NOT NULL,
  pl_team_actual       NUMERIC,
  pl_per_min_actual    NUMERIC
);

CREATE INDEX IF NOT EXISTS periods_practice_id_idx ON periods(practice_id);
```

Expected: All three tables created with no errors.

- [ ] **Step 4: Copy the DATABASE_URL**

In Neon console, go to Project Settings > Connection String. Copy the connection string. You will use this in Task 10 when setting Vercel env vars. For local dev, create `simulator/.env.local`:
```
DATABASE_URL=<paste your neon connection string here>
SITE_PASSWORD=bearsnation
COOKIE_SECRET=<generate a random 32-char string, e.g. openssl rand -hex 16>
```

Add `simulator/.env.local` to `.gitignore` if not already there.

- [ ] **Step 5: Commit**

```bash
git add simulator/lib/types.ts simulator/lib/db.ts
git commit -m "feat: add types and Neon database connection layer"
```

---

## Task 3: Authentication

**Files:**
- Create: `simulator/lib/auth.ts`
- Create: `simulator/middleware.ts`
- Create: `simulator/app/login/page.tsx`
- Create: `simulator/app/api/login/route.ts`

- [ ] **Step 1: Create auth helpers**

Create `simulator/lib/auth.ts`:
```typescript
import { SignJWT, jwtVerify } from 'jose'

const COOKIE_NAME = 'bls-session'
const secret = new TextEncoder().encode(
  process.env.COOKIE_SECRET ?? 'dev-secret-change-me'
)

export async function signSession(): Promise<string> {
  return new SignJWT({ authenticated: true })
    .setProtectedHeader({ alg: 'HS256' })
    .setExpirationTime('30d')
    .sign(secret)
}

export async function verifySession(token: string): Promise<boolean> {
  try {
    await jwtVerify(token, secret)
    return true
  } catch {
    return false
  }
}

export { COOKIE_NAME }
```

- [ ] **Step 2: Create the middleware**

Create `simulator/middleware.ts`:
```typescript
import { NextRequest, NextResponse } from 'next/server'
import { verifySession, COOKIE_NAME } from '@/lib/auth'

const PUBLIC_PATHS = ['/login', '/api/login']

export async function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl

  if (PUBLIC_PATHS.some(p => pathname.startsWith(p))) {
    return NextResponse.next()
  }

  const token = req.cookies.get(COOKIE_NAME)?.value
  if (token && await verifySession(token)) {
    return NextResponse.next()
  }

  const loginUrl = new URL('/login', req.url)
  loginUrl.searchParams.set('from', pathname)
  return NextResponse.redirect(loginUrl)
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
```

- [ ] **Step 3: Create the login API route**

Create `simulator/app/api/login/route.ts`:
```typescript
import { NextRequest, NextResponse } from 'next/server'
import { signSession, COOKIE_NAME } from '@/lib/auth'

export async function POST(req: NextRequest) {
  const { password } = await req.json()

  if (password !== process.env.SITE_PASSWORD) {
    return NextResponse.json({ error: 'Invalid password' }, { status: 401 })
  }

  const token = await signSession()
  const response = NextResponse.json({ ok: true })
  response.cookies.set(COOKIE_NAME, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 60 * 60 * 24 * 30, // 30 days
    path: '/',
  })
  return response
}
```

- [ ] **Step 4: Create the login page**

Create `simulator/app/login/page.tsx`:
```typescript
'use client'

import { useState, FormEvent } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import styles from './login.module.css'

export default function LoginPage() {
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()
  const searchParams = useSearchParams()

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError('')

    const res = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password }),
    })

    if (res.ok) {
      const from = searchParams.get('from') ?? '/simulator'
      router.push(from)
    } else {
      setError('Incorrect password')
      setLoading(false)
    }
  }

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <div className={styles.header}>
          <h1>Baylor Football</h1>
          <p>Practice Load Simulator</p>
        </div>
        <form onSubmit={handleSubmit} className={styles.form}>
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            placeholder="Enter password"
            className={styles.input}
            autoFocus
          />
          {error && <p className={styles.error}>{error}</p>}
          <button type="submit" disabled={loading} className={styles.btn}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  )
}
```

- [ ] **Step 5: Create login CSS module**

Create `simulator/app/login/login.module.css`:
```css
.container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
}
.card {
  background: #fff;
  border-radius: 10px;
  padding: 40px;
  width: 320px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}
.header {
  text-align: center;
  margin-bottom: 28px;
}
.header h1 {
  font-size: 20px;
  font-weight: 800;
  color: #154734;
}
.header p {
  font-size: 13px;
  color: #757575;
  margin-top: 4px;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
}
.input:focus {
  outline: none;
  border-color: #154734;
}
.btn {
  background: #154734;
  color: #fff;
  border: none;
  padding: 10px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.error {
  font-size: 12px;
  color: #c62828;
  text-align: center;
}
```

- [ ] **Step 6: Verify auth flow**

```bash
npm run dev
```
Navigate to `http://localhost:3000/simulator`. Expected: Redirected to `/login`. Enter the password from `.env.local`. Expected: Redirected to `/simulator` (which will 404 for now — that's fine). Stop server.

- [ ] **Step 7: Commit**

```bash
git add simulator/lib/auth.ts simulator/middleware.ts simulator/app/login/ simulator/app/api/login/
git commit -m "feat: add password gate middleware and login page"
```

---

## Task 4: Core Calculation Libraries

**Files:**
- Create: `simulator/lib/periodMap.ts`
- Create: `simulator/lib/loadCalc.ts`
- Create: `simulator/tests/periodMap.test.ts`
- Create: `simulator/tests/loadCalc.test.ts`

- [ ] **Step 1: Write failing tests for periodMap**

Create `simulator/tests/periodMap.test.ts`:
```typescript
import { describe, it, expect } from 'vitest'
import { canonicalize } from '@/lib/periodMap'

describe('canonicalize', () => {
  it('maps INDY 1 to INDIVIDUAL', () => {
    expect(canonicalize('INDY 1')).toBe('INDIVIDUAL')
  })
  it('maps INDY 2 to INDIVIDUAL', () => {
    expect(canonicalize('INDY 2')).toBe('INDIVIDUAL')
  })
  it('maps SPT 1 to SPECIAL TEAMS', () => {
    expect(canonicalize('SPT 1')).toBe('SPECIAL TEAMS')
  })
  it('maps SPT 2 to SPECIAL TEAMS', () => {
    expect(canonicalize('SPT 2')).toBe('SPECIAL TEAMS')
  })
  it('maps TEAM 1 to TEAM', () => {
    expect(canonicalize('TEAM 1')).toBe('TEAM')
  })
  it('maps TEAM 3 to TEAM', () => {
    expect(canonicalize('TEAM 3')).toBe('TEAM')
  })
  it('maps PERF SPRINTS to PERFECT SPRINTS', () => {
    expect(canonicalize('PERF SPRINTS')).toBe('PERFECT SPRINTS')
  })
  it('maps RZ LOCKOUT to REDZONE LOCKOUT', () => {
    expect(canonicalize('RZ LOCKOUT')).toBe('REDZONE LOCKOUT')
  })
  it('returns exact name when no mapping exists', () => {
    expect(canonicalize('TEAM TEMPO')).toBe('TEAM TEMPO')
  })
  it('is case-insensitive', () => {
    expect(canonicalize('indy 1')).toBe('INDIVIDUAL')
  })
})
```

- [ ] **Step 2: Run to verify it fails**

```bash
npx vitest run tests/periodMap.test.ts
```
Expected: FAIL — "Cannot find module '@/lib/periodMap'"

- [ ] **Step 3: Implement periodMap**

Create `simulator/lib/periodMap.ts`:
```typescript
// Maps Catapult raw period names to canonical simulator names.
// Add entries as new Catapult name variants are discovered during sync.
const PERIOD_MAP: Record<string, string> = {
  'INDY 1': 'INDIVIDUAL',
  'INDY 2': 'INDIVIDUAL',
  'SPT 1': 'SPECIAL TEAMS',
  'SPT 2': 'SPECIAL TEAMS',
  'SPT 3': 'SPECIAL TEAMS',
  'SPT 4': 'SPECIAL TEAMS',
  'TEAM 1': 'TEAM',
  'TEAM 2': 'TEAM',
  'TEAM 3': 'TEAM',
  'TEAM 4': 'TEAM',
  'PERF SPRINTS': 'PERFECT SPRINTS',
  'RZ LOCKOUT': 'REDZONE LOCKOUT',
}

export function canonicalize(rawName: string): string {
  const upper = rawName.trim().toUpperCase()
  return PERIOD_MAP[upper] ?? upper
}
```

- [ ] **Step 4: Run to verify it passes**

```bash
npx vitest run tests/periodMap.test.ts
```
Expected: All 10 tests PASS.

- [ ] **Step 5: Write failing tests for loadCalc**

Create `simulator/tests/loadCalc.test.ts`:
```typescript
import { describe, it, expect } from 'vitest'
import {
  computePlPerMin,
  computePeriodPlTeam,
  computePeriodPlPlayer,
  computeSessionLoad,
  classify,
  generateSwaps,
} from '@/lib/loadCalc'
import type { ActivePeriod } from '@/lib/types'

const RATIO = 0.09772

describe('computePlPerMin', () => {
  it('divides baseline by default minutes', () => {
    expect(computePlPerMin(432, 10)).toBeCloseTo(43.2)
  })
})

describe('computePeriodPlTeam', () => {
  it('scales load by minutes and tempo', () => {
    const plPerMin = 43.2
    expect(computePeriodPlTeam(plPerMin, 10, 1.0)).toBeCloseTo(432)
    expect(computePeriodPlTeam(plPerMin, 20, 1.0)).toBeCloseTo(864)
    expect(computePeriodPlTeam(plPerMin, 10, 0.85)).toBeCloseTo(367.2)
  })
})

describe('computePeriodPlPlayer', () => {
  it('multiplies by 0.09772', () => {
    expect(computePeriodPlPlayer(432)).toBeCloseTo(432 * RATIO)
  })
})

describe('classify', () => {
  it('classifies GREEN at or below 420', () => {
    expect(classify(420)).toBe('GREEN')
    expect(classify(100)).toBe('GREEN')
  })
  it('classifies YELLOW between 421 and 470', () => {
    expect(classify(421)).toBe('YELLOW')
    expect(classify(470)).toBe('YELLOW')
  })
  it('classifies RED above 470', () => {
    expect(classify(471)).toBe('RED')
    expect(classify(600)).toBe('RED')
  })
})

describe('computeSessionLoad', () => {
  const makePeriod = (name: string, minutes: number, plBaseline: number, active = true): ActivePeriod => ({
    id: 1,
    practice_id: 1,
    name,
    order_index: 0,
    minutes,
    pl_team_projected: plBaseline,
    pl_team_actual: null,
    pl_per_min_actual: null,
    active,
    added: false,
  })

  it('sums active periods and applies tempo', () => {
    const periods = [
      makePeriod('TEAM', 10, 432),       // pl_per_min = 43.2, plTeam = 432 * 1.0
      makePeriod('INDIVIDUAL', 15, 364), // pl_per_min = 36.4, plTeam = 546 * 1.0
    ]
    const result = computeSessionLoad(periods, 'THUD', 10)
    expect(result.plTeam).toBe(Math.round(432 + 546))
    expect(result.plPlayer).toBe(Math.round(978 * RATIO))
    expect(result.totalMinutes).toBe(25)
    expect(result.classification).toBeDefined()
  })

  it('skips inactive periods', () => {
    const periods = [
      makePeriod('TEAM', 10, 432, true),
      makePeriod('INDIVIDUAL', 15, 364, false),
    ]
    const result = computeSessionLoad(periods, 'THUD', 10)
    expect(result.plTeam).toBe(Math.round(432))
    expect(result.totalMinutes).toBe(10)
  })

  it('uses pl_per_min_actual when available', () => {
    const period: ActivePeriod = {
      id: 1, practice_id: 1, name: 'TEAM', order_index: 0,
      minutes: 10, pl_team_projected: 432,
      pl_team_actual: 450, pl_per_min_actual: 45,
      active: true, added: false,
    }
    const result = computeSessionLoad([period], 'THUD', 10)
    // Should use pl_per_min_actual=45, not baseline 43.2
    expect(result.plTeam).toBe(Math.round(45 * 10 * 1.0))
  })
})

describe('generateSwaps', () => {
  it('returns an array', () => {
    const result = generateSwaps([], 400, 'GREEN', 1.0)
    expect(Array.isArray(result)).toBe(true)
  })
})
```

- [ ] **Step 6: Run to verify it fails**

```bash
npx vitest run tests/loadCalc.test.ts
```
Expected: FAIL — "Cannot find module '@/lib/loadCalc'"

- [ ] **Step 7: Implement loadCalc**

Create `simulator/lib/loadCalc.ts`:
```typescript
import type { ActivePeriod, SessionLoad } from '@/lib/types'

export const RATIO = 0.09772

export const TEMPO_MULT: Record<string, number> = {
  TAG: 0.85,
  THUD: 1.0,
  'THUD/LIVE': 1.15,
  LIVE: 1.25,
}

// Period baseline load constants (team-level, from 2026 GPS actuals where n>=3)
export const PERIOD_DEFAULTS: Record<string, { plTeam: number; defaultMinutes: number }> = {
  'RUN THRU':         { plTeam: 555, defaultMinutes: 10 },
  'REDZONE LOCKOUT':  { plTeam: 534, defaultMinutes: 10 },
  'PERFECT SPRINTS':  { plTeam: 491, defaultMinutes:  5 },
  'TEAM':             { plTeam: 432, defaultMinutes: 12 },
  '7 ON 7':           { plTeam: 368, defaultMinutes: 10 },
  'FAST BREAK':       { plTeam: 357, defaultMinutes: 10 },
  'INDIVIDUAL':       { plTeam: 364, defaultMinutes: 15 },
  'TEAM RUN PAP':     { plTeam: 297, defaultMinutes:  8 },
  'UNIT TEACH':       { plTeam: 293, defaultMinutes:  8 },
  'STRETCH':          { plTeam: 274, defaultMinutes: 10 },
  'TEAM TEMPO':       { plTeam: 235, defaultMinutes: 10 },
  'SPECIAL TEAMS':    { plTeam: 226, defaultMinutes: 10 },
  'BLITZ':            { plTeam: 221, defaultMinutes:  8 },
  'POST PRACTICE':    { plTeam: 181, defaultMinutes: 10 },
  '1 ON 1':           { plTeam: 160, defaultMinutes:  8 },
  '9 ON 7':           { plTeam: 160, defaultMinutes:  8 },
  'PERIMETER':        { plTeam: 136, defaultMinutes:  8 },
  'WINNING EDGE':     { plTeam: 112, defaultMinutes:  5 },
  'SPT RUN THRU':     { plTeam: 108, defaultMinutes:  8 },
  'TEAM COMP':        { plTeam:  98, defaultMinutes:  8 },
}

export const THRESH_GREEN = 420
export const THRESH_YELLOW = 470

export function computePlPerMin(plTeamBaseline: number, defaultMinutes: number): number {
  return plTeamBaseline / defaultMinutes
}

export function computePeriodPlTeam(
  plPerMin: number,
  actualMinutes: number,
  tempoMult: number
): number {
  return plPerMin * actualMinutes * tempoMult
}

export function computePeriodPlPlayer(periodPlTeam: number): number {
  return periodPlTeam * RATIO
}

export function classify(ppLoad: number): 'GREEN' | 'YELLOW' | 'RED' {
  if (ppLoad <= THRESH_GREEN) return 'GREEN'
  if (ppLoad <= THRESH_YELLOW) return 'YELLOW'
  return 'RED'
}

export function computeSessionLoad(
  periods: ActivePeriod[],
  tempo: string,
  _playerCount = 75  // reserved for future per-player breakdown
): SessionLoad {
  const mult = TEMPO_MULT[tempo] ?? 1.0
  let totalPlTeam = 0
  let totalMinutes = 0

  for (const p of periods) {
    if (!p.active) continue
    const defaults = PERIOD_DEFAULTS[p.name]
    const defaultMins = defaults?.defaultMinutes ?? 10
    const plPerMin = p.pl_per_min_actual != null
      ? p.pl_per_min_actual
      : computePlPerMin(p.pl_team_projected, defaultMins)
    totalPlTeam += computePeriodPlTeam(plPerMin, p.minutes, mult)
    totalMinutes += p.minutes
  }

  const plPlayer = Math.round(totalPlTeam * RATIO)
  return {
    plTeam: Math.round(totalPlTeam),
    plPlayer,
    totalMinutes,
    classification: classify(plPlayer),
    plPerMinSession: totalMinutes > 0 ? Math.round((plPlayer / totalMinutes) * 10) / 10 : 0,
  }
}

export interface SwapSuggestion {
  out: string        // period name to remove (or '(add new)')
  inn: string        // period name to add (or '(remove)')
  delta: number      // PL/player change
  newPP: number
  newClass: 'GREEN' | 'YELLOW' | 'RED'
}

const LIGHT_OPTIONS = ['WINNING EDGE', 'TEAM COMP', 'PERIMETER', 'SPT RUN THRU', '1 ON 1']
const HEAVY_OPTIONS = ['TEAM', 'REDZONE LOCKOUT', 'BLITZ', 'TEAM RUN PAP', '7 ON 7']

export function generateSwaps(
  periods: ActivePeriod[],
  currentPP: number,
  currentClass: 'GREEN' | 'YELLOW' | 'RED',
  tempoMult: number
): SwapSuggestion[] {
  const suggestions: SwapSuggestion[] = []
  const active = periods.filter(p => p.active)

  if (currentClass === 'RED' || currentClass === 'YELLOW') {
    const heavy = [...active]
      .sort((a, b) => (b.pl_team_projected ?? 0) - (a.pl_team_projected ?? 0))
      .filter(p => (p.pl_team_projected ?? 0) >= 300)
      .slice(0, 3)

    for (const hp of heavy) {
      for (const lp of LIGHT_OPTIONS) {
        const dTeam = Math.round(((PERIOD_DEFAULTS[lp]?.plTeam ?? 0) - hp.pl_team_projected) * tempoMult)
        const dPP = Math.round(dTeam * RATIO)
        const newPP = currentPP + dPP
        const newClass = classify(newPP)
        if (newClass !== currentClass && dPP < 0) {
          suggestions.push({ out: hp.name, inn: lp, delta: dPP, newPP, newClass })
        }
      }
    }

    for (const hp of [...active].sort((a, b) => b.pl_team_projected - a.pl_team_projected).slice(0, 2)) {
      const dTeam = -Math.round(hp.pl_team_projected * tempoMult)
      const dPP = Math.round(dTeam * RATIO)
      const newPP = currentPP + dPP
      const newClass = classify(newPP)
      if (newClass !== currentClass) {
        suggestions.push({ out: hp.name, inn: '(remove)', delta: dPP, newPP, newClass })
      }
    }
  } else {
    const light = active.filter(p => (p.pl_team_projected ?? 0) < 250).slice(0, 3)

    for (const lp of light) {
      for (const hp of HEAVY_OPTIONS) {
        const dTeam = Math.round(((PERIOD_DEFAULTS[hp]?.plTeam ?? 0) - lp.pl_team_projected) * tempoMult)
        const dPP = Math.round(dTeam * RATIO)
        const newPP = currentPP + dPP
        const newClass = classify(newPP)
        if (newClass !== currentClass && dPP > 0) {
          suggestions.push({ out: lp.name, inn: hp, delta: dPP, newPP, newClass })
        }
      }
    }

    for (const hp of HEAVY_OPTIONS) {
      const dTeam = Math.round((PERIOD_DEFAULTS[hp]?.plTeam ?? 0) * tempoMult)
      const dPP = Math.round(dTeam * RATIO)
      const newPP = currentPP + dPP
      const newClass = classify(newPP)
      if (newClass !== currentClass) {
        suggestions.push({ out: '(add new)', inn: hp, delta: dPP, newPP, newClass })
      }
    }
  }

  const seen = new Set<string>()
  return suggestions
    .filter(s => { const k = `${s.out}>${s.inn}`; if (seen.has(k)) return false; seen.add(k); return true })
    .sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta))
    .slice(0, 5)
}
```

- [ ] **Step 8: Run to verify tests pass**

```bash
npx vitest run tests/loadCalc.test.ts tests/periodMap.test.ts
```
Expected: All tests PASS.

- [ ] **Step 9: Commit**

```bash
git add simulator/lib/periodMap.ts simulator/lib/loadCalc.ts simulator/tests/
git commit -m "feat: add period map and load calculation libraries with tests"
```

---

## Task 5: Practice API Routes

**Files:**
- Create: `simulator/app/api/practices/route.ts`
- Create: `simulator/app/api/practices/[id]/route.ts`

- [ ] **Step 1: Create GET /api/practices**

Create `simulator/app/api/practices/route.ts`:
```typescript
import { NextResponse } from 'next/server'
import { sql } from '@/lib/db'
import type { Practice } from '@/lib/types'

export async function GET() {
  try {
    const rows = await sql`
      SELECT * FROM practices
      ORDER BY practice_num ASC
    ` as Practice[]
    return NextResponse.json(rows)
  } catch (err) {
    console.error('GET /api/practices failed:', err)
    return NextResponse.json({ error: 'Database error' }, { status: 500 })
  }
}
```

- [ ] **Step 2: Create GET /api/practices/[id]**

Create `simulator/app/api/practices/[id]/route.ts`:
```typescript
import { NextRequest, NextResponse } from 'next/server'
import { sql } from '@/lib/db'
import type { Practice, Period, PracticeWithPeriods } from '@/lib/types'

export async function GET(
  _req: NextRequest,
  { params }: { params: { id: string } }
) {
  const id = parseInt(params.id, 10)
  if (isNaN(id)) {
    return NextResponse.json({ error: 'Invalid id' }, { status: 400 })
  }

  try {
    const [practice] = await sql`
      SELECT * FROM practices WHERE id = ${id}
    ` as Practice[]

    if (!practice) {
      return NextResponse.json({ error: 'Not found' }, { status: 404 })
    }

    const periods = await sql`
      SELECT * FROM periods
      WHERE practice_id = ${id}
      ORDER BY order_index ASC
    ` as Period[]

    const result: PracticeWithPeriods = { ...practice, periods }
    return NextResponse.json(result)
  } catch (err) {
    console.error(`GET /api/practices/${id} failed:`, err)
    return NextResponse.json({ error: 'Database error' }, { status: 500 })
  }
}
```

- [ ] **Step 3: Verify routes respond (requires seed data — run after Task 7)**

This step is deferred to after Task 7. Mark it complete after seeding.

- [ ] **Step 4: Commit**

```bash
git add simulator/app/api/practices/
git commit -m "feat: add GET /api/practices and /api/practices/[id] routes"
```

---

## Task 6: Period Update Route

**Files:**
- Create: `simulator/app/api/practices/[id]/periods/[pid]/route.ts`

- [ ] **Step 1: Create PATCH route**

Create `simulator/app/api/practices/[id]/periods/[pid]/route.ts`:
```typescript
import { NextRequest, NextResponse } from 'next/server'
import { sql } from '@/lib/db'

export async function PATCH(
  req: NextRequest,
  { params }: { params: { id: string; pid: string } }
) {
  const practiceId = parseInt(params.id, 10)
  const periodId = parseInt(params.pid, 10)

  if (isNaN(practiceId) || isNaN(periodId)) {
    return NextResponse.json({ error: 'Invalid id' }, { status: 400 })
  }

  const body = await req.json()
  const minutes = Number(body.minutes)

  if (!Number.isFinite(minutes) || minutes <= 0 || minutes > 120) {
    return NextResponse.json({ error: 'minutes must be a positive number <= 120' }, { status: 400 })
  }

  try {
    const rows = await sql`
      UPDATE periods
      SET minutes = ${minutes}
      WHERE id = ${periodId} AND practice_id = ${practiceId}
      RETURNING id, minutes
    `
    if (rows.length === 0) {
      return NextResponse.json({ error: 'Not found' }, { status: 404 })
    }
    return NextResponse.json(rows[0])
  } catch (err) {
    console.error('PATCH period failed:', err)
    return NextResponse.json({ error: 'Database error' }, { status: 500 })
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add simulator/app/api/practices/
git commit -m "feat: add PATCH /api/practices/[id]/periods/[pid] for minute updates"
```

---

## Task 7: Seed Script

**Files:**
- Create: `simulator/scripts/seed.ts`

- [ ] **Step 1: Create the seed script**

Create `simulator/scripts/seed.ts`:
```typescript
import { neon } from '@neondatabase/serverless'
import * as dotenv from 'dotenv'
import { resolve } from 'path'

dotenv.config({ path: resolve(__dirname, '../.env.local') })

const sql = neon(process.env.DATABASE_URL!)

// Period defaults: name, default_minutes, pl_team_baseline
const PERIOD_DEFAULTS = [
  ['RUN THRU',        10, 555],
  ['REDZONE LOCKOUT', 10, 534],
  ['PERFECT SPRINTS',  5, 491],
  ['TEAM',            12, 432],
  ['7 ON 7',          10, 368],
  ['FAST BREAK',      10, 357],
  ['INDIVIDUAL',      15, 364],
  ['TEAM RUN PAP',     8, 297],
  ['UNIT TEACH',       8, 293],
  ['STRETCH',         10, 274],
  ['TEAM TEMPO',      10, 235],
  ['SPECIAL TEAMS',   10, 226],
  ['BLITZ',            8, 221],
  ['POST PRACTICE',   10, 181],
  ['1 ON 1',           8, 160],
  ['9 ON 7',           8, 160],
  ['PERIMETER',        8, 136],
  ['WINNING EDGE',     5, 112],
  ['SPT RUN THRU',     8, 108],
  ['TEAM COMP',        8,  98],
]

// 2026 Spring practices with period compositions
// Duration and period minutes derived from practice face Excel
const PRACTICES = [
  {
    num: 1,  date: '2026-03-24', day: 'Tue', dress: 'Helmets',    tempo: 'TAG',       emphasis: 'NDD - New & 10',                    duration: 128,
    periods: [
      ['RUN THRU',10],['SPT RUN THRU',8],['STRETCH',10],['TEAM TEMPO',10],['SPECIAL TEAMS',10],['INDIVIDUAL',15],
      ['UNIT TEACH',8],['1 ON 1',8],['7 ON 7',10],['TEAM',12],['SPECIAL TEAMS',10],['TEAM',12]
    ]
  },
  {
    num: 2,  date: '2026-03-26', day: 'Thu', dress: 'Helmets',    tempo: 'TAG',       emphasis: 'NDD - 2nd Short/Med',               duration: 127,
    periods: [
      ['RUN THRU',10],['SPT RUN THRU',8],['STRETCH',10],['TEAM TEMPO',10],['SPECIAL TEAMS',10],['INDIVIDUAL',15],
      ['UNIT TEACH',8],['TEAM',12],['7 ON 7',10],['TEAM',12],['SPECIAL TEAMS',10],['TEAM',12]
    ]
  },
  {
    num: 3,  date: '2026-03-28', day: 'Sat', dress: 'Shells',     tempo: 'THUD',      emphasis: 'NDD - 2nd Long/XL',                 duration: 139,
    periods: [
      ['RUN THRU',10],['SPT RUN THRU',8],['STRETCH',10],['TEAM TEMPO',10],['SPECIAL TEAMS',10],['INDIVIDUAL',15],
      ['WINNING EDGE',5],['UNIT TEACH',8],['PERIMETER',8],['9 ON 7',8],['7 ON 7',10],['TEAM',12],['TEAM',12],['SPECIAL TEAMS',10],['TEAM',12]
    ]
  },
  {
    num: 4,  date: '2026-03-30', day: 'Mon', dress: 'Full Pads',  tempo: 'THUD',      emphasis: 'RZ / SY',                           duration: 142,
    periods: [
      ['RUN THRU',10],['SPT RUN THRU',8],['STRETCH',10],['TEAM TEMPO',10],['SPECIAL TEAMS',10],['INDIVIDUAL',15],
      ['UNIT TEACH',8],['TEAM COMP',8],['TEAM RUN PAP',8],['7 ON 7',10],['TEAM',12],['TEAM',12],['SPECIAL TEAMS',10],['TEAM',12]
    ]
  },
  {
    num: 5,  date: '2026-03-31', day: 'Tue', dress: 'Shells',     tempo: 'THUD',      emphasis: 'Tite Red Zone',                     duration: 136,
    periods: [
      ['RUN THRU',10],['SPT RUN THRU',8],['STRETCH',10],['TEAM TEMPO',10],['SPECIAL TEAMS',10],['INDIVIDUAL',15],
      ['UNIT TEACH',8],['TEAM',12],['9 ON 7',8],['7 ON 7',10],['TEAM',12],['TEAM',12],['SPECIAL TEAMS',10],['REDZONE LOCKOUT',10]
    ]
  },
  {
    num: 6,  date: '2026-04-02', day: 'Thu', dress: 'Full Pads',  tempo: 'THUD/LIVE', emphasis: '3rd Down / RZ Scrimmage',           duration: 167,
    periods: [
      ['RUN THRU',10],['SPT RUN THRU',8],['STRETCH',10],['SPECIAL TEAMS',10],['INDIVIDUAL',15],['SPECIAL TEAMS',10],
      ['TEAM',12],['SPECIAL TEAMS',10],['TEAM',12],['SPECIAL TEAMS',10],['TEAM',12],['TEAM',12]
    ]
  },
  {
    num: 7,  date: '2026-04-07', day: 'Tue', dress: 'Shells',     tempo: 'THUD',      emphasis: '2 Minute',                          duration: 132,
    periods: [
      ['RUN THRU',10],['SPT RUN THRU',8],['STRETCH',10],['TEAM TEMPO',10],['SPECIAL TEAMS',10],['INDIVIDUAL',15],
      ['WINNING EDGE',5],['UNIT TEACH',8],['7 ON 7',10],['TEAM',12],['TEAM',12],['SPECIAL TEAMS',10],['TEAM',12]
    ]
  },
  {
    num: 8,  date: '2026-04-09', day: 'Thu', dress: 'Shells',     tempo: 'TAG',       emphasis: 'Coming Out',                        duration: 129,
    periods: [
      ['RUN THRU',10],['SPT RUN THRU',8],['STRETCH',10],['TEAM TEMPO',10],['SPECIAL TEAMS',10],['INDIVIDUAL',15],
      ['UNIT TEACH',8],['7 ON 7',10],['TEAM',12],['TEAM COMP',8],['TEAM',12],['SPECIAL TEAMS',10],['TEAM',12]
    ]
  },
  {
    num: 9,  date: '2026-04-11', day: 'Sat', dress: 'Full Pads',  tempo: 'THUD/LIVE', emphasis: 'Goal Line',                         duration: 136,
    periods: [
      ['RUN THRU',10],['SPT RUN THRU',8],['STRETCH',10],['SPECIAL TEAMS',10],['INDIVIDUAL',15],
      ['UNIT TEACH',8],['7 ON 7',10],['BLITZ',8],['TEAM',12],['SPECIAL TEAMS',10],['TEAM',12]
    ]
  },
  {
    num: 10, date: '2026-04-14', day: 'Tue', dress: 'Shells',     tempo: 'THUD',      emphasis: 'Short Yardage',                     duration: 143,
    periods: [
      ['RUN THRU',10],['SPT RUN THRU',8],['STRETCH',10],['TEAM TEMPO',10],['SPECIAL TEAMS',10],['INDIVIDUAL',15],
      ['WINNING EDGE',5],['UNIT TEACH',8],['PERIMETER',8],['9 ON 7',8],['7 ON 7',10],['TEAM',12],['TEAM',12],['SPECIAL TEAMS',10],['TEAM',12]
    ]
  },
  {
    num: 11, date: '2026-04-16', day: 'Thu', dress: 'Shells',     tempo: 'THUD',      emphasis: 'Red Zone Lock Out',                 duration: 130,
    periods: [
      ['RUN THRU',10],['SPT RUN THRU',8],['STRETCH',10],['TEAM TEMPO',10],['SPECIAL TEAMS',10],['INDIVIDUAL',15],
      ['UNIT TEACH',8],['7 ON 7',10],['TEAM',12],['TEAM',12],['SPECIAL TEAMS',10],['REDZONE LOCKOUT',10]
    ]
  },
  {
    num: 12, date: '2026-04-18', day: 'Sat', dress: 'Full Pads',  tempo: 'LIVE',      emphasis: 'GL / RZ / 2 Min Scrimmage',         duration: 166,
    periods: [
      ['RUN THRU',10],['SPT RUN THRU',8],['STRETCH',10],['SPECIAL TEAMS',10],['INDIVIDUAL',15],['SPECIAL TEAMS',10],
      ['TEAM',12],['SPECIAL TEAMS',10],['TEAM',12],['SPECIAL TEAMS',10],['TEAM',12],['TEAM',12]
    ]
  },
  {
    num: 13, date: '2026-04-21', day: 'Tue', dress: 'Helmets',    tempo: 'TAG',       emphasis: 'Call It',                           duration: 134,
    periods: [
      ['RUN THRU',10],['SPT RUN THRU',8],['STRETCH',10],['TEAM TEMPO',10],['SPECIAL TEAMS',10],['INDIVIDUAL',15],
      ['WINNING EDGE',5],['UNIT TEACH',8],['7 ON 7',10],['TEAM',12],['TEAM',12],['SPECIAL TEAMS',10],['TEAM',12]
    ]
  },
  {
    num: 14, date: '2026-04-23', day: 'Thu', dress: 'Full Pads',  tempo: 'THUD/LIVE', emphasis: 'Situation Review / Scrimmage',      duration: 120,
    periods: [
      ['RUN THRU',10],['SPT RUN THRU',8],['STRETCH',10],['TEAM TEMPO',10],['SPECIAL TEAMS',10],['INDIVIDUAL',15],
      ['UNIT TEACH',8],['TEAM COMP',8],['1 ON 1',8],['7 ON 7',10],['BLITZ',8],['TEAM',12],['SPECIAL TEAMS',10],['TEAM',12]
    ]
  },
  {
    num: 15, date: '2026-04-25', day: 'Sat', dress: 'Full Pads',  tempo: 'THUD',      emphasis: 'Spring Game',                       duration: 188,
    periods: [
      ['STRETCH',10],['INDIVIDUAL',15],['1 ON 1',8],['TEAM COMP',8],['SPECIAL TEAMS',10],['PERIMETER',8],
      ['7 ON 7',10],['9 ON 7',8],['SPECIAL TEAMS',10],['TEAM COMP',8]
    ]
  },
]

async function seed() {
  console.log('Seeding period_defaults...')
  for (const [name, defaultMinutes, plTeamBaseline] of PERIOD_DEFAULTS) {
    const plPerMin = (plTeamBaseline as number) / (defaultMinutes as number)
    await sql`
      INSERT INTO period_defaults (name, default_minutes, pl_team_baseline, pl_per_min_baseline)
      VALUES (${name as string}, ${defaultMinutes as number}, ${plTeamBaseline as number}, ${plPerMin})
      ON CONFLICT (name) DO UPDATE SET
        default_minutes     = EXCLUDED.default_minutes,
        pl_team_baseline    = EXCLUDED.pl_team_baseline,
        pl_per_min_baseline = EXCLUDED.pl_per_min_baseline
    `
  }
  console.log(`  Inserted ${PERIOD_DEFAULTS.length} period defaults`)

  console.log('Seeding practices and periods...')
  for (const p of PRACTICES) {
    const [practice] = await sql`
      INSERT INTO practices (season, practice_num, practice_date, day_of_week, dress, tempo, emphasis, total_duration_min)
      VALUES ('2026 Spring', ${p.num}, ${p.date}, ${p.day}, ${p.dress}, ${p.tempo}, ${p.emphasis}, ${p.duration})
      ON CONFLICT DO NOTHING
      RETURNING id
    `
    if (!practice) {
      console.log(`  Skipped P${p.num} (already exists)`)
      continue
    }
    const practiceId = practice.id

    for (let i = 0; i < p.periods.length; i++) {
      const [name, minutes] = p.periods[i] as [string, number]
      const defaults = PERIOD_DEFAULTS.find(d => d[0] === name)
      const plTeamBaseline = defaults ? defaults[2] as number : 300
      await sql`
        INSERT INTO periods (practice_id, name, order_index, minutes, pl_team_projected)
        VALUES (${practiceId}, ${name}, ${i}, ${minutes}, ${plTeamBaseline})
      `
    }
    console.log(`  Seeded P${p.num} with ${p.periods.length} periods`)
  }

  console.log('Seed complete.')
}

seed().catch(err => { console.error(err); process.exit(1) })
```

- [ ] **Step 2: Install ts-node for running the script**

```bash
npm install --save-dev ts-node
```

- [ ] **Step 3: Run the seed script**

```bash
npx ts-node --project tsconfig.json scripts/seed.ts
```
Expected output:
```
Seeding period_defaults...
  Inserted 20 period defaults
Seeding practices and periods...
  Seeded P1 with 12 periods
  ...
  Seeded P15 with 10 periods
Seed complete.
```

- [ ] **Step 4: Verify in Neon console**

In Neon SQL editor, run:
```sql
SELECT COUNT(*) FROM practices;   -- expected: 15
SELECT COUNT(*) FROM periods;     -- expected: ~190
SELECT COUNT(*) FROM period_defaults; -- expected: 20
```

- [ ] **Step 5: Commit**

```bash
git add simulator/scripts/seed.ts
git commit -m "feat: add seed script for 2026 Spring practice data"
```

---

## Task 8: Catapult API Client

**Files:**
- Create: `simulator/lib/catapult.ts`
- Create: `simulator/tests/catapult.test.ts`

- [ ] **Step 1: Write failing tests**

Create `simulator/tests/catapult.test.ts`:
```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { CatapultClient } from '@/lib/catapult'

// Mock global fetch
const mockFetch = vi.fn()
vi.stubGlobal('fetch', mockFetch)

describe('CatapultClient', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    process.env.CATAPULT_TOKEN = 'test-token'
  })

  it('throws if CATAPULT_TOKEN is not set', () => {
    delete process.env.CATAPULT_TOKEN
    expect(() => new CatapultClient()).toThrow('CATAPULT_TOKEN')
  })

  it('listActivities sends GET with date range', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => [{ id: 'abc', name: 'SP26 - P1 - 03.24.26' }],
    })
    const client = new CatapultClient()
    const result = await client.listActivities('2026-03-24T00:00:00', '2026-03-24T23:59:59')
    expect(result).toHaveLength(1)
    expect(result[0].id).toBe('abc')
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/activities'),
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: 'Bearer test-token' }),
      })
    )
  })

  it('getPeriodStats sends POST with group_by period', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => [{ period_name: 'TEAM 1', average_player_load: 42.5 }],
    })
    const client = new CatapultClient()
    const result = await client.getPeriodStats('activity-uuid')
    expect(result).toHaveLength(1)
    expect(result[0].period_name).toBe('TEAM 1')
    const body = JSON.parse((mockFetch.mock.calls[0][1] as RequestInit).body as string)
    expect(body.group_by).toContain('period')
  })

  it('throws CatapultAPIError on non-200 response', async () => {
    mockFetch.mockResolvedValueOnce({ ok: false, status: 401, text: async () => 'Unauthorized' })
    const client = new CatapultClient()
    await expect(client.listActivities('2026-01-01', '2026-01-02')).rejects.toThrow('401')
  })
})
```

- [ ] **Step 2: Run to verify it fails**

```bash
npx vitest run tests/catapult.test.ts
```
Expected: FAIL — "Cannot find module '@/lib/catapult'"

- [ ] **Step 3: Implement the Catapult client**

Create `simulator/lib/catapult.ts`:
```typescript
const BASE_URL = 'https://connect-us.catapultsports.com/api/v6'

export class CatapultAPIError extends Error {
  constructor(public statusCode: number, message: string) {
    super(`Catapult API error ${statusCode}: ${message}`)
  }
}

export interface CatapultActivity {
  id: string
  name: string
  start_time: number
  end_time: number
}

export interface CatapultPeriodStat {
  period_name: string
  average_player_load: number
  player_load_per_minute: number
  total_duration: number
  [key: string]: unknown
}

export class CatapultClient {
  private token: string

  constructor() {
    const token = process.env.CATAPULT_TOKEN?.trim()
    if (!token) throw new Error('CATAPULT_TOKEN environment variable is not set')
    this.token = token
  }

  private get headers(): Record<string, string> {
    return {
      Authorization: `Bearer ${this.token}`,
      'Content-Type': 'application/json',
      Accept: 'application/json',
    }
  }

  private async get<T>(path: string, params?: Record<string, string>): Promise<T> {
    const url = new URL(BASE_URL + path)
    if (params) Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v))

    let delay = 2000
    for (let attempt = 0; attempt < 4; attempt++) {
      const res = await fetch(url.toString(), { headers: this.headers })
      if (res.status === 200) return res.json() as Promise<T>
      if ([429, 502, 503].includes(res.status)) {
        await new Promise(r => setTimeout(r, delay))
        delay *= 2
        continue
      }
      throw new CatapultAPIError(res.status, await res.text())
    }
    throw new CatapultAPIError(429, 'Max retries exceeded')
  }

  private async post<T>(path: string, body: unknown): Promise<T> {
    let delay = 2000
    for (let attempt = 0; attempt < 4; attempt++) {
      const res = await fetch(BASE_URL + path, {
        method: 'POST',
        headers: this.headers,
        body: JSON.stringify(body),
      })
      if (res.status === 200) return res.json() as Promise<T>
      if ([429, 502, 503].includes(res.status)) {
        await new Promise(r => setTimeout(r, delay))
        delay *= 2
        continue
      }
      throw new CatapultAPIError(res.status, await res.text())
    }
    throw new CatapultAPIError(429, 'Max retries exceeded')
  }

  async listActivities(startTime: string, endTime: string): Promise<CatapultActivity[]> {
    return this.get<CatapultActivity[]>('/activities', {
      start_time: startTime,
      end_time: endTime,
    })
  }

  async getPeriodStats(activityId: string): Promise<CatapultPeriodStat[]> {
    const result = await this.post<CatapultPeriodStat[]>('/stats', {
      filters: [{ name: 'activity_id', comparison: '=', values: [activityId] }],
      parameters: [
        'average_player_load',
        'player_load_per_minute',
        'total_duration',
      ],
      group_by: ['period'],
      source: 'cached_stats',
    })
    return Array.isArray(result) ? result : []
  }
}
```

- [ ] **Step 4: Run to verify tests pass**

```bash
npx vitest run tests/catapult.test.ts
```
Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add simulator/lib/catapult.ts simulator/tests/catapult.test.ts
git commit -m "feat: add Catapult Connect v6 TypeScript client with tests"
```

---

## Task 9: GPS Sync API Route

**Files:**
- Create: `simulator/app/api/sync/route.ts`

- [ ] **Step 1: Create the sync route**

Create `simulator/app/api/sync/route.ts`:
```typescript
import { NextRequest, NextResponse } from 'next/server'
import { sql } from '@/lib/db'
import { CatapultClient, CatapultAPIError } from '@/lib/catapult'
import { canonicalize } from '@/lib/periodMap'
import type { Practice, Period } from '@/lib/types'

export async function POST(req: NextRequest) {
  const { practice_id } = await req.json()
  const id = parseInt(practice_id, 10)
  if (isNaN(id)) {
    return NextResponse.json({ error: 'Invalid practice_id' }, { status: 400 })
  }

  // Load practice from DB
  const [practice] = await sql`SELECT * FROM practices WHERE id = ${id}` as Practice[]
  if (!practice) {
    return NextResponse.json({ error: 'Practice not found' }, { status: 404 })
  }

  const client = new CatapultClient()

  // Find the Catapult session for this practice date
  const dateStr = practice.practice_date.slice(0, 10) // "YYYY-MM-DD"
  const startTime = `${dateStr}T00:00:00`
  const endTime   = `${dateStr}T23:59:59`

  let activities
  try {
    activities = await client.listActivities(startTime, endTime)
  } catch (err) {
    const msg = err instanceof CatapultAPIError ? err.message : String(err)
    return NextResponse.json({ error: `Catapult error: ${msg}` }, { status: 502 })
  }

  // Filter to practice sessions (name contains standalone 'P' token, no 'Walk Thru')
  const practiceActivities = activities.filter(a =>
    /\bP\d+\b/.test(a.name) && !a.name.includes('Walk Thru')
  )

  if (practiceActivities.length === 0) {
    return NextResponse.json({
      error: `No practice session found in Catapult for ${dateStr}`,
      activities_found: activities.map(a => a.name),
    }, { status: 404 })
  }

  const activity = practiceActivities[0]

  // Fetch period-level stats
  let periodStats
  try {
    periodStats = await client.getPeriodStats(activity.id)
  } catch (err) {
    const msg = err instanceof CatapultAPIError ? err.message : String(err)
    return NextResponse.json({ error: `Catapult stats error: ${msg}` }, { status: 502 })
  }

  // Load DB periods for this practice
  const dbPeriods = await sql`
    SELECT * FROM periods WHERE practice_id = ${id} ORDER BY order_index
  ` as Period[]

  // Match and update
  const matched: string[] = []
  const unmatched: string[] = []

  for (const stat of periodStats) {
    const canonical = canonicalize(stat.period_name)
    const dbPeriod = dbPeriods.find(p => p.name === canonical)

    if (dbPeriod) {
      const plTeamActual = stat.average_player_load
      const plPerMinActual = stat.player_load_per_minute ?? null
      await sql`
        UPDATE periods
        SET pl_team_actual = ${plTeamActual},
            pl_per_min_actual = ${plPerMinActual}
        WHERE id = ${dbPeriod.id}
      `
      matched.push(canonical)
    } else {
      unmatched.push(stat.period_name)
    }
  }

  // Mark practice as synced
  await sql`UPDATE practices SET synced_at = NOW() WHERE id = ${id}`

  return NextResponse.json({
    ok: true,
    activity_name: activity.name,
    matched,
    unmatched,
    synced_at: new Date().toISOString(),
  })
}
```

- [ ] **Step 2: Commit**

```bash
git add simulator/app/api/sync/
git commit -m "feat: add POST /api/sync route for Catapult GPS data ingestion"
```

---

## Task 10: Global Layout and Design Tokens

**Files:**
- Modify: `simulator/app/globals.css`
- Modify: `simulator/app/layout.tsx`
- Modify: `simulator/app/page.tsx`

- [ ] **Step 1: Replace globals.css with Baylor design tokens**

Replace all content in `simulator/app/globals.css`:
```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  --navy: #154734;
  --gold: #FFB81C;
  --green: #2e7d32;
  --green-bg: #e8f5e9;
  --green-border: #a5d6a7;
  --yellow: #f9a825;
  --yellow-bg: #fff8e1;
  --yellow-border: #ffe082;
  --red: #c62828;
  --red-bg: #ffebee;
  --red-border: #ef9a9a;
  --gray-50: #fafafa;
  --gray-100: #f5f5f5;
  --gray-200: #eeeeee;
  --gray-300: #e0e0e0;
  --gray-400: #bdbdbd;
  --gray-600: #757575;
  --gray-800: #424242;
  --gray-900: #212121;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  color: var(--gray-900);
  background: #f0f2f5;
  line-height: 1.5;
}
```

- [ ] **Step 2: Update root layout**

Replace `simulator/app/layout.tsx`:
```typescript
import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Baylor Football — Practice Load Simulator',
  description: 'Plan and simulate practice load for Baylor Football',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
```

- [ ] **Step 3: Update root page to redirect**

Replace `simulator/app/page.tsx`:
```typescript
import { redirect } from 'next/navigation'

export default function Home() {
  redirect('/simulator')
}
```

- [ ] **Step 4: Commit**

```bash
git add simulator/app/globals.css simulator/app/layout.tsx simulator/app/page.tsx
git commit -m "feat: add Baylor design tokens and root layout"
```

---

## Task 11: Simulator UI Components

**Files:**
- Create: `simulator/components/PracticeSelector.tsx` + `.module.css`
- Create: `simulator/components/LoadGauge.tsx` + `.module.css`
- Create: `simulator/components/PeriodItem.tsx` + `.module.css`
- Create: `simulator/components/PeriodList.tsx`
- Create: `simulator/components/AddPeriod.tsx`
- Create: `simulator/components/SwapSuggestions.tsx` + `.module.css`

- [ ] **Step 1: Create PracticeSelector**

Create `simulator/components/PracticeSelector.tsx`:
```typescript
'use client'

import type { Practice } from '@/lib/types'
import styles from './PracticeSelector.module.css'

interface Props {
  practices: Practice[]
  selectedId: number
  onChange: (id: number) => void
}

export function PracticeSelector({ practices, selectedId, onChange }: Props) {
  const selected = practices.find(p => p.id === selectedId)

  return (
    <div>
      <select
        className={styles.select}
        value={selectedId}
        onChange={e => onChange(Number(e.target.value))}
      >
        {practices.map(p => (
          <option key={p.id} value={p.id}>
            P{p.practice_num} — {p.practice_date} ({p.day_of_week})
          </option>
        ))}
      </select>
      {selected && (
        <div className={styles.meta}>
          <div className={styles.metaItem}>
            <div className={styles.metaLabel}>Dress</div>
            <div className={styles.metaValue}>{selected.dress}</div>
          </div>
          <div className={styles.metaItem}>
            <div className={styles.metaLabel}>Tempo</div>
            <div className={styles.metaValue}>{selected.tempo}</div>
          </div>
          <div className={styles.metaItem}>
            <div className={styles.metaLabel}>Duration</div>
            <div className={styles.metaValue}>{selected.total_duration_min} min</div>
          </div>
          <div className={styles.metaItem}>
            <div className={styles.metaLabel}>Emphasis</div>
            <div className={styles.metaValue}>{selected.emphasis}</div>
          </div>
        </div>
      )}
    </div>
  )
}
```

Create `simulator/components/PracticeSelector.module.css`:
```css
.select {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid var(--gray-300);
  border-radius: 6px;
  font-size: 13px;
  font-family: inherit;
  background: #fff;
  cursor: pointer;
}
.select:focus { outline: none; border-color: var(--navy); }
.meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
  margin-top: 10px;
  font-size: 12px;
}
.metaItem {
  background: var(--gray-50);
  padding: 6px 8px;
  border-radius: 4px;
}
.metaLabel {
  font-weight: 600;
  color: var(--gray-600);
  font-size: 10px;
  text-transform: uppercase;
}
.metaValue { font-weight: 600; color: var(--gray-900); }
```

- [ ] **Step 2: Create LoadGauge**

Create `simulator/components/LoadGauge.tsx`:
```typescript
'use client'

import type { SessionLoad } from '@/lib/types'
import styles from './LoadGauge.module.css'

const CLASS_COLOR: Record<string, string> = {
  GREEN: 'var(--green)',
  YELLOW: 'var(--yellow)',
  RED: 'var(--red)',
}

interface Props {
  load: SessionLoad
  originalPP: number
}

export function LoadGauge({ load, originalPP }: Props) {
  const { plPlayer, plTeam, totalMinutes, classification, plPerMinSession } = load
  const color = CLASS_COLOR[classification]
  const pct = Math.min(100, Math.max(0, (plPlayer - 150) / (550 - 150) * 100))
  const delta = plPlayer - originalPP

  return (
    <div className={styles.container}>
      <div className={styles.value} style={{ color }}>{plPlayer}</div>
      <div className={styles.unit}>PL / Player</div>
      <div className={styles.bar}>
        <div className={styles.fill} style={{ width: `${pct}%`, background: color }} />
      </div>
      <div className={styles.markers}>
        <span>200</span>
        <span style={{ color: 'var(--green)' }}>GRN &le;420</span>
        <span style={{ color: 'var(--yellow)' }}>YEL 421-470</span>
        <span style={{ color: 'var(--red)' }}>RED &gt;470</span>
        <span>550</span>
      </div>
      <span className={styles.badge} style={{ background: color }}>{classification}</span>

      {delta !== 0 && (
        <div className={styles.delta} style={{ color: delta > 0 ? 'var(--red)' : 'var(--green)' }}>
          <span>{delta > 0 ? '▲' : '▼'}</span>
          <span>{delta > 0 ? '+' : ''}{delta} PL/player from original</span>
        </div>
      )}

      <div className={styles.detail}>
        <div className={styles.detailItem}>
          <div className={styles.detailVal}>{plTeam.toLocaleString()}</div>
          <div className={styles.detailLabel}>Team PL</div>
        </div>
        <div className={styles.detailItem}>
          <div className={styles.detailVal}>{totalMinutes}</div>
          <div className={styles.detailLabel}>Duration (min)</div>
        </div>
        <div className={styles.detailItem}>
          <div className={styles.detailVal}>{plPerMinSession}</div>
          <div className={styles.detailLabel}>PL/min</div>
        </div>
      </div>
    </div>
  )
}
```

Create `simulator/components/LoadGauge.module.css`:
```css
.container { text-align: center; padding: 8px 0; }
.value { font-size: 36px; font-weight: 800; transition: color 0.3s ease; }
.unit { font-size: 14px; font-weight: 600; color: var(--gray-600); }
.bar {
  height: 14px; background: var(--gray-200); border-radius: 7px;
  overflow: hidden; position: relative; margin: 8px 0;
}
.fill { height: 100%; border-radius: 7px; transition: width 0.4s ease, background 0.4s ease; }
.markers {
  display: flex; justify-content: space-between;
  font-size: 9px; color: var(--gray-400); padding: 0 2px;
}
.badge {
  display: inline-block; padding: 3px 12px; border-radius: 12px;
  font-size: 12px; font-weight: 700; color: #fff; margin-top: 6px;
}
.delta {
  display: flex; justify-content: center; align-items: center;
  gap: 6px; margin-top: 8px; font-size: 12px; font-weight: 600;
}
.detail {
  margin-top: 10px; padding-top: 8px; border-top: 1px solid var(--gray-200);
  font-size: 12px; color: var(--gray-600); display: flex; justify-content: space-between;
}
.detailItem { text-align: center; }
.detailVal { font-weight: 800; font-size: 14px; color: var(--gray-900); }
.detailLabel { font-size: 9px; margin-top: 2px; }
```

- [ ] **Step 3: Create PeriodItem**

Create `simulator/components/PeriodItem.tsx`:
```typescript
'use client'

import { useRef, useCallback } from 'react'
import type { ActivePeriod } from '@/lib/types'
import { PERIOD_DEFAULTS, RATIO, TEMPO_MULT } from '@/lib/loadCalc'
import styles from './PeriodItem.module.css'

interface Props {
  period: ActivePeriod
  orderNum: number
  tempo: string
  onToggle: () => void
  onMinutesChange: (minutes: number) => void
}

function tierInfo(plTeam: number): { label: string; cls: string } {
  if (plTeam >= 400) return { label: 'HEAVY', cls: styles.heavy }
  if (plTeam >= 200) return { label: 'MEDIUM', cls: styles.medium }
  return { label: 'LIGHT', cls: styles.light }
}

export function PeriodItem({ period, orderNum, tempo, onToggle, onMinutesChange }: Props) {
  const tempoMult = TEMPO_MULT[tempo] ?? 1.0
  const defaults = PERIOD_DEFAULTS[period.name]
  const defaultMins = defaults?.defaultMinutes ?? 10
  const plPerMin = period.pl_per_min_actual ?? (period.pl_team_projected / defaultMins)
  const periodPlTeam = plPerMin * period.minutes * tempoMult
  const periodPlPlayer = Math.round(periodPlTeam * RATIO)
  const plPerMinDisplay = (periodPlPlayer / period.minutes).toFixed(1)
  const tier = tierInfo(period.pl_team_projected)
  const hasActual = period.pl_team_actual != null

  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const handleMinutesChange = useCallback((val: string) => {
    const mins = parseFloat(val)
    if (!Number.isFinite(mins) || mins <= 0) return
    onMinutesChange(mins)
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      // Persist to DB — handled by parent via PATCH
    }, 600)
  }, [onMinutesChange])

  const itemCls = [
    styles.item,
    !period.active ? styles.removed : '',
    period.added ? styles.added : '',
  ].filter(Boolean).join(' ')

  return (
    <div className={itemCls}>
      <div className={styles.order}>{period.active ? orderNum : '-'}</div>
      <div className={styles.name}>{period.name}</div>
      {hasActual && <span className={styles.actualBadge}>ACTUAL GPS</span>}
      <div className={`${styles.tier} ${tier.cls}`}>{tier.label}</div>
      <input
        type="number"
        className={styles.minsInput}
        value={period.minutes}
        min={1}
        max={120}
        step={1}
        disabled={!period.active}
        onChange={e => handleMinutesChange(e.target.value)}
        title="Duration in minutes"
      />
      <span className={styles.minsLabel}>min</span>
      <div className={styles.load}>+{periodPlPlayer} PL/p</div>
      <div className={styles.plPerMin}>{plPerMinDisplay}/min</div>
      <button
        className={period.active ? styles.removeBtn : styles.undoBtn}
        onClick={onToggle}
        title={period.active ? 'Remove' : 'Restore'}
      >
        {period.active ? '×' : '↻'}
      </button>
    </div>
  )
}
```

Create `simulator/components/PeriodItem.module.css`:
```css
.item {
  display: flex; align-items: center; gap: 8px; padding: 8px 12px;
  background: #fff; border-radius: 6px; border: 1px solid var(--gray-200);
  transition: all 0.2s ease;
}
.item:hover { border-color: var(--gray-300); }
.removed { opacity: 0.4; border-style: dashed; text-decoration: line-through; }
.added { border-color: var(--green-border); background: #f1f8e9; }
.order {
  width: 22px; height: 22px; background: var(--gray-100); border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 10px; font-weight: 700; color: var(--gray-600); flex-shrink: 0;
}
.name { flex: 1; font-size: 13px; font-weight: 600; }
.actualBadge {
  font-size: 9px; font-weight: 700; background: var(--green-bg);
  color: var(--green); padding: 2px 5px; border-radius: 3px; white-space: nowrap;
}
.tier { font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px; width: 44px; text-align: center; }
.heavy { color: var(--red); }
.medium { color: var(--yellow); }
.light { color: var(--green); }
.minsInput {
  width: 44px; padding: 3px 5px; border: 1px solid var(--gray-300);
  border-radius: 4px; font-size: 12px; font-weight: 700; text-align: center;
  font-family: inherit;
}
.minsInput:focus { outline: none; border-color: var(--navy); }
.minsLabel { font-size: 10px; color: var(--gray-600); }
.load {
  font-size: 12px; font-weight: 700; padding: 2px 8px; border-radius: 4px;
  min-width: 62px; text-align: center;
  background: var(--gray-100); color: var(--gray-800);
}
.plPerMin { font-size: 11px; color: var(--gray-600); min-width: 48px; text-align: right; }
.removeBtn, .undoBtn {
  width: 22px; height: 22px; border-radius: 50%; border: none;
  font-size: 14px; font-weight: 700; cursor: pointer;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.removeBtn { background: var(--red-bg); color: var(--red); }
.removeBtn:hover { background: var(--red); color: #fff; }
.undoBtn { background: var(--green-bg); color: var(--green); }
.undoBtn:hover { background: var(--green); color: #fff; }
```

- [ ] **Step 4: Create PeriodList**

Create `simulator/components/PeriodList.tsx`:
```typescript
'use client'

import type { ActivePeriod } from '@/lib/types'
import { PeriodItem } from './PeriodItem'

interface Props {
  periods: ActivePeriod[]
  tempo: string
  onToggle: (idx: number) => void
  onMinutesChange: (idx: number, minutes: number) => void
}

export function PeriodList({ periods, tempo, onToggle, onMinutesChange }: Props) {
  let orderNum = 0
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
      {periods.map((p, idx) => {
        if (p.active) orderNum++
        return (
          <PeriodItem
            key={`${p.id}-${idx}`}
            period={p}
            orderNum={orderNum}
            tempo={tempo}
            onToggle={() => onToggle(idx)}
            onMinutesChange={mins => onMinutesChange(idx, mins)}
          />
        )
      })}
    </div>
  )
}
```

- [ ] **Step 5: Create AddPeriod**

Create `simulator/components/AddPeriod.tsx`:
```typescript
'use client'

import { useState } from 'react'
import { PERIOD_DEFAULTS } from '@/lib/loadCalc'
import styles from './PracticeSelector.module.css'

interface Props {
  onAdd: (name: string, minutes: number) => void
}

export function AddPeriod({ onAdd }: Props) {
  const [selected, setSelected] = useState('')
  const drills = Object.keys(PERIOD_DEFAULTS).sort()

  return (
    <div style={{ display: 'flex', gap: '6px', marginTop: '8px' }}>
      <select
        className={styles.select}
        value={selected}
        onChange={e => setSelected(e.target.value)}
        style={{ flex: 1 }}
      >
        <option value="">Select drill...</option>
        {drills.map(d => <option key={d} value={d}>{d}</option>)}
      </select>
      <button
        style={{
          background: 'var(--navy)', color: '#fff', border: 'none',
          padding: '8px 14px', borderRadius: '6px', fontWeight: 700,
          fontSize: '12px', cursor: 'pointer', whiteSpace: 'nowrap',
        }}
        onClick={() => {
          if (!selected) return
          const defaultMins = PERIOD_DEFAULTS[selected]?.defaultMinutes ?? 10
          onAdd(selected, defaultMins)
          setSelected('')
        }}
      >
        + Add
      </button>
    </div>
  )
}
```

- [ ] **Step 6: Create SwapSuggestions**

Create `simulator/components/SwapSuggestions.tsx`:
```typescript
'use client'

import type { ActivePeriod } from '@/lib/types'
import type { SwapSuggestion } from '@/lib/loadCalc'
import styles from './SwapSuggestions.module.css'

interface Props {
  suggestions: SwapSuggestion[]
  classification: 'GREEN' | 'YELLOW' | 'RED'
  onApply: (swap: SwapSuggestion) => void
}

export function SwapSuggestions({ suggestions, classification, onApply }: Props) {
  const title = classification === 'GREEN' ? 'To Raise Per-Player Load' : 'To Lower Per-Player Load'

  if (suggestions.length === 0) {
    return (
      <p style={{ fontSize: '11px', color: 'var(--gray-400)', padding: '8px' }}>
        No single-swap changes shift the classification. Try adjusting multiple periods.
      </p>
    )
  }

  return (
    <div>
      <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px', color: 'var(--gray-600)', marginBottom: '8px' }}>
        {title}
      </div>
      {suggestions.map((s, i) => (
        <div key={i} className={styles.card} onClick={() => onApply(s)}>
          <span className={s.out === '(add new)' ? '' : styles.out}>{s.out}</span>
          <span className={styles.arrow}>→</span>
          <span className={styles.inn}>{s.inn}</span>
          <span className={`${styles.delta} ${s.delta < 0 ? styles.down : styles.up}`}>
            {s.delta > 0 ? '+' : ''}{s.delta} PL/p → {s.newClass}
          </span>
        </div>
      ))}
    </div>
  )
}
```

Create `simulator/components/SwapSuggestions.module.css`:
```css
.card {
  display: flex; align-items: center; gap: 8px; padding: 8px 12px;
  background: #fff; border: 1px dashed var(--gray-300); border-radius: 6px;
  cursor: pointer; transition: all 0.15s ease; margin-bottom: 4px; font-size: 12px;
}
.card:hover { border-color: var(--navy); background: var(--gray-50); }
.out { color: var(--red); font-weight: 600; }
.arrow { color: var(--gray-400); }
.inn { color: var(--green); font-weight: 600; }
.delta { margin-left: auto; font-weight: 700; font-size: 11px; }
.down { color: var(--green); }
.up { color: var(--red); }
```

- [ ] **Step 7: Commit**

```bash
git add simulator/components/
git commit -m "feat: add all simulator UI components"
```

---

## Task 12: Simulator Page

**Files:**
- Create: `simulator/app/simulator/page.tsx`
- Create: `simulator/app/simulator/SimulatorClient.tsx`
- Create: `simulator/app/simulator/simulator.module.css`

- [ ] **Step 1: Create the client-side simulator logic**

Create `simulator/app/simulator/SimulatorClient.tsx`:
```typescript
'use client'

import { useState, useCallback, useEffect } from 'react'
import type { Practice, PracticeWithPeriods, ActivePeriod } from '@/lib/types'
import { PERIOD_DEFAULTS, TEMPO_MULT, computeSessionLoad, generateSwaps } from '@/lib/loadCalc'
import { PracticeSelector } from '@/components/PracticeSelector'
import { LoadGauge } from '@/components/LoadGauge'
import { PeriodList } from '@/components/PeriodList'
import { AddPeriod } from '@/components/AddPeriod'
import { SwapSuggestions } from '@/components/SwapSuggestions'
import type { SwapSuggestion } from '@/lib/loadCalc'
import styles from './simulator.module.css'

interface Props {
  practices: Practice[]
}

export function SimulatorClient({ practices }: Props) {
  const [selectedId, setSelectedId] = useState(practices[0]?.id ?? 0)
  const [periods, setPeriods] = useState<ActivePeriod[]>([])
  const [originalPP, setOriginalPP] = useState(0)
  const [loading, setLoading] = useState(false)

  async function loadPractice(id: number) {
    setLoading(true)
    const res = await fetch(`/api/practices/${id}`)
    const data: PracticeWithPeriods = await res.json()
    const active: ActivePeriod[] = data.periods.map(p => ({ ...p, active: true, added: false }))
    setPeriods(active)
    const practice = practices.find(p => p.id === id)!
    const load = computeSessionLoad(active, practice.tempo)
    setOriginalPP(load.plPlayer)
    setLoading(false)
  }

  useEffect(() => { if (selectedId) loadPractice(selectedId) }, [selectedId])

  const practice = practices.find(p => p.id === selectedId)
  const load = practice ? computeSessionLoad(periods, practice.tempo) : null
  const tempoMult = TEMPO_MULT[practice?.tempo ?? 'THUD'] ?? 1.0

  const swaps = load
    ? generateSwaps(periods, load.plPlayer, load.classification, tempoMult)
    : []

  const handleToggle = useCallback((idx: number) => {
    setPeriods(prev => {
      const next = [...prev]
      if (!next[idx].active && next[idx].added) {
        next.splice(idx, 1)
      } else {
        next[idx] = { ...next[idx], active: !next[idx].active }
      }
      return next
    })
  }, [])

  const handleMinutesChange = useCallback((idx: number, minutes: number) => {
    setPeriods(prev => {
      const next = [...prev]
      next[idx] = { ...next[idx], minutes }
      return next
    })
    // Persist to DB
    const period = periods[idx]
    fetch(`/api/practices/${selectedId}/periods/${period.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ minutes }),
    }).catch(console.error)
  }, [periods, selectedId])

  const handleAdd = useCallback((name: string, minutes: number) => {
    const defaults = PERIOD_DEFAULTS[name]
    const newPeriod: ActivePeriod = {
      id: -Date.now(), // temp id for client-added periods
      practice_id: selectedId,
      name,
      order_index: periods.length,
      minutes: minutes,
      pl_team_projected: defaults?.plTeam ?? 300,
      pl_team_actual: null,
      pl_per_min_actual: null,
      active: true,
      added: true,
    }
    setPeriods(prev => [...prev, newPeriod])
  }, [periods, selectedId])

  const handleSwap = useCallback((swap: SwapSuggestion) => {
    setPeriods(prev => {
      const next = [...prev]
      if (swap.out === '(add new)') {
        handleAdd(swap.inn, PERIOD_DEFAULTS[swap.inn]?.defaultMinutes ?? 10)
        return prev
      }
      if (swap.inn === '(remove)') {
        const idx = next.findIndex(p => p.active && p.name === swap.out)
        if (idx !== -1) next[idx] = { ...next[idx], active: false }
        return next
      }
      const idx = next.findIndex(p => p.active && p.name === swap.out)
      if (idx !== -1) {
        next[idx] = { ...next[idx], active: false }
        const defaults = PERIOD_DEFAULTS[swap.inn]
        next.splice(idx + 1, 0, {
          id: -Date.now(),
          practice_id: selectedId,
          name: swap.inn,
          order_index: idx + 1,
          minutes: defaults?.defaultMinutes ?? 10,
          pl_team_projected: defaults?.plTeam ?? 300,
          pl_team_actual: null,
          pl_per_min_actual: null,
          active: true,
          added: true,
        })
      }
      return next
    })
  }, [handleAdd, selectedId])

  const handleReset = () => loadPractice(selectedId)

  if (!practice || !load) return <div style={{ padding: 20 }}>{loading ? 'Loading...' : 'No practice data.'}</div>

  const activeCount = periods.filter(p => p.active).length

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>Avg Player Load Simulator</h1>
          <div className={styles.sub}>Adjust Drill Selection to Manipulate Per-Player Load</div>
        </div>
      </header>

      <div className={styles.layout}>
        <div className={styles.sidebar}>
          <div className={styles.card}>
            <div className={styles.cardTitle}>Select Practice</div>
            <PracticeSelector
              practices={practices}
              selectedId={selectedId}
              onChange={id => { setSelectedId(id); }}
            />
          </div>

          <div className={styles.card}>
            <div className={styles.cardTitle}>Avg Player Load</div>
            <LoadGauge load={load} originalPP={originalPP} />
          </div>

          <div className={styles.card}>
            <div className={styles.cardTitle}>Add a Period</div>
            <AddPeriod onAdd={handleAdd} />
          </div>

          <div className={styles.card}>
            <SwapSuggestions
              suggestions={swaps}
              classification={load.classification}
              onApply={handleSwap}
            />
          </div>

          <button className={styles.resetBtn} onClick={handleReset}>Reset to Original</button>
        </div>

        <div className={styles.main}>
          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <div className={styles.cardTitle} style={{ marginBottom: 0 }}>Period Composition</div>
              <div style={{ fontSize: '11px', color: 'var(--gray-600)' }}>
                {activeCount} periods | Click × to remove, ↻ to restore
              </div>
            </div>
            {loading ? (
              <div style={{ padding: 20, textAlign: 'center', color: 'var(--gray-400)' }}>Loading...</div>
            ) : (
              <PeriodList
                periods={periods}
                tempo={practice.tempo}
                onToggle={handleToggle}
                onMinutesChange={handleMinutesChange}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
```

Create `simulator/app/simulator/simulator.module.css`:
```css
.container { max-width: 1100px; margin: 0 auto; padding: 20px; }
.header {
  background: var(--navy); color: #fff; padding: 20px 28px; border-radius: 10px;
  margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;
}
.title { font-size: 20px; font-weight: 800; letter-spacing: -0.5px; }
.sub { color: var(--gold); font-size: 12px; font-weight: 500; margin-top: 2px; }
.layout { display: grid; grid-template-columns: 320px 1fr; gap: 16px; }
.sidebar { display: flex; flex-direction: column; gap: 12px; }
.main { display: flex; flex-direction: column; gap: 12px; }
.card {
  background: #fff; border-radius: 8px; padding: 16px;
  border: 1px solid var(--gray-200); box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.cardTitle {
  font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.5px; color: var(--gray-600); margin-bottom: 10px;
}
.cardHeader {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;
}
.resetBtn {
  background: none; border: 1px solid var(--gray-300); padding: 6px 14px;
  border-radius: 6px; font-size: 11px; font-weight: 600; cursor: pointer;
  color: var(--gray-600); width: 100%; margin-top: 4px;
}
.resetBtn:hover { border-color: var(--navy); color: var(--navy); }
```

- [ ] **Step 2: Create the server page**

Create `simulator/app/simulator/page.tsx`:
```typescript
import { sql } from '@/lib/db'
import type { Practice } from '@/lib/types'
import { SimulatorClient } from './SimulatorClient'

export default async function SimulatorPage() {
  const practices = await sql`
    SELECT * FROM practices ORDER BY practice_num ASC
  ` as Practice[]

  return <SimulatorClient practices={practices} />
}
```

- [ ] **Step 3: Test the simulator end-to-end**

```bash
npm run dev
```
1. Navigate to `http://localhost:3000` — should redirect to `/simulator`
2. If not logged in, should redirect to `/login` — enter password
3. Simulator should load P1 by default with periods and gauge
4. Change practice — periods and gauge should update
5. Edit a minutes field — gauge should recalculate immediately
6. Click remove button on a period — period should grey out, gauge updates
7. Click restore (↻) — period restores, gauge updates
8. Add a period via the Add panel — new period appears highlighted green
9. Check swap suggestions appear and are clickable

Expected: All interactions work without errors in browser console.

- [ ] **Step 4: Commit**

```bash
git add simulator/app/simulator/
git commit -m "feat: add simulator page with full interactive load planning"
```

---

## Task 13: Admin Page (GPS Sync)

**Files:**
- Create: `simulator/app/admin/page.tsx`
- Create: `simulator/app/admin/AdminClient.tsx`

- [ ] **Step 1: Create the admin client component**

Create `simulator/app/admin/AdminClient.tsx`:
```typescript
'use client'

import { useState } from 'react'
import type { Practice } from '@/lib/types'

interface SyncResult {
  ok?: boolean
  error?: string
  activity_name?: string
  matched?: string[]
  unmatched?: string[]
  synced_at?: string
}

interface Props {
  practices: Practice[]
}

export function AdminClient({ practices }: Props) {
  const [selectedId, setSelectedId] = useState(practices[0]?.id ?? 0)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<SyncResult | null>(null)

  async function handleSync() {
    setLoading(true)
    setResult(null)
    try {
      const res = await fetch('/api/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ practice_id: selectedId }),
      })
      const data = await res.json()
      setResult(data)
    } catch (err) {
      setResult({ error: String(err) })
    }
    setLoading(false)
  }

  const containerStyle: React.CSSProperties = {
    maxWidth: 600, margin: '40px auto', padding: '0 20px',
  }
  const cardStyle: React.CSSProperties = {
    background: '#fff', borderRadius: 8, padding: 24,
    border: '1px solid var(--gray-200)', boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
  }

  return (
    <div style={containerStyle}>
      <div style={{ background: 'var(--navy)', color: '#fff', padding: '16px 24px', borderRadius: 10, marginBottom: 20 }}>
        <h1 style={{ fontSize: 18, fontWeight: 800 }}>Admin — GPS Sync</h1>
        <p style={{ color: 'var(--gold)', fontSize: 12, marginTop: 4 }}>Sync Catapult GPS actuals into the simulator</p>
      </div>

      <div style={cardStyle}>
        <label style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', color: 'var(--gray-600)', display: 'block', marginBottom: 8 }}>
          Select Practice
        </label>
        <select
          value={selectedId}
          onChange={e => setSelectedId(Number(e.target.value))}
          style={{ width: '100%', padding: '8px 10px', border: '1px solid var(--gray-300)', borderRadius: 6, fontSize: 13, fontFamily: 'inherit', marginBottom: 12 }}
        >
          {practices.map(p => (
            <option key={p.id} value={p.id}>
              P{p.practice_num} — {p.practice_date} ({p.day_of_week}) {p.synced_at ? '✓ synced' : ''}
            </option>
          ))}
        </select>

        <button
          onClick={handleSync}
          disabled={loading}
          style={{
            background: 'var(--navy)', color: '#fff', border: 'none', padding: '10px 20px',
            borderRadius: 6, fontWeight: 700, fontSize: 13, cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.7 : 1, width: '100%',
          }}
        >
          {loading ? 'Syncing...' : 'Sync GPS Data'}
        </button>

        {result && (
          <div style={{ marginTop: 16, padding: 12, borderRadius: 6, background: result.ok ? 'var(--green-bg)' : 'var(--red-bg)', border: `1px solid ${result.ok ? 'var(--green-border)' : 'var(--red-border)'}` }}>
            {result.ok ? (
              <>
                <p style={{ fontWeight: 700, color: 'var(--green)', marginBottom: 6 }}>Sync complete</p>
                <p style={{ fontSize: 12 }}>Activity: {result.activity_name}</p>
                <p style={{ fontSize: 12 }}>Matched periods: {result.matched?.join(', ') || 'none'}</p>
                {result.unmatched && result.unmatched.length > 0 && (
                  <p style={{ fontSize: 12, color: 'var(--yellow)' }}>Unmatched: {result.unmatched.join(', ')}</p>
                )}
                <p style={{ fontSize: 11, color: 'var(--gray-600)', marginTop: 4 }}>{result.synced_at}</p>
              </>
            ) : (
              <p style={{ color: 'var(--red)', fontWeight: 600, fontSize: 13 }}>Error: {result.error}</p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Create the admin server page**

Create `simulator/app/admin/page.tsx`:
```typescript
import { sql } from '@/lib/db'
import type { Practice } from '@/lib/types'
import { AdminClient } from './AdminClient'

export default async function AdminPage() {
  const practices = await sql`
    SELECT * FROM practices ORDER BY practice_num ASC
  ` as Practice[]

  return <AdminClient practices={practices} />
}
```

- [ ] **Step 3: Test the admin page**

```bash
npm run dev
```
Navigate to `http://localhost:3000/admin`. Expected: Shows practice selector and Sync GPS Data button. (Sync will fail without a real `CATAPULT_TOKEN` — expected behavior in local dev.)

- [ ] **Step 4: Commit**

```bash
git add simulator/app/admin/
git commit -m "feat: add admin page with GPS sync UI"
```

---

## Task 14: Reference Page

**Files:**
- Create: `simulator/app/reference/page.tsx`

- [ ] **Step 1: Create the reference page**

Create `simulator/app/reference/page.tsx`:
```typescript
import { PERIOD_DEFAULTS, RATIO, classify } from '@/lib/loadCalc'

function tierInfo(plTeam: number): { label: string; color: string } {
  if (plTeam >= 400) return { label: 'HEAVY', color: 'var(--red)' }
  if (plTeam >= 200) return { label: 'MEDIUM', color: 'var(--yellow)' }
  return { label: 'LIGHT', color: 'var(--green)' }
}

export default function ReferencePage() {
  const sorted = Object.entries(PERIOD_DEFAULTS).sort((a, b) => b[1].plTeam - a[1].plTeam)

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '20px', fontFamily: 'Inter, sans-serif' }}>
      <div style={{ background: 'var(--navy)', color: '#fff', padding: '14px 20px', borderRadius: 6, marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: 16, fontWeight: 800 }}>Per-Player Load Reference Card</h2>
          <div style={{ color: 'var(--gold)', fontSize: 11 }}>Baylor Football | 2026 GPS Actuals + 2025 Baseline</div>
        </div>
        <div style={{ color: 'rgba(255,255,255,0.7)', fontSize: 10 }}>GREEN &le;420 | YELLOW 421-470 | RED &gt;470</div>
      </div>

      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
        <thead>
          <tr style={{ background: 'var(--gray-100)' }}>
            {['Tier', 'Period', 'PL/Player (THUD)', 'PL/min', 'Team PL', 'Default Min'].map((h, i) => (
              <th key={h} style={{ padding: '6px 8px', textAlign: i >= 2 ? 'right' : 'left', fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.3px' }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map(([name, d]) => {
            const ppLoad = Math.round(d.plTeam * RATIO)
            const tier = tierInfo(d.plTeam)
            const plPerMin = (ppLoad / d.defaultMinutes).toFixed(1)
            return (
              <tr key={name} style={{ borderBottom: '1px solid var(--gray-200)' }}>
                <td style={{ padding: '5px 8px' }}>
                  <span style={{ background: tier.color, color: '#fff', padding: '2px 6px', borderRadius: 3, fontSize: 9, fontWeight: 700 }}>
                    {tier.label}
                  </span>
                </td>
                <td style={{ padding: '5px 8px', fontWeight: 600 }}>{name}</td>
                <td style={{ padding: '5px 8px', textAlign: 'right', fontWeight: 700 }}>{ppLoad}</td>
                <td style={{ padding: '5px 8px', textAlign: 'right', color: 'var(--gray-600)' }}>{plPerMin}</td>
                <td style={{ padding: '5px 8px', textAlign: 'right', color: 'var(--gray-600)' }}>{d.plTeam}</td>
                <td style={{ padding: '5px 8px', textAlign: 'right', color: 'var(--gray-600)' }}>{d.defaultMinutes}</td>
              </tr>
            )
          })}
        </tbody>
      </table>

      <div style={{ marginTop: 20, textAlign: 'right' }}>
        <button
          onClick={() => window.print()}
          style={{ background: 'var(--navy)', color: '#fff', border: 'none', padding: '8px 20px', borderRadius: 6, fontWeight: 700, fontSize: 12, cursor: 'pointer' }}
        >
          Print Reference Card
        </button>
      </div>

      <style>{`
        @media print {
          button { display: none !important; }
          @page { size: landscape; margin: 0.4in; }
        }
      `}</style>
    </div>
  )
}
```

- [ ] **Step 2: Test the reference page**

```bash
npm run dev
```
Navigate to `http://localhost:3000/reference`. Expected: Sorted table of all drill types with PL/player, PL/min, team PL, and default minutes. Print button triggers print dialog in landscape.

- [ ] **Step 3: Run all tests**

```bash
npx vitest run
```
Expected: All tests pass.

- [ ] **Step 4: Commit**

```bash
git add simulator/app/reference/
git commit -m "feat: add printable reference card page"
```

---

## Task 15: Vercel Deployment

**Files:**
- Create: `simulator/next.config.ts` (update if needed)
- No new files — deployment is configuration

- [ ] **Step 1: Install Vercel CLI**

```bash
npm install -g vercel
```

- [ ] **Step 2: Link the project to Vercel**

From the `simulator/` directory:
```bash
vercel link
```
When prompted:
- Link to existing project? No (create new)
- Project name: `baylor-load-sim`
- Which scope? (your personal account)
- Directory: `./` (the simulator directory)

- [ ] **Step 3: Set environment variables in Vercel**

```bash
vercel env add CATAPULT_TOKEN production
# paste your JWT token from gps_report/.env when prompted

vercel env add DATABASE_URL production
# paste your Neon connection string when prompted

vercel env add SITE_PASSWORD production
# enter your chosen password

vercel env add COOKIE_SECRET production
# enter a random 32-char string (run: node -e "console.log(require('crypto').randomBytes(16).toString('hex'))")
```

- [ ] **Step 4: Configure Vercel to build from the simulator/ subdirectory**

In the Vercel dashboard (vercel.com), go to your project settings:
- Root Directory: `simulator`
- Framework Preset: Next.js (auto-detected)
- Build Command: `npm run build` (default)
- Output Directory: `.next` (default)

- [ ] **Step 5: Deploy to production**

```bash
vercel --prod
```
Expected output:
```
Deploying to production...
Build completed
https://baylor-load-sim.vercel.app
```

- [ ] **Step 6: Smoke test production**

1. Open the production URL
2. Should redirect to `/login` — enter password
3. Simulator loads with P1 data from Neon
4. Change a practice — loads correctly
5. Edit period minutes — recalculates, PATCH fires (check Vercel function logs)
6. Navigate to `/reference` — table renders, print works
7. Navigate to `/admin` — sync button present

- [ ] **Step 7: Set up auto-deploy from git**

In Vercel dashboard, go to Git settings:
- Connect to GitHub repo: `erash11/FaceComps`
- Production branch: `main`
- Root directory: `simulator`

From this point on, `git push origin main` auto-deploys to production.

- [ ] **Step 8: Commit**

```bash
cd ..
git add simulator/
git commit -m "feat: configure Vercel deployment for baylor-load-sim"
```

---

## Self-Review

### Spec coverage check

| Spec requirement | Task |
|---|---|
| Next.js 14 App Router | Task 1 |
| Vercel Hobby hosting | Task 15 |
| Neon PostgreSQL | Tasks 2, 7 |
| Password gate (middleware + login) | Task 3 |
| Practice + period DB schema | Task 2 |
| Duration-scaled load (PL/min) | Task 4 |
| Editable period minutes | Tasks 11, 12 |
| PL/player gauge + classification | Tasks 4, 11 |
| Swap suggestions | Tasks 4, 11 |
| ACTUAL GPS badge on synced periods | Task 11 |
| Catapult API client (TypeScript) | Task 8 |
| POST /api/sync with period grouping | Task 9 |
| Canonical period name mapping | Task 4 |
| Seed script (2026 Spring data) | Task 7 |
| /admin GPS sync panel | Task 13 |
| /reference printable card | Task 14 |
| Out-of-scope: position breakdowns | — |
| Out-of-scope: multi-week calendar | — |

All spec requirements are covered.

### Type consistency check

- `ActivePeriod` defined in `lib/types.ts` (Task 2), used in `lib/loadCalc.ts` (Task 4), `components/PeriodItem.tsx` (Task 11), `SimulatorClient.tsx` (Task 12) — consistent
- `computeSessionLoad` signature matches usage in `SimulatorClient.tsx` — consistent
- `generateSwaps` returns `SwapSuggestion[]` — imported from `lib/loadCalc` in both `SimulatorClient.tsx` and `SwapSuggestions.tsx` — consistent
- `PERIOD_DEFAULTS` exported from `lib/loadCalc.ts`, imported in `AddPeriod.tsx` and `SimulatorClient.tsx` — consistent
- `CatapultClient` exported from `lib/catapult.ts`, imported in `/api/sync/route.ts` — consistent
