# VALD ForceDecks Recording Pipeline and CLI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Modernize VALD authentication, retrieve and cache ForceDecks recordings, derive individual trial traces, persist them idempotently alongside dashboard-compatible averages, and expose the workflow through a CLI.

**Architecture:** `ForceDecksClient` remains the HTTP boundary and gains explicit methods for the documented VALD resources. Raw recordings are cached as atomic gzip JSON files, a pure extraction module slices samples by VALD trial intervals, and a persistence service upserts individual and averaged trials into SQLite. A standard-library `argparse` CLI composes those modules without coupling them to Flask routes.

**Tech Stack:** Python 3.11+, requests, python-dotenv, Flask-SQLAlchemy, NumPy/SciPy, pytest, gzip JSON, argparse, CSV.

## Global Constraints

- Use `https://auth.prd.vald.com/oauth/token` with `grant_type=client_credentials` and `audience=vald-api-external`.
- Do not send the deprecated `scope=api.external` parameter.
- Never log or persist client secrets, bearer tokens, or real athlete sample rows in tests.
- Prefer `/v2019q3/teams/{teamId}/tests/{testId}/recording`; retain `/recordings/{recordingId}` only as an explicit compatibility method.
- Cache raw responses under `data/vald/recordings/<team-id>/<recording-id>.json.gz`.
- Preserve existing worktree changes and database contents; do not reset or recreate the production database.
- Store individual trials and retain one derived `is_averaged=true` trial for dashboard compatibility.
- Use VALD trial IDs as the individual-trial idempotency key.
- Perform initial live verification against a temporary SQLite database.
- Follow test-driven development: every production behavior begins with a failing test.

---

## File Structure

```text
services/forcedecks_api.py          OAuth transport and documented API methods
services/vald_recording_cache.py    Atomic gzip cache and recording exports
services/vald_trial_extractor.py    Pure recording-to-trial transformation
services/vald_sync.py               API/cache/extraction/database orchestration
models/trial.py                     Persistent VALD identifiers and trial metrics
scripts/migrate_vald_trials.py      Non-destructive SQLite schema migration
vald_cli.py                         argparse command surface
tests/conftest.py                   Synthetic fixtures and temporary Flask app
tests/test_forcedecks_api.py        Authentication, retries, resources, pagination
tests/test_vald_recording_cache.py  Cache validation, atomic writes, exports
tests/test_vald_trial_extractor.py  Header parsing and interval slicing
tests/test_vald_sync.py             Idempotent persistence and averaged rows
tests/test_vald_cli.py              CLI parsing and output contracts
docs/VALD_API_REFERENCE.md          Current endpoint and operating reference
.env.example                        March 2026 configuration names
.gitignore                          Raw recording cache exclusion
requirements-dev.txt                pytest dependency
```

---

### Task 1: Test Harness and March 2026 OAuth Transport

**Files:**
- Create: `requirements-dev.txt`
- Create: `tests/conftest.py`
- Create: `tests/test_forcedecks_api.py`
- Modify: `config.py`
- Modify: `services/forcedecks_api.py`

**Interfaces:**
- Produces: `ForceDecksClient.__init__(client_id, client_secret, tenant_id, region="use", token_url=..., timeout=30, session=None)`
- Produces: `ForceDecksClient.authenticate(force=False) -> str`
- Produces: `ForceDecksClient.request_json(method, endpoint, *, base_url=None, params=None) -> dict | list | None`
- Produces: `AuthenticationError`, `PermissionDeniedError`, `DataNotFoundError`, `RateLimitError`, `InvalidResponseError`

- [ ] **Step 1: Add pytest as an isolated development dependency**

Create `requirements-dev.txt`:

```text
-r requirements.txt
pytest>=8.0,<9
```

- [ ] **Step 2: Create reusable synthetic response and app fixtures**

Create `tests/conftest.py`:

```python
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class FakeResponse:
    def __init__(self, status_code, payload=None, headers=None, text=""):
        self.status_code = status_code
        self._payload = payload
        self.headers = headers or {}
        self.text = text

    def json(self):
        if self._payload is None:
            raise ValueError("No JSON payload")
        return self._payload


@pytest.fixture
def fake_response():
    return FakeResponse
```

- [ ] **Step 3: Write failing OAuth and error-handling tests**

Add to `tests/test_forcedecks_api.py`:

```python
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest

from services.forcedecks_api import (
    AuthenticationError,
    ForceDecksClient,
    PermissionDeniedError,
)


def make_client(session):
    return ForceDecksClient(
        client_id="client-id",
        client_secret="client-secret",
        tenant_id="tenant-id",
        session=session,
    )


def test_authenticate_uses_march_2026_contract(fake_response):
    session = Mock()
    session.post.return_value = fake_response(
        200,
        {"access_token": "token", "expires_in": 7200},
    )
    client = make_client(session)

    assert client.authenticate() == "token"
    session.post.assert_called_once_with(
        "https://auth.prd.vald.com/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": "client-id",
            "client_secret": "client-secret",
            "audience": "vald-api-external",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )


def test_authenticate_reuses_unexpired_token(fake_response):
    session = Mock()
    session.post.return_value = fake_response(
        200,
        {"access_token": "token", "expires_in": 7200},
    )
    client = make_client(session)

    client.authenticate()
    client.authenticate()

    assert session.post.call_count == 1


def test_access_denied_explains_credential_migration(fake_response):
    session = Mock()
    session.post.return_value = fake_response(
        401,
        {"error": "access_denied"},
    )
    client = make_client(session)

    with pytest.raises(AuthenticationError, match="March 2026"):
        client.authenticate()


def test_request_refreshes_once_after_401(fake_response):
    session = Mock()
    session.post.side_effect = [
        fake_response(200, {"access_token": "first", "expires_in": 7200}),
        fake_response(200, {"access_token": "second", "expires_in": 7200}),
    ]
    session.request.side_effect = [
        fake_response(401, {"error": "expired"}),
        fake_response(200, {"ok": True}),
    ]
    client = make_client(session)

    assert client.request_json("GET", "/version") == {"ok": True}
    assert session.post.call_count == 2
    assert session.request.call_count == 2


def test_recording_403_is_permission_error(fake_response):
    session = Mock()
    session.post.return_value = fake_response(
        200,
        {"access_token": "token", "expires_in": 7200},
    )
    session.request.return_value = fake_response(403, {"error": "forbidden"})
    client = make_client(session)

    with pytest.raises(PermissionDeniedError, match="recording permission"):
        client.request_json(
            "GET",
            "/v2019q3/teams/tenant-id/tests/test-id/recording",
        )
```

- [ ] **Step 4: Run the tests and verify RED**

