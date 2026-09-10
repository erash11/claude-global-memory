# VALD External API Reference

Verified against official VALD documentation and live Swagger on 2026-06-23.

## Authentication

- Token URL: `https://auth.prd.vald.com/oauth/token`
- Grant: `client_credentials`
- Audience: `vald-api-external`
- Do not send the deprecated `scope=api.external`.
- Cache tokens until shortly before `expires_in`.

## United States East Base URLs

| API | Base URL |
|---|---|
| ForceDecks | `https://prd-use-api-extforcedecks.valdperformance.com` |
| Profiles | `https://prd-use-api-externalprofile.valdperformance.com` |
| Tenants | `https://prd-use-api-externaltenants.valdperformance.com` |

## ForceDecks Endpoints

| Purpose | Method and path | Status |
|---|---|---|
| Tests | `GET /tests` | Current |
| Trial metrics/reps | `GET /v2019q3/teams/{teamId}/tests/{testId}/trials` | Current |
| Recording by test | `GET /v2019q3/teams/{teamId}/tests/{testId}/recording` | Current; permission required |
| Recording file by test | `GET /v2019q3/teams/{teamId}/tests/{testId}/recording/file` | Current; permission required |
| Recording by ID | `GET /v2019q3/teams/{teamId}/recordings/{recordingId}` | Deprecated compatibility route |
| Result definitions | `GET /resultdefinitions` | Current |

## Test Pagination

Call `/tests` with `tenantId`, `modifiedFromUtc`, and optional `profileId`.
Set the next `modifiedFromUtc` to the last returned test's
`modifiedDateUtc`. Stop when VALD returns HTTP 204.

## Raw Recording Contract

Use `includeSampleData=true` to receive `recordingDataHeader` and
`recordingData`. Resolve columns by header names. Trial `startTime` and
`endTime` values are seconds relative to the recording.

The CLI caches complete recording responses under:

```text
data/vald/recordings/<team-id>/<recording-id>.json.gz
```

## CLI Examples

```powershell
python vald_cli.py auth check
python vald_cli.py profiles list --search Nelms
python vald_cli.py tests list --profile-id <uuid> --from 2025-08-01
python vald_cli.py trials get --test-id <uuid>
python vald_cli.py recordings export --test-id <uuid> --format csv --output recording.csv
python vald_cli.py sync --profile-id <uuid> --from 2025-08-01
```

Use `--json` before the command group for machine-readable output:

```powershell
python vald_cli.py --json auth check
```

## Errors

- `401`: invalid, expired, or pre-March-2026 credentials.
- `403`: API client lacks permission for the resource.
- `404`: identifier is not visible in the selected tenant.
- `429`: honor `Retry-After`.

## Official Sources

- https://support.vald.com/hc/en-au/articles/23415335574553-How-to-integrate-with-VALD-APIs
- https://support.vald.com/hc/en-au/articles/38086939480729-A-guide-to-using-the-External-ForceDecks-API
- https://support.vald.com/hc/en-au/articles/55205316766233-API-Updates-March-2026-Breaking-Changes
- https://prd-use-api-extforcedecks.valdperformance.com/swagger/index.html
