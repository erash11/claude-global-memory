# Cinematic Mode — Design Spec

**Date:** 2026-06-10
**Status:** Approved (brainstorming session with Eric)

## Goal

Add a full-screen, broadcast-style 3D globe "season tour" on top of the existing 2D map,
to show coaches and administrators how much travel and time a team spends on the road.
The 2D map remains the everyday working view; cinematic mode is the presentation layer.

## Decisions (from brainstorming)

| Question | Decision |
|---|---|
| Rebuild scope | Keep 2D map, add cinematic mode (option C) |
| Overlay layout | Itinerary side rail — all info visible at once, no clicking required (option C) |
| Playback | Auto-play by default; operator controls (space/arrows/rail-click) optional |
| Tech | `react-globe.gl` (Three.js), lazy-loaded so the daily map bundle is unaffected |

## Experience

- "Cinematic" button in the sport map header opens a full-screen dark overlay.
  Esc or ✕ returns to the map exactly as it was.
- The season plays as one scene per road trip, chronological (13 for 2026 softball,
  postseason included). Each scene (~4.5s, auto-advancing):
  - Camera flies to the destination
  - Arc draws from the previous location (gold = conference, teal = non-conference)
  - Destination dot pulses; rail entry highlights, then checks off
  - Cumulative mileage counter ticks up
- Multi-stop trips (e.g. Florida swing) are ONE scene with chained legs
  (Waco → DeLand → Orlando → Waco).
- Finale: camera pulls back to show all arcs lit + season totals card
  (total miles, trips, timezone crossings).
- Controls (operator only): space = pause/play, ←/→ = prev/next trip,
  click rail entry = jump. The room never needs to interact.

## Itinerary rail (left panel, dark glass)

Every trip in date order: destination, dates, opponent(s), round-trip miles,
travel mode. Visited = checked + dimmed; active = gold glow; upcoming = muted.
Running total pinned at bottom (`6,420 / 10,842 mi`).

## Architecture

New files only; the single existing change is one header button in `SportMap.jsx`.

```
src/components/cinematic/
  CinematicMode.jsx   — full-screen shell; playback state machine; keyboard controls
  GlobeStage.jsx      — react-globe.gl wrapper: arcs, points, camera fly-tos
  ItineraryRail.jsx   — chronological trip list + running total
src/utils/
  buildTimeline.js    — pure: sport JSON → ordered scenes (legs, per-trip miles,
                        cumulative miles, timezone). Sport-agnostic.
```

- `CinematicMode` is loaded via `React.lazy` + dynamic import — the Three.js chunk
  is only fetched on first open.
- `buildTimeline` consumes the existing sport JSON schema unchanged, so every
  future sport gets cinematic mode for free.

## Reliability

- Globe texture bundled in `public/` — no CDN dependence at presentation time.
- No WebGL → graceful "not supported on this device" panel; 2D map unaffected.

## Testing

- Unit tests for `buildTimeline`: scene ordering, multi-stop leg chaining,
  scene count, and **cumulative total === `calcTotalMiles`** so the two views
  can never disagree on mileage.
- Manual UAT for animation quality and big-screen legibility.
