# VALD ForceDecks Recording Pipeline and CLI Design

**Date:** 2026-06-23
**Status:** Approved direction

## Objective

Modernize the existing VALD ForceDecks integration and add a command-line
interface that can retrieve tests, trial metrics, and raw recordings without
breaking the current CMJ dashboard.

The pipeline will preserve immutable VALD responses on disk, derive individual
trial force traces from each recording, store those processed trials in the
existing database, and continue producing the averaged trace expected by the
dashboard.

## Scope

This phase covers the VALD External ForceDecks, Profiles, and Tenants APIs.
It does not add other VALD products or redesign the dashboard.

The implementation will:

1. Migrate authentication to the March 2026 OAuth contract.
2. Replace guessed API routes with documented routes.
3. Retrieve tests with server-side `profileId` filtering and cursor-style
   pagination through `modifiedFromUtc`.
4. Retrieve trial metadata and metrics from:
   `/v2019q3/teams/{teamId}/tests/{testId}/trials`.
5. Retrieve raw sample data from the supported test route:
   `/v2019q3/teams/{teamId}/tests/{testId}/recording?includeSampleData=true`.
6. Support explicit recording-ID retrieval through:
   `/v2019q3/teams/{teamId}/recordings/{recordingId}?includeSampleData=true`.
   This route is retained for the account capability confirmed by VALD Support,
   but it is treated as a compatibility route because Swagger marks it
   deprecated.
7. Cache raw API responses as compressed JSON.
8. Slice recordings into individual trials using the trial `startTime` and
   `endTime` values.
9. Store individual processed trials and a derived averaged trial in SQLite.
10. Provide CLI access and optional CSV export.

## Architecture

### API client

`ForceDecksClient` remains the transport boundary, but it will use explicit
methods for each documented resource:

- authenticate
- list tests
- list trial metrics
- get recording by test ID
- get recording by recording ID
- list result definitions

Profiles and tenants use separate base URLs behind dedicated client methods or
small focused clients. A ForceDecks base URL will not be reused for profile or
tenant routes.

Authentication uses:

- Token URL: `https://auth.prd.vald.com/oauth/token`
- Grant: `client_credentials`
- Required parameter: `audience=vald-api-external`
- No legacy `scope`

Access tokens are cached in memory until shortly before expiry. A single `401`
causes one forced refresh and retry. `403` is reported as a permissions error
and specifically identifies recording access when applicable. `429` honors
`Retry-After`.

### Raw recording cache

Raw recordings are immutable source artifacts and remain outside the database:

```text
data/vald/recordings/<team-id>/<recording-id>.json.gz
```

Each file contains the complete VALD recording response, including sample
headers and rows. Writes are atomic: data is written to a temporary file and
renamed only after compression succeeds.

The cache behavior is:

- Reuse an existing valid file by default.
- `--refresh` explicitly replaces it.
- A zero-byte, invalid gzip, or invalid JSON file is treated as corrupt and
  downloaded again.
- Athlete names are not used in paths.
- Credentials and access tokens are never written to cache or logs.

The cache directory is ignored by Git. A small metadata summary may be printed,
but raw sample rows are not printed to the terminal by default.

### Trial extraction

VALD trial records provide `startTime` and `endTime` in seconds relative to the
recording. Recording data provides a `recordingDataHeader`, sample rows, and a
sampling frequency.

Extraction will:

1. Resolve column indexes by header name instead of assuming a fixed order.
2. Select rows whose time value falls within the trial interval.
3. Preserve left and right vertical force independently when available.
4. Calculate total vertical force as left plus right.
5. Preserve the VALD trial ID, test ID, recording ID, trial order, timestamps,
   sampling frequency, and the trial metric response.
6. Reject an interval with no samples and report the test and trial IDs.

Small floating-point differences at interval boundaries are handled using the
actual time column rather than converting seconds directly to integer indexes.

### Database compatibility

The existing `Trial` model remains the dashboard-facing representation.
Individual extracted trials are stored with:

- `is_averaged = false`
- `data_source = "forcedecks"`
- VALD test, trial, and recording identifiers
- combined force-time data
- left and right raw force arrays
- sampling frequency
- movement initiation and quality fields when calculable
- trial-level metric JSON

A derived averaged trial is also stored with `is_averaged = true`. This keeps
the current dashboard behavior while making individual trials available for
future clinical review.

