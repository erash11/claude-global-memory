# Multi-Sport Travel Map Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the single-file Baylor Softball travel map into a hosted Vite + React SPA where staff select a sport from a landing page to see schedule, distances, time zones, travel mode, and congestion flags on an interactive US map.

**Architecture:** Vite + React SPA at the project root. Navigation is a single `view` state in `App.jsx` — no router library. Each sport's schedule lives in `src/data/<sport>.json`; `src/data/index.js` is the sport registry. `USMap.jsx` owns all D3 rendering; `SportMap.jsx` owns sidebar/filters; `SportGrid.jsx` is the landing page. Utility functions in `src/utils/` are pure and unit-tested with Vitest.

**Tech Stack:** React 19, D3 v7, Vite 6, Vitest 2 (utility tests only — components are manually tested via dev server)

---

## File Map

### Create (new files)
| File | Responsibility |
|------|---------------|
| `package.json` | Project deps and scripts |
| `vite.config.js` | Vite + Vitest config |
| `index.html` | HTML entry point |
| `.gitignore` | Exclude node_modules, dist |
| `src/main.jsx` | React root mount |
| `src/App.jsx` | View state router (grid ↔ sport) |
| `src/components/SportGrid.jsx` | Landing page sport card grid |
| `src/components/SportMap.jsx` | Sidebar + layout wrapper per sport |
| `src/components/USMap.jsx` | D3 map (refactored from softball.jsx) |
| `src/data/softball.json` | 2026 softball schedule in new JSON schema |
| `src/data/index.js` | Sport registry |
| `src/utils/haversine.js` | Haversine distance in miles |
| `src/utils/parseDate.js` | Date string → sort key and day-of-year |
| `src/utils/groupByDest.js` | Group games by lat/lng destination |
| `src/utils/calcMiles.js` | Total miles with tripId-based trip routing |
| `src/utils/timezones.js` | State → timezone, FIPS map, crossing calc |
| `src/utils/congestion.js` | Sliding window congestion detector |
| `src/utils/__tests__/haversine.test.js` | |
| `src/utils/__tests__/parseDate.test.js` | |
| `src/utils/__tests__/groupByDest.test.js` | |
| `src/utils/__tests__/calcMiles.test.js` | |
| `src/utils/__tests__/timezones.test.js` | |
| `src/utils/__tests__/congestion.test.js` | |

### Do not modify
- `baylor-softball-travel-map.jsx` — reference only (source of truth for extracted logic)
- `baylor-softball-globe.jsx` — archived, ignore
- `scratch/` — discard after new app is working

---

## Task 1: Scaffold Vite project at root

**Files:**
- Create: `package.json`
- Create: `vite.config.js`
- Create: `index.html`
- Create: `.gitignore`
- Create: `src/main.jsx`
- Create: `src/App.jsx`

- [ ] **Step 1: Create `package.json`**

```json
{
  "name": "baylor-travel-map",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "dependencies": {
    "d3": "^7.9.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.4",
    "vite": "^6.0.0",
    "vitest": "^2.0.0"
  }
}
```

- [ ] **Step 2: Create `vite.config.js`**

```js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'node',
  },
});
```

- [ ] **Step 3: Create `index.html`**

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Baylor Athletics — Travel Demands</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link
      href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"
      rel="stylesheet"
    />
  </head>
  <body style="margin:0;padding:0;background:#0f172a">
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

- [ ] **Step 4: Create `.gitignore`**

```
node_modules
dist
.env
.env.local
```

- [ ] **Step 5: Create `src/main.jsx`**

```jsx
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

- [ ] **Step 6: Create stub `src/App.jsx`**

```jsx
import { useState } from 'react';

export default function App() {
  return <div style={{ color: '#fff', padding: 40 }}>Baylor Travel Map — scaffold OK</div>;
}
```

- [ ] **Step 7: Create stub component files so imports don't break later**

Create `src/components/SportGrid.jsx`:
```jsx
export default function SportGrid({ onSelect }) {
  return <div style={{ color: '#fff' }}>SportGrid placeholder</div>;
}
```

Create `src/components/SportMap.jsx`:
```jsx
export default function SportMap({ sport, onBack }) {
  return <div style={{ color: '#fff' }}>SportMap placeholder</div>;
}
```

Create `src/components/USMap.jsx`:
```jsx
export default function USMap(props) {
  return <div style={{ color: '#fff' }}>USMap placeholder</div>;
}
```

- [ ] **Step 8: Install dependencies**

```bash
npm install
```

Expected: `node_modules/` created, no errors.

- [ ] **Step 9: Verify dev server starts**

```bash
npm run dev
```

Expected: Vite outputs a localhost URL. Opening it shows "Baylor Travel Map — scaffold OK" on a dark background.

Stop the dev server (Ctrl+C).

- [ ] **Step 10: Commit**

```bash
git add package.json vite.config.js index.html .gitignore src/
git commit -m "feat: scaffold Vite + React project at root"
```

---

## Task 2: Utility — haversine and parseDate

**Files:**
- Create: `src/utils/haversine.js`
- Create: `src/utils/parseDate.js`
- Create: `src/utils/__tests__/haversine.test.js`
- Create: `src/utils/__tests__/parseDate.test.js`

- [ ] **Step 1: Write failing test for `haversine`**

Create `src/utils/__tests__/haversine.test.js`:

```js
import { describe, it, expect } from 'vitest';
import { haversine } from '../haversine.js';