Run:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\venv\Scripts\python.exe -m pytest tests/test_forcedecks_api.py -v
```

Expected: collection or import failure because the new constructor and
`PermissionDeniedError` do not exist.

- [ ] **Step 5: Add current configuration with legacy-name fallback**

Modify the ForceDecks configuration section in `config.py`:

```python
    VALD_REGION = os.environ.get('VALD_REGION', 'use')
    VALD_TOKEN_URL = os.environ.get(
        'VALD_TOKEN_URL',
        'https://auth.prd.vald.com/oauth/token'
    )
    VALD_CLIENT_ID = os.environ.get(
        'VALD_CLIENT_ID',
        os.environ.get('FORCEDECKS_CLIENT_ID')
    )
    VALD_CLIENT_SECRET = os.environ.get(
        'VALD_CLIENT_SECRET',
        os.environ.get('FORCEDECKS_CLIENT_SECRET')
    )
    VALD_TENANT_ID = os.environ.get(
        'VALD_TENANT_ID',
        os.environ.get('FORCEDECKS_ORG_ID')
    )
    VALD_RECORDING_CACHE = os.environ.get(
        'VALD_RECORDING_CACHE',
        os.path.join(BASE_DIR, 'data', 'vald', 'recordings')
    )
```

Retain the existing `FORCEDECKS_*` class attributes temporarily so existing
scripts continue to load while later tasks migrate their callers.

- [ ] **Step 6: Replace the authentication and request core**

In `services/forcedecks_api.py`, retain the public exception names used by
existing scripts and implement this transport core:

```python
from datetime import datetime, timedelta, timezone
import logging
import time
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class ForceDecksAPIError(Exception):
    pass


class AuthenticationError(ForceDecksAPIError):
    pass


class PermissionDeniedError(ForceDecksAPIError):
    pass


class RateLimitError(ForceDecksAPIError):
    pass


class DataNotFoundError(ForceDecksAPIError):
    pass


class InvalidResponseError(ForceDecksAPIError):
    pass


class ForceDecksClient:
    REGION_BASE_URLS = {
        "use": "https://prd-use-api-extforcedecks.valdperformance.com",
        "aue": "https://prd-aue-api-extforcedecks.valdperformance.com",
        "euw": "https://prd-euw-api-extforcedecks.valdperformance.com",
    }
    PROFILE_BASE_URLS = {
        key: value.replace("extforcedecks", "externalprofile")
        for key, value in REGION_BASE_URLS.items()
    }
    TENANT_BASE_URLS = {
        key: value.replace("extforcedecks", "externaltenants")
        for key, value in REGION_BASE_URLS.items()
    }

    def __init__(
        self,
        base_url=None,
        timeout=30,
        api_key=None,
        client_id=None,
        client_secret=None,
        org_id=None,
        tenant_id=None,
        region="use",
        token_url="https://auth.prd.vald.com/oauth/token",
        session=None,
    ):
        if api_key and not client_id:
            logger.warning("FORCEDECKS_API_KEY is no longer supported")
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id or org_id
        self.region = region
        self.base_url = (base_url or self.REGION_BASE_URLS[region]).rstrip("/")
        self.profile_base_url = self.PROFILE_BASE_URLS[region]
        self.tenant_base_url = self.TENANT_BASE_URLS[region]
        self.token_url = token_url
        self.timeout = timeout
        self.session = session or requests.Session()
        self.access_token = None
        self.token_expires_at = None

    def authenticate(self, force=False):
        now = datetime.now(timezone.utc)
        if (
            not force
            and self.access_token
            and self.token_expires_at
            and now < self.token_expires_at - timedelta(seconds=60)
        ):
            return self.access_token
        if not self.client_id or not self.client_secret:
            raise AuthenticationError("VALD_CLIENT_ID and VALD_CLIENT_SECRET are required")
        response = self.session.post(
            self.token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "audience": "vald-api-external",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=self.timeout,
        )
        if response.status_code != 200:
            try:
                error = response.json().get("error", "unknown")
            except ValueError:
                error = "unknown"
            if error == "access_denied":
                raise AuthenticationError(
                    "VALD rejected these credentials. Confirm the replacement "
                    "client credentials issued for the March 2026 migration."
                )
            raise AuthenticationError(
                f"VALD authentication failed with HTTP {response.status_code}: {error}"
            )
        payload = response.json()
        self.access_token = payload.get("access_token")
        if not self.access_token:
            raise AuthenticationError("VALD token response omitted access_token")
        self.token_expires_at = now + timedelta(
            seconds=int(payload.get("expires_in", 3600))
        )
        return self.access_token

    def request_json(
        self,
        method,
        endpoint,
        *,
        base_url=None,
        params=None,
        max_retries=3,
    ):
        refreshed = False
        target = f"{(base_url or self.base_url).rstrip('/')}/{endpoint.lstrip('/')}"
        for attempt in range(max_retries):
            token = self.authenticate(force=refreshed)
            response = self.session.request(
                method,
                target,
                params=params,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json",
                },
                timeout=self.timeout,
            )
            if response.status_code == 401 and not refreshed:
                refreshed = True
                continue
            if response.status_code == 403:
                detail = (
                    "VALD denied recording permission for this API client."
                    if "/recording" in endpoint
                    else "VALD denied access to this resource."
                )
                raise PermissionDeniedError(detail)
            if response.status_code == 404:
                raise DataNotFoundError(f"VALD resource not found: {endpoint}")
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "1"))
                if attempt == max_retries - 1:
                    raise RateLimitError("VALD rate limit retries exhausted")
                time.sleep(retry_after)
                continue
            if response.status_code == 204:
                return None
            if response.status_code >= 400:
                raise ForceDecksAPIError(
                    f"VALD request failed with HTTP {response.status_code}"
                )
            try:
                return response.json()
            except ValueError as exc:
                raise InvalidResponseError(
                    f"VALD returned invalid JSON for {endpoint}"
                ) from exc
        raise ForceDecksAPIError("VALD request retries exhausted")
```

- [ ] **Step 7: Run the OAuth tests and verify GREEN**

Run:

```powershell
.\venv\Scripts\python.exe -m pytest tests/test_forcedecks_api.py -v
```

Expected: all Task 1 tests pass.

- [ ] **Step 8: Commit Task 1**

```powershell
git add requirements-dev.txt tests/conftest.py tests/test_forcedecks_api.py config.py services/forcedecks_api.py
git commit -m "feat: modernize VALD OAuth transport"
```

---

### Task 2: Documented ForceDecks, Profiles, and Tenants Resources

**Files:**
- Modify: `tests/test_forcedecks_api.py`
- Modify: `services/forcedecks_api.py`

**Interfaces:**
- Consumes: `ForceDecksClient.request_json(...)`
- Produces: `list_tests(profile_id, modified_from_utc, recorded_to=None) -> list[dict]`
- Produces: `get_trials(test_id, team_id=None) -> list[dict]`
- Produces: `get_recording_by_test(test_id, team_id=None, include_samples=False) -> dict`
- Produces: `get_recording_by_id(recording_id, team_id=None, include_samples=False) -> dict`
- Produces: `list_result_definitions() -> list[dict]`
- Produces: `list_profiles(search=None) -> list[dict]`
- Produces: `list_tenants() -> list[dict]`

- [ ] **Step 1: Write failing resource and pagination tests**

Append to `tests/test_forcedecks_api.py`:

```python
def test_list_tests_uses_profile_filter_and_paginates(fake_response):
    session = Mock()
    session.post.return_value = fake_response(
        200,
        {"access_token": "token", "expires_in": 7200},
    )
    session.request.side_effect = [
        fake_response(
            200,
            {
                "tests": [
                    {
                        "testId": "test-1",
                        "profileId": "profile-1",
                        "modifiedDateUtc": "2026-01-02T00:00:00.000Z",
                        "recordedDateUtc": "2026-01-01T00:00:00.000Z",
                    }
                ]
            },
        ),
        fake_response(204),
    ]
    client = make_client(session)

    tests = client.list_tests(
        profile_id="profile-1",
        modified_from_utc="2026-01-01T00:00:00.000Z",
    )

    assert [item["testId"] for item in tests] == ["test-1"]
    first_params = session.request.call_args_list[0].kwargs["params"]
    second_params = session.request.call_args_list[1].kwargs["params"]
    assert first_params == {
        "tenantId": "tenant-id",
        "modifiedFromUtc": "2026-01-01T00:00:00.000Z",
        "profileId": "profile-1",
    }
    assert second_params["modifiedFromUtc"] == "2026-01-02T00:00:00.000Z"