Imports are idempotent. The stable key is the VALD trial ID. Re-running an
import updates a matching trial rather than duplicating it. The averaged row is
recomputed from the current valid individual trials.

Database changes use an explicit migration script that preserves existing
records. The implementation will not delete or reset the current database.

### Command-line interface

The entry point is:

```powershell
python vald_cli.py <command>
```

Initial commands:

```text
vald_cli.py auth check
vald_cli.py tenants list
vald_cli.py profiles list [--search TEXT]
vald_cli.py tests list --profile-id UUID --from DATE [--to DATE]
vald_cli.py trials get --test-id UUID
vald_cli.py recordings get (--test-id UUID | --recording-id UUID)
                           [--include-samples] [--refresh]
vald_cli.py recordings export (--test-id UUID | --recording-id UUID)
                              --format json|csv --output PATH
vald_cli.py sync --profile-id UUID --from DATE [--to DATE] [--refresh]
```

Human-readable tables are the default. `--json` produces machine-readable
output for list and metadata commands. Raw recording sample rows require an
explicit export or `--include-samples`.

`sync` performs the complete path:

```text
tests -> trials -> recording cache -> extraction -> individual database rows
      -> averaged database row
```

## Configuration

The existing `.env` remains the credential source. The documented variables
are:

```text
VALD_CLIENT_ID
VALD_CLIENT_SECRET
VALD_TENANT_ID
VALD_REGION=use
VALD_TOKEN_URL=https://auth.prd.vald.com/oauth/token
VALD_RECORDING_CACHE=data/vald/recordings
```

For migration, existing `FORCEDECKS_CLIENT_ID`,
`FORCEDECKS_CLIENT_SECRET`, and `FORCEDECKS_ORG_ID` names remain accepted with
a deprecation warning. New documentation uses the `VALD_*` names.

The implementation will detect old credentials that return `401 access_denied`
and explain that replacement credentials issued for the March 2026 migration
are required.

## Error and Recovery Behavior

- `401`: refresh once; then report invalid or obsolete credentials.
- `403` on recording routes: report that the API client lacks recording
  permission, even if the organization account has it.
- `404`: report the team, test, or recording identifier involved.
- `429`: honor `Retry-After`, retry within a bounded attempt count.
- Network timeout: retry with exponential backoff.
- Partial sync: keep completed cache files and database rows; rerunning resumes
  idempotently.
- Invalid recording schema: retain the raw cache file for diagnosis but do not
  write derived database rows.
- Unsupported recording headers: show the received header names without
  printing sample data.

## Testing Strategy

Implementation follows test-driven development.

Unit tests cover:

- March 2026 OAuth request shape and token reuse.
- `401`, `403`, `404`, and `429` behavior.
- Test pagination and `profileId` query construction.
- Both supported test-ID and compatibility recording-ID routes.
- Atomic gzip cache writes and corrupt-cache recovery.
- Header-based recording parsing.
- Trial boundary slicing.
- Left, right, and combined force construction.
- Idempotent trial upserts and averaged-row replacement.
- CLI argument validation and JSON output.

Fixture responses contain synthetic identifiers and force samples. Real Baylor
athlete data and credentials are never committed.

Integration verification uses the configured Baylor account and performs:

1. OAuth check.
2. One metadata-only recording request.
3. One sample-data recording request.
4. One trial extraction into a temporary database.
5. A repeat sync proving cache reuse and database idempotency.

The production database is not used for initial integration verification.

## Reference Sheet

The implementation will add `docs/VALD_API_REFERENCE.md`, generated from and
linked to the current official VALD guides and Swagger definitions. It will
document authentication, regional base URLs, endpoints, parameters, response
shapes, pagination, permissions, rate/error handling, and CLI examples.

The reference sheet will clearly distinguish:

- Current supported routes.
- Deprecated compatibility routes.
- Routes requiring VALD-granted recording permission.
- Confirmed behavior versus project-specific interpretation.

## Acceptance Criteria

The work is complete when:

1. New VALD credentials can authenticate using the March 2026 contract.
2. A profile-filtered test query returns complete paginated results.
3. Trial metrics can be retrieved for a test.
4. A permitted recording can be downloaded with sample data and cached.
5. Individual trial traces are correctly sliced from that recording.
6. Re-running the same sync creates no duplicate trial rows.
7. The existing averaged dashboard trace remains available.
8. JSON and CSV recording exports work.
9. The API reference sheet reflects current official documentation.
10. Automated tests pass and live verification succeeds against a temporary
    database.