describe('haversine', () => {
  it('returns 0 for identical points', () => {
    expect(haversine(31.5493, -97.1467, 31.5493, -97.1467)).toBe(0);
  });

  it('calculates Waco to San Diego within 10 miles of 1303', () => {
    const dist = haversine(31.5493, -97.1467, 32.7749, -117.0714);
    expect(dist).toBeGreaterThan(1290);
    expect(dist).toBeLessThan(1316);
  });

  it('calculates Waco to Clemson within 10 miles of 1007', () => {
    const dist = haversine(31.5493, -97.1467, 34.6834, -82.8374);
    expect(dist).toBeGreaterThan(996);
    expect(dist).toBeLessThan(1018);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
npm test
```

Expected: FAIL — `Cannot find module '../haversine.js'`

- [ ] **Step 3: Create `src/utils/haversine.js`**

```js
export function haversine(lat1, lng1, lat2, lng2) {
  const R = 3959;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLng / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}
```

- [ ] **Step 4: Write failing test for `parseDate`**

Create `src/utils/__tests__/parseDate.test.js`:

```js
import { describe, it, expect } from 'vitest';
import { parseDate, parseDateAsDayOfYear } from '../parseDate.js';

describe('parseDate', () => {
  it('converts "Feb 5" to 205', () => {
    expect(parseDate('Feb 5')).toBe(205);
  });
  it('converts "Mar 11" to 311', () => {
    expect(parseDate('Mar 11')).toBe(311);
  });
  it('handles range like "Mar 7-8" by taking first date', () => {
    expect(parseDate('Mar 7-8')).toBe(307);
  });
});

describe('parseDateAsDayOfYear', () => {
  it('returns 1 for Jan 1', () => {
    expect(parseDateAsDayOfYear('Jan 1')).toBe(1);
  });
  it('returns 32 for Feb 1', () => {
    expect(parseDateAsDayOfYear('Feb 1')).toBe(32);
  });
  it('returns 60 for Mar 1', () => {
    expect(parseDateAsDayOfYear('Mar 1')).toBe(60);
  });
  it('handles range "Mar 7-8" by taking day 7', () => {
    expect(parseDateAsDayOfYear('Mar 7-8')).toBe(66);
  });
  it('returns 121 for May 1', () => {
    expect(parseDateAsDayOfYear('May 1')).toBe(121);
  });
});
```

- [ ] **Step 5: Create `src/utils/parseDate.js`**

```js
const MONTH_NAMES = {
  Jan: 1, Feb: 2, Mar: 3, Apr: 4, May: 5, Jun: 6,
  Jul: 7, Aug: 8, Sep: 9, Oct: 10, Nov: 11, Dec: 12,
};

// Cumulative days before each month (non-leap year)
const MONTH_OFFSETS = [0, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];

// Returns month*100+day for game list sorting.
// Handles range strings like "Mar 7-8" by using the first date.
export function parseDate(dateStr) {
  const clean = dateStr.split(/\s*-\s*/)[0].trim();
  const parts = clean.split(' ');
  return (MONTH_NAMES[parts[0]] || 0) * 100 + (parseInt(parts[1]) || 0);
}

// Returns day-of-year (1–365) for congestion window arithmetic.
// Handles range strings like "Mar 7-8" by using the first date.
export function parseDateAsDayOfYear(dateStr) {
  const clean = dateStr.split(/\s*-\s*/)[0].trim();
  const [mon, day] = clean.split(' ');
  const month = MONTH_NAMES[mon] || 1;
  return MONTH_OFFSETS[month] + (parseInt(day) || 1);
}
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
npm test
```

Expected: All 8 tests PASS.

- [ ] **Step 7: Commit**

```bash
git add src/utils/haversine.js src/utils/parseDate.js src/utils/__tests__/
git commit -m "feat: add haversine and parseDate utilities with tests"
```

---

## Task 3: Utility — groupByDest and calcMiles

**Files:**
- Create: `src/utils/groupByDest.js`
- Create: `src/utils/calcMiles.js`
- Create: `src/utils/__tests__/groupByDest.test.js`
- Create: `src/utils/__tests__/calcMiles.test.js`

- [ ] **Step 1: Write failing tests for `groupByDest`**

Create `src/utils/__tests__/groupByDest.test.js`:

```js
import { describe, it, expect } from 'vitest';
import { groupByDest } from '../groupByDest.js';

const games = [
  { date: 'Feb 5', opponent: 'A', location: 'Waco, TX', lat: 31.5, lng: -97.1, home: true, tripId: null },
  { date: 'Feb 6', opponent: 'B', location: 'Waco, TX', lat: 31.5, lng: -97.1, home: true, tripId: null },
  { date: 'Feb 12', opponent: 'C', location: 'San Diego, CA', lat: 32.7, lng: -117.0, home: false, tripId: null },
  { date: 'Feb 13', opponent: 'D', location: 'San Diego, CA', lat: 32.7, lng: -117.0, home: false, tripId: null },
  { date: 'Mar 11', opponent: 'E', location: 'DeLand, FL', lat: 29.0, lng: -81.3, home: false, tripId: 'florida-swing' },
];

describe('groupByDest', () => {
  it('merges games at the same lat/lng', () => {
    const result = groupByDest(games);
    expect(result).toHaveLength(3);
  });

  it('groups games into the games array per destination', () => {
    const result = groupByDest(games);
    const waco = result.find(d => d.location === 'Waco, TX');
    expect(waco.games).toHaveLength(2);
  });

  it('preserves tripId on destination', () => {
    const result = groupByDest(games);
    const deland = result.find(d => d.location === 'DeLand, FL');
    expect(deland.tripId).toBe('florida-swing');
  });

  it('sets tripId to null for destinations without a trip', () => {
    const result = groupByDest(games);
    const sd = result.find(d => d.location === 'San Diego, CA');
    expect(sd.tripId).toBeNull();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
npm test
```

Expected: FAIL — `Cannot find module '../groupByDest.js'`

- [ ] **Step 3: Create `src/utils/groupByDest.js`**

```js
export function groupByDest(games) {
  const map = {};
  games.forEach(g => {
    const key = `${g.lat},${g.lng}`;
    if (!map[key]) {
      map[key] = {
        location: g.location,
        lat: g.lat,
        lng: g.lng,
        home: g.home,
        tripId: g.tripId || null,
        games: [],
      };
    }
    map[key].games.push(g);
    if (g.tripId) map[key].tripId = g.tripId;
  });
  return Object.values(map);
}
```

- [ ] **Step 4: Write failing tests for `calcMiles`**

Create `src/utils/__tests__/calcMiles.test.js`:

```js
import { describe, it, expect } from 'vitest';
import { calcTotalMiles } from '../calcMiles.js';

const HOME = { lat: 31.5493, lng: -97.1467 };

const SD = { location: 'San Diego, CA', lat: 32.7749, lng: -117.0714, tripId: null };
const DELAND = { location: 'DeLand, FL', lat: 29.0283, lng: -81.3032, tripId: 'florida-swing' };
const ORLANDO = { location: 'Orlando, FL', lat: 28.6024, lng: -81.2001, tripId: 'florida-swing' };

const trips = [
  { id: 'florida-swing', label: 'Florida Swing', stops: ['DeLand, FL', 'Orlando, FL'] },
];

describe('calcTotalMiles', () => {
  it('doubles a single away trip (round trip)', () => {
    const miles = calcTotalMiles([SD], [], HOME);
    // Waco→San Diego ~1303 miles one-way, round trip ~2606
    expect(miles).toBeGreaterThan(2580);
    expect(miles).toBeLessThan(2640);
  });

  it('models a multi-stop trip as a chain, not double round trips', () => {
    const chain = calcTotalMiles([DELAND, ORLANDO], trips, HOME);
    const naiveDoubled = calcTotalMiles([DELAND, ORLANDO], [], HOME);
    expect(chain).toBeLessThan(naiveDoubled);
  });

  it('counts trip mileage once even if both stops appear in awayDests', () => {
    const once = calcTotalMiles([DELAND, ORLANDO], trips, HOME);
    // Waco→DeLand→Orlando→Waco should be roughly 2200-2400 miles
    expect(once).toBeGreaterThan(2100);
    expect(once).toBeLessThan(2600);
  });

  it('returns 0 for empty list', () => {
    expect(calcTotalMiles([], [], HOME)).toBe(0);
  });
});
```

- [ ] **Step 5: Create `src/utils/calcMiles.js`**

```js
import { haversine } from './haversine.js';

export function calcTotalMiles(awayDests, trips, home) {
  let total = 0;
  const tripsHandled = new Set();

  awayDests.forEach(d => {
    if (d.tripId) {
      if (tripsHandled.has(d.tripId)) return;
      tripsHandled.add(d.tripId);
      const trip = trips.find(t => t.id === d.tripId);
      if (!trip) return;
      const stops = trip.stops
        .map(loc => awayDests.find(dd => dd.location === loc))
        .filter(Boolean);
      if (stops.length === 0) return;
      total += haversine(home.lat, home.lng, stops[0].lat, stops[0].lng);
      for (let i = 0; i < stops.length - 1; i++) {
        total += haversine(stops[i].lat, stops[i].lng, stops[i + 1].lat, stops[i + 1].lng);
      }
      total += haversine(stops[stops.length - 1].lat, stops[stops.length - 1].lng, home.lat, home.lng);
    } else {
      total += haversine(home.lat, home.lng, d.lat, d.lng) * 2;
    }
  });

  return total;
}
```

- [ ] **Step 6: Run tests**

```bash
npm test
```

Expected: All tests PASS.

- [ ] **Step 7: Commit**

```bash
git add src/utils/groupByDest.js src/utils/calcMiles.js src/utils/__tests__/groupByDest.test.js src/utils/__tests__/calcMiles.test.js
git commit -m "feat: add groupByDest and calcMiles utilities with tests"
```

---

## Task 4: Utility — timezones

**Files:**
- Create: `src/utils/timezones.js`
- Create: `src/utils/__tests__/timezones.test.js`

- [ ] **Step 1: Write failing tests**

Create `src/utils/__tests__/timezones.test.js`:

```js
import { describe, it, expect } from 'vitest';
import { getDestinationTimezone, computeTimezoneChanges } from '../timezones.js';

describe('getDestinationTimezone', () => {
  it('returns Central for Waco, TX', () => {
    expect(getDestinationTimezone('Waco, TX')).toBe('Central');
  });
  it('returns Pacific for San Diego, CA', () => {
    expect(getDestinationTimezone('San Diego, CA')).toBe('Pacific');
  });
  it('returns Eastern for Clemson, SC', () => {
    expect(getDestinationTimezone('Clemson, SC')).toBe('Eastern');
  });
  it('returns Mountain for Tucson, AZ', () => {
    expect(getDestinationTimezone('Tucson, AZ')).toBe('Mountain');
  });
  it('defaults to Central for unrecognized location', () => {
    expect(getDestinationTimezone('Unknown Place')).toBe('Central');
  });
});

describe('computeTimezoneChanges', () => {
  const HOME = { city: 'Waco, TX' };
  const dests = [
    { location: 'Waco, TX', home: true, tripId: null },
    { location: 'San Diego, CA', home: false, tripId: null },
    { location: 'Clemson, SC', home: false, tripId: null },
    { location: 'DeLand, FL', home: false, tripId: 'florida-swing' },
    { location: 'Orlando, FL', home: false, tripId: 'florida-swing' },
    { location: 'Lubbock, TX', home: false, tripId: null },
  ];

  it('excludes home destinations', () => {
    const changes = computeTimezoneChanges(dests, [], HOME);
    expect(Object.values(changes).flat().every(d => !d.home)).toBe(true);
  });

  it('excludes destinations in the same zone as home', () => {
    const changes = computeTimezoneChanges(dests, [], HOME);
    expect(changes['Central']).toBeUndefined();
  });

  it('groups crossing destinations by zone', () => {
    const changes = computeTimezoneChanges(dests, [], HOME);
    expect(changes['Pacific']).toHaveLength(1);
    expect(changes['Eastern']).toHaveLength(3); // Clemson, DeLand, Orlando
  });

  it('counts each zone once per multi-stop trip', () => {
    const trips = [{ id: 'florida-swing', stops: ['DeLand, FL', 'Orlando, FL'] }];
    const changes = computeTimezoneChanges(dests, trips, HOME);
    // DeLand and Orlando are both Eastern — should only count once for the trip
    expect(changes['Eastern']).toHaveLength(2); // Clemson (no trip) + once for the swing trip
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
npm test
```

Expected: FAIL — `Cannot find module '../timezones.js'`

- [ ] **Step 3: Create `src/utils/timezones.js`**

```js
// Maps 2-letter state abbreviation → time zone name
const STATE_ABBR_TIMEZONES = {
  AL: 'Central',  AK: 'Alaska',   AZ: 'Mountain', AR: 'Central',  CA: 'Pacific',
  CO: 'Mountain', CT: 'Eastern',  DE: 'Eastern',  FL: 'Eastern',  GA: 'Eastern',
  HI: 'Hawaii',   ID: 'Mountain', IL: 'Central',  IN: 'Eastern',  IA: 'Central',
  KS: 'Central',  KY: 'Eastern',  LA: 'Central',  ME: 'Eastern',  MD: 'Eastern',
  MA: 'Eastern',  MI: 'Eastern',  MN: 'Central',  MS: 'Central',  MO: 'Central',
  MT: 'Mountain', NE: 'Central',  NV: 'Pacific',  NH: 'Eastern',  NJ: 'Eastern',
  NM: 'Mountain', NY: 'Eastern',  NC: 'Eastern',  ND: 'Central',  OH: 'Eastern',
  OK: 'Central',  OR: 'Pacific',  PA: 'Eastern',  RI: 'Eastern',  SC: 'Eastern',
  SD: 'Central',  TN: 'Central',  TX: 'Central',  UT: 'Mountain', VT: 'Eastern',
  VA: 'Eastern',  WA: 'Pacific',  WV: 'Eastern',  WI: 'Central',  WY: 'Mountain',
  DC: 'Eastern',
};

// Maps FIPS code (zero-padded 2-digit string) → time zone name.
// Used to color state SVG paths by time zone.
export const FIPS_TIMEZONES = {
  '01': 'Central',   // Alabama
  '02': 'Alaska',    // Alaska
  '04': 'Mountain',  // Arizona
  '05': 'Central',   // Arkansas
  '06': 'Pacific',   // California
  '08': 'Mountain',  // Colorado
  '09': 'Eastern',   // Connecticut
  '10': 'Eastern',   // Delaware
  '11': 'Eastern',   // DC
  '12': 'Eastern',   // Florida
  '13': 'Eastern',   // Georgia
  '15': 'Hawaii',    // Hawaii
  '16': 'Mountain',  // Idaho
  '17': 'Central',   // Illinois
  '18': 'Eastern',   // Indiana
  '19': 'Central',   // Iowa
  '20': 'Central',   // Kansas
  '21': 'Eastern',   // Kentucky
  '22': 'Central',   // Louisiana
  '23': 'Eastern',   // Maine
  '24': 'Eastern',   // Maryland
  '25': 'Eastern',   // Massachusetts
  '26': 'Eastern',   // Michigan
  '27': 'Central',   // Minnesota
  '28': 'Central',   // Mississippi
  '29': 'Central',   // Missouri
  '30': 'Mountain',  // Montana
  '31': 'Central',   // Nebraska
  '32': 'Pacific',   // Nevada
  '33': 'Eastern',   // New Hampshire
  '34': 'Eastern',   // New Jersey
  '35': 'Mountain',  // New Mexico
  '36': 'Eastern',   // New York
  '37': 'Eastern',   // North Carolina
  '38': 'Central',   // North Dakota
  '39': 'Eastern',   // Ohio
  '40': 'Central',   // Oklahoma
  '41': 'Pacific',   // Oregon
  '42': 'Eastern',   // Pennsylvania
  '44': 'Eastern',   // Rhode Island
  '45': 'Eastern',   // South Carolina
  '46': 'Central',   // South Dakota
  '47': 'Central',   // Tennessee
  '48': 'Central',   // Texas
  '49': 'Mountain',  // Utah
  '50': 'Eastern',   // Vermont
  '51': 'Eastern',   // Virginia
  '53': 'Pacific',   // Washington
  '54': 'Eastern',   // West Virginia
  '55': 'Central',   // Wisconsin
  '56': 'Mountain',  // Wyoming
};

// rgba fill colors for SVG state tints — applied over the dark base fill
export const TZ_FILL_COLORS = {
  Pacific:  'rgba(99, 179, 237, 0.18)',
  Mountain: 'rgba(154, 230, 180, 0.18)',
  Central:  'rgba(252, 211, 77, 0.15)',
  Eastern:  'rgba(245, 101, 101, 0.18)',
};

// Colors for floating zone label text
export const TZ_LABEL_COLORS = {
  Pacific:  'rgba(99, 179, 237, 0.70)',
  Mountain: 'rgba(154, 230, 180, 0.70)',
  Central:  'rgba(252, 211, 77, 0.70)',
  Eastern:  'rgba(245, 101, 101, 0.70)',
};

// Short display abbreviations
export const TZ_ABBR = {
  Pacific: 'PT', Mountain: 'MT', Central: 'CT', Eastern: 'ET',
};

// Derives time zone from a location string like "San Diego, CA"
export function getDestinationTimezone(location) {
  const match = location.match(/,\s*([A-Z]{2})$/);
  if (!match) return 'Central';
  return STATE_ABBR_TIMEZONES[match[1]] || 'Central';
}

// Returns a map of { zone: [destination, ...] } for away destinations
// that cross a time zone boundary from the home city.
// Multi-stop trips that visit multiple destinations in the same foreign zone
// are counted only once for that zone.
export function computeTimezoneChanges(destinations, trips, home) {
  const homeZone = getDestinationTimezone(home.city);
  const changes = {};
  const tripZonesSeen = {};

  destinations
    .filter(d => !d.home)
    .forEach(dest => {
      const zone = getDestinationTimezone(dest.location);
      if (zone === homeZone) return;

      if (dest.tripId) {
        if (!tripZonesSeen[dest.tripId]) tripZonesSeen[dest.tripId] = new Set();
        if (tripZonesSeen[dest.tripId].has(zone)) return;
        tripZonesSeen[dest.tripId].add(zone);
      }

      if (!changes[zone]) changes[zone] = [];
      changes[zone].push(dest);
    });

  return changes;
}
```

- [ ] **Step 4: Run tests**

```bash
npm test
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/utils/timezones.js src/utils/__tests__/timezones.test.js
git commit -m "feat: add timezones utility with FIPS map and crossing computation"
```

---

## Task 5: Utility — congestion

**Files:**
- Create: `src/utils/congestion.js`
- Create: `src/utils/__tests__/congestion.test.js`

- [ ] **Step 1: Write failing tests**

Create `src/utils/__tests__/congestion.test.js`:

```js
import { describe, it, expect } from 'vitest';
import { detectCongestion, dayOfYearToDisplay } from '../congestion.js';

// 8 games in 6 days (Mar 6-11) — should flag with threshold {games:5, windowDays:7}
const DENSE_GAMES = [
  { date: 'Mar 6',  opponent: 'Iowa State', location: 'Waco, TX',  home: true },
  { date: 'Mar 6',  opponent: 'Iowa State', location: 'Waco, TX',  home: true },
  { date: 'Mar 7-8',opponent: 'Iowa State', location: 'Waco, TX',  home: true },
  { date: 'Mar 11', opponent: 'Stetson',   location: 'DeLand, FL', home: false },
  { date: 'Mar 13', opponent: 'UCF',       location: 'Orlando, FL',home: false },
  { date: 'Mar 14', opponent: 'UCF',       location: 'Orlando, FL',home: false },
  { date: 'Mar 15', opponent: 'UCF',       location: 'Orlando, FL',home: false },
];

// 2 games in 10 days — should not flag
const SPARSE_GAMES = [
  { date: 'Feb 5',  opponent: 'A', location: 'Waco, TX', home: true },
  { date: 'Feb 25', opponent: 'B', location: 'Huntsville, TX', home: false },
];

describe('detectCongestion', () => {
  const threshold = { games: 5, windowDays: 7 };

  it('returns empty array when no congestion', () => {
    expect(detectCongestion(SPARSE_GAMES, threshold)).toHaveLength(0);
  });

  it('flags a dense game cluster', () => {
    const periods = detectCongestion(DENSE_GAMES, threshold);
    expect(periods.length).toBeGreaterThan(0);
  });

  it('flagged period contains game count >= threshold', () => {
    const periods = detectCongestion(DENSE_GAMES, threshold);
    expect(periods[0].gameCount).toBeGreaterThanOrEqual(5);
  });

  it('flagged period has startDoy and endDoy', () => {
    const periods = detectCongestion(DENSE_GAMES, threshold);
    expect(periods[0]).toHaveProperty('startDoy');
    expect(periods[0]).toHaveProperty('endDoy');
    expect(periods[0].endDoy).toBeGreaterThan(periods[0].startDoy);
  });
});

describe('dayOfYearToDisplay', () => {
  it('converts doy 1 to "Jan 1"', () => {
    expect(dayOfYearToDisplay(1)).toBe('Jan 1');
  });
  it('converts doy 32 to "Feb 1"', () => {
    expect(dayOfYearToDisplay(32)).toBe('Feb 1');
  });
  it('converts doy 60 to "Mar 1"', () => {
    expect(dayOfYearToDisplay(60)).toBe('Mar 1');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
npm test
```

Expected: FAIL — `Cannot find module '../congestion.js'`

- [ ] **Step 3: Create `src/utils/congestion.js`**

```js
import { parseDateAsDayOfYear } from './parseDate.js';

const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
// Cumulative days before each month (non-leap year, 0-indexed by month 0=Jan)
const MONTH_OFFSETS = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365];

// Detects windows of windowDays days containing >= minGames games.
// Returns an array of period objects: { startDoy, endDoy, games, gameCount }.
// Once a game is part of a flagged period, it does not seed a new period.
export function detectCongestion(games, { games: minGames, windowDays }) {
  const dated = games
    .map(g => ({ ...g, doy: parseDateAsDayOfYear(g.date) }))
    .sort((a, b) => a.doy - b.doy);

  const covered = new Set();
  const periods = [];

  for (let i = 0; i < dated.length; i++) {
    if (covered.has(i)) continue;
    const windowEnd = dated[i].doy + windowDays - 1;

    const inWindow = dated.reduce((acc, g, j) => {
      if (g.doy >= dated[i].doy && g.doy <= windowEnd) acc.push({ game: g, idx: j });
      return acc;
    }, []);

    if (inWindow.length >= minGames) {
      inWindow.forEach(({ idx }) => covered.add(idx));
      periods.push({
        startDoy: dated[i].doy,
        endDoy: windowEnd,
        games: inWindow.map(({ game }) => game),
        gameCount: inWindow.length,
      });
    }
  }

  return periods;
}

// Converts a day-of-year number back to a display string like "Mar 6"
export function dayOfYearToDisplay(doy) {
  let m = 0;
  while (m < 11 && MONTH_OFFSETS[m + 1] < doy) m++;
  const day = doy - MONTH_OFFSETS[m];
  return `${MONTHS[m]} ${day}`;
}
```

- [ ] **Step 4: Run tests**

```bash
npm test
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/utils/congestion.js src/utils/__tests__/congestion.test.js
git commit -m "feat: add congestion detection utility with tests"
```

---

## Task 6: Data — softball.json and sport registry

**Files:**
- Create: `src/data/softball.json`
- Create: `src/data/index.js`

No unit tests — static data. Verify by running the dev server after Task 8 (USMap).

- [ ] **Step 1: Create `src/data/softball.json`**

Convert the existing `games` array from `baylor-softball-travel-map.jsx`. Key changes:
- `swing: "florida-swing"` → `tripId: "florida-swing"` on each Florida Swing game
- All other games get `tripId: null`
- Add `travelMode` to each game (null for home games)
- `TRIP_SWINGS` → `trips` array with `travelMode` added

```json
{
  "sport": "softball",
  "label": "Softball",
  "season": "2026",
  "lastUpdated": "2026-04-09",
  "home": { "city": "Waco, TX", "lat": 31.5493, "lng": -97.1467 },
  "colors": { "conference": "#FFB81C", "nonConference": "#4ecdc4" },
  "congestionThreshold": { "games": 5, "windowDays": 7 },
  "trips": [
    {
      "id": "florida-swing",
      "label": "Florida Swing",
      "travelMode": "flight",
      "stops": ["DeLand, FL", "Orlando, FL"]
    }
  ],
  "games": [
    { "date": "Feb 5",   "opponent": "Mississippi State", "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": "L 0-10", "conference": false, "tournament": "Getterman Classic", "tripId": null, "travelMode": null },
    { "date": "Feb 6",   "opponent": "New Mexico",        "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": "W 8-7",  "conference": false, "tournament": "Getterman Classic", "tripId": null, "travelMode": null },
    { "date": "Feb 6",   "opponent": "Wichita State",     "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": "W 3-2",  "conference": false, "tournament": "Getterman Classic", "tripId": null, "travelMode": null },
    { "date": "Feb 7",   "opponent": "Wichita State",     "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": "W 9-8",  "conference": false, "tournament": "Getterman Classic", "tripId": null, "travelMode": null },
    { "date": "Feb 8",   "opponent": "Northwestern St.",  "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": "W 9-1",  "conference": false, "tournament": "Getterman Classic", "tripId": null, "travelMode": null },
    { "date": "Feb 10",  "opponent": "South Dakota St.",  "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": "W 10-2", "conference": false, "tripId": null, "travelMode": null },
    { "date": "Feb 12",  "opponent": "San Diego State",   "location": "San Diego, CA",  "lat": 32.7749, "lng": -117.0714, "home": false, "result": "L 3-4",  "conference": false, "tournament": "Campbell/Cartier Classic", "tripId": null, "travelMode": "flight" },
    { "date": "Feb 13",  "opponent": "Oregon State",      "location": "San Diego, CA",  "lat": 32.7749, "lng": -117.0714, "home": false, "result": "W 5-4",  "conference": false, "tournament": "Campbell/Cartier Classic", "tripId": null, "travelMode": "flight" },
    { "date": "Feb 13",  "opponent": "San Diego State",   "location": "San Diego, CA",  "lat": 32.7749, "lng": -117.0714, "home": false, "result": "W 11-2", "conference": false, "tournament": "Campbell/Cartier Classic", "tripId": null, "travelMode": "flight" },
    { "date": "Feb 14",  "opponent": "Fordham",           "location": "San Diego, CA",  "lat": 32.7749, "lng": -117.0714, "home": false, "result": "W 6-1",  "conference": false, "tournament": "Campbell/Cartier Classic", "tripId": null, "travelMode": "flight" },
    { "date": "Feb 14",  "opponent": "North Dakota",      "location": "San Diego, CA",  "lat": 32.7749, "lng": -117.0714, "home": false, "result": "W 2-0",  "conference": false, "tournament": "Campbell/Cartier Classic", "tripId": null, "travelMode": "flight" },
    { "date": "Feb 20",  "opponent": "Lipscomb",          "location": "Clemson, SC",    "lat": 34.6834, "lng": -82.8374,  "home": false, "result": "W 6-4",  "conference": false, "tournament": "Clemson Classic", "tripId": null, "travelMode": "flight" },
    { "date": "Feb 21",  "opponent": "Coastal Carolina",  "location": "Clemson, SC",    "lat": 34.6834, "lng": -82.8374,  "home": false, "result": "W 3-2",  "conference": false, "tournament": "Clemson Classic", "tripId": null, "travelMode": "flight" },
    { "date": "Feb 21",  "opponent": "Clemson",           "location": "Clemson, SC",    "lat": 34.6834, "lng": -82.8374,  "home": false, "result": "L 0-8",  "conference": false, "tournament": "Clemson Classic", "tripId": null, "travelMode": "flight" },
    { "date": "Feb 22",  "opponent": "Clemson",           "location": "Clemson, SC",    "lat": 34.6834, "lng": -82.8374,  "home": false, "result": "L 0-3",  "conference": false, "tournament": "Clemson Classic", "tripId": null, "travelMode": "flight" },
    { "date": "Feb 25",  "opponent": "Sam Houston",       "location": "Huntsville, TX", "lat": 30.7235, "lng": -95.5508,  "home": false, "result": "W 6-3",  "conference": false, "tripId": null, "travelMode": "bus" },
    { "date": "Feb 28",  "opponent": "McNeese",           "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": "L 4-5",  "conference": false, "tripId": null, "travelMode": null },
    { "date": "Feb 28",  "opponent": "McNeese",           "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": "L 2-6",  "conference": false, "tripId": null, "travelMode": null },
    { "date": "Mar 1",   "opponent": "McNeese",           "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": "W 8-0",  "conference": false, "tripId": null, "travelMode": null },
    { "date": "Mar 3",   "opponent": "Stephen F. Austin", "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": "W 4-0",  "conference": false, "tripId": null, "travelMode": null },
    { "date": "Mar 6",   "opponent": "Iowa State",        "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": "W 8-1",  "conference": false, "tripId": null, "travelMode": null },
    { "date": "Mar 6",   "opponent": "Iowa State",        "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": "W 4-2",  "conference": false, "tripId": null, "travelMode": null },
    { "date": "Mar 7-8", "opponent": "Iowa State",        "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": "W 5-4",  "conference": false, "tripId": null, "travelMode": null },
    { "date": "Mar 11",  "opponent": "Stetson",           "location": "DeLand, FL",     "lat": 29.0283, "lng": -81.3032,  "home": false, "result": null,      "conference": false, "tripId": "florida-swing", "travelMode": null },
    { "date": "Mar 13",  "opponent": "UCF",               "location": "Orlando, FL",    "lat": 28.6024, "lng": -81.2001,  "home": false, "result": null,      "conference": true,  "tripId": "florida-swing", "travelMode": null },
    { "date": "Mar 14",  "opponent": "UCF",               "location": "Orlando, FL",    "lat": 28.6024, "lng": -81.2001,  "home": false, "result": null,      "conference": true,  "tripId": "florida-swing", "travelMode": null },
    { "date": "Mar 15",  "opponent": "UCF",               "location": "Orlando, FL",    "lat": 28.6024, "lng": -81.2001,  "home": false, "result": null,      "conference": true,  "tripId": "florida-swing", "travelMode": null },
    { "date": "Mar 20",  "opponent": "Texas",             "location": "Austin, TX",     "lat": 30.2849, "lng": -97.7341,  "home": false, "result": null,      "conference": false, "tripId": null, "travelMode": "bus" },
    { "date": "Mar 21",  "opponent": "Texas",             "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": null,      "conference": false, "tripId": null, "travelMode": null },
    { "date": "Mar 24",  "opponent": "UT Arlington",      "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": null,      "conference": false, "tripId": null, "travelMode": null },
    { "date": "Mar 27",  "opponent": "Arizona",           "location": "Tucson, AZ",     "lat": 32.2319, "lng": -110.9501, "home": false, "result": null,      "conference": true,  "tripId": null, "travelMode": "flight" },
    { "date": "Mar 28",  "opponent": "Arizona",           "location": "Tucson, AZ",     "lat": 32.2319, "lng": -110.9501, "home": false, "result": null,      "conference": true,  "tripId": null, "travelMode": "flight" },
    { "date": "Mar 29",  "opponent": "Arizona",           "location": "Tucson, AZ",     "lat": 32.2319, "lng": -110.9501, "home": false, "result": null,      "conference": true,  "tripId": null, "travelMode": "flight" },
    { "date": "Mar 31",  "opponent": "Incarnate Word",    "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": null,      "conference": false, "tripId": null, "travelMode": null },
    { "date": "Apr 2",   "opponent": "Houston",           "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": null,      "conference": false, "tripId": null, "travelMode": null },
    { "date": "Apr 3",   "opponent": "Houston",           "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": null,      "conference": true,  "tripId": null, "travelMode": null },
    { "date": "Apr 4",   "opponent": "Houston",           "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": null,      "conference": true,  "tripId": null, "travelMode": null },
    { "date": "Apr 6",   "opponent": "Lamar",             "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": null,      "conference": false, "tripId": null, "travelMode": null },
    { "date": "Apr 8",   "opponent": "UT Arlington",      "location": "Arlington, TX",  "lat": 32.7299, "lng": -97.1151,  "home": false, "result": null,      "conference": false, "tripId": null, "travelMode": "bus" },
    { "date": "Apr 10",  "opponent": "Kansas",            "location": "Lawrence, KS",   "lat": 38.9543, "lng": -95.2558,  "home": false, "result": null,      "conference": true,  "tripId": null, "travelMode": "charter" },
    { "date": "Apr 11",  "opponent": "Kansas",            "location": "Lawrence, KS",   "lat": 38.9543, "lng": -95.2558,  "home": false, "result": null,      "conference": true,  "tripId": null, "travelMode": "charter" },
    { "date": "Apr 12",  "opponent": "Kansas",            "location": "Lawrence, KS",   "lat": 38.9543, "lng": -95.2558,  "home": false, "result": null,      "conference": true,  "tripId": null, "travelMode": "charter" },
    { "date": "Apr 15",  "opponent": "Texas A&M",         "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": null,      "conference": false, "tripId": null, "travelMode": null },
    { "date": "Apr 17",  "opponent": "Utah",              "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": null,      "conference": true,  "tripId": null, "travelMode": null },
    { "date": "Apr 18",  "opponent": "Utah",              "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": null,      "conference": true,  "tripId": null, "travelMode": null },
    { "date": "Apr 19",  "opponent": "Utah",              "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": null,      "conference": true,  "tripId": null, "travelMode": null },
    { "date": "Apr 22",  "opponent": "Texas State",       "location": "San Marcos, TX", "lat": 29.8833, "lng": -97.9414,  "home": false, "result": null,      "conference": false, "tripId": null, "travelMode": "bus" },
    { "date": "Apr 24",  "opponent": "Oklahoma State",    "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": null,      "conference": true,  "tripId": null, "travelMode": null },
    { "date": "Apr 25",  "opponent": "Oklahoma State",    "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": null,      "conference": true,  "tripId": null, "travelMode": null },
    { "date": "Apr 26",  "opponent": "Oklahoma State",    "location": "Waco, TX",       "lat": 31.5493, "lng": -97.1467,  "home": true,  "result": null,      "conference": true,  "tripId": null, "travelMode": null },
    { "date": "Apr 30",  "opponent": "Texas Tech",        "location": "Lubbock, TX",    "lat": 33.5843, "lng": -101.8456, "home": false, "result": null,      "conference": true,  "tripId": null, "travelMode": "bus" },
    { "date": "May 1",   "opponent": "Texas Tech",        "location": "Lubbock, TX",    "lat": 33.5843, "lng": -101.8456, "home": false, "result": null,      "conference": true,  "tripId": null, "travelMode": "bus" },
    { "date": "May 2",   "opponent": "Texas Tech",        "location": "Lubbock, TX",    "lat": 33.5843, "lng": -101.8456, "home": false, "result": null,      "conference": true,  "tripId": null, "travelMode": "bus" },
    { "date": "May 6-9", "opponent": "Big 12 Tournament", "location": "Oklahoma City, OK", "lat": 35.4676, "lng": -97.5164, "home": false, "result": null,   "conference": true,  "tournament": "Big 12 Tournament", "tripId": null, "travelMode": "bus" }
  ]
}
```

- [ ] **Step 2: Create `src/data/index.js`**

```js
import softball from './softball.json';

// Active sports have a full data object imported above.
// Coming-soon entries are stubs — SportGrid renders them as muted cards.
export const sports = [
  softball,
  { sport: 'baseball',    label: 'Baseball',    season: '2026', status: 'coming-soon' },
  { sport: 'soccer',      label: 'Soccer',      season: '2026', status: 'coming-soon' },
  { sport: 'basketball',  label: 'Basketball',  season: '2026', status: 'coming-soon' },
  { sport: 'football',    label: 'Football',    season: '2026', status: 'coming-soon' },
  { sport: 'volleyball',  label: 'Volleyball',  season: '2026', status: 'coming-soon' },
];
```

- [ ] **Step 3: Commit**

```bash
git add src/data/
git commit -m "feat: add softball.json data file and sport registry"
```

---

## Task 7: USMap component

**Files:**
- Modify: `src/components/USMap.jsx` (replace stub with full implementation)

This is a refactor of the `USMap` function from `baylor-softball-travel-map.jsx` with these changes:
- Accepts `sport` prop (`{ home, trips, colors }`) instead of hardcoded `WACO`/`TRIP_SWINGS`
- `swing` field on destinations → `tripId`
- `decodeTopo` now preserves `id: g.id` (FIPS code) for timezone lookup in Task 8
- All other behavior (zoom, arcs, glow, labels, mileage) is identical to the original

- [ ] **Step 1: Replace `src/components/USMap.jsx` with full implementation**

```jsx
import { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import * as d3 from 'd3';

function decodeTopo(topo) {
  const { arcs, transform, objects } = topo;
  const { scale, translate } = transform;
  const decoded = arcs.map(arc => {
    let x = 0, y = 0;
    return arc.map(([dx, dy]) => {
      x += dx; y += dy;
      return [x * scale[0] + translate[0], y * scale[1] + translate[1]];
    });
  });
  function resolve(idx) { return idx >= 0 ? decoded[idx] : [...decoded[~idx]].reverse(); }
  function ring(indices) {
    let c = [];
    indices.forEach(i => { const pts = resolve(i); if (c.length) pts.shift(); c = c.concat(pts); });
    return c;
  }
  return objects.states.geometries.map(g => {
    const base = { id: g.id, properties: g.properties || {} };
    if (g.type === 'Polygon') return { type: 'Feature', ...base, geometry: { type: 'Polygon', coordinates: g.arcs.map(r => ring(r)) } };
    if (g.type === 'MultiPolygon') return { type: 'Feature', ...base, geometry: { type: 'MultiPolygon', coordinates: g.arcs.map(p => p.map(r => ring(r))) } };
    return null;
  }).filter(Boolean);
}

export default function USMap({ sport, destinations, selectedDest, hoveredDest, onHover, onSelect, showTimezones }) {
  const containerRef = useRef(null);
  const svgRef = useRef(null);
  const [features, setFeatures] = useState([]);
  const [dims, setDims] = useState({ w: 900, h: 560 });
  const [zoom, setZoom] = useState({ k: 1, x: 0, y: 0 });

  const home = sport.home;
  const trips = sport.trips || [];
  const colors = sport.colors;

  useEffect(() => {
    fetch('https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json')
      .then(r => r.json())
      .then(topo => setFeatures(decodeTopo(topo)))
      .catch(() => {});
  }, []);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver(entries => {
      const { width, height } = entries[0].contentRect;
      if (width > 50) setDims({ w: width, h: height });
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  useEffect(() => {
    const svg = d3.select(svgRef.current);
    if (!svg.node()) return;
    const zb = d3.zoom().scaleExtent([1, 8]).on('zoom', e => {
      setZoom({ k: e.transform.k, x: e.transform.x, y: e.transform.y });
    });
    svg.call(zb);
    svgRef.current.__zoomBehavior = zb;
    return () => svg.on('.zoom', null);
  }, []);

  const handleZoomIn  = useCallback(() => { const s = d3.select(svgRef.current); const zb = svgRef.current.__zoomBehavior; if (zb) s.transition().duration(300).call(zb.scaleBy, 1.5); }, []);
  const handleZoomOut = useCallback(() => { const s = d3.select(svgRef.current); const zb = svgRef.current.__zoomBehavior; if (zb) s.transition().duration(300).call(zb.scaleBy, 0.67); }, []);
  const handleReset   = useCallback(() => { const s = d3.select(svgRef.current); const zb = svgRef.current.__zoomBehavior; if (zb) s.transition().duration(400).call(zb.transform, d3.zoomIdentity); }, []);

  const projection = useMemo(() => d3.geoAlbersUsa().scale(dims.w * 1.25).translate([dims.w / 2, dims.h / 2]), [dims]);
  const pathGen = useMemo(() => d3.geoPath().projection(projection), [projection]);
  const proj = (lat, lng) => projection([lng, lat]);
  const homeXY = proj(home.lat, home.lng);
  const active = selectedDest || hoveredDest;

  function arcPath(x1, y1, x2, y2) {
    const dx = x2 - x1, dy = y2 - y1;
    const dist = Math.sqrt(dx * dx + dy * dy);
    if (dist < 1) return `M ${x1} ${y1} L ${x2} ${y2}`;
    const bend = Math.min(dist * 0.28, 70);
    const mx = (x1 + x2) / 2 - (dy / dist) * bend;
    const my = (y1 + y2) / 2 + (dx / dist) * bend;
    return `M ${x1} ${y1} Q ${mx} ${my} ${x2} ${y2}`;
  }

  // Resolve travelMode for a destination (game-level overrides trip-level)
  function getTravelMode(dest) {
    if (!dest.tripId) {
      const g = dest.games.find(g => g.travelMode);
      return g ? g.travelMode : 'tbd';
    }
    const g = dest.games.find(g => g.travelMode);
    if (g) return g.travelMode;
    const trip = trips.find(t => t.id === dest.tripId);
    return trip ? (trip.travelMode || 'tbd') : 'tbd';
  }

  function travelModeDash(mode) {
    if (mode === 'bus') return '6,4';
    if (mode === 'tbd') return '2,3';
    return null; // flight / charter = solid
  }

  const awayDests = destinations.filter(d => !d.home);

  const tripRoutes = useMemo(() => {
    const routes = [];
    const handled = new Set();
    trips.forEach(trip => {
      const stops = trip.stops.map(loc => awayDests.find(d => d.location === loc)).filter(Boolean);
      if (stops.length < 2) return;
      const isActive = active && stops.some(s => s.location === active.location);
      const mode = trip.travelMode || 'tbd';
      const dash = travelModeDash(mode);
      const legs = [];
      const allStops = [{ lat: home.lat, lng: home.lng }, ...stops, { lat: home.lat, lng: home.lng }];
      for (let i = 0; i < allStops.length - 1; i++) {
        const [x1, y1] = proj(allStops[i].lat, allStops[i].lng) || [0, 0];
        const [x2, y2] = proj(allStops[i + 1].lat, allStops[i + 1].lng) || [0, 0];
        legs.push({ path: arcPath(x1, y1, x2, y2), x2, y2 });
      }
      routes.push({ trip, stops, legs, isActive, dash });
      stops.forEach(s => handled.add(s.location));
    });
    return { routes, handledLocations: handled };
  }, [awayDests, trips, home, active, proj]);

  const soloArcs = useMemo(() => {
    return awayDests
      .filter(d => !tripRoutes.handledLocations.has(d.location))
      .map(d => {
        const [hx, hy] = homeXY || [0, 0];
        const xy = proj(d.lat, d.lng);
        if (!xy) return null;
        const [dx, dy] = xy;
        const isActive = active && active.location === d.location;
        const mode = getTravelMode(d);
        const dash = travelModeDash(mode);
        return { dest: d, path: arcPath(hx, hy, dx, dy), dx, dy, isActive, dash };
      })
      .filter(Boolean);
  }, [awayDests, homeXY, active]);

  const arcColor = (dest) => dest.games.some(g => g.conference) ? colors.conference : colors.nonConference;

  if (!homeXY) return <div ref={containerRef} style={{ flex: 1 }} />;

  return (
    <div ref={containerRef} style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
      <svg
        ref={svgRef}
        width={dims.w}
        height={dims.h}
        style={{ display: 'block', cursor: 'grab', userSelect: 'none' }}
      >
        <g transform={`translate(${zoom.x},${zoom.y}) scale(${zoom.k})`}>
          {/* State base fills */}
          {features.map((f, i) => (
            <path key={`bg-${i}`} d={pathGen(f)} fill="#1e293b" />
          ))}

          {/* State borders */}
          {features.map((f, i) => (
            <path key={`border-${i}`} d={pathGen(f)} fill="none" stroke="#334155" strokeWidth={0.5 / zoom.k} />
          ))}

          {/* Trip routes (multi-stop) */}
          {tripRoutes.routes.map(({ trip, legs, isActive, dash }) =>
            legs.map((leg, li) => (
              <path
                key={`trip-${trip.id}-${li}`}
                d={leg.path}
                fill="none"
                stroke={isActive ? '#fff' : '#4ecdc4'}
                strokeWidth={(isActive ? 2.2 : 1.4) / zoom.k}
                strokeDasharray={dash ? dash.split(',').map(v => `${parseFloat(v) / zoom.k}`).join(',') : undefined}
                opacity={isActive ? 1 : 0.55}
                filter={isActive ? 'url(#glow)' : undefined}
              />
            ))
          )}

          {/* Solo arcs */}
          {soloArcs.map(({ dest, path, isActive, dash }) => (
            <path
              key={`arc-${dest.location}`}
              d={path}
              fill="none"
              stroke={isActive ? '#fff' : arcColor(dest)}
              strokeWidth={(isActive ? 2.2 : 1.4) / zoom.k}
              strokeDasharray={dash ? dash.split(',').map(v => `${parseFloat(v) / zoom.k}`).join(',') : undefined}
              opacity={isActive ? 1 : 0.6}
              filter={isActive ? 'url(#glow)' : undefined}
            />
          ))}

          {/* Destination dots */}
          {awayDests.map(d => {
            const xy = proj(d.lat, d.lng);
            if (!xy) return null;
            const isActive = active && active.location === d.location;
            return (
              <circle
                key={`dot-${d.location}`}
                cx={xy[0]} cy={xy[1]}
                r={(isActive ? 6 : 4) / zoom.k}
                fill={isActive ? '#fff' : arcColor(d)}
                stroke={isActive ? arcColor(d) : 'none'}
                strokeWidth={1.5 / zoom.k}
                style={{ cursor: 'pointer' }}
                onMouseEnter={() => onHover(d)}
                onMouseLeave={() => onHover(null)}
                onClick={() => onSelect(d)}
                filter={isActive ? 'url(#glow)' : undefined}
              />
            );
          })}

          {/* Mileage label on hover */}
          {active && (() => {
            const xy = proj(active.lat, active.lng);
            if (!xy) return null;
            const trip = active.tripId ? trips.find(t => t.id === active.tripId) : null;
            let milesLabel = '';
            if (trip) {
              const stops = trip.stops.map(loc => awayDests.find(d => d.location === loc)).filter(Boolean);
              // import calcTotalMiles inline for display
              milesLabel = `${Math.round(active.distMiles || 0).toLocaleString()} mi`;
            } else {
              milesLabel = active.distMiles ? `${Math.round(active.distMiles).toLocaleString()} mi RT` : '';
            }
            return (
              <text
                x={xy[0]} y={xy[1] - 10 / zoom.k}
                textAnchor="middle"
                fontSize={11 / zoom.k}
                fill="#fff"
                fontFamily="JetBrains Mono, monospace"
                style={{ pointerEvents: 'none' }}
              >
                {active.location}
              </text>
            );
          })()}

          {/* Home dot (Waco) */}
          {homeXY && (
            <circle
              cx={homeXY[0]} cy={homeXY[1]}
              r={5 / zoom.k}
              fill={colors.conference}
              stroke="#fff"
              strokeWidth={1.5 / zoom.k}
            />
          )}

          <defs>
            <filter id="glow">
              <feGaussianBlur stdDeviation="3" result="coloredBlur" />
              <feMerge><feMergeNode in="coloredBlur" /><feMergeNode in="SourceGraphic" /></feMerge>
            </filter>
          </defs>
        </g>
      </svg>

      {/* Zoom controls */}
      <div style={{ position: 'absolute', bottom: 16, right: 16, display: 'flex', flexDirection: 'column', gap: 4 }}>
        {zoom.k > 1.05 && (
          <div style={{ color: '#64748b', fontSize: 11, textAlign: 'center', fontFamily: 'JetBrains Mono, monospace', marginBottom: 4 }}>
            {Math.round(zoom.k * 100)}%
          </div>
        )}
        {[{ label: '+', fn: handleZoomIn }, { label: '−', fn: handleZoomOut }, { label: '⊙', fn: handleReset }].map(({ label, fn }) => (
          <button
            key={label}
            onClick={fn}
            style={{ width: 32, height: 32, background: '#1e293b', border: '1px solid #334155', color: '#94a3b8', borderRadius: 4, cursor: 'pointer', fontSize: 16, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
          >
            {label}
          </button>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify it renders (temporary wiring in App.jsx)**

Temporarily update `src/App.jsx` to render USMap with softball data:

```jsx
import { useState } from 'react';
import USMap from './components/USMap.jsx';
import softball from './data/softball.json';
import { groupByDest } from './utils/groupByDest.js';

export default function App() {
  const [hovered, setHovered] = useState(null);
  const [selected, setSelected] = useState(null);
  const destinations = groupByDest(softball.games);
  return (
    <div style={{ display: 'flex', height: '100vh', background: '#0f172a' }}>
      <USMap
        sport={softball}
        destinations={destinations}
        selectedDest={selected}
        hoveredDest={hovered}
        onHover={setHovered}
        onSelect={d => setSelected(prev => prev?.location === d.location ? null : d)}
        showTimezones={false}
      />
    </div>
  );
}
```

```bash
npm run dev
```

Expected: US map renders with softball arcs. Hover/click on destinations works. Zoom buttons work.

- [ ] **Step 3: Revert App.jsx to stub**

```jsx
import { useState } from 'react';
export default function App() {
  return <div style={{ color: '#fff', padding: 40 }}>scaffold</div>;
}
```

- [ ] **Step 4: Commit**

```bash
git add src/components/USMap.jsx src/App.jsx
git commit -m "feat: add USMap component refactored from softball.jsx"
```

---

## Task 8: Time zone overlay in USMap

**Files:**
- Modify: `src/components/USMap.jsx`

Add the timezone tint layer between state base fills and borders. Add floating zone labels. Add a toggle button in the zoom controls.

- [ ] **Step 1: Add timezone imports at top of `USMap.jsx`**

After the `import * as d3 from 'd3';` line, add:

```jsx
import { FIPS_TIMEZONES, TZ_FILL_COLORS, TZ_LABEL_COLORS } from '../utils/timezones.js';
```

- [ ] **Step 2: Add timezone tint layer between base fills and borders**

In the SVG `<g>` element, between the `{/* State base fills */}` block and `{/* State borders */}` block, add:

```jsx
          {/* Timezone tints — rendered over base fills, under borders */}
          {showTimezones && features.map((f, i) => {
            const fips = String(f.id).padStart(2, '0');
            const zone = FIPS_TIMEZONES[fips];
            if (!zone || zone === 'Alaska' || zone === 'Hawaii') return null;
            return (
              <path
                key={`tz-${i}`}
                d={pathGen(f)}
                fill={TZ_FILL_COLORS[zone]}
                stroke="none"
                style={{ pointerEvents: 'none' }}
              />
            );
          })}

          {/* Floating timezone zone labels */}
          {showTimezones && [
            { zone: 'Pacific',  x: 0.10, y: 0.25 },
            { zone: 'Mountain', x: 0.30, y: 0.20 },
            { zone: 'Central',  x: 0.55, y: 0.20 },
            { zone: 'Eastern',  x: 0.80, y: 0.20 },
          ].map(({ zone, x, y }) => (
            <text
              key={`tz-label-${zone}`}
              x={dims.w * x}
              y={dims.h * y}
              textAnchor="middle"
              fontSize={11 / zoom.k}
              fill={TZ_LABEL_COLORS[zone]}
              fontFamily="DM Sans, sans-serif"
              fontWeight="700"
              letterSpacing="0.08em"
              style={{ pointerEvents: 'none', userSelect: 'none' }}
            >
              {zone.toUpperCase()}
            </text>
          ))}
```

Note: the floating labels are in the SVG `<g>` that is transformed by zoom/pan. Their position coordinates (`dims.w * x`) are in unzoomed space, so at zoom > 1 they will drift. To keep them fixed on screen, move them outside the `<g transform>` block in the SVG but still inside `<svg>`. Adjust the placement in the SVG directly:

```jsx
      {/* Fixed timezone labels (outside zoom transform) */}
      {showTimezones && (
        <g style={{ pointerEvents: 'none' }}>
          {[
            { zone: 'Pacific',  x: 0.10 },
            { zone: 'Mountain', x: 0.30 },
            { zone: 'Central',  x: 0.55 },
            { zone: 'Eastern',  x: 0.80 },
          ].map(({ zone, x }) => (
            <text
              key={`tz-label-${zone}`}
              x={dims.w * x}
              y={28}
              textAnchor="middle"
              fontSize={11}
              fill={TZ_LABEL_COLORS[zone]}
              fontFamily="DM Sans, sans-serif"
              fontWeight="700"
              letterSpacing="0.08em"
            >
              {zone.toUpperCase()}
            </text>
          ))}
        </g>
      )}
```

Place this `<g>` after the closing `</g>` of the zoom transform group but still inside `<svg>`.

- [ ] **Step 3: Verify timezone overlay (temporary wiring)**

Temporarily update `src/App.jsx` to pass `showTimezones={true}`:

```jsx
import { useState } from 'react';
import USMap from './components/USMap.jsx';
import softball from './data/softball.json';
import { groupByDest } from './utils/groupByDest.js';

export default function App() {
  const [hovered, setHovered] = useState(null);
  const [selected, setSelected] = useState(null);
  const destinations = groupByDest(softball.games);
  return (
    <div style={{ display: 'flex', height: '100vh', background: '#0f172a' }}>
      <USMap
        sport={softball}
        destinations={destinations}
        selectedDest={selected}
        hoveredDest={hovered}
        onHover={setHovered}
        onSelect={d => setSelected(prev => prev?.location === d.location ? null : d)}
        showTimezones={true}
      />
    </div>
  );
}
```

```bash
npm run dev
```

Expected: Each state renders with a subtle color tint. Pacific states blue, Mountain green, Central gold, Eastern red. Zone labels appear near the top of each zone. Travel arcs and dots render on top.

- [ ] **Step 4: Revert App.jsx to stub, commit**

```jsx
import { useState } from 'react';
export default function App() {
  return <div style={{ color: '#fff', padding: 40 }}>scaffold</div>;
}
```

```bash
git add src/components/USMap.jsx src/App.jsx
git commit -m "feat: add timezone tint overlay and floating labels to USMap"
```

---

## Task 9: Travel mode arc styles in USMap

**Files:**
- Modify: `src/components/USMap.jsx`

The `travelModeDash` helper and `getTravelMode` functions are already implemented in Task 7. This task adds the travel mode legend to USMap's overlay area so it's visible on the map itself.

- [ ] **Step 1: Add travel mode legend overlay to USMap**

Inside the main `<div>` container (after the `</svg>` tag and before the zoom controls `<div>`), add:

```jsx
      {/* Travel mode legend */}
      <div style={{
        position: 'absolute', bottom: 16, left: 16,
        background: 'rgba(15,23,42,0.85)', border: '1px solid #1e293b',
        borderRadius: 6, padding: '8px 12px', display: 'flex', flexDirection: 'column', gap: 5,
      }}>
        {[
          { mode: 'flight',  label: 'Flight / Charter', dash: null },
          { mode: 'bus',     label: 'Bus',               dash: '6px 4px' },
          { mode: 'tbd',     label: 'TBD',               dash: '2px 3px' },
        ].map(({ mode, label, dash }) => (
          <div key={mode} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <svg width={32} height={10}>
              <line
                x1={0} y1={5} x2={32} y2={5}
                stroke="#94a3b8"
                strokeWidth={1.5}
                strokeDasharray={dash || undefined}
              />
            </svg>
            <span style={{ color: '#64748b', fontSize: 10, fontFamily: 'DM Sans, sans-serif' }}>{label}</span>
          </div>
        ))}
      </div>
```

- [ ] **Step 2: Verify travel mode legend renders**

Temporarily restore the App.jsx wiring from Task 8 Step 3 and run `npm run dev`.

Expected: Bottom-left corner shows three legend rows with solid, dashed, and dotted line samples labeled "Flight / Charter", "Bus", "TBD". Arcs to San Diego and Clemson render solid; arcs to Huntsville/Austin/Arlington/San Marcos/Lubbock/Oklahoma City render dashed.

Revert App.jsx to stub.

- [ ] **Step 3: Commit**

```bash
git add src/components/USMap.jsx src/App.jsx
git commit -m "feat: add travel mode arc styles and legend to USMap"
```

---

## Task 10: SportMap component

**Files:**
- Modify: `src/components/SportMap.jsx` (replace stub with full implementation)

Refactored from the `App` component in `baylor-softball-travel-map.jsx`. Accepts `sport` prop (full sport JSON object) and `onBack` callback. Includes existing sidebar behavior plus timezone toggle state wired to USMap.

- [ ] **Step 1: Replace `src/components/SportMap.jsx` with full implementation**

```jsx
import { useState, useMemo } from 'react';
import USMap from './USMap.jsx';
import { groupByDest } from '../utils/groupByDest.js';
import { calcTotalMiles } from '../utils/calcMiles.js';
import { parseDate } from '../utils/parseDate.js';
import { haversine } from '../utils/haversine.js';

const FILTER_LABELS = ['All', 'Away', 'Home', 'Conference'];

export default function SportMap({ sport, onBack }) {
  const [filter, setFilter] = useState('All');
  const [selectedDest, setSelectedDest] = useState(null);
  const [hoveredDest, setHoveredDest] = useState(null);
  const [showTimezones, setShowTimezones] = useState(true);

  const home = sport.home;
  const trips = sport.trips || [];
  const colors = sport.colors;

  const allDests = useMemo(() => groupByDest(sport.games), [sport]);
  const awayDests = useMemo(() => allDests.filter(d => !d.home), [allDests]);

  const filteredGames = useMemo(() => {
    return sport.games.filter(g => {
      if (filter === 'Away') return !g.home;
      if (filter === 'Home') return g.home;
      if (filter === 'Conference') return g.conference;
      return true;
    });
  }, [sport.games, filter]);

  const destinations = useMemo(() => groupByDest(filteredGames), [filteredGames]);

  // Stats always from full unfiltered game list
  const totalMiles = useMemo(() => calcTotalMiles(awayDests, trips, home), [awayDests, trips, home]);
  const awayTrips = useMemo(() => {
    const seen = new Set();
    awayDests.forEach(d => {
      if (d.tripId) seen.add(d.tripId);
      else seen.add(d.location);
    });
    return seen.size;
  }, [awayDests]);
  const homeGames = useMemo(() => sport.games.filter(g => g.home).length, [sport]);
  const confGames = useMemo(() => sport.games.filter(g => g.conference).length, [sport]);

  const farthestDest = useMemo(() => {
    return awayDests.reduce((max, d) => {
      const mi = haversine(home.lat, home.lng, d.lat, d.lng);
      return mi > (max?.mi || 0) ? { ...d, mi } : max;
    }, null);
  }, [awayDests, home]);

  function handleSelect(dest) {
    setSelectedDest(prev => prev?.location === dest.location ? null : dest);
  }

  const sortedDests = useMemo(() => {
    return [...destinations].sort((a, b) => {
      const aDate = Math.min(...a.games.map(g => parseDate(g.date)));
      const bDate = Math.min(...b.games.map(g => parseDate(g.date)));
      return aDate - bDate;
    });
  }, [destinations]);

  const resultColor = r => r?.startsWith('W') ? '#4ade80' : r?.startsWith('L') ? '#f87171' : '#64748b';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: '#0f172a', fontFamily: 'DM Sans, sans-serif', color: '#fff', overflow: 'hidden' }}>
      {/* Header */}
      <div style={{ background: '#154734', padding: '12px 20px', display: 'flex', alignItems: 'center', gap: 16, flexShrink: 0 }}>
        <button
          onClick={onBack}
          style={{ background: 'none', border: '1px solid rgba(255,255,255,0.3)', color: '#fff', borderRadius: 4, padding: '4px 10px', cursor: 'pointer', fontSize: 13 }}
        >
          ← All Sports
        </button>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 700, fontSize: 18 }}>Baylor {sport.label} {sport.season}</div>
          <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.6)' }}>Travel Demands</div>
        </div>
        {/* Filter buttons */}
        <div style={{ display: 'flex', gap: 6 }}>
          {FILTER_LABELS.map(f => (
            <button
              key={f}
              onClick={() => { setFilter(f); setSelectedDest(null); }}
              style={{
                background: filter === f ? '#FFB81C' : 'rgba(255,255,255,0.1)',
                color: filter === f ? '#000' : '#fff',
                border: 'none', borderRadius: 4, padding: '5px 12px',
                cursor: 'pointer', fontSize: 12, fontWeight: filter === f ? 700 : 400,
              }}
            >
              {f}
            </button>
          ))}
        </div>
        {/* Timezone toggle */}
        <button
          onClick={() => setShowTimezones(v => !v)}
          style={{
            background: showTimezones ? 'rgba(99,179,237,0.2)' : 'rgba(255,255,255,0.08)',
            border: `1px solid ${showTimezones ? 'rgba(99,179,237,0.5)' : 'rgba(255,255,255,0.2)'}`,
            color: showTimezones ? 'rgba(99,179,237,0.9)' : '#64748b',
            borderRadius: 4, padding: '5px 10px', cursor: 'pointer', fontSize: 12,
          }}
        >
          Time Zones
        </button>
      </div>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Map */}
        <USMap
          sport={sport}
          destinations={destinations}
          selectedDest={selectedDest}
          hoveredDest={hoveredDest}
          onHover={setHoveredDest}
          onSelect={handleSelect}
          showTimezones={showTimezones}
        />

        {/* Sidebar */}
        <div style={{ width: 300, background: '#0c1420', borderLeft: '1px solid #1e293b', display: 'flex', flexDirection: 'column', overflow: 'hidden', flexShrink: 0 }}>
          {/* Stat cards */}
          <div style={{ padding: 16, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, flexShrink: 0 }}>
            {[
              { label: 'Total Miles', value: `${Math.round(totalMiles).toLocaleString()}`, sub: 'season travel' },
              { label: 'Away Trips',  value: awayTrips,              sub: 'unique destinations' },
              { label: 'Home Games', value: homeGames,              sub: 'at Waco' },
              { label: 'Conf. Games', value: confGames,             sub: 'Big 12' },
            ].map(({ label, value, sub }) => (
              <div key={label} style={{ background: '#1e293b', borderRadius: 6, padding: '10px 12px' }}>
                <div style={{ fontSize: 10, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 4 }}>{label}</div>
                <div style={{ fontSize: 22, fontWeight: 700, fontFamily: 'JetBrains Mono, monospace', color: colors.conference }}>{value}</div>
                <div style={{ fontSize: 10, color: '#475569' }}>{sub}</div>
              </div>
            ))}
          </div>

          {/* Farthest trip */}
          {farthestDest && (
            <div style={{ margin: '0 16px 12px', background: '#1e293b', borderRadius: 6, padding: '10px 12px', borderLeft: `3px solid ${colors.nonConference}` }}>
              <div style={{ fontSize: 10, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 2 }}>Farthest Trip</div>
              <div style={{ fontWeight: 600, fontSize: 13 }}>{farthestDest.location}</div>
              <div style={{ fontSize: 11, color: colors.nonConference, fontFamily: 'JetBrains Mono, monospace' }}>
                {Math.round(farthestDest.mi).toLocaleString()} mi one-way
              </div>
            </div>
          )}

          {/* Destination list */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '0 16px 16px' }}>
            {sortedDests.map(dest => {
              const isExpanded = selectedDest?.location === dest.location;
              const trip = dest.tripId ? trips.find(t => t.id === dest.tripId) : null;
              const mi = dest.home ? null : haversine(home.lat, home.lng, dest.lat, dest.lng);
              return (
                <div
                  key={dest.location}
                  onClick={() => handleSelect(dest)}
                  style={{
                    background: isExpanded ? '#1e293b' : 'transparent',
                    border: `1px solid ${isExpanded ? '#334155' : 'transparent'}`,
                    borderRadius: 6, marginBottom: 4, padding: '8px 10px', cursor: 'pointer',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: 13 }}>
                        {dest.home ? '⌂ ' : ''}{dest.location}
                      </div>
                      {trip && <div style={{ fontSize: 10, color: colors.nonConference }}>{trip.label}</div>}
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: 11, color: '#64748b', fontFamily: 'JetBrains Mono, monospace' }}>
                        {dest.games.length}g
                      </div>
                      {mi && <div style={{ fontSize: 10, color: '#475569' }}>{Math.round(mi).toLocaleString()} mi</div>}
                    </div>
                  </div>
                  {isExpanded && (
                    <div style={{ marginTop: 8, borderTop: '1px solid #334155', paddingTop: 8 }}>
                      {dest.games.map((g, i) => (
                        <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4, fontSize: 12 }}>
                          <div>
                            <span style={{ color: '#64748b', fontFamily: 'JetBrains Mono, monospace', marginRight: 6 }}>{g.date}</span>
                            {g.opponent}
                            {g.tournament && <span style={{ fontSize: 10, color: '#475569', marginLeft: 4 }}>({g.tournament})</span>}
                          </div>
                          <div style={{ color: resultColor(g.result), fontFamily: 'JetBrains Mono, monospace', fontSize: 11 }}>
                            {g.result || '—'}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Wire up App.jsx to test SportMap**

```jsx
import softball from './data/softball.json';
import SportMap from './components/SportMap.jsx';

export default function App() {
  return <SportMap sport={softball} onBack={() => {}} />;
}
```

```bash
npm run dev
```

Expected: Full sport map with header, filter buttons, timezone toggle, map, stat cards, farthest trip card, and scrollable destination list. Clicking destinations expands game detail. Timezone toggle shows/hides the zone tints.

- [ ] **Step 3: Revert App.jsx to stub, commit**

```jsx
import { useState } from 'react';
export default function App() {
  return <div style={{ color: '#fff', padding: 40 }}>scaffold</div>;
}
```

```bash
git add src/components/SportMap.jsx src/App.jsx
git commit -m "feat: add SportMap component with sidebar, filters, and timezone toggle"
```

---

## Task 11: Time zone crossing summary in sidebar

**Files:**
- Modify: `src/components/SportMap.jsx`

Add a "Time Zone Changes" section below the farthest trip card.

- [ ] **Step 1: Add `computeTimezoneChanges` import to SportMap**

In `src/components/SportMap.jsx`, add to the imports:

```jsx
import { computeTimezoneChanges, TZ_LABEL_COLORS, TZ_ABBR } from '../utils/timezones.js';
```

- [ ] **Step 2: Compute timezone changes in SportMap**

Add this `useMemo` after the `farthestDest` memo:

```jsx
  const tzChanges = useMemo(
    () => computeTimezoneChanges(allDests, trips, home),
    [allDests, trips, home]
  );
  const totalCrossings = useMemo(
    () => Object.values(tzChanges).reduce((sum, dests) => sum + dests.length, 0),
    [tzChanges]
  );
```

- [ ] **Step 3: Add timezone changes section to sidebar**

In the sidebar JSX, insert this block after the `{/* Farthest trip */}` block and before `{/* Destination list */}`:

```jsx
          {/* Time Zone Changes */}
          {totalCrossings > 0 && (
            <div style={{ margin: '0 16px 12px', background: '#1e293b', borderRadius: 6, padding: '10px 12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <div style={{ fontSize: 10, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                  Time Zone Changes
                </div>
                <div style={{ fontSize: 11, color: '#64748b', fontFamily: 'JetBrains Mono, monospace' }}>
                  {totalCrossings} crossing{totalCrossings !== 1 ? 's' : ''}
                </div>
              </div>
              {['Eastern', 'Mountain', 'Pacific'].filter(z => tzChanges[z]).map(zone => (
                <div
                  key={zone}
                  onClick={() => {
                    // Highlight first destination in this zone
                    const first = tzChanges[zone][0];
                    if (first) setSelectedDest(prev => prev?.location === first.location ? null : first);
                  }}
                  style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '5px 0', borderBottom: '1px solid #283548', cursor: 'pointer' }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div style={{ width: 8, height: 8, borderRadius: 2, background: TZ_LABEL_COLORS[zone] }} />
                    <span style={{ fontSize: 12 }}>{zone} Time</span>
                    <span style={{ fontSize: 10, color: '#64748b', fontFamily: 'JetBrains Mono, monospace' }}>({TZ_ABBR[zone]})</span>
                  </div>
                  <div style={{ fontSize: 11, color: '#64748b' }}>
                    {tzChanges[zone].length} trip{tzChanges[zone].length !== 1 ? 's' : ''}
                  </div>
                </div>
              ))}
            </div>
          )}
```

- [ ] **Step 4: Verify**

Wire up `App.jsx` to `SportMap` as in Task 10 Step 2. Run `npm run dev`.

Expected: Below "Farthest Trip", a "Time Zone Changes" section lists Eastern (trips to Clemson, DeLand, Orlando), Mountain (Tucson), and Pacific (San Diego) with trip counts. Clicking a row selects the first destination in that zone.

- [ ] **Step 5: Revert App.jsx and commit**

```jsx
import { useState } from 'react';
export default function App() {
  return <div style={{ color: '#fff', padding: 40 }}>scaffold</div>;
}
```

```bash
git add src/components/SportMap.jsx src/App.jsx
git commit -m "feat: add timezone crossing summary to SportMap sidebar"
```

---

## Task 12: Congestion warnings in sidebar

**Files:**
- Modify: `src/components/SportMap.jsx`

Add a "High Load Periods" section below the time zone section.

- [ ] **Step 1: Add `detectCongestion` import**

```jsx
import { detectCongestion, dayOfYearToDisplay } from '../utils/congestion.js';
```

- [ ] **Step 2: Compute congestion in SportMap**

Add after the `totalCrossings` memo:

```jsx
  const congestionPeriods = useMemo(
    () => sport.congestionThreshold
      ? detectCongestion(sport.games, sport.congestionThreshold)
      : [],
    [sport]
  );
```

- [ ] **Step 3: Add warning dot to stat cards when congestion is detected**

Find the stat card grid JSX. Add a warning indicator to the "Total Miles" card label when `congestionPeriods.length > 0`:

```jsx
                <div style={{ fontSize: 10, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 4, display: 'flex', alignItems: 'center', gap: 4 }}>
                  {label}
                  {label === 'Away Trips' && congestionPeriods.length > 0 && (
                    <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#f97316', display: 'inline-block' }} title="High load periods detected" />
                  )}
                </div>
```

- [ ] **Step 4: Add High Load Periods section to sidebar**

Insert after the `{/* Time Zone Changes */}` block:

```jsx
          {/* High Load Periods */}
          {congestionPeriods.length > 0 && (
            <div style={{ margin: '0 16px 12px', background: '#1e293b', borderRadius: 6, padding: '10px 12px', borderLeft: '3px solid #f97316' }}>
              <div style={{ fontSize: 10, color: '#f97316', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 8 }}>
                High Load Periods
              </div>
              {congestionPeriods.map((period, i) => {
                const locations = [...new Set(period.games.filter(g => !g.home).map(g => g.location))];
                return (
                  <div key={i} style={{ marginBottom: i < congestionPeriods.length - 1 ? 8 : 0, paddingBottom: i < congestionPeriods.length - 1 ? 8 : 0, borderBottom: i < congestionPeriods.length - 1 ? '1px solid #283548' : 'none' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
                      <span style={{ fontSize: 12, fontFamily: 'JetBrains Mono, monospace', color: '#f97316' }}>
                        {dayOfYearToDisplay(period.startDoy)} – {dayOfYearToDisplay(period.endDoy)}
                      </span>
                      <span style={{ fontSize: 11, color: '#64748b' }}>{period.gameCount}g</span>
                    </div>
                    <div style={{ fontSize: 11, color: '#475569' }}>
                      {locations.length > 0 ? locations.join(', ') : 'All home games'}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
```

- [ ] **Step 5: Verify**

Wire App.jsx to SportMap, run `npm run dev`.

Expected: "High Load Periods" section appears with an orange left border. The Mar 6–Mar 12 window (8 games in 7 days: Iowa State series + Florida Swing start) should flag. The "Away Trips" stat card shows a small orange dot.

- [ ] **Step 6: Revert App.jsx and commit**

```jsx
import { useState } from 'react';
export default function App() {
  return <div style={{ color: '#fff', padding: 40 }}>scaffold</div>;
}
```

```bash
git add src/components/SportMap.jsx src/App.jsx
git commit -m "feat: add high load period congestion warnings to SportMap sidebar"
```

---

## Task 13: SportGrid landing page

**Files:**
- Modify: `src/components/SportGrid.jsx` (replace stub with full implementation)

- [ ] **Step 1: Replace `src/components/SportGrid.jsx` with full implementation**

```jsx
import { useMemo } from 'react';
import { sports } from '../data/index.js';
import { groupByDest } from '../utils/groupByDest.js';
import { calcTotalMiles } from '../utils/calcMiles.js';
import { haversine } from '../utils/haversine.js';
import { computeTimezoneChanges } from '../utils/timezones.js';

function SportCard({ sport, onClick }) {
  const isActive = !sport.status;

  const stats = useMemo(() => {
    if (!isActive) return null;
    const allDests = groupByDest(sport.games);
    const awayDests = allDests.filter(d => !d.home);
    const totalMiles = calcTotalMiles(awayDests, sport.trips || [], sport.home);
    const awayTrips = (() => {
      const seen = new Set();
      awayDests.forEach(d => { if (d.tripId) seen.add(d.tripId); else seen.add(d.location); });
      return seen.size;
    })();
    const tzChanges = computeTimezoneChanges(allDests, sport.trips || [], sport.home);
    const totalCrossings = Object.values(tzChanges).reduce((s, d) => s + d.length, 0);
    return { totalMiles, awayTrips, totalCrossings };
  }, [sport, isActive]);

  return (
    <div
      onClick={isActive ? onClick : undefined}
      style={{
        background: isActive ? '#1e293b' : '#131d2a',
        border: `1px solid ${isActive ? '#334155' : '#1a2535'}`,
        borderRadius: 8,
        padding: 20,
        cursor: isActive ? 'pointer' : 'default',
        opacity: isActive ? 1 : 0.5,
        transition: 'border-color 0.15s, transform 0.15s',
        position: 'relative',
        overflow: 'hidden',
      }}
      onMouseEnter={e => { if (isActive) e.currentTarget.style.borderColor = sport.colors?.conference || '#334155'; }}
      onMouseLeave={e => { if (isActive) e.currentTarget.style.borderColor = '#334155'; }}
    >
      {/* Color accent bar */}
      {isActive && (
        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: sport.colors?.conference || '#FFB81C', borderRadius: '8px 8px 0 0' }} />
      )}

      <div style={{ marginTop: isActive ? 8 : 0 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
          <div>
            <div style={{ fontWeight: 700, fontSize: 18, color: isActive ? '#f1f5f9' : '#475569' }}>
              {sport.label}
            </div>
            <div style={{ fontSize: 12, color: '#475569', marginTop: 2 }}>{sport.season}</div>
          </div>
          {!isActive && (
            <div style={{ fontSize: 10, color: '#334155', background: '#1e293b', padding: '2px 8px', borderRadius: 12, border: '1px solid #334155' }}>
              Coming Soon
            </div>
          )}
        </div>

        {isActive && stats && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8 }}>
            {[
              { label: 'Miles',    value: `${Math.round(stats.totalMiles / 1000 * 10) / 10}k` },
              { label: 'Trips',    value: stats.awayTrips },
              { label: 'TZ Cross', value: stats.totalCrossings },
            ].map(({ label, value }) => (
              <div key={label} style={{ textAlign: 'center' }}>
                <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 16, fontWeight: 700, color: sport.colors?.conference || '#FFB81C' }}>
                  {value}
                </div>
                <div style={{ fontSize: 10, color: '#475569', marginTop: 2 }}>{label}</div>
              </div>
            ))}
          </div>
        )}

        {isActive && sport.lastUpdated && (
          <div style={{ fontSize: 10, color: '#334155', marginTop: 12 }}>
            Updated {sport.lastUpdated}
          </div>
        )}
      </div>
    </div>
  );
}

export default function SportGrid({ onSelect }) {
  return (
    <div style={{ minHeight: '100vh', background: '#0f172a', fontFamily: 'DM Sans, sans-serif', color: '#fff' }}>
      {/* Header */}
      <div style={{ background: '#154734', padding: '20px 32px' }}>
        <div style={{ fontSize: 22, fontWeight: 700 }}>Baylor Athletics</div>
        <div style={{ fontSize: 14, color: 'rgba(255,255,255,0.65)', marginTop: 2 }}>Travel Demands by Sport</div>
      </div>

      {/* Grid */}
      <div style={{ padding: 32, maxWidth: 960, margin: '0 auto' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 16 }}>
          {sports.map(sport => (
            <SportCard
              key={sport.sport}
              sport={sport}
              onClick={() => onSelect(sport)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Wire App.jsx to test SportGrid**

```jsx
import SportGrid from './components/SportGrid.jsx';
import softball from './data/softball.json';
import SportMap from './components/SportMap.jsx';
import { useState } from 'react';

export default function App() {
  const [sport, setSport] = useState(null);
  if (sport) return <SportMap sport={sport} onBack={() => setSport(null)} />;
  return <SportGrid onSelect={setSport} />;
}
```

```bash
npm run dev
```

Expected: Landing page shows a grid of sport cards. Softball card displays miles (~13k), away trips, and timezone crossings with a gold accent bar. Baseball/Soccer/Basketball/Football/Volleyball show as muted "Coming Soon" cards. Clicking Softball opens the full map. The "← All Sports" back button returns to the grid.

- [ ] **Step 3: Commit**

```bash
git add src/components/SportGrid.jsx src/App.jsx
git commit -m "feat: add SportGrid landing page with sport cards"
```

---

## Task 14: Wire App.jsx and final integration

**Files:**
- Modify: `src/App.jsx` (final version)

- [ ] **Step 1: Write final `src/App.jsx`**

```jsx
import { useState } from 'react';
import SportGrid from './components/SportGrid.jsx';
import SportMap from './components/SportMap.jsx';

export default function App() {
  const [view, setView] = useState({ page: 'grid' });

  if (view.page === 'sport') {
    return (
      <SportMap
        sport={view.sport}
        onBack={() => setView({ page: 'grid' })}
      />
    );
  }

  return (
    <SportGrid
      onSelect={sport => setView({ page: 'sport', sport })}
    />
  );
}
```

- [ ] **Step 2: Full integration test**

```bash
npm run dev
```

Walk through the complete flow:
1. Landing page loads at root URL — sport cards visible
2. Softball card shows miles, trips, timezone crossings
3. Click Softball — map loads with arcs, sidebar, filters
4. Toggle "Time Zones" button — zone tints appear/disappear
5. Click a destination — sidebar card expands, arc highlights
6. "High Load Periods" section shows orange-bordered congestion flag
7. "Time Zone Changes" section lists crossing destinations
8. Click "← All Sports" — returns to landing grid
9. Run `npm run build` — verify no build errors

```bash
npm run build
```

Expected: `dist/` folder created with no errors.

- [ ] **Step 3: Run all utility tests one final time**

```bash
npm test
```

Expected: All tests PASS.

- [ ] **Step 4: Commit**

```bash
git add src/App.jsx
git commit -m "feat: wire App.jsx navigation and complete integration"
```

---

## Task 15: Deploy to GitHub Pages

**Files:**
- Modify: `vite.config.js` — add `base` for the repo subdirectory path
- Create: `.github/workflows/deploy.yml` — GitHub Actions build + deploy workflow

GitHub Pages serves the site from the `gh-pages` branch. A GitHub Actions workflow builds on every push to `main` and publishes `dist/` automatically.

- [ ] **Step 1: Verify build output locally**

```bash
npm run build && npm run preview
```

Open the preview URL. Confirm full app works. Stop preview server (Ctrl+C).

- [ ] **Step 2: Add `base` to `vite.config.js`**

GitHub Pages serves the site at `https://<username>.github.io/<repo-name>/`. Vite needs the repo name as the base path so asset URLs resolve correctly.

Replace the contents of `vite.config.js`:

```js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: '/Travel_Map/',   // must match the GitHub repo name exactly
  test: {
    environment: 'node',
  },
});
```

- [ ] **Step 3: Rebuild with new base and verify preview still works**

```bash
npm run build && npm run preview
```

Expected: Preview URL is now served at `/Travel_Map/` path. App still works.

Stop preview server.

- [ ] **Step 4: Create GitHub Actions deploy workflow**

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: dist

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 5: Enable GitHub Pages in repo settings**

1. Push the workflow file to `main` (next step)
2. Go to the GitHub repo → **Settings** → **Pages**
3. Under **Source**, select **GitHub Actions**
4. Save

- [ ] **Step 6: Commit and push**

```bash
git add vite.config.js .github/workflows/deploy.yml
git commit -m "chore: configure GitHub Pages deployment via GitHub Actions"
git push origin main
```

- [ ] **Step 7: Verify deployment**

1. Go to the GitHub repo → **Actions** tab
2. Watch the "Deploy to GitHub Pages" workflow run
3. When it completes, open `https://<your-github-username>.github.io/Travel_Map/`

Expected: Full app loads at the GitHub Pages URL. Walk through the integration test from Task 14 Step 2.

---

## Self-Review

**Spec coverage:**
- [x] Any sport added via JSON file — covered by `src/data/index.js` registry pattern (Tasks 6, 13)
- [x] Hosted URL — Task 15
- [x] Time zone tints on map — Task 8
- [x] Floating zone labels — Task 8
- [x] Time zone crossing summary in sidebar — Task 11
- [x] Congestion detection and display — Task 12
- [x] Travel mode arc styles (solid/dashed/dotted) — Task 9
- [x] Travel mode legend on map — Task 9
- [x] Multi-stop trip routing (tripId) — Tasks 3, 7
- [x] Landing page grid with sport cards — Task 13
- [x] Back button navigation — Task 10
- [x] No emoji in sport names — SportGrid uses `sport.label` only (no icon field rendered)
- [x] game-level travelMode overrides trip-level — `getTravelMode()` in Task 7

**Placeholder scan:** No TBDs, TODOs, or incomplete steps found.

**Type consistency:**
- `tripId` used consistently (not `swing`) across all tasks ✓
- `sport.trips` (not `TRIP_SWINGS`) used everywhere ✓
- `sport.home` (not `WACO`) used everywhere ✓
- `travelModeDash()` defined in Task 7, used in Tasks 7, 9 ✓
- `computeTimezoneChanges(destinations, trips, home)` — `home` is `{ city, lat, lng }` object, matches usage in Tasks 4 and 11 ✓
- `detectCongestion(games, { games, windowDays })` — matches usage in Task 12 ✓
- `dayOfYearToDisplay(doy)` — defined and exported in Task 5, imported in Task 12 ✓