def test_recording_methods_use_supported_and_compatibility_routes(fake_response):
    session = Mock()
    session.post.return_value = fake_response(
        200,
        {"access_token": "token", "expires_in": 7200},
    )
    session.request.side_effect = [
        fake_response(200, {"id": "recording-1"}),
        fake_response(200, {"id": "recording-1"}),
    ]
    client = make_client(session)

    client.get_recording_by_test("test-1", include_samples=True)
    client.get_recording_by_id("recording-1", include_samples=True)

    urls = [call.args[1] for call in session.request.call_args_list]
    assert urls[0].endswith(
        "/v2019q3/teams/tenant-id/tests/test-1/recording"
    )
    assert urls[1].endswith(
        "/v2019q3/teams/tenant-id/recordings/recording-1"
    )
    assert all(
        call.kwargs["params"] == {"includeSampleData": "true"}
        for call in session.request.call_args_list
    )


def test_profiles_use_external_profile_base_url(fake_response):
    session = Mock()
    session.post.return_value = fake_response(
        200,
        {"access_token": "token", "expires_in": 7200},
    )
    session.request.return_value = fake_response(
        200,
        {"profiles": [{"profileId": "profile-1", "givenName": "Test"}]},
    )
    client = make_client(session)

    profiles = client.list_profiles(search="Test")

    assert profiles[0]["profileId"] == "profile-1"
    assert "externalprofile" in session.request.call_args.args[1]
```

- [ ] **Step 2: Run the tests and verify RED**

Run:

```powershell
.\venv\Scripts\python.exe -m pytest tests/test_forcedecks_api.py -v
```

Expected: failures because the resource methods do not exist.

- [ ] **Step 3: Implement the resource methods**

Add these methods to `ForceDecksClient`:

```python
    def _team_id(self, team_id):
        value = team_id or self.tenant_id
        if not value:
            raise ValueError("A VALD tenant/team ID is required")
        return value

    def list_tests(self, profile_id, modified_from_utc, recorded_to=None):
        cursor = modified_from_utc
        collected = []
        seen_cursors = set()
        while cursor not in seen_cursors:
            seen_cursors.add(cursor)
            payload = self.request_json(
                "GET",
                "/tests",
                params={
                    "tenantId": self._team_id(None),
                    "modifiedFromUtc": cursor,
                    "profileId": profile_id,
                },
            )
            if payload is None:
                break
            page = payload.get("tests", []) if isinstance(payload, dict) else payload
            if not page:
                break
            for test in page:
                recorded = test.get("recordedDateUtc", "")
                if not recorded_to or recorded[:10] <= recorded_to:
                    collected.append(test)
            next_cursor = page[-1].get("modifiedDateUtc")
            if not next_cursor or next_cursor == cursor:
                break
            cursor = next_cursor
        return collected

    def get_trials(self, test_id, team_id=None):
        payload = self.request_json(
            "GET",
            f"/v2019q3/teams/{self._team_id(team_id)}/tests/{test_id}/trials",
        )
        return payload or []

    def get_recording_by_test(
        self,
        test_id,
        team_id=None,
        include_samples=False,
    ):
        return self.request_json(
            "GET",
            f"/v2019q3/teams/{self._team_id(team_id)}/tests/{test_id}/recording",
            params={
                "includeSampleData": str(bool(include_samples)).lower(),
            },
        )

    def get_recording_by_id(
        self,
        recording_id,
        team_id=None,
        include_samples=False,
    ):
        return self.request_json(
            "GET",
            f"/v2019q3/teams/{self._team_id(team_id)}/recordings/{recording_id}",
            params={
                "includeSampleData": str(bool(include_samples)).lower(),
            },
        )

    def list_result_definitions(self):
        payload = self.request_json("GET", "/resultdefinitions")
        if isinstance(payload, dict):
            return payload.get("resultDefinitions", [])
        return payload or []

    def list_profiles(self, search=None):
        payload = self.request_json(
            "GET",
            "/profiles",
            base_url=self.profile_base_url,
            params={
                "tenantId": self._team_id(None),
                **({"search": search} if search else {}),
            },
        )
        if isinstance(payload, dict):
            return payload.get("profiles", [])
        return payload or []

    def list_tenants(self):
        payload = self.request_json(
            "GET",
            "/tenants",
            base_url=self.tenant_base_url,
        )
        if isinstance(payload, dict):
            return payload.get("tenants", [])
        return payload or []
```

Replace the old guessed implementations of `get_trial_force_trace`,
`get_session_trials`, `get_athlete_info`, `list_profiles`, and `list_teams`.
Keep compatibility wrappers only where current callers require them:

```python
    def list_teams(self):
        return self.list_tenants()

    def get_session_trials(self, athlete_id, session_date, test_type="CMJ"):
        tests = self.list_tests(
            profile_id=athlete_id,
            modified_from_utc=f"{session_date}T00:00:00.000Z",
            recorded_to=session_date,
        )
        matching = [
            test for test in tests
            if test.get("recordedDateUtc", "")[:10] == session_date
            and (not test_type or test.get("testType") == test_type)
        ]
        if not matching:
            return []
        return self.get_trials(matching[0]["testId"])
```

- [ ] **Step 4: Run the resource tests and verify GREEN**

Run:

```powershell
.\venv\Scripts\python.exe -m pytest tests/test_forcedecks_api.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit Task 2**

```powershell
git add tests/test_forcedecks_api.py services/forcedecks_api.py
git commit -m "feat: add documented VALD API resources"
```

---

### Task 3: Atomic Recording Cache, Exports, and Trial Extraction

**Files:**
- Create: `services/vald_recording_cache.py`
- Create: `services/vald_trial_extractor.py`
- Create: `tests/test_vald_recording_cache.py`
- Create: `tests/test_vald_trial_extractor.py`
- Modify: `.gitignore`

