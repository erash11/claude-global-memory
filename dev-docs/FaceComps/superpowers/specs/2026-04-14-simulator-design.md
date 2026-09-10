# Practice Load Simulator — Production Design Spec

**Date:** 2026-04-14
**Author:** Eric Rash
**Status:** Approved

---

## Overview

Rebuild `Practice_Load_Simulator_v2.html` as a production-grade Next.js web application hosted on Vercel. The app allows Baylor Football performance staff and coaches to plan and manipulate practice load in real time, with GPS actuals pulled automatically from the Catapult Connect v6 API post-practice.

**Primary users:** Internal Baylor Football performance staff and coaches
**Access:** Lightweight password gate (shared password, no user accounts)
**Hosting:** Vercel Hobby (free tier)
**Database:** Neon PostgreSQL (free tier)

---

## Architecture

```
Browser (coaches / staff)
    ↓ HTTPS
Vercel (Next.js 14 App Router)
    ├── /app                    → React UI
    ├── /api/sync/route.ts      → Catapult GPS sync (server-side only)
    ├── /api/practices/route.ts → CRUD for practice + period data
    └── middleware.ts           → Password gate (signed cookie check)

Neon (free PostgreSQL)
    ├── practices
    ├── periods
    └── period_defaults

Catapult Connect v6 API
    └── Fetched server-side via /api/sync — never called from browser
```

### Data flow

1. Practice face data (date, dress, tempo, periods, minutes) is pre-populated into Neon at season start
2. Coaches use the simulator to plan load by adjusting periods and durations before practice
3. After practice, a staff member opens `/admin` and clicks "Sync GPS" for that practice
4. The `/api/sync` route authenticates to Catapult with `CATAPULT_TOKEN`, fetches period-level stats, maps period names to canonical names, and writes `pl_team_actual` + `pl_per_min_actual` to Neon
5. The UI reads from Neon on every load — Catapult is never called from the browser

---

## Authentication

A single `SITE_PASSWORD` environment variable is stored in Vercel. Next.js middleware checks for a signed session cookie on every request. If missing or invalid, the user is redirected to `/login`. On correct password entry, a signed cookie is set (httpOnly, secure, sameSite=strict).

No user accounts, no database required for auth.

---

## Database Schema

### `period_defaults`
Canonical period load constants derived from 2025/2026 GPS actuals. One row per drill type.

| Column | Type | Notes |
|---|---|---|
| name | VARCHAR PK | e.g. "TEAM", "INDIVIDUAL" |
| default_minutes | NUMERIC | avg duration from GPS history |
| pl_team_baseline | NUMERIC | hardcoded baseline from 2026 GPS (current constants) |
| pl_per_min_baseline | NUMERIC | pl_team_baseline / default_minutes |

### `practices`
One row per practice.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| season | VARCHAR | e.g. "2026 Spring" |
| practice_num | INTEGER | P1–P15 |
| practice_date | DATE | |
| day_of_week | VARCHAR | |
| dress | VARCHAR | Helmets / Shells / Full Pads |
| tempo | VARCHAR | TAG / THUD / THUD/LIVE / LIVE |
| emphasis | VARCHAR | |
| total_duration_min | INTEGER | sum of all period minutes |
| synced_at | TIMESTAMP | null until GPS sync runs |

### `periods`
One row per period per practice.

| Column | Type | Notes |
|---|---|---|
| id | SERIAL PK | |
| practice_id | INTEGER FK | → practices.id |
| name | VARCHAR | canonical period name |
| order_index | INTEGER | display order |
| minutes | NUMERIC | from practice face; editable by staff |
| pl_team_projected | NUMERIC | baseline value (from period_defaults) |
| pl_team_actual | NUMERIC | populated post-practice via GPS sync; null until then |
| pl_per_min_actual | NUMERIC | populated post-practice; null until then |

---

## Load Calculation

Duration scaling is the core change from v2. Period load is no longer a fixed constant — it scales with actual minutes.

```
pl_per_min         = pl_team_baseline / default_minutes       (intensity fingerprint, fixed per drill type)
period_pl_team     = pl_per_min × actual_minutes × tempo_mult (scales with duration)
period_pl_player   = period_pl_team × 0.09772
session_pl_player  = sum(period_pl_player for all active periods)
pl_per_min_display = session_pl_player / total_minutes        (session-level intensity)
```

