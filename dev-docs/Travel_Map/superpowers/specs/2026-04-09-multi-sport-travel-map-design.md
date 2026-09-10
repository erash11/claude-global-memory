# Multi-Sport Travel Map — Design Spec
**Date:** 2026-04-09  
**Author:** Eric Rash, Director of Applied Performance  
**Status:** Approved

---

## Overview

Expand the existing Baylor Softball travel map into a hosted, multi-sport web application that any Baylor Athletics staff member can visit via a URL. Staff select their sport from a landing page, which opens an interactive US map showing that sport's full season schedule, travel distances, time zone crossings, travel mode, and congestion warnings.

---

## Goals

- Any Baylor sport can be added by dropping in one JSON data file — no component code changes
- Staff access via a hosted URL (deployed to Vercel or GitHub Pages)
- Time zone distinctions visible on the map and summarized in the sidebar
- Travel congestion periods (high game density in short windows) are automatically flagged
- Travel mode (bus vs. flight) is reflected in arc style on the map
- Multi-stop road trips (team stays out, does not return home between games) are modeled as a single continuous route
- Architecture is designed so a future drag-and-drop CSV/JSON upload feature (Approach C) can be added without structural changes

---

## Architecture

**Approach B:** Vite + React SPA with per-sport JSON data files.

```
src/
  App.jsx                  ← top-level: renders SportGrid or SportMap based on view state
  components/
    SportGrid.jsx          ← landing page: grid of sport cards
    SportMap.jsx           ← full map + sidebar for a single sport
    USMap.jsx              ← extracted D3 map component (refactored from softball jsx)
  data/
    softball.json          ← 2026 softball schedule (converted from existing games array)
    index.js               ← exports array of all available sport data files
  utils/
    haversine.js           ← distance calculation
    calcMiles.js           ← total miles with multi-stop trip support
    timezones.js           ← maps US state abbreviations → ET | CT | MT | PT
    congestion.js          ← sliding window congestion detection
index.html
vite.config.js
```

No client-side router library. Navigation is a single `view` state in `App.jsx`: `{ page: 'grid' }` or `{ page: 'sport', sport: sportData }`.

---

## Data Format

Each sport lives in `src/data/<sport>.json`. Adding a sport = create the file, add it to `src/data/index.js`.

`index.js` exports a flat array of entries. Active sports import their JSON; coming-soon entries are stubs:

```js
import softball from './softball.json';

export const sports = [
  softball,
  { sport: 'baseball', label: 'Baseball', season: '2026', status: 'coming-soon' },
  { sport: 'soccer',   label: 'Soccer',   season: '2026', status: 'coming-soon' },
];
```

The `SportGrid` component checks for `status === 'coming-soon'` and renders those cards in a muted style without a click handler.

```json
{
  "sport": "softball",
  "label": "Softball",
  "season": "2026",
  "icon": "softball",
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
    {
      "date": "Feb 5",
      "opponent": "Mississippi State",
      "location": "Waco, TX",
      "lat": 31.5493,
      "lng": -97.1467,
      "home": true,
      "result": "L 0-10",
      "conference": false,
      "tournament": "Getterman Classic",
      "tripId": null,
      "travelMode": null
    }
  ]
}
```

**Field notes:**
- `tripId` — links a game to a `trips` entry. Games sharing a `tripId` are modeled as one continuous road trip (Waco → stop1 → stop2 → ... → Waco). Replaces the existing `swing` field.
- `travelMode` — on trips object (whole trip shares a mode) or on individual games. Values: `"bus"` | `"flight"` | `"charter"` | `"tbd"`. Null for home games. If both are set, game-level `travelMode` overrides the trip-level value for that specific game.
- `congestionThreshold` — per-sport config for the sliding window detector. Softball default: 5 games in 7 days.
- `icon` — text identifier for the sport (e.g. `"softball"`, `"baseball"`). No emojis — the landing page uses text-only sport names for a professional appearance.
- `lastUpdated` — ISO date string shown on the landing page card.

---

## Landing Page (`SportGrid`)