**Interfaces:**
- Produces: `RecordingCache(root: Path)`
- Produces: `RecordingCache.load(team_id, recording_id) -> dict | None`
- Produces: `RecordingCache.store(team_id, recording_id, payload) -> Path`
- Produces: `RecordingCache.get_or_fetch(team_id, recording_id, fetcher, refresh=False) -> tuple[dict, Path, bool]`
- Produces: `export_recording_json(recording, output_path) -> Path`
- Produces: `export_recording_csv(recording, output_path) -> Path`
- Produces: `extract_trials(recording, trials, test_id) -> list[dict]`

- [ ] **Step 1: Write failing cache tests**

Create `tests/test_vald_recording_cache.py`:

```python
import gzip
import json

from services.vald_recording_cache import (
    RecordingCache,
    export_recording_csv,
)


def recording():
    return {
        "id": "recording-1",
        "recordingDataHeader": ["Time", "Z Left", "Z Right"],
        "recordingData": [[0.0, 100.0, 200.0], [0.01, 110.0, 210.0]],
    }


def test_store_writes_valid_gzip_json_atomically(tmp_path):
    cache = RecordingCache(tmp_path)

    path = cache.store("team-1", "recording-1", recording())

    assert path == tmp_path / "team-1" / "recording-1.json.gz"
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        assert json.load(handle)["id"] == "recording-1"
    assert not list(path.parent.glob("*.tmp"))


def test_get_or_fetch_reuses_valid_cache(tmp_path):
    cache = RecordingCache(tmp_path)
    cache.store("team-1", "recording-1", recording())
    calls = []

    payload, path, downloaded = cache.get_or_fetch(
        "team-1",
        "recording-1",
        lambda: calls.append(True),
    )

    assert payload["id"] == "recording-1"
    assert downloaded is False
    assert calls == []


def test_corrupt_cache_is_downloaded_again(tmp_path):
    cache = RecordingCache(tmp_path)
    path = tmp_path / "team-1" / "recording-1.json.gz"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"not-gzip")

    payload, _, downloaded = cache.get_or_fetch(
        "team-1",
        "recording-1",
        recording,
    )

    assert payload["id"] == "recording-1"
    assert downloaded is True


def test_csv_export_uses_recording_headers(tmp_path):
    output = tmp_path / "recording.csv"

    export_recording_csv(recording(), output)

    assert output.read_text(encoding="utf-8").splitlines() == [
        "Time,Z Left,Z Right",
        "0.0,100.0,200.0",
        "0.01,110.0,210.0",
    ]
```

- [ ] **Step 2: Write failing extraction tests**

Create `tests/test_vald_trial_extractor.py`:

```python
import pytest

from services.vald_trial_extractor import RecordingSchemaError, extract_trials


def recording():
    return {
        "id": "recording-1",
        "samplingFrequency": 100,
        "recordingDataHeader": ["Time", "Z Left", "Z Right"],
        "recordingData": [
            [0.00, 100.0, 200.0],
            [0.01, 110.0, 210.0],
            [0.02, 120.0, 220.0],
            [0.03, 130.0, 230.0],
        ],
    }


def test_extract_trials_slices_by_time_and_combines_force():
    trials = [
        {
            "id": "trial-1",
            "startTime": 0.01,
            "endTime": 0.02,
            "results": [{"resultId": 1, "value": 3.5}],
        }
    ]

    extracted = extract_trials(recording(), trials, test_id="test-1")

    assert extracted == [
        {
            "trial_id": "trial-1",
            "test_id": "test-1",
            "recording_id": "recording-1",
            "trial_number": 1,
            "sampling_rate": 100,
            "time": [0.01, 0.02],
            "force_left": [110.0, 120.0],
            "force_right": [210.0, 220.0],
            "force_total": [320.0, 340.0],
            "metrics": [{"resultId": 1, "value": 3.5}],
        }
    ]


def test_extract_trials_reports_received_headers():
    payload = recording()
    payload["recordingDataHeader"] = ["Time", "Unknown"]

    with pytest.raises(RecordingSchemaError, match="Time, Unknown"):
        extract_trials(payload, [], test_id="test-1")
```

- [ ] **Step 3: Run both test modules and verify RED**

Run:

```powershell
.\venv\Scripts\python.exe -m pytest tests/test_vald_recording_cache.py tests/test_vald_trial_extractor.py -v
```

Expected: import failures because both modules are absent.

- [ ] **Step 4: Implement the recording cache and exports**

Create `services/vald_recording_cache.py`:

```python
from pathlib import Path
import csv
import gzip
import json
import os
import tempfile


class RecordingCache:
    def __init__(self, root):
        self.root = Path(root)

    def path_for(self, team_id, recording_id):
        return self.root / str(team_id) / f"{recording_id}.json.gz"

    def load(self, team_id, recording_id):
        path = self.path_for(team_id, recording_id)
        if not path.exists() or path.stat().st_size == 0:
            return None
        try:
            with gzip.open(path, "rt", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError):
            return None
        return payload if isinstance(payload, dict) else None

    def store(self, team_id, recording_id, payload):
        path = self.path_for(team_id, recording_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temp_name = tempfile.mkstemp(
            prefix=f"{recording_id}.",
            suffix=".tmp",
            dir=path.parent,
        )
        os.close(descriptor)
        temp_path = Path(temp_name)
        try:
            with gzip.open(temp_path, "wt", encoding="utf-8") as handle:
                json.dump(payload, handle, separators=(",", ":"))
            temp_path.replace(path)
        finally:
            temp_path.unlink(missing_ok=True)
        return path

    def get_or_fetch(
        self,
        team_id,
        recording_id,
        fetcher,
        refresh=False,
    ):
        if not refresh:
            cached = self.load(team_id, recording_id)
            if cached is not None:
                return cached, self.path_for(team_id, recording_id), False
        payload = fetcher()
        path = self.store(team_id, recording_id, payload)
        return payload, path, True


def export_recording_json(recording, output_path):
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(recording, indent=2),
        encoding="utf-8",
    )
    return path


def export_recording_csv(recording, output_path):
    headers = recording.get("recordingDataHeader", [])
    rows = recording.get("recordingData", [])
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(headers)
        writer.writerows(rows)
    return path
```

- [ ] **Step 5: Implement pure trial extraction**

Create `services/vald_trial_extractor.py`:

```python
class RecordingSchemaError(ValueError):
    pass


def _find_header(headers, candidates):
    normalized = {
        str(header).strip().lower(): index
        for index, header in enumerate(headers)
    }
    for candidate in candidates:
        if candidate.lower() in normalized:
            return normalized[candidate.lower()]
    return None


def extract_trials(recording, trials, test_id):
    headers = recording.get("recordingDataHeader", [])
    rows = recording.get("recordingData", [])
    time_index = _find_header(headers, ["Time"])
    left_index = _find_header(headers, ["Z Left", "ForceZ Left"])
    right_index = _find_header(headers, ["Z Right", "ForceZ Right"])
    if time_index is None or (left_index is None and right_index is None):
        raise RecordingSchemaError(
            "Unsupported recording headers: " + ", ".join(map(str, headers))
        )

    extracted = []
    for number, trial in enumerate(trials, start=1):
        start = float(trial["startTime"])
        end = float(trial["endTime"])
        selected = [
            row for row in rows
            if start <= float(row[time_index]) <= end
        ]
        if not selected:
            raise RecordingSchemaError(
                f"No samples for test {test_id}, trial {trial.get('id')}"
            )
        times = [float(row[time_index]) for row in selected]
        left = [
            float(row[left_index]) if left_index is not None else 0.0
            for row in selected
        ]
        right = [
            float(row[right_index]) if right_index is not None else 0.0
            for row in selected
        ]
        extracted.append(
            {
                "trial_id": trial["id"],
                "test_id": test_id,
                "recording_id": recording["id"],
                "trial_number": number,
                "sampling_rate": int(recording["samplingFrequency"]),
                "time": times,
                "force_left": left,
                "force_right": right,
                "force_total": [
                    left_value + right_value
                    for left_value, right_value in zip(left, right)
                ],
                "metrics": trial.get("results", []),
            }
        )
    return extracted
```