**Tempo multipliers:** TAG=0.85, THUD=1.0, THUD/LIVE=1.15, LIVE=1.25

**Thresholds (per-player):** GREEN ≤ 420 | YELLOW 421–470 | RED > 470

When GPS actuals are available (`pl_team_actual` is not null), the UI uses `pl_per_min_actual` instead of `pl_per_min_baseline` for that period's calculation. Actual periods show an "ACTUAL GPS" badge; projected show "PROJECTED".

---

## UI Components

```
/app
  layout.tsx                 — password gate wrapper, Baylor nav header
  page.tsx                   — redirects to /simulator
  /login
    page.tsx                 — password entry form
  /simulator
    page.tsx                 — main simulator view
    components/
      PracticeSelector.tsx   — dropdown + metadata grid (date, dress, tempo, emphasis)
      LoadGauge.tsx          — PL/player number, GREEN/YELLOW/RED bar, delta from original, team PL, duration, period count
      PeriodList.tsx         — ordered list of periods
      PeriodItem.tsx         — name | minutes (inline editable) | PL/player | PL/min | tier badge | ACTUAL/PROJECTED badge | remove/restore btn
      AddPeriod.tsx          — drill picker dropdown + Add button
      SwapSuggestions.tsx    — contextual swap cards (same logic as v2)
  /admin
    page.tsx                 — GPS sync panel; practice selector + "Sync GPS" button + sync status/log
  /reference
    page.tsx                 — printable per-player load reference card

/api
  practices/route.ts         — GET /api/practices (list), GET /api/practices/[id], PATCH /api/practices/[id]/periods/[pid]
  sync/route.ts              — POST /api/sync { practice_id } → Catapult fetch → Neon write
```

### Key behavioral details

- `minutes` on each `PeriodItem` is an inline `<input type="number">` — editing it triggers an immediate recalculation client-side and a debounced PATCH to Neon
- Periods with actual GPS data show a green "ACTUAL GPS" badge; projected show a gray "PROJECTED" badge
- The gauge delta row shows change from the original loaded value, same as v2
- Swap suggestions are contextual (lower-load swaps when RED/YELLOW, higher-load when GREEN), same logic as v2

---

## Catapult API Integration

Reuses the auth pattern from `DataBase_GPS_Reporting/gps_report/src/api_client.py`, rewritten in TypeScript.

**Auth:** JWT Bearer token from `CATAPULT_TOKEN` env var (same long-lived token as the GPS reporting project)
**Base URL:** `https://connect-us.catapultsports.com/api/v6`
**Key endpoint:** `POST /stats` with period-level grouping (e.g. `group_by: ["period"]` or `["period", "athlete"]` — exact parameter to be confirmed during implementation against live API)

**Sync flow:**
1. Staff POSTs to `/api/sync` with `{ practice_id }`
2. Route looks up practice date in Neon
3. Calls `GET /activities` to find the Catapult session matching that date
4. Calls `POST /stats` with period-level group_by for that activity_id
5. Maps Catapult period names to canonical names via `lib/periodMap.ts`
6. Writes `pl_team_actual` and `pl_per_min_actual` to Neon for matched periods
7. Returns `{ matched: N, unmatched: [...], synced_at: timestamp }` to the UI

**Period name canonical mapping** lives in `lib/periodMap.ts` — same mappings from SPEC_SHEET.md (INDY 1/2 → INDIVIDUAL, SPT 1/2 → SPECIAL TEAMS, etc.).

---

## Environment Variables

All stored in Vercel dashboard, never in code:

| Variable | Purpose |
|---|---|
| `CATAPULT_TOKEN` | JWT Bearer token for Catapult Connect v6 |
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `SITE_PASSWORD` | Shared password for the password gate |
| `COOKIE_SECRET` | Secret for signing the session cookie |

---

## Deployment

- `git push` to `main` → Vercel auto-deploys
- Neon database is pre-seeded with 2026 Spring practice data (P1–P15) via a one-time seed script
- No CI/CD beyond Vercel's built-in deploy pipeline needed for this scale

---

## What Is NOT in Scope

- Position-group breakdowns (future)
- Multi-week / season-view calendar (future — see `Spring_Practice_Load_Calendar_v3.html`)
- Individual athlete load (future)
- Automated post-practice sync trigger (future — manual sync via `/admin` is sufficient)
- ForceDecks integration (separate project)