- Baylor green/gold header with site title "Baylor Athletics — Travel Demands"
- Responsive grid of sport cards
- Each card shows: sport name (text only, no emoji), season year, total miles, away trips, time zone crossings, last updated date
- Card color accent comes from `colors.conference` in the sport JSON
- Sports with no data file render as muted "Coming Soon" cards (defined in `index.js` with `status: 'coming-soon'`)
- Clicking an active card sets `view` to `{ page: 'sport', sport: data }` and renders `SportMap`

---

## Sport Map Page (`SportMap` + `USMap`)

Preserves all existing softball map behavior:
- D3 AlbersUSA projection, TopoJSON state boundaries
- Curved bezier arcs from home to each destination
- Zoom/pan (1x–8x), scroll + buttons + reset
- Hover/select destinations, arc glow effects
- Filter buttons: All | Away | Home | Conference
- Sidebar: 2×2 stat cards, farthest trip callout, scrollable destination list with game detail

### New: Time Zone Overlay

- Bottom-most SVG layer — rendered before state boundaries, arcs, and dots
- State fills tinted at ~12% opacity by zone:
  - Pacific → `rgba(99, 179, 237, 0.12)` (blue)
  - Mountain → `rgba(154, 230, 180, 0.12)` (green)
  - Central → `rgba(252, 211, 77, 0.10)` (gold)
  - Eastern → `rgba(245, 101, 101, 0.12)` (red)
- Four floating SVG text labels ("PACIFIC", "MOUNTAIN", "CENTRAL", "EASTERN") positioned in the geographic center of each zone
- Toggle button in map controls to show/hide the overlay (default: on)
- Time zone for each destination is derived from its state via `timezones.js`

### New: Arc Style by Travel Mode

- `flight` / `charter` → solid arc (current style)
- `bus` → dashed arc (`strokeDasharray`)
- `tbd` → dotted arc
- Travel mode legend in the sidebar beneath the filter buttons

### New: Multi-Stop Trip Routing

- Replaces the existing `TRIP_SWINGS` / `swing` pattern
- `tripId` groups games into continuous road trips
- Mileage: Waco → stop1 → stop2 → ... → Waco (not separate round trips)
- On hover, all legs of the trip highlight together
- Sidebar card labeled with `trips[].label` and shows route sequence

### New Sidebar Sections

**Time Zone Crossings** (below stat cards):
- Waco = CT; any away destination in a different zone is a crossing
- Grouped by zone with trip count and destination names
- Each row clickable → highlights those destinations on the map
- Multi-stop trips that cross multiple zones count each zone once

**High Load Periods** (below time zone section):
- Sliding window algorithm (`congestion.js`) scans for windows where game count ≥ `congestionThreshold.games` within `congestionThreshold.windowDays` days
- Each flagged period shows: date range, game count, destinations involved
- Visual warning indicator on the stat card area when any period is flagged

---

## Routing / Navigation

No URL-based routing in the initial version. State lives in `App.jsx`:

```js
const [view, setView] = useState({ page: 'grid' });
// → { page: 'sport', sport: softballData }
```

A back button on the sport map page calls `setView({ page: 'grid' })`.

---

## Hosting

Deploy as a static site via **GitHub Pages** using a GitHub Actions workflow. On every push to `main`, the workflow runs `npm run build` and publishes `dist/` to the `gh-pages` environment. Vite's `base` config must be set to the repo name (e.g. `/Travel_Map/`) so asset paths resolve correctly under the Pages subdirectory.

---

## Future: Drag-and-Drop Import (Approach C Roadmap)

The JSON schema above is the target format for a future file upload feature. When ready:
1. Add a file input to the landing page
2. Parse the uploaded CSV or JSON client-side and convert to the schema above
3. Pass the parsed object directly to `SportMap` — no data file write required
4. No architecture changes needed; the component already accepts a sport data object as a prop

---

## What Is Not In Scope

- Authentication / access control (public URL, no login)
- Backend or database
- Automatic schedule ingestion from baylorbears.com
- Mobile-optimized layout (desktop-first, responsive-friendly but not mobile-first)
- Historical seasons (one season per sport JSON file for now)