- [ ] **Step 6: Ignore raw cache files**

Append to `.gitignore`:

```text
# VALD immutable raw recording cache
data/vald/recordings/
```

- [ ] **Step 7: Run both modules and verify GREEN**

Run:

```powershell
.\venv\Scripts\python.exe -m pytest tests/test_vald_recording_cache.py tests/test_vald_trial_extractor.py -v
```

Expected: all tests pass.

- [ ] **Step 8: Commit Task 3**

```powershell
git add .gitignore services/vald_recording_cache.py services/vald_trial_extractor.py tests/test_vald_recording_cache.py tests/test_vald_trial_extractor.py
git commit -m "feat: cache and extract VALD recordings"
```

---

### Task 4: Non-Destructive Trial Schema and Idempotent Sync

**Files:**
- Modify: `app.py`
- Modify: `models/trial.py`
- Create: `scripts/migrate_vald_trials.py`
- Create: `services/vald_sync.py`
- Create: `tests/test_vald_sync.py`

**Interfaces:**
- Consumes: `ForceDecksClient`, `RecordingCache`, `extract_trials`
- Produces: `sync_test(app, client, cache, athlete, test, refresh=False) -> dict`
- Produces: `sync_profile(app, client, cache, athlete, date_from, date_to=None, refresh=False) -> dict`

- [ ] **Step 1: Write failing idempotent-sync test**

Create `tests/test_vald_sync.py`:

```python
from datetime import date
from unittest.mock import Mock

from app import create_app
from models import Athlete, Trial, db
from services.vald_recording_cache import RecordingCache
from services.vald_sync import sync_test


def make_test_app(tmp_path):
    app = create_app(
        "development",
        config_overrides={
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.db'}",
        },
    )
    db.drop_all()
    db.create_all()
    return app


def recording():
    return {
        "id": "recording-1",
        "samplingFrequency": 1000,
        "recordingDataHeader": ["Time", "Z Left", "Z Right"],
        "recordingData": [
            [
                index / 1000,
                300.0 + (index % 100),
                300.0 + (index % 100),
            ]
            for index in range(400)
        ],
    }


def test_sync_test_is_idempotent_and_keeps_average(tmp_path):
    app = make_test_app(tmp_path)
    client = Mock()
    client.tenant_id = "team-1"
    client.get_trials.return_value = [
        {
            "id": "trial-1",
            "startTime": 0.00,
            "endTime": 0.399,
            "results": [],
        }
    ]
    client.get_recording_by_test.return_value = recording()
    cache = RecordingCache(tmp_path / "cache")
    test = {
        "testId": "test-1",
        "recordingId": "recording-1",
        "recordedDateUtc": "2026-01-01T00:00:00.000Z",
        "testType": "CMJ",
    }

    with app.app_context():
        athlete = Athlete(
            name="Synthetic Athlete",
            position="Guard",
            injury_date=None,
            normative_data="{}",
            forcedecks_id="profile-1",
        )
        db.session.add(athlete)
        db.session.commit()

        first = sync_test(app, client, cache, athlete, test)
        second = sync_test(app, client, cache, athlete, test)

        assert first["individual_trials"] == 1
        assert second["individual_trials"] == 1
        assert Trial.query.filter_by(
            forcedecks_trial_id="trial-1",
            is_averaged=False,
        ).count() == 1
        assert Trial.query.filter_by(
            forcedecks_test_id="test-1",
            is_averaged=True,
        ).count() == 1
```

- [ ] **Step 2: Run the sync test and verify RED**

Run:

```powershell
.\venv\Scripts\python.exe -m pytest tests/test_vald_sync.py -v
```

Expected: import failure because `services.vald_sync` does not exist.

- [ ] **Step 3: Extend the Trial model without removing existing columns**

First, modify `create_app` in `app.py` so tests can select a database before
Flask-SQLAlchemy is initialized:

```python
def create_app(config_name='development', config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    if config_overrides:
        app.config.update(config_overrides)
```

Keep the rest of the factory in its current order after this configuration
block.

Add to `models/trial.py`:

```python
    forcedecks_recording_id = db.Column(
        db.String(100),
        nullable=True,
        index=True,
    )
    trial_metrics = db.Column(db.Text, nullable=True)

    def get_trial_metrics(self):
        return json.loads(self.trial_metrics) if self.trial_metrics else []

    def set_trial_metrics(self, data):
        self.trial_metrics = json.dumps(data)
```

Add these fields to `to_dict()`:

```python
            'forcedecks_recording_id': self.forcedecks_recording_id,
            'trial_metrics': self.get_trial_metrics(),
```

- [ ] **Step 4: Create a non-destructive SQLite migration**

Create `scripts/migrate_vald_trials.py`:

```python
from pathlib import Path
import sqlite3

from config import Config


COLUMNS = {
    "forcedecks_recording_id": "VARCHAR(100)",
    "trial_metrics": "TEXT",
}


def sqlite_path():
    uri = Config.SQLALCHEMY_DATABASE_URI
    prefix = "sqlite:///"
    if not uri.startswith(prefix):
        raise RuntimeError("This migration script supports SQLite only")
    return Path(uri[len(prefix):]).resolve()


def migrate(path=None):
    database = Path(path).resolve() if path else sqlite_path()
    connection = sqlite3.connect(database)
    try:
        existing = {
            row[1]
            for row in connection.execute("PRAGMA table_info(trials)")
        }
        for name, sql_type in COLUMNS.items():
            if name not in existing:
                connection.execute(
                    f"ALTER TABLE trials ADD COLUMN {name} {sql_type}"
                )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS "
            "ix_trials_forcedecks_recording_id "
            "ON trials (forcedecks_recording_id)"
        )
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    migrate()
```

- [ ] **Step 5: Implement sync orchestration**

Create `services/vald_sync.py`:

```python
from datetime import date
import json

import numpy as np

from models import Session, Trial, db
from services.forcedecks_processor import (
    calculate_movement_initiation,
    compute_session_average,
    validate_trial_quality,
)
from services.vald_trial_extractor import extract_trials


def _session_for(athlete, test):
    test_date = date.fromisoformat(test["recordedDateUtc"][:10])
    session = Session.query.filter_by(
        athlete_id=athlete.id,
        test_date=test_date,
        test_type=test.get("testType") or "CMJ",
    ).first()
    if session is None:
        session = Session(
            athlete_id=athlete.id,
            test_date=test_date,
            test_type=test.get("testType") or "CMJ",
            metrics="{}",
            notes="Imported from VALD ForceDecks",
        )
        db.session.add(session)
        db.session.flush()
    return session


def _upsert_individual(session, extracted):
    trial = Trial.query.filter_by(
        forcedecks_trial_id=extracted["trial_id"],
        is_averaged=False,
    ).first()
    if trial is None:
        trial = Trial(
            session_id=session.id,
            trial_number=extracted["trial_number"],
            force_time_data="[]",
            movement_initiation_index=0,
            is_averaged=False,
            data_source="forcedecks",
        )
        db.session.add(trial)
    trial.session_id = session.id
    trial.trial_number = extracted["trial_number"]
    trial.forcedecks_test_id = extracted["test_id"]
    trial.forcedecks_trial_id = extracted["trial_id"]
    trial.forcedecks_recording_id = extracted["recording_id"]
    trial.sampling_rate = extracted["sampling_rate"]
    trial.force_time_data = json.dumps(
        list(zip(extracted["time"], extracted["force_total"]))
    )
    trial.raw_force_left = json.dumps(extracted["force_left"])
    trial.raw_force_right = json.dumps(extracted["force_right"])
    trial.trial_metrics = json.dumps(extracted["metrics"])
    force = np.asarray(extracted["force_total"], dtype=float)
    valid, _ = validate_trial_quality(force)
    trial.quality_score = 100.0 if valid else 0.0
    trial.movement_initiation_index = 0
    return trial


def _replace_average(session, test_id, extracted):
    Trial.query.filter_by(
        session_id=session.id,
        forcedecks_test_id=test_id,
        is_averaged=True,
    ).delete()
    average = compute_session_average(extracted)
    averaged = Trial(
        session_id=session.id,
        trial_number=0,
        force_time_data=json.dumps(
            list(
                zip(
                    average["averaged_trace"]["time"],
                    average["averaged_trace"]["force"],
                )
            )
        ),
        movement_initiation_index=average["movement_initiation_index"],
        forcedecks_test_id=test_id,
        forcedecks_recording_id=extracted[0]["recording_id"],
        sampling_rate=average["averaged_trace"]["sampling_rate"],
        is_averaged=True,
        data_source="forcedecks",
        quality_score=average["quality_score"],
    )
    db.session.add(averaged)
    session.set_metrics(average["metrics"])
    return averaged


def sync_test(app, client, cache, athlete, test, refresh=False):
    test_id = test["testId"]
    recording_id = test["recordingId"]
    team_id = test.get("tenantId") or client.tenant_id
    trials = client.get_trials(test_id, team_id=team_id)
    recording, cache_path, downloaded = cache.get_or_fetch(
        team_id,
        recording_id,
        lambda: client.get_recording_by_test(
            test_id,
            team_id=team_id,
            include_samples=True,
        ),
        refresh=refresh,
    )
    extracted = extract_trials(recording, trials, test_id)
    session = _session_for(athlete, test)
    for item in extracted:
        _upsert_individual(session, item)
    _replace_average(session, test_id, extracted)
    db.session.commit()
    return {
        "test_id": test_id,
        "recording_id": recording_id,
        "cache_path": str(cache_path),
        "downloaded": downloaded,
        "individual_trials": len(extracted),
    }


def sync_profile(
    app,
    client,
    cache,
    athlete,
    date_from,
    date_to=None,
    refresh=False,
):
    tests = client.list_tests(
        profile_id=athlete.forcedecks_id,
        modified_from_utc=f"{date_from}T00:00:00.000Z",
        recorded_to=date_to,
    )
    results = [
        sync_test(app, client, cache, athlete, test, refresh=refresh)
        for test in tests
    ]
    return {
        "profile_id": athlete.forcedecks_id,
        "tests_synced": len(results),
        "results": results,
    }
```

If `validate_trial_quality` rejects short synthetic fixtures, adjust only the
fixture duration or test-specific quality assertion. Do not weaken production
validation to satisfy the test.

- [ ] **Step 6: Run the migration against a copied temporary database**

Run:

```powershell
Copy-Item .\instance\cmj_report.db $env:TEMP\pt_dash_vald_migration_test.db -Force
.\venv\Scripts\python.exe -c "from scripts.migrate_vald_trials import migrate; migrate(r'$env:TEMP\pt_dash_vald_migration_test.db')"
```

Expected: command exits successfully and the source database timestamp does not
change.

- [ ] **Step 7: Run the sync test and verify GREEN**

Run:

```powershell
.\venv\Scripts\python.exe -m pytest tests/test_vald_sync.py -v
```

Expected: all tests pass with one individual and one averaged trial after both
sync calls.

- [ ] **Step 8: Commit Task 4**

```powershell
git add app.py models/trial.py scripts/migrate_vald_trials.py services/vald_sync.py tests/test_vald_sync.py
git commit -m "feat: persist VALD trials idempotently"
```

---

### Task 5: VALD CLI

**Files:**
- Create: `vald_cli.py`
- Create: `tests/test_vald_cli.py`

**Interfaces:**
- Consumes: `ForceDecksClient`, `RecordingCache`, export helpers, `sync_profile`
- Produces: `build_parser() -> argparse.ArgumentParser`
- Produces: `main(argv=None) -> int`

- [ ] **Step 1: Write failing CLI contract tests**

Create `tests/test_vald_cli.py`:

```python
import json
from unittest.mock import Mock

import vald_cli


def test_parser_requires_one_recording_identifier():
    parser = vald_cli.build_parser()

    args = parser.parse_args(
        [
            "recordings",
            "get",
            "--test-id",
            "test-1",
            "--include-samples",
        ]
    )

    assert args.test_id == "test-1"
    assert args.recording_id is None
    assert args.include_samples is True


def test_auth_check_json_output(monkeypatch, capsys):
    client = Mock()
    client.authenticate.return_value = "secret-token"
    monkeypatch.setattr(vald_cli, "make_client", lambda: client)

    result = vald_cli.main(["--json", "auth", "check"])

    assert result == 0
    assert json.loads(capsys.readouterr().out) == {
        "authenticated": True
    }
```

- [ ] **Step 2: Run CLI tests and verify RED**

Run:

```powershell
.\venv\Scripts\python.exe -m pytest tests/test_vald_cli.py -v
```

Expected: import failure because `vald_cli.py` does not exist.

- [ ] **Step 3: Implement parser, client factory, and output helpers**

Create `vald_cli.py` with this command structure:

