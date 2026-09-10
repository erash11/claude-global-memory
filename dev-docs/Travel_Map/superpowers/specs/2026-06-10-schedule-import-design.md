# Schedule Import (CSV → Sport JSON) — Design Spec

**Date:** 2026-06-10
**Status:** Approved (brainstorming session with Eric)

## Goal

Let Eric convert a schedule CSV into a sport on the map without hand-editing JSON.
Eric is the only intended user — coaches consume the finished map. No backend, no auth.

## Decisions (from brainstorming)

| Question | Decision |
|---|---|
| Who uses it | Eric only; staff/coaches just view the published map |
| Persistence | Browser preview via localStorage + "Download JSON" → Eric commits to `src/data/` |
| Tool home | In the live site — "+ Import Schedule" card on the sport grid |
| Geocoding | Bundled US city database, lazy-loaded on the import page only; optional `lat,lng` CSV columns override; inline manual fix for unknown cities |

## CSV format

One row per game. Header row required. Downloadable template on the import page.

| Column | Required | Notes |
|---|---|---|
| `date` | yes | e.g. `Feb 5` (matches existing parseDate format) |
| `opponent` | yes | |
| `location` | yes* | `City, ST`. *Blank allowed on home games → defaults to home city |
| `home` | yes | TRUE/FALSE (case-insensitive; also accepts yes/no, 1/0) |
| `conference` | no | default FALSE |
| `result` | no | `W 6-3` / `L 0-8`; blank = upcoming (null) |
| `tournament` | no | display label |
| `tripId` | no | games sharing a tripId become one multi-stop trip; stops in date order |
| `travelMode` | no | flight / bus / charter / tbd |
| `lat`, `lng` | no | override geocoder for this row |

Sport-level fields come from a small form on the import page: sport id, label,
season, home city (default Waco, TX / 31.5493, -97.1467), colors default Baylor
palette, congestionThreshold default {games: 5, windowDays: 7}.

Trips registry derivation: for each distinct tripId, stops = unique destinations
in date order, label defaults to editable "<City> Swing"-style suggestion,
travelMode = first game's mode.

## Flow

1. Grid → "+ Import Schedule" card → import page (`view.page === 'import'`)
2. Fill sport form, drag/drop or pick CSV
3. **Validate**: per-row errors with row numbers (unknown city, bad date, bad
   home flag, missing required). Unknown cities fixable inline (enter lat/lng).
   Import is blocked until errors are resolved.
4. **Preview**: renders the real `SportMap` with the imported sport — stats,
   arcs, timezones, cinematic mode all work.
5. **Save** → localStorage; sport appears on grid with "Imported" badge
   (with a remove option). **Download JSON** → ready-to-commit `<sport>.json`.

## Architecture

```
src/components/import/ImportPage.jsx  — dropzone, form, validation report, actions
src/utils/parseCsv.js                 — CSV text → row objects (hand-rolled, handles
                                        quoted fields/commas/CRLF/escaped quotes)
src/utils/csvToSport.js               — rows + metadata → sport object matching the
                                        existing JSON schema exactly; pure; validation
                                        + trip derivation + defaults
src/utils/geocode.js                  — lazy fetch of public/us-cities.json, lookup
public/us-cities.json                 — trimmed US city DB (city|ST → [lat,lng]),
                                        fetched only on import page
src/utils/importedSports.js           — localStorage load/save/remove of imported sports
```

- `App.jsx`: adds `{ page: 'import' }` view
- `SportGrid.jsx`: merges imported sports (localStorage) with built-in registry;
  imported cards get a badge + remove; adds the "+ Import Schedule" card
- No changes to map/cinematic components — they receive a sport object as always

## Error handling

- CSV parse failures → friendly message, nothing imported
- Row-level issues → listed with row number + reason; blocking vs warning
  (warning: blank result; blocking: unknown city without override, bad date)
- localStorage quota/corruption → imported list degrades to empty, never crashes grid

## Testing

- Unit: parseCsv (quotes, commas-in-fields, CRLF, empty lines); csvToSport
  (defaults, trip derivation, home-blank-location, error cases)
- Round-trip: softball.json → CSV → csvToSport → deep-equal original (schema lock)
- Manual Playwright walkthrough on the running site