```python
import argparse
from datetime import date, timedelta
import json
import os
from pathlib import Path
import sys

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from config import Config
from models import Athlete
from services.forcedecks_api import ForceDecksClient, ForceDecksAPIError
from services.vald_recording_cache import (
    RecordingCache,
    export_recording_csv,
    export_recording_json,
)
from services.vald_sync import sync_profile


def make_client():
    return ForceDecksClient(
        client_id=Config.VALD_CLIENT_ID,
        client_secret=Config.VALD_CLIENT_SECRET,
        tenant_id=Config.VALD_TENANT_ID,
        region=Config.VALD_REGION,
        token_url=Config.VALD_TOKEN_URL,
        timeout=Config.FORCEDECKS_TIMEOUT,
    )


def build_parser():
    parser = argparse.ArgumentParser(prog="vald_cli.py")
    parser.add_argument("--json", action="store_true", dest="json_output")
    groups = parser.add_subparsers(dest="group", required=True)

    auth = groups.add_parser("auth").add_subparsers(
        dest="command",
        required=True,
    )
    auth.add_parser("check")

    tenants = groups.add_parser("tenants").add_subparsers(
        dest="command",
        required=True,
    )
    tenants.add_parser("list")

    profiles = groups.add_parser("profiles").add_subparsers(
        dest="command",
        required=True,
    )
    profiles_list = profiles.add_parser("list")
    profiles_list.add_argument("--search")

    tests = groups.add_parser("tests").add_subparsers(
        dest="command",
        required=True,
    )
    tests_list = tests.add_parser("list")
    tests_list.add_argument("--profile-id", required=True)
    tests_list.add_argument("--from", required=True, dest="date_from")
    tests_list.add_argument("--to", dest="date_to")

    trials = groups.add_parser("trials").add_subparsers(
        dest="command",
        required=True,
    )
    trials_get = trials.add_parser("get")
    trials_get.add_argument("--test-id", required=True)

    recordings = groups.add_parser("recordings").add_subparsers(
        dest="command",
        required=True,
    )
    for command in ("get", "export"):
        item = recordings.add_parser(command)
        identifiers = item.add_mutually_exclusive_group(required=True)
        identifiers.add_argument("--test-id")
        identifiers.add_argument("--recording-id")
        item.add_argument("--include-samples", action="store_true")
        item.add_argument("--refresh", action="store_true")
        if command == "export":
            item.add_argument(
                "--format",
                choices=["json", "csv"],
                required=True,
            )
            item.add_argument("--output", required=True)

    sync = groups.add_parser("sync")
    sync.add_argument("--profile-id", required=True)
    sync.add_argument("--from", required=True, dest="date_from")
    sync.add_argument("--to", dest="date_to")
    sync.add_argument("--refresh", action="store_true")
    return parser


def emit(payload, as_json=False):
    if as_json:
        print(json.dumps(payload, indent=2, default=str))
        return
    if isinstance(payload, list):
        for item in payload:
            print(" | ".join(f"{key}={value}" for key, value in item.items()))
    elif isinstance(payload, dict):
        for key, value in payload.items():
            print(f"{key}: {value}")
    else:
        print(payload)
```

- [ ] **Step 4: Implement command dispatch without printing raw samples**

Append to `vald_cli.py`:

```python
def _recording(client, args):
    if args.test_id:
        return client.get_recording_by_test(
            args.test_id,
            include_samples=args.include_samples or args.command == "export",
        )
    return client.get_recording_by_id(
        args.recording_id,
        include_samples=args.include_samples or args.command == "export",
    )


def _recording_summary(recording):
    return {
        "recording_id": recording.get("id"),
        "sampling_frequency": recording.get("samplingFrequency"),
        "duration": recording.get("duration"),
        "headers": recording.get("recordingDataHeader", []),
        "sample_rows": len(recording.get("recordingData", [])),
    }


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        client = make_client()
        if args.group == "auth":
            client.authenticate()
            emit({"authenticated": True}, args.json_output)
            return 0
        if args.group == "tenants":
            emit(client.list_tenants(), args.json_output)
            return 0
        if args.group == "profiles":
            emit(client.list_profiles(search=args.search), args.json_output)
            return 0
        if args.group == "tests":
            emit(
                client.list_tests(
                    args.profile_id,
                    f"{args.date_from}T00:00:00.000Z",
                    args.date_to,
                ),
                args.json_output,
            )
            return 0
        if args.group == "trials":
            emit(client.get_trials(args.test_id), args.json_output)
            return 0
        if args.group == "recordings":
            recording = _recording(client, args)
            if args.command == "get":
                payload = recording if args.include_samples else _recording_summary(recording)
                emit(payload, args.json_output)
                return 0
            output = Path(args.output)
            if args.format == "json":
                export_recording_json(recording, output)
            else:
                export_recording_csv(recording, output)
            emit({"output": str(output.resolve())}, args.json_output)
            return 0
        if args.group == "sync":
            app = create_app("development")
            cache = RecordingCache(Config.VALD_RECORDING_CACHE)
            with app.app_context():
                athlete = Athlete.query.filter_by(
                    forcedecks_id=args.profile_id,
                ).one_or_none()
                if athlete is None:
                    raise ValueError(
                        f"No local athlete maps to profile {args.profile_id}"
                    )
                result = sync_profile(
                    app,
                    client,
                    cache,
                    athlete,
                    args.date_from,
                    args.date_to,
                    args.refresh,
                )
            emit(result, args.json_output)
            return 0
    except (ForceDecksAPIError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

For `recordings get --include-samples`, require `--json` before printing the
full payload. Add this guard at the start of that branch:

```python
            if args.command == "get":
                if args.include_samples and not args.json_output:
                    raise ValueError(
                        "--include-samples requires --json or use recordings export"
                    )
```

- [ ] **Step 5: Run CLI tests and verify GREEN**

Run:

```powershell
.\venv\Scripts\python.exe -m pytest tests/test_vald_cli.py -v
.\venv\Scripts\python.exe vald_cli.py --help
```

Expected: tests pass and help lists all command groups.

- [ ] **Step 6: Commit Task 5**

```powershell
git add vald_cli.py tests/test_vald_cli.py
git commit -m "feat: add VALD ForceDecks CLI"
```

---

### Task 6: Current Reference Sheet, Environment Migration, and Full Verification

**Files:**
- Create: `docs/VALD_API_REFERENCE.md`
- Modify: `.env.example`
- Modify: `README.md`
- Modify: `import_forcedecks_metrics.py`
- Modify: `import_forcedecks_data.py`
- Modify: `bulk_import_forcedecks.py`
- Modify: `routes/api.py`

**Interfaces:**
- Consumes: all previous tasks
- Produces: documented operator workflow and current callers using documented client methods

- [ ] **Step 1: Replace `.env.example` VALD settings**

Replace the old ForceDecks credential section with:

```text
# VALD External APIs - March 2026 OAuth
VALD_CLIENT_ID=your_client_id
VALD_CLIENT_SECRET=your_client_secret
VALD_TENANT_ID=your_tenant_uuid
VALD_REGION=use
VALD_TOKEN_URL=https://auth.prd.vald.com/oauth/token
VALD_RECORDING_CACHE=data/vald/recordings
FORCEDECKS_TIMEOUT=30
```

- [ ] **Step 2: Create the API reference sheet**

Create `docs/VALD_API_REFERENCE.md` with these exact sections and endpoint
table:

```markdown
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

## CLI Examples

```powershell
python vald_cli.py auth check
python vald_cli.py profiles list --search Nelms
python vald_cli.py tests list --profile-id <uuid> --from 2025-08-01
python vald_cli.py trials get --test-id <uuid>
python vald_cli.py recordings export --test-id <uuid> --format csv --output recording.csv
python vald_cli.py sync --profile-id <uuid> --from 2025-08-01
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
```

- [ ] **Step 3: Update existing scripts and route callers**

In `import_forcedecks_metrics.py`, replace direct `_make_request` use:

```python
response = client.get_trials(test_id, team_id=org_id)
```

In `import_forcedecks_data.py`, `bulk_import_forcedecks.py`, and
`routes/api.py`:

1. Construct `ForceDecksClient` with `VALD_CLIENT_ID`,
   `VALD_CLIENT_SECRET`, `VALD_TENANT_ID`, `VALD_REGION`, and
   `VALD_TOKEN_URL`.
2. Replace `get_session_trials(...)` import logic with `sync_test(...)` or
   `sync_profile(...)`.
3. Do not call the deleted guessed `/api/v1/.../force-trace` methods.
4. Preserve response JSON fields currently consumed by the web UI.

The route-level sync handler should instantiate:

```python
client = ForceDecksClient(
    client_id=current_app.config["VALD_CLIENT_ID"],
    client_secret=current_app.config["VALD_CLIENT_SECRET"],
    tenant_id=current_app.config["VALD_TENANT_ID"],
    region=current_app.config["VALD_REGION"],
    token_url=current_app.config["VALD_TOKEN_URL"],
    timeout=current_app.config["FORCEDECKS_TIMEOUT"],
)
cache = RecordingCache(current_app.config["VALD_RECORDING_CACHE"])
```

Then call:

```python
result = sync_profile(
    current_app,
    client,
    cache,
    athlete,
    start_date.isoformat(),
    end_date.isoformat(),
    refresh=False,
)
```

- [ ] **Step 4: Add the operator workflow to README**

Add:

```markdown
## VALD ForceDecks CLI

1. Put the March 2026 VALD credentials in `.env`.
2. Verify authentication:
   `python vald_cli.py auth check`
3. Confirm a profile:
   `python vald_cli.py profiles list --search "<name>"`
4. Inspect tests:
   `python vald_cli.py tests list --profile-id <uuid> --from YYYY-MM-DD`
5. Export or sync a recording.
6. Run `python scripts/migrate_vald_trials.py` once before syncing into the
   existing SQLite database.

Raw recordings are cached under `data/vald/recordings/` and are not committed.
The sync stores individual trials plus one averaged dashboard trial.
```

- [ ] **Step 5: Run all automated verification**

Run:

```powershell
.\venv\Scripts\python.exe -m pytest tests -v
.\venv\Scripts\python.exe -m compileall services models scripts vald_cli.py
git diff --check
```

Expected: all tests pass, compilation succeeds, and `git diff --check` emits
no errors.

- [ ] **Step 6: Verify the repository does not contain secrets or raw cache**

Run:

```powershell
git status --short
git ls-files | rg "data/vald/recordings|\.env$"
rg -n "client_secret\s*=\s*['\"][^'\"]+|Bearer eyJ" . --glob '!venv/**' --glob '!.env'
```

Expected: no tracked raw recordings, no tracked `.env`, and no literal bearer
tokens or credentials.

- [ ] **Step 7: Run live authentication and recording checks**

After the user places the replacement March 2026 credentials in `.env`, run:

```powershell
.\venv\Scripts\python.exe vald_cli.py --json auth check
.\venv\Scripts\python.exe vald_cli.py --json tests list --profile-id <known-profile-id> --from 2025-08-01
.\venv\Scripts\python.exe vald_cli.py --json trials get --test-id <returned-test-id>
.\venv\Scripts\python.exe vald_cli.py --json recordings get --test-id <returned-test-id>
```

Expected:

- Authentication returns `{"authenticated": true}`.
- Tests include `testId` and `recordingId`.
- Trials include at least one `startTime` and `endTime`.
- Recording metadata returns HTTP 200 and identifies the recording.

- [ ] **Step 8: Verify sample retrieval and idempotent sync in a temporary database**

Set a process-local temporary database and cache:

```powershell
$env:DATABASE_URL = "sqlite:///$($env:TEMP -replace '\\','/')/pt_dash_vald_live_test.db"
$env:VALD_RECORDING_CACHE = "$env:TEMP\pt_dash_vald_recordings"
Remove-Item -LiteralPath "$env:TEMP\pt_dash_vald_live_test.db" -ErrorAction SilentlyContinue
.\venv\Scripts\python.exe app.py
```

Do not leave the Flask server running. Instead, initialize the temporary
database through:

```powershell
.\venv\Scripts\python.exe -c "from app import create_app; create_app('development'); print('temporary database initialized')"
```

Insert or map one synthetic local athlete to the verified profile ID using a
small one-off Flask shell expression, then run the sync twice:

```powershell
.\venv\Scripts\python.exe vald_cli.py --json sync --profile-id <known-profile-id> --from 2025-08-01
.\venv\Scripts\python.exe vald_cli.py --json sync --profile-id <known-profile-id> --from 2025-08-01
```

Query the temporary database:

```powershell
.\venv\Scripts\python.exe -c "from app import create_app; from models import Trial; app=create_app('development'); ctx=app.app_context(); ctx.push(); print({'individual': Trial.query.filter_by(is_averaged=False).count(), 'averaged': Trial.query.filter_by(is_averaged=True).count()})"
```

Expected: the second sync reports cache reuse and trial counts do not double.

- [ ] **Step 9: Run existing application smoke verification**

Run:

```powershell
.\venv\Scripts\python.exe -c "from app import create_app; app=create_app('development'); client=app.test_client(); print(client.get('/').status_code)"
```

Expected: HTTP 200 from the dashboard route.

- [ ] **Step 10: Commit Task 6**

```powershell
git add .env.example README.md docs/VALD_API_REFERENCE.md import_forcedecks_metrics.py import_forcedecks_data.py bulk_import_forcedecks.py routes/api.py
git commit -m "docs: document and wire VALD recording workflow"
```

---

## Final Verification Checklist

- [ ] New OAuth request uses `audience=vald-api-external`.
- [ ] No code calls `security.valdperformance.com`.
- [ ] No code calls guessed `/api/v1/.../force-trace` routes.
- [ ] Tests query VALD with server-side `profileId`.
- [ ] Trial metrics come from `/tests/{testId}/trials`.
- [ ] Raw samples come from a supported test recording route.
- [ ] Recording-ID compatibility route is isolated and labeled deprecated.
- [ ] Cache writes are atomic and corrupt cache files recover.
- [ ] Individual trial rows are idempotent by VALD trial ID.
- [ ] Exactly one averaged row exists per imported test.
- [ ] Existing dashboard route returns HTTP 200.
- [ ] Raw cache and `.env` are not tracked.
- [ ] Reference sheet and README match the implemented CLI.
- [ ] Live recording permission is verified with HTTP 200.
