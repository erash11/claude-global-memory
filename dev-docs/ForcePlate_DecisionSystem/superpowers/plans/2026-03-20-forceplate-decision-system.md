# ForcePlate Decision System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python pipeline that pulls CMJ force plate data from the VALD API, classifies Football athletes using the Pentheny framework, and displays results in a Streamlit dashboard with weekly PDF export.

**Architecture:** VALD REST API → DuckDB (raw_tests + classified_athletes + athlete_baselines) → 4-step classification engine → Streamlit dashboard + WeasyPrint PDF report. Single CLI entry point (`run_pipeline.py`) orchestrates all layers.

**Tech Stack:** Python 3.11+, requests, PyJWT, python-dotenv, duckdb, pandas, pyyaml, streamlit, plotly, kaleido, jinja2, weasyprint, pytest

---

## File Map

```
ForcePlate_DecisionSystem/
├── .env                              # credentials (never committed)
├── .gitignore
├── requirements.txt
├── run_pipeline.py                   # CLI entry point
├── config/
│   └── thresholds.yaml              # position-specific NFL/NCAA norms + prescriptions
├── src/
│   ├── __init__.py
│   ├── db.py                        # DuckDB connection + schema init
│   ├── ingest/
│   │   ├── __init__.py
│   │   ├── vald_client.py           # OAuth2 client + REST methods
│   │   └── pipeline.py             # pull → filter → upsert → pivot
│   ├── classify/
│   │   ├── __init__.py
│   │   ├── asymmetry.py            # Step 1: bilateral asymmetry screen
│   │   ├── mrsi.py                 # Step 2: mRSI primary classification
│   │   ├── eccentric.py            # Step 3: eccentric profile confirmation
│   │   ├── p1p2.py                 # Step 4: P1/P2 concentric impulse quadrant
│   │   └── engine.py               # orchestrates steps 1-4 + longitudinal flags
│   └── report/
│       ├── __init__.py
│       ├── components/
│       │   ├── radar_chart.py       # Plotly radar chart builder
│       │   ├── phase_profile.py     # braking/propulsive/landing phase cards
│       │   └── roster_table.py      # color-coded team roster table
│       ├── dashboard.py            # Streamlit app entry point
│       └── pdf_report.py           # Jinja2 → WeasyPrint PDF/HTML
├── templates/
│   └── weekly_report.html          # Jinja2 template
├── tests/
│   ├── test_asymmetry.py
│   ├── test_mrsi.py
│   ├── test_eccentric.py
│   ├── test_p1p2.py
│   ├── test_engine.py
│   ├── test_db.py
│   └── test_pipeline.py
├── data/                            # gitignored
└── reports/                         # gitignored
```

---

## Task 1: Project Scaffold

**Files:**
- Create: `.gitignore`
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `src/__init__.py`, `src/ingest/__init__.py`, `src/classify/__init__.py`, `src/report/__init__.py`, `src/report/components/__init__.py`

- [ ] **Step 1: Create `.gitignore`**

```
.env
data/
reports/
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/
dist/
```

- [ ] **Step 2: Create `requirements.txt`**

```
requests>=2.31
PyJWT>=2.8
python-dotenv>=1.0
duckdb>=0.10
pandas>=2.2
pyyaml>=6.0
streamlit>=1.35
plotly>=5.22
kaleido>=0.2,<1.0
jinja2>=3.1
weasyprint>=62.0
pytest>=8.0
```

> **Note:** `kaleido<1.0` uses a self-contained Chromium; v1.x requires an external Chrome/Chromium install. Pin to `<1.0` to avoid the hard dependency.

- [ ] **Step 3: Create `.env.example`**

```
VALD_CLIENT_ID=your_client_id_here
VALD_CLIENT_SECRET=your_client_secret_here
VALD_REGION_URL=https://prd-use-api-forcedecks.valdperformance.com
VALD_TEAM_ID=your_football_team_id_here
```

- [ ] **Step 4: Create all `__init__.py` files (empty)**

```bash
mkdir -p src/ingest src/classify src/report/components tests data reports
touch src/__init__.py src/ingest/__init__.py src/classify/__init__.py
touch src/report/__init__.py src/report/components/__init__.py
```

- [ ] **Step 5: Install dependencies**

```bash
pip install -r requirements.txt
```

Expected: all packages install without error.

- [ ] **Step 6: Commit**

```bash
git init
git add .gitignore requirements.txt .env.example src/
git commit -m "chore: project scaffold"
```

---

## Task 2: DuckDB Schema

**Files:**
- Create: `src/db.py`
- Create: `tests/test_db.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_db.py
import duckdb
import pytest
from src.db import get_connection, init_schema

def test_schema_creates_tables(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = get_connection(db_path)
    init_schema(conn)
    tables = conn.execute("SHOW TABLES").fetchall()
    table_names = {t[0] for t in tables}
    assert "raw_tests" in table_names
    assert "classified_athletes" in table_names
    assert "athlete_baselines" in table_names
    conn.close()

def test_raw_tests_primary_key(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = get_connection(db_path)
    init_schema(conn)
    conn.execute("""
        INSERT INTO raw_tests VALUES
        ('t1','a1','Athlete One','DB','skill','2026-01-10','RSI-modified',0.72,'m/s',now())
    """)
    # Insert same pk again — should not raise, should be ignored
    conn.execute("""
        INSERT INTO raw_tests VALUES
        ('t1','a1','Athlete One','DB','skill','2026-01-10','RSI-modified',0.72,'m/s',now())
        ON CONFLICT DO NOTHING
    """)
    count = conn.execute("SELECT COUNT(*) FROM raw_tests").fetchone()[0]
    assert count == 1
    conn.close()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_db.py -v
```

Expected: `ImportError: cannot import name 'get_connection'`

- [ ] **Step 3: Implement `src/db.py`**

```python
import duckdb

def get_connection(db_path: str = "data/forceplate.db") -> duckdb.DuckDBPyConnection:
    return duckdb.connect(db_path)

def init_schema(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS raw_tests (
            test_id         VARCHAR NOT NULL,
            athlete_id      VARCHAR NOT NULL,
            athlete_name    VARCHAR,
            position        VARCHAR,
            position_group  VARCHAR,
            test_date       DATE,
            metric_name     VARCHAR,
            metric_value    DOUBLE,
            metric_unit     VARCHAR,
            pulled_at       TIMESTAMP DEFAULT now(),
            PRIMARY KEY (test_id, metric_name)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS classified_athletes (
            test_id            VARCHAR PRIMARY KEY,
            athlete_id         VARCHAR,
            athlete_name       VARCHAR,
            position           VARCHAR,
            position_group     VARCHAR,
            test_date          DATE,
            asymmetry_pct      DOUBLE,
            asymmetry_flag     VARCHAR,
            mrsi               DOUBLE,
            mrsi_group         VARCHAR,
            ecc_peak_power_bm  DOUBLE,
            ecc_profile        VARCHAR,
            final_group        VARCHAR,
            concentric_impulse DOUBLE,
            p1_impulse         DOUBLE,
            p2_impulse         DOUBLE,
            p1p2_quadrant      VARCHAR,
            ci_quartile        INTEGER,
            prescription       VARCHAR,
            baseline_mrsi      DOUBLE,
            mrsi_pct_change    DOUBLE,
            readiness_flag     VARCHAR,
            clinical_notes     VARCHAR,
            classified_at      TIMESTAMP DEFAULT now()
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS athlete_baselines (
            athlete_id    VARCHAR PRIMARY KEY,
            baseline_mrsi DOUBLE,
            baseline_date DATE,
            updated_at    TIMESTAMP DEFAULT now()
        )
    """)
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_db.py -v
```

Expected: 2 PASS

- [ ] **Step 5: Commit**

```bash
git add src/db.py tests/test_db.py
git commit -m "feat: DuckDB schema with raw_tests, classified_athletes, athlete_baselines"
```

---

## Task 3: VALD API Client

**Files:**
- Create: `src/ingest/vald_client.py`
- Create: `tests/test_vald_client.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_vald_client.py
import pytest
from unittest.mock import patch, MagicMock
from src.ingest.vald_client import VALDClient

FAKE_TOKEN_RESPONSE = {
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9."
                    "eyJleHAiOjk5OTk5OTk5OTl9.signature",
    "token_type": "Bearer",
    "expires_in": 86400,
}

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("VALD_CLIENT_ID", "test_id")
    monkeypatch.setenv("VALD_CLIENT_SECRET", "test_secret")
    monkeypatch.setenv("VALD_REGION_URL", "https://api.example.com")
    monkeypatch.setenv("VALD_TEAM_ID", "team123")
    return VALDClient()

def test_get_token_fetches_and_caches(client):
    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = FAKE_TOKEN_RESPONSE
        mock_post.return_value.raise_for_status = MagicMock()
        token1 = client.get_token()
        token2 = client.get_token()
        assert token1 == token2
        assert mock_post.call_count == 1  # cached — only fetched once

def test_get_token_posts_correct_body(client):
    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = FAKE_TOKEN_RESPONSE
        mock_post.return_value.raise_for_status = MagicMock()
        client.get_token()
        call_kwargs = mock_post.call_args
        body = call_kwargs[1]["json"]
        assert body["client_id"] == "test_id"
        assert body["audience"] == "vald-api-external"
        assert body["grant_type"] == "client_credentials"

def test_get_teams_calls_correct_endpoint(client):
    with patch.object(client, "get_token", return_value="fake_token"):
        with patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = [{"id": "t1", "name": "Football"}]
            mock_get.return_value.raise_for_status = MagicMock()
            teams = client.get_teams()
            assert len(teams) == 1
            url = mock_get.call_args[0][0]
            assert "tenant" in url.lower() or "team" in url.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_vald_client.py -v
```

Expected: `ImportError: cannot import name 'VALDClient'`

- [ ] **Step 3: Implement `src/ingest/vald_client.py`**

```python
import os
import time
import requests
import jwt
from dotenv import load_dotenv

load_dotenv()

AUTH_URL = "https://auth.prd.vald.com/oauth/token"
TOKEN_EXPIRY_BUFFER_SECONDS = 60


class VALDClient:
    def __init__(self):
        self._client_id = os.environ["VALD_CLIENT_ID"]
        self._client_secret = os.environ["VALD_CLIENT_SECRET"]
        self._region_url = os.environ["VALD_REGION_URL"].rstrip("/")
        self._team_id = os.environ["VALD_TEAM_ID"]
        self._token: str | None = None
        self._token_exp: float = 0.0
        self._result_definitions: dict | None = None

    def get_token(self) -> str:
        now = time.time()
        if self._token and now < self._token_exp - TOKEN_EXPIRY_BUFFER_SECONDS:
            return self._token
        resp = requests.post(
            AUTH_URL,
            json={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "audience": "vald-api-external",
                "grant_type": "client_credentials",
            },
        )
        resp.raise_for_status()
        data = resp.json()
        self._token = data["access_token"]
        try:
            claims = jwt.decode(self._token, options={"verify_signature": False})
            self._token_exp = float(claims.get("exp", now + data.get("expires_in", 3600)))
        except Exception:
            self._token_exp = now + data.get("expires_in", 3600)
        return self._token

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.get_token()}"}

    def get_teams(self) -> list[dict]:
        resp = requests.get(
            f"{self._region_url}/v2019q3/tenants",
            headers=self._headers(),
        )
        resp.raise_for_status()
        return resp.json()

    def get_profiles(self, team_id: str | None = None) -> list[dict]:
        tid = team_id or self._team_id
        resp = requests.get(
            f"{self._region_url}/v2019q3/teams/{tid}/profiles",
            headers=self._headers(),
        )
        resp.raise_for_status()
        return resp.json()

    def get_tests(self, from_date: str, test_type: str = "CMJ") -> list[dict]:
        params = {
            "from": from_date,
            "testType": test_type,
        }
        resp = requests.get(
            f"{self._region_url}/v2019q3/teams/{self._team_id}/tests",
            headers=self._headers(),
            params=params,
        )
        resp.raise_for_status()
        return resp.json()

    def get_result_definitions(self) -> dict:
        if self._result_definitions is not None:
            return self._result_definitions
        resp = requests.get(
            f"{self._region_url}/v2019q3/resultdefinitions",
            headers=self._headers(),
        )
        resp.raise_for_status()
        defs = resp.json()
        self._result_definitions = {d["name"]: d.get("unit", "") for d in defs}
        return self._result_definitions
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_vald_client.py -v
```

Expected: 3 PASS

- [ ] **Step 5: Commit**

```bash
git add src/ingest/vald_client.py tests/test_vald_client.py
git commit -m "feat: VALD API client with OAuth2 token caching"
```

---

## Task 4: Configuration File (thresholds.yaml)

**Files:**
- Create: `config/thresholds.yaml`

No tests needed — pure data file. Values sourced from VALD Normative Data Report 2024-25 NFL and NCAA Football Report (NFL medians used as P50; full P25/P75 populated per position).

- [ ] **Step 1: Create `config/thresholds.yaml`**

```yaml
# VALD ForceDecks CMJ metric names exactly as returned by the API
target_metrics:
  - "Jump Height (Imp-Mom) [cm]"
  - "RSI-modified [m/s]"
  - "Flight Time:Contraction Time"
  - "Peak Power [W]"
  - "Peak Power / BM [W/kg]"
  - "Velocity at Peak Power [m/s]"
  - "Concentric Peak Force / BM [N/kg]"
  - "Eccentric Peak Power [W]"
  - "Eccentric Peak Power / BM [W/kg]"
  - "Eccentric Peak Velocity [m/s]"
  - "Eccentric Peak Force / BM [N/kg]"
  - "Eccentric Deceleration RFD / BM [N/s/kg]"
  - "Eccentric Mean Braking Force [N]"
  - "Eccentric Mean Force [N]"
  - "Force at Zero Velocity [N]"
  - "Force at Zero Velocity / BM [N/kg]"
  - "Concentric Impulse [N·s]"
  - "Concentric Impulse @100ms [N·s]"
  - "Concentric Impulse 100ms:Total"
  - "Concentric Mean Force / BM [N/kg]"
  - "Concentric RFD [N/s]"
  - "Concentric RFD @100ms [N/s]"
  - "P1 Concentric Impulse [N·s]"
  - "P2 Concentric Impulse [N·s]"
  - "P2:P1 Concentric Impulse Ratio"
  - "Peak Landing Force [N]"
  - "Peak Landing Force / BM [N/kg]"
  - "JH-Relative Peak Landing Force"
  - "Landing RFD [N/s]"
  - "Landing RFD 50ms [N/s]"
  - "Landing Stiffness [N/m]"
  - "Eccentric Duration [s]"
  - "Concentric Duration [s]"
  - "Countermovement Depth [cm]"
  - "ECC:CON Duration Ratio"
  - "ECC:CON Mean Force Ratio"
  - "ECC:CON Peak Power Ratio"
  - "Contraction Time [s]"
  - "CMJ Stiffness [N/m]"
  - "Lower-Limb Stiffness [N/m]"
  - "Bilateral Asymmetry Braking Impulse [%]"
  - "Body Mass [kg]"

# Maps position abbreviation to full position name used in thresholds
position_map:
  DB: "Defensive Back"
  CB: "Defensive Back"
  S:  "Defensive Back"
  LB: "Linebacker"
  OLB: "Linebacker"
  ILB: "Linebacker"
  MLB: "Linebacker"
  QB: "Quarterback"
  RB: "Running Back"
  FB: "Running Back"
  WR: "Wide Receiver"
  TE: "Tight End"
  ST: "Special Teams"
  K:  "Kicker/Punter"
  P:  "Kicker/Punter"
  DL: "Defensive Line"
  DE: "Defensive Line"
  DT: "Defensive Line"
  NT: "Defensive Line"
  OL: "Offensive Line"
  OT: "Offensive Line"
  OG: "Offensive Line"
  C:  "Offensive Line"
  G:  "Offensive Line"
  T:  "Offensive Line"

# Position group for simplified reporting (skill vs big)
position_group_map:
  "Defensive Back": skill
  "Linebacker": skill
  "Quarterback": skill
  "Running Back": skill
  "Wide Receiver": skill
  "Tight End": skill
  "Special Teams": skill
  "Kicker/Punter": skill
  "Defensive Line": big
  "Offensive Line": big

# Per-position NFL normative thresholds (P25/P50/P75)
# Source: VALD Normative Data Report 2024-25 NFL and NCAA Football Report
positions:
  "Defensive Back":
    mrsi:             { p25: 0.66, p50: 0.74, p75: 0.83 }
    peak_power_bm:    { p25: 63.1, p50: 67.4, p75: 71.8 }
    edrfd_bm:         { p25: 90,   p50: 119,  p75: 152  }
    ecc_peak_power_bm:{ p25: 19.5, p50: 24.1, p75: 28.6 }
    asymmetry_braking:{ caution: 10, flag: 15 }
    cm_depth_flag_cm: 33.7   # P50 depth; deeper than this = SSC flag
    epf_bm_gold:      2.5
    epf_bm_ecc_flag:  2.0
    concentric_impulse_quartiles:
      q1_max: 262
      q2_max: 275
      q3_max: 290
      # > q3_max = Q4

  "Linebacker":
    mrsi:             { p25: 0.59, p50: 0.66, p75: 0.73 }
    peak_power_bm:    { p25: 57.2, p50: 61.3, p75: 65.5 }
    edrfd_bm:         { p25: 82,   p50: 108,  p75: 137  }
    ecc_peak_power_bm:{ p25: 19.6, p50: 23.8, p75: 28.0 }
    asymmetry_braking:{ caution: 10, flag: 15 }
    cm_depth_flag_cm: 34.5
    epf_bm_gold:      2.5
    epf_bm_ecc_flag:  2.0
    concentric_impulse_quartiles:
      q1_max: 304
      q2_max: 320
      q3_max: 335

  "Quarterback":
    mrsi:             { p25: 0.56, p50: 0.65, p75: 0.74 }
    peak_power_bm:    { p25: 54.7, p50: 60.6, p75: 65.9 }
    edrfd_bm:         { p25: 79,   p50: 103,  p75: 129  }
    ecc_peak_power_bm:{ p25: 18.7, p50: 22.2, p75: 26.0 }
    asymmetry_braking:{ caution: 10, flag: 15 }
    cm_depth_flag_cm: 33.7
    epf_bm_gold:      2.5
    epf_bm_ecc_flag:  2.0
    concentric_impulse_quartiles:
      q1_max: 271
      q2_max: 288
      q3_max: 302

  "Running Back":
    mrsi:             { p25: 0.61, p50: 0.69, p75: 0.79 }
    peak_power_bm:    { p25: 60.6, p50: 64.5, p75: 68.8 }
    edrfd_bm:         { p25: 84,   p50: 114,  p75: 149  }
    ecc_peak_power_bm:{ p25: 18.3, p50: 22.4, p75: 26.4 }
    asymmetry_braking:{ caution: 10, flag: 15 }
    cm_depth_flag_cm: 33.1
    epf_bm_gold:      2.5
    epf_bm_ecc_flag:  2.0
    concentric_impulse_quartiles:
      q1_max: 275
      q2_max: 291
      q3_max: 308

  "Wide Receiver":
    mrsi:             { p25: 0.65, p50: 0.74, p75: 0.82 }
    peak_power_bm:    { p25: 62.9, p50: 67.5, p75: 72.0 }
    edrfd_bm:         { p25: 86,   p50: 116,  p75: 153  }
    ecc_peak_power_bm:{ p25: 19.3, p50: 23.6, p75: 28.3 }
    asymmetry_braking:{ caution: 10, flag: 15 }
    cm_depth_flag_cm: 33.6
    epf_bm_gold:      2.5
    epf_bm_ecc_flag:  2.0
    concentric_impulse_quartiles:
      q1_max: 259
      q2_max: 278
      q3_max: 295

  "Tight End":
    mrsi:             { p25: 0.57, p50: 0.64, p75: 0.70 }
    peak_power_bm:    { p25: 56.5, p50: 59.8, p75: 63.4 }
    edrfd_bm:         { p25: 75,   p50: 95,   p75: 120  }
    ecc_peak_power_bm:{ p25: 18.5, p50: 22.0, p75: 25.9 }
    asymmetry_braking:{ caution: 10, flag: 15 }
    cm_depth_flag_cm: 34.4
    epf_bm_gold:      2.5
    epf_bm_ecc_flag:  2.0
    concentric_impulse_quartiles:
      q1_max: 316
      q2_max: 329
      q3_max: 341

  "Special Teams":
    mrsi:             { p25: 0.54, p50: 0.58, p75: 0.62 }
    peak_power_bm:    { p25: 50.2, p50: 55.3, p75: 60.8 }
    edrfd_bm:         { p25: 71,   p50: 94,   p75: 110  }
    ecc_peak_power_bm:{ p25: 17.2, p50: 20.8, p75: 23.7 }
    asymmetry_braking:{ caution: 10, flag: 15 }
    cm_depth_flag_cm: 32.6
    epf_bm_gold:      2.5
    epf_bm_ecc_flag:  2.0
    concentric_impulse_quartiles:
      q1_max: 270
      q2_max: 293
      q3_max: 311

  "Kicker/Punter":
    mrsi:             { p25: 0.58, p50: 0.65, p75: 0.71 }
    peak_power_bm:    { p25: 53.5, p50: 57.6, p75: 61.5 }
    edrfd_bm:         { p25: 85,   p50: 106,  p75: 131  }
    ecc_peak_power_bm:{ p25: 21.6, p50: 24.9, p75: 28.5 }
    asymmetry_braking:{ caution: 10, flag: 15 }
    cm_depth_flag_cm: 35.7
    epf_bm_gold:      2.5
    epf_bm_ecc_flag:  2.0
    concentric_impulse_quartiles:
      q1_max: 249
      q2_max: 267
      q3_max: 285

  "Defensive Line":
    mrsi:             { p25: 0.48, p50: 0.56, p75: 0.64 }
    peak_power_bm:    { p25: 50.6, p50: 55.1, p75: 59.9 }
    edrfd_bm:         { p25: 64,   p50: 89,   p75: 119  }
    ecc_peak_power_bm:{ p25: 17.1, p50: 20.9, p75: 25.3 }
    asymmetry_braking:{ caution: 10, flag: 15 }
    cm_depth_flag_cm: 33.5
    epf_bm_gold:      2.5
    epf_bm_ecc_flag:  2.0
    concentric_impulse_quartiles:
      q1_max: 338
      q2_max: 357
      q3_max: 378

  "Offensive Line":
    mrsi:             { p25: 0.40, p50: 0.47, p75: 0.54 }
    peak_power_bm:    { p25: 46.2, p50: 49.7, p75: 53.6 }
    edrfd_bm:         { p25: 52,   p50: 74,   p75: 99   }
    ecc_peak_power_bm:{ p25: 15.4, p50: 18.5, p75: 22.4 }
    asymmetry_braking:{ caution: 10, flag: 15 }
    cm_depth_flag_cm: 33.7
    epf_bm_gold:      2.5
    epf_bm_ecc_flag:  2.0
    concentric_impulse_quartiles:
      q1_max: 351
      q2_max: 373
      q3_max: 397

# Training prescriptions keyed by "group.quadrant"
# group: gold | purple | white
# quadrant: low_p1 | low_p2 | balanced | low_bw
prescriptions:
  gold.low_p1: >
    Gold – Low P1: Add 1–2 early-phase exercises (pause squat, IMTP).
    Maintain Gold programming. Target: improve initial drive off the floor.
  gold.low_p2: >
    Gold – Low P2: Emphasize loaded CMJ and jump squat at end-range;
    Olympic lift variations (hang clean, push jerk) for triple-extension finish.
  gold.balanced: >
    Gold – Balanced: Standard Gold programming — progressive overload is
    the primary lever.
  gold.low_bw: >
    Gold – Low BW: Investigate body composition; relative power metrics.
    Consider VBT-guided loading and plyometric volume building.
  purple.low_p1: >
    Purple – Low P1: Prioritize early-phase RFD work; deload top-end
    plyos until P1 improves. Methods: pause squat at parallel, isometric
    mid-thigh pull.
  purple.low_p2: >
    Purple – Low P2: Reduce maximal strength emphasis; increase
    light-load ballistic work. Methods: jump squat (20–30% 1RM), loaded CMJ.
  purple.balanced: >
    Purple – Balanced: Focus on total volume and mRSI recovery;
    no phase-specific adjusting needed.
  purple.low_bw: >
    Purple – Low BW: General strength base before phase-specific work;
    prioritize relative strength ratio. VBT at moderate loads (0.6–0.8 m/s).
  white.low_p1: >
    White – Low P1: Isometric mid-thigh pull; pause holds at parallel;
    no plyometric work until group improves.
  white.low_p2: >
    White – Low P2: Bodyweight jump squats with focus on full
    triple-extension only; no reactive work.
  white.balanced: >
    White – Balanced: Standard White structural loading;
    no phase-specific adjustments.
  white.low_bw: >
    White – Low BW: Clinical + nutrition review if applicable;
    structural load only; prioritize relative strength.
```

- [ ] **Step 2: Commit**

```bash
git add config/thresholds.yaml
git commit -m "feat: thresholds.yaml with NFL normative data for all 10 positions"
```

---

## Task 5: Classification — Step 1 Asymmetry

**Files:**
- Create: `src/classify/asymmetry.py`
- Create: `tests/test_asymmetry.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_asymmetry.py
from src.classify.asymmetry import screen_asymmetry

def test_pass():
    result = screen_asymmetry(9.9)
    assert result["asymmetry_flag"] == "pass"
    assert result["asymmetry_pct"] == 9.9

def test_caution():
    result = screen_asymmetry(12.0)
    assert result["asymmetry_flag"] == "caution"

def test_flag():
    result = screen_asymmetry(16.0)
    assert result["asymmetry_flag"] == "flag"

def test_boundary_caution_low():
    assert screen_asymmetry(10.0)["asymmetry_flag"] == "caution"

def test_boundary_flag():
    assert screen_asymmetry(15.0)["asymmetry_flag"] == "caution"

def test_boundary_flag_high():
    assert screen_asymmetry(15.01)["asymmetry_flag"] == "flag"

def test_none_returns_pass():
    result = screen_asymmetry(None)
    assert result["asymmetry_flag"] == "pass"
    assert result["asymmetry_pct"] is None
```

- [ ] **Step 2: Run to verify fail**

```bash
pytest tests/test_asymmetry.py -v
```

- [ ] **Step 3: Implement `src/classify/asymmetry.py`**

```python
def screen_asymmetry(asymmetry_pct: float | None) -> dict:
    if asymmetry_pct is None:
        return {"asymmetry_pct": None, "asymmetry_flag": "pass"}
    if asymmetry_pct > 15:
        flag = "flag"
    elif asymmetry_pct >= 10:
        flag = "caution"
    else:
        flag = "pass"
    return {"asymmetry_pct": asymmetry_pct, "asymmetry_flag": flag}
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_asymmetry.py -v
```

Expected: 7 PASS

- [ ] **Step 5: Commit**

```bash
git add src/classify/asymmetry.py tests/test_asymmetry.py
git commit -m "feat: asymmetry screen (Step 1)"
```

---

## Task 6: Classification — Step 2 mRSI

**Files:**
- Create: `src/classify/mrsi.py`
- Create: `tests/test_mrsi.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_mrsi.py
from src.classify.mrsi import classify_mrsi

DB_THRESHOLDS = {"mrsi": {"p25": 0.66, "p50": 0.74, "p75": 0.83}}
OL_THRESHOLDS = {"mrsi": {"p25": 0.40, "p50": 0.47, "p75": 0.54}}

def test_gold_above_p75():
    result = classify_mrsi(0.84, DB_THRESHOLDS)
    assert result["mrsi_group"] == "gold"

def test_purple_between_p25_p75():
    result = classify_mrsi(0.70, DB_THRESHOLDS)
    assert result["mrsi_group"] == "purple"

def test_white_below_p25():
    result = classify_mrsi(0.50, DB_THRESHOLDS)
    assert result["mrsi_group"] == "white"

def test_boundary_at_p75_is_gold():
    result = classify_mrsi(0.83, DB_THRESHOLDS)
    assert result["mrsi_group"] == "gold"

def test_boundary_at_p25_is_purple():
    result = classify_mrsi(0.66, DB_THRESHOLDS)
    assert result["mrsi_group"] == "purple"

def test_ol_thresholds():
    result = classify_mrsi(0.42, OL_THRESHOLDS)
    assert result["mrsi_group"] == "purple"
    result2 = classify_mrsi(0.35, OL_THRESHOLDS)
    assert result2["mrsi_group"] == "white"

def test_returns_mrsi_value():
    result = classify_mrsi(0.72, DB_THRESHOLDS)
    assert result["mrsi"] == 0.72
```

- [ ] **Step 2: Run to verify fail**

```bash
pytest tests/test_mrsi.py -v
```

- [ ] **Step 3: Implement `src/classify/mrsi.py`**

```python
def classify_mrsi(mrsi_value: float, position_thresholds: dict) -> dict:
    t = position_thresholds["mrsi"]
    if mrsi_value >= t["p75"]:
        group = "gold"
    elif mrsi_value >= t["p25"]:
        group = "purple"
    else:
        group = "white"
    return {"mrsi": mrsi_value, "mrsi_group": group}
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_mrsi.py -v
```

Expected: 7 PASS

- [ ] **Step 5: Commit**

```bash
git add src/classify/mrsi.py tests/test_mrsi.py
git commit -m "feat: mRSI primary classification (Step 2)"
```

---

## Task 7: Classification — Step 3 Eccentric Profile

**Files:**
- Create: `src/classify/eccentric.py`
- Create: `tests/test_eccentric.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_eccentric.py
from src.classify.eccentric import confirm_eccentric_profile

THRESHOLDS = {
    "peak_power_bm": {"p25": 63.1, "p50": 67.4, "p75": 71.8},
    "epf_bm_gold": 2.5,
    "epf_bm_ecc_flag": 2.0,
    "cm_depth_flag_cm": 33.7,
}

def test_gold_confirm():
    result = confirm_eccentric_profile(
        epf_bm=2.6, peak_power_bm=72.0, cm_depth_cm=30.0,
        thresholds=THRESHOLDS
    )
    assert result["ecc_profile"] == "gold_confirm"
    assert "ssc_depth_flag" not in result["clinical_notes"]

def test_purple_mid_epf():
    result = confirm_eccentric_profile(
        epf_bm=2.2, peak_power_bm=67.0, cm_depth_cm=30.0,
        thresholds=THRESHOLDS
    )
    assert result["ecc_profile"] == "purple"

def test_ecc_flag_low_epf():
    result = confirm_eccentric_profile(
        epf_bm=1.8, peak_power_bm=65.0, cm_depth_cm=30.0,
        thresholds=THRESHOLDS
    )
    assert result["ecc_profile"] == "ecc_flag"

def test_ssc_depth_note_appended():
    result = confirm_eccentric_profile(
        epf_bm=2.6, peak_power_bm=72.0, cm_depth_cm=36.0,
        thresholds=THRESHOLDS
    )
    assert "ssc_depth_flag" in result["clinical_notes"]

def test_none_epf_returns_purple():
    result = confirm_eccentric_profile(
        epf_bm=None, peak_power_bm=67.0, cm_depth_cm=30.0,
        thresholds=THRESHOLDS
    )
    assert result["ecc_profile"] == "purple"
```

- [ ] **Step 2: Run to verify fail**

```bash
pytest tests/test_eccentric.py -v
```

- [ ] **Step 3: Implement `src/classify/eccentric.py`**

```python
def confirm_eccentric_profile(
    epf_bm: float | None,
    peak_power_bm: float | None,
    cm_depth_cm: float | None,
    thresholds: dict,
) -> dict:
    notes = []
    gold_epf = thresholds.get("epf_bm_gold", 2.5)
    flag_epf = thresholds.get("epf_bm_ecc_flag", 2.0)
    gold_pp = thresholds["peak_power_bm"]["p75"]
    depth_flag = thresholds.get("cm_depth_flag_cm", 34.0)

    if epf_bm is None:
        profile = "purple"
    elif epf_bm < flag_epf:
        profile = "ecc_flag"
        notes.append("ecc_deficit_flag: EPF/BM < 2.0x — clinical review recommended")
    elif epf_bm >= gold_epf and peak_power_bm is not None and peak_power_bm >= gold_pp:
        profile = "gold_confirm"
    else:
        profile = "purple"

    if cm_depth_cm is not None and abs(cm_depth_cm) > depth_flag:
        notes.append("ssc_depth_flag: excessive countermovement depth — SSC coupling concern")

    return {
        "ecc_profile": profile,
        "clinical_notes": "; ".join(notes),
    }
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_eccentric.py -v
```

Expected: 5 PASS

- [ ] **Step 5: Commit**

```bash
git add src/classify/eccentric.py tests/test_eccentric.py
git commit -m "feat: eccentric profile confirmation (Step 3)"
```

---

## Task 8: Classification — Step 4 P1/P2 Quadrant

**Files:**
- Create: `src/classify/p1p2.py`
- Create: `tests/test_p1p2.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_p1p2.py
from src.classify.p1p2 import classify_p1p2

# Q boundaries: q1_max=262, q2_max=275, q3_max=290
# Q2 midpoint = (262+275)/2 = 268.5 → p1_median=268.5*0.62≈166.5, p2_median=268.5*0.38≈102
# Q4 midpoint = (290+290*1.15)/2 = 290*1.075 = 311.75 → p1≈193, p2≈118
QUARTILE_CONFIG = {
    "concentric_impulse_quartiles": {
        "q1_max": 262, "q2_max": 275, "q3_max": 290
    }
}

def test_q1_low_bw():
    # Q1 midpoint=(0+262)/2=131 → p1_median≈81.2, p2_median≈49.8
    # p1=70, p2=40 → both below medians → low_bw
    result = classify_p1p2(ci=250, p1=70, p2=40, position_thresholds=QUARTILE_CONFIG, final_group="white")
    assert result["ci_quartile"] == 1
    assert result["p1p2_quadrant"] == "low_bw"

def test_q4_balanced():
    # Q4: p1=200, p2=125 — both above Q4 medians (≈193, ≈118) → balanced
    result = classify_p1p2(ci=300, p1=200, p2=125, position_thresholds=QUARTILE_CONFIG, final_group="gold")
    assert result["ci_quartile"] == 4
    assert result["p1p2_quadrant"] == "balanced"

def test_low_p1():
    # Q2 p1_median≈166.5 — p1=150 is below, p2=110 is above p2_median≈102 → low_p1
    result = classify_p1p2(ci=268, p1=150, p2=110, position_thresholds=QUARTILE_CONFIG, final_group="purple")
    assert result["ci_quartile"] == 2
    assert result["p1p2_quadrant"] == "low_p1"

def test_low_p2():
    # Q2 p2_median≈102 — p1=180 is above, p2=80 is below → low_p2
    result = classify_p1p2(ci=268, p1=180, p2=80, position_thresholds=QUARTILE_CONFIG, final_group="purple")
    assert result["ci_quartile"] == 2
    assert result["p1p2_quadrant"] == "low_p2"

def test_prescription_attached():
    result = classify_p1p2(ci=268, p1=150, p2=110, position_thresholds=QUARTILE_CONFIG, final_group="purple")
    assert result["prescription"] != ""
```

- [ ] **Step 2: Run to verify fail**

```bash
pytest tests/test_p1p2.py -v
```

- [ ] **Step 3: Implement `src/classify/p1p2.py`**

```python
import yaml
from pathlib import Path

_PRESCRIPTIONS: dict | None = None

def _load_prescriptions() -> dict:
    global _PRESCRIPTIONS
    if _PRESCRIPTIONS is None:
        cfg_path = Path("config/thresholds.yaml")
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f)
        _PRESCRIPTIONS = cfg.get("prescriptions", {})
    return _PRESCRIPTIONS

def _quartile_ci_median(q_cfg: dict, quartile: int) -> float:
    """Return the midpoint of the CI quartile boundary for a given position's thresholds."""
    q1, q2, q3 = q_cfg["q1_max"], q_cfg["q2_max"], q_cfg["q3_max"]
    bounds = {1: (0, q1), 2: (q1, q2), 3: (q2, q3), 4: (q3, q3 * 1.15)}
    lo, hi = bounds[quartile]
    return (lo + hi) / 2


def classify_p1p2(
    ci: float,
    p1: float | None,
    p2: float | None,
    position_thresholds: dict,
    final_group: str,
) -> dict:
    q_cfg = position_thresholds["concentric_impulse_quartiles"]
    if ci <= q_cfg["q1_max"]:
        quartile = 1
    elif ci <= q_cfg["q2_max"]:
        quartile = 2
    elif ci <= q_cfg["q3_max"]:
        quartile = 3
    else:
        quartile = 4

    # P1 and P2 sub-quadrant: compare to proportional share of quartile CI midpoint
    # P1 is ~62% of total CI; P2 is ~38% — empirical split from VALD normative data
    ci_mid = _quartile_ci_median(q_cfg, quartile)
    p1_median = ci_mid * 0.62
    p2_median = ci_mid * 0.38
    p1_low = p1 is None or p1 < p1_median
    p2_low = p2 is None or p2 < p2_median

    if p1_low and p2_low:
        quadrant = "low_bw"
    elif p1_low:
        quadrant = "low_p1"
    elif p2_low:
        quadrant = "low_p2"
    else:
        quadrant = "balanced"

    prescription_key = f"{final_group}.{quadrant}"
    prescriptions = _load_prescriptions()
    prescription = prescriptions.get(prescription_key, "")

    return {
        "concentric_impulse": ci,
        "p1_impulse": p1,
        "p2_impulse": p2,
        "ci_quartile": quartile,
        "p1p2_quadrant": quadrant,
        "prescription": prescription,
    }
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_p1p2.py -v
```

Expected: 5 PASS

- [ ] **Step 5: Commit**

```bash
git add src/classify/p1p2.py tests/test_p1p2.py
git commit -m "feat: P1/P2 concentric impulse quadrant classification (Step 4)"
```

---

## Task 9: Classification Engine + Longitudinal Flags

**Files:**
- Create: `src/classify/engine.py`
- Create: `tests/test_engine.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_engine.py
import yaml
from src.classify.engine import classify_test, compute_readiness_flag

with open("config/thresholds.yaml") as f:
    THRESHOLDS = yaml.safe_load(f)

DB_POSITION = "Defensive Back"

GOLD_METRICS = {
    "Bilateral Asymmetry Braking Impulse [%]": 8.0,
    "RSI-modified [m/s]": 0.85,
    "Eccentric Peak Force / BM [N/kg]": 27.0,
    "Peak Power / BM [W/kg]": 73.0,
    "Countermovement Depth [cm]": -30.0,
    "Concentric Impulse [N·s]": 295.0,
    "P1 Concentric Impulse [N·s]": 185.0,
    "P2 Concentric Impulse [N·s]": 110.0,
    "Eccentric Peak Power / BM [W/kg]": 25.0,
}

WHITE_METRICS = {
    "Bilateral Asymmetry Braking Impulse [%]": 5.0,
    "RSI-modified [m/s]": 0.50,
    "Eccentric Peak Force / BM [N/kg]": 20.0,
    "Peak Power / BM [W/kg]": 60.0,
    "Countermovement Depth [cm]": -30.0,
    "Concentric Impulse [N·s]": 255.0,
    "P1 Concentric Impulse [N·s]": 155.0,
    "P2 Concentric Impulse [N·s]": 85.0,
    "Eccentric Peak Power / BM [W/kg]": 18.0,
}

def test_gold_classification():
    result = classify_test(GOLD_METRICS, DB_POSITION, THRESHOLDS, baseline_mrsi=None)
    assert result["final_group"] == "gold"
    assert result["asymmetry_flag"] == "pass"

def test_white_skips_steps_3_4():
    result = classify_test(WHITE_METRICS, DB_POSITION, THRESHOLDS, baseline_mrsi=None)
    assert result["final_group"] == "white"
    # Steps 3+4 still run but group stays white
    assert result["mrsi_group"] == "white"

def test_flag_asymmetry_overrides():
    metrics = dict(GOLD_METRICS)
    metrics["Bilateral Asymmetry Braking Impulse [%]"] = 18.0
    result = classify_test(metrics, DB_POSITION, THRESHOLDS, baseline_mrsi=None)
    assert result["asymmetry_flag"] == "flag"
    assert "clinical eval" in result["clinical_notes"].lower() or result["asymmetry_flag"] == "flag"

def test_readiness_green_no_baseline():
    flag = compute_readiness_flag(current_mrsi=0.72, baseline_mrsi=None, prev_mrsi=None, days_since_prev=None)
    assert flag == "green"

def test_readiness_yellow():
    # current drop = (0.72-0.66)/0.72 = 8.3% (above 5%, below 10% — not single-test red)
    # prev drop = (0.72-0.67)/0.72 = 6.9% (above 5%) — both > 5% → yellow
    flag = compute_readiness_flag(current_mrsi=0.66, baseline_mrsi=0.72, prev_mrsi=0.67, days_since_prev=3)
    assert flag == "yellow"

def test_readiness_red_single_drop():
    flag = compute_readiness_flag(current_mrsi=0.60, baseline_mrsi=0.72, prev_mrsi=0.71, days_since_prev=3)
    # single-test drop > 10% from baseline = red
    assert flag == "red"

def test_readiness_gap_resets_consecutive():
    # 25-day gap → consecutive counter resets → no consecutive flag
    # current_mrsi=0.67 is a 6.9% drop from 0.72 — below single-test red (>10%) but above yellow (>5%)
    # Without gap reset, prev_drop=6.9% would combine for yellow; with gap reset → green
    flag = compute_readiness_flag(current_mrsi=0.67, baseline_mrsi=0.72, prev_mrsi=0.67, days_since_prev=25)
    assert flag == "green"
```

- [ ] **Step 2: Run to verify fail**

```bash
pytest tests/test_engine.py -v
```

- [ ] **Step 3: Implement `src/classify/engine.py`**

```python
from src.classify.asymmetry import screen_asymmetry
from src.classify.mrsi import classify_mrsi
from src.classify.eccentric import confirm_eccentric_profile
from src.classify.p1p2 import classify_p1p2

CONSECUTIVE_GAP_RESET_DAYS = 21


def compute_readiness_flag(
    current_mrsi: float,
    baseline_mrsi: float | None,
    prev_mrsi: float | None,
    days_since_prev: int | None,
) -> str:
    if baseline_mrsi is None:
        return "green"

    pct_drop_from_baseline = (baseline_mrsi - current_mrsi) / baseline_mrsi * 100

    # Single-test red: drop > 10% from baseline in one session
    if pct_drop_from_baseline > 10:
        return "red"

    # Consecutive test logic — BOTH tests must independently exceed each threshold
    gap_reset = days_since_prev is None or days_since_prev > CONSECUTIVE_GAP_RESET_DAYS
    if not gap_reset and prev_mrsi is not None:
        prev_drop = (baseline_mrsi - prev_mrsi) / baseline_mrsi * 100
        if pct_drop_from_baseline > 15 and prev_drop > 15:
            return "red"
        if pct_drop_from_baseline > 10 and prev_drop > 10:
            return "orange"
        if pct_drop_from_baseline > 5 and prev_drop > 5:
            return "yellow"

    return "green"


def classify_test(
    test_metrics: dict,
    position: str,
    thresholds: dict,
    baseline_mrsi: float | None,
    prev_mrsi: float | None = None,
    days_since_prev: int | None = None,
) -> dict:
    pos_t = thresholds["positions"][position]
    notes = []

    # Step 1: Asymmetry screen
    asym_pct = test_metrics.get("Bilateral Asymmetry Braking Impulse [%]")
    asym = screen_asymmetry(asym_pct)
    if asym["asymmetry_flag"] == "flag":
        notes.append("asymmetry_flag: >15% — restrict bilateral high-load work; clinical eval within 48h")
    elif asym["asymmetry_flag"] == "caution":
        notes.append("asymmetry_caution: 10–15% — flag for review")

    # Step 2: mRSI primary classification
    mrsi_val = test_metrics.get("RSI-modified [m/s]")
    mrsi_result = classify_mrsi(mrsi_val or 0.0, pos_t)
    final_group = mrsi_result["mrsi_group"]

    # Step 3: Eccentric profile confirmation (always runs; refines group)
    # EPF/BM (force ratio) is used for the 2.5x/2.0x gates
    # Eccentric Peak Power/BM is stored separately for display in the radar chart
    epf_bm = test_metrics.get("Eccentric Peak Force / BM [N/kg]")
    ecc_peak_power_bm = test_metrics.get("Eccentric Peak Power / BM [W/kg]")
    peak_power_bm = test_metrics.get("Peak Power / BM [W/kg]")
    cm_depth = test_metrics.get("Countermovement Depth [cm]")
    ecc = confirm_eccentric_profile(
        epf_bm=epf_bm,
        peak_power_bm=peak_power_bm,
        cm_depth_cm=abs(cm_depth) if cm_depth else None,
        thresholds=pos_t,
    )
    if ecc["clinical_notes"]:
        notes.append(ecc["clinical_notes"])
    if ecc["ecc_profile"] == "ecc_flag" and final_group == "gold":
        final_group = "purple"  # ECC flag downgrades gold to purple

    # Step 4: P1/P2 quadrant
    ci = test_metrics.get("Concentric Impulse [N·s]", 0.0)
    p1 = test_metrics.get("P1 Concentric Impulse [N·s]")
    p2 = test_metrics.get("P2 Concentric Impulse [N·s]")
    p1p2 = classify_p1p2(ci=ci, p1=p1, p2=p2, position_thresholds=pos_t, final_group=final_group)

    # Longitudinal flag
    readiness_flag = compute_readiness_flag(mrsi_val or 0.0, baseline_mrsi, prev_mrsi, days_since_prev)

    mrsi_pct_change = None
    if baseline_mrsi and mrsi_val:
        mrsi_pct_change = (mrsi_val - baseline_mrsi) / baseline_mrsi * 100

    return {
        "asymmetry_pct": asym["asymmetry_pct"],
        "asymmetry_flag": asym["asymmetry_flag"],
        "mrsi": mrsi_result["mrsi"],
        "mrsi_group": mrsi_result["mrsi_group"],
        "ecc_peak_power_bm": ecc_peak_power_bm,   # Eccentric Peak Power/BM [W/kg] for display
        "ecc_profile": ecc["ecc_profile"],
        "final_group": final_group,
        "concentric_impulse": p1p2["concentric_impulse"],
        "p1_impulse": p1p2["p1_impulse"],
        "p2_impulse": p1p2["p2_impulse"],
        "ci_quartile": p1p2["ci_quartile"],
        "p1p2_quadrant": p1p2["p1p2_quadrant"],
        "prescription": p1p2["prescription"],
        "baseline_mrsi": baseline_mrsi,
        "mrsi_pct_change": mrsi_pct_change,
        "readiness_flag": readiness_flag,
        "clinical_notes": "; ".join(notes),
    }
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_engine.py -v
```

Expected: 7 PASS

- [ ] **Step 5: Run all tests**

```bash
pytest tests/ -v
```

Expected: all PASS

- [ ] **Step 6: Commit**

```bash
git add src/classify/engine.py tests/test_engine.py
git commit -m "feat: classification engine with longitudinal readiness flags"
```

---

## Task 10: Ingest Pipeline

**Files:**
- Create: `src/ingest/pipeline.py`
- Create: `tests/test_pipeline.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_pipeline.py
import pandas as pd
import pytest
from unittest.mock import MagicMock, patch
from src.ingest.pipeline import filter_target_metrics, pivot_tests, resolve_position

TARGET_METRICS = ["RSI-modified [m/s]", "Peak Power / BM [W/kg]"]

POSITION_MAP = {
    "DB": "Defensive Back",
    "WR": "Wide Receiver",
    "OL": "Offensive Line",
}

POS_GROUP_MAP = {
    "Defensive Back": "skill",
    "Wide Receiver": "skill",
    "Offensive Line": "big",
}

def test_filter_keeps_target_metrics():
    rows = [
        {"metric_name": "RSI-modified [m/s]", "metric_value": 0.72},
        {"metric_name": "Some Other Metric", "metric_value": 1.0},
    ]
    result = filter_target_metrics(rows, TARGET_METRICS)
    assert len(result) == 1
    assert result[0]["metric_name"] == "RSI-modified [m/s]"

def test_pivot_produces_wide_dict():
    rows = [
        {"test_id": "t1", "athlete_id": "a1", "athlete_name": "Joe", "position": "DB",
         "position_group": "skill", "test_date": "2026-01-10",
         "metric_name": "RSI-modified [m/s]", "metric_value": 0.72, "metric_unit": "m/s"},
        {"test_id": "t1", "athlete_id": "a1", "athlete_name": "Joe", "position": "DB",
         "position_group": "skill", "test_date": "2026-01-10",
         "metric_name": "Peak Power / BM [W/kg]", "metric_value": 67.0, "metric_unit": "W/kg"},
    ]
    result = pivot_tests(rows)
    assert "t1" in result
    assert result["t1"]["metrics"]["RSI-modified [m/s]"] == 0.72
    assert result["t1"]["position"] == "DB"

def test_resolve_position_known():
    pos, group = resolve_position("DB", POSITION_MAP, POS_GROUP_MAP)
    assert pos == "Defensive Back"
    assert group == "skill"

def test_resolve_position_unknown_defaults_to_skill():
    pos, group = resolve_position("UNKNOWN", POSITION_MAP, POS_GROUP_MAP)
    assert group == "skill"
```

- [ ] **Step 2: Run to verify fail**

```bash
pytest tests/test_pipeline.py -v
```

- [ ] **Step 3: Implement `src/ingest/pipeline.py`**

```python
import os
from datetime import date
from typing import Any

import duckdb
import pandas as pd
import yaml
from dotenv import load_dotenv

from src.db import get_connection, init_schema
from src.ingest.vald_client import VALDClient
from src.classify.engine import classify_test

load_dotenv()

DEFAULT_FROM_DATE = "2026-01-01"


def load_config() -> dict:
    with open("config/thresholds.yaml") as f:
        return yaml.safe_load(f)


def filter_target_metrics(rows: list[dict], target_metrics: list[str]) -> list[dict]:
    target_set = set(target_metrics)
    return [r for r in rows if r.get("metric_name") in target_set]


def resolve_position(
    position_abbr: str,
    position_map: dict,
    position_group_map: dict,
) -> tuple[str, str]:
    full_position = position_map.get(position_abbr, position_abbr)
    group = position_group_map.get(full_position, "skill")
    return full_position, group


def pivot_tests(rows: list[dict]) -> dict[str, dict]:
    by_test: dict[str, dict] = {}
    for row in rows:
        tid = row["test_id"]
        if tid not in by_test:
            by_test[tid] = {
                "athlete_id": row["athlete_id"],
                "athlete_name": row["athlete_name"],
                "position": row["position"],
                "position_group": row["position_group"],
                "test_date": row["test_date"],
                "metrics": {},
            }
        by_test[tid]["metrics"][row["metric_name"]] = row["metric_value"]
    return by_test


def get_baseline(conn: duckdb.DuckDBPyConnection, athlete_id: str) -> float | None:
    row = conn.execute(
        "SELECT baseline_mrsi FROM athlete_baselines WHERE athlete_id = ?",
        [athlete_id],
    ).fetchone()
    return row[0] if row else None


def get_prev_test(
    conn: duckdb.DuckDBPyConnection, athlete_id: str, current_date: str
) -> tuple[float | None, int | None]:
    row = conn.execute(
        """
        SELECT mrsi, test_date FROM classified_athletes
        WHERE athlete_id = ? AND test_date < ?
        ORDER BY test_date DESC LIMIT 1
        """,
        [athlete_id, current_date],
    ).fetchone()
    if not row:
        return None, None
    prev_mrsi, prev_date = row
    days = (date.fromisoformat(str(current_date)) - date.fromisoformat(str(prev_date))).days
    return prev_mrsi, days


def upsert_raw(conn: duckdb.DuckDBPyConnection, rows: list[dict]) -> int:
    inserted = 0
    for row in rows:
        result = conn.execute(
            """
            INSERT INTO raw_tests
            (test_id, athlete_id, athlete_name, position, position_group,
             test_date, metric_name, metric_value, metric_unit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT DO NOTHING
            """,
            [
                row["test_id"], row["athlete_id"], row["athlete_name"],
                row["position"], row["position_group"], row["test_date"],
                row["metric_name"], row["metric_value"], row.get("metric_unit", ""),
            ],
        )
        inserted += result.rowcount if result.rowcount > 0 else 0
    return inserted


def upsert_classified(conn: duckdb.DuckDBPyConnection, test_id: str, athlete_id: str,
                       athlete_name: str, position: str, position_group: str,
                       test_date: str, result: dict) -> None:
    conn.execute(
        """
        INSERT INTO classified_athletes
        (test_id, athlete_id, athlete_name, position, position_group, test_date,
         asymmetry_pct, asymmetry_flag, mrsi, mrsi_group, ecc_peak_power_bm,
         ecc_profile, final_group, concentric_impulse, p1_impulse, p2_impulse,
         p1p2_quadrant, ci_quartile, prescription, baseline_mrsi, mrsi_pct_change,
         readiness_flag, clinical_notes)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT (test_id) DO UPDATE SET
            asymmetry_pct = excluded.asymmetry_pct,
            asymmetry_flag = excluded.asymmetry_flag,
            mrsi = excluded.mrsi,
            mrsi_group = excluded.mrsi_group,
            ecc_peak_power_bm = excluded.ecc_peak_power_bm,
            ecc_profile = excluded.ecc_profile,
            final_group = excluded.final_group,
            concentric_impulse = excluded.concentric_impulse,
            p1_impulse = excluded.p1_impulse,
            p2_impulse = excluded.p2_impulse,
            p1p2_quadrant = excluded.p1p2_quadrant,
            ci_quartile = excluded.ci_quartile,
            prescription = excluded.prescription,
            baseline_mrsi = excluded.baseline_mrsi,
            mrsi_pct_change = excluded.mrsi_pct_change,
            readiness_flag = excluded.readiness_flag,
            clinical_notes = excluded.clinical_notes,
            classified_at = now()
        """,
        [
            test_id, athlete_id, athlete_name, position, position_group, test_date,
            result["asymmetry_pct"], result["asymmetry_flag"],
            result["mrsi"], result["mrsi_group"], result["ecc_peak_power_bm"],
            result["ecc_profile"], result["final_group"],
            result["concentric_impulse"], result["p1_impulse"], result["p2_impulse"],
            result["p1p2_quadrant"], result["ci_quartile"], result["prescription"],
            result["baseline_mrsi"], result["mrsi_pct_change"],
            result["readiness_flag"], result["clinical_notes"],
        ],
    )


def set_baseline_if_missing(
    conn: duckdb.DuckDBPyConnection, athlete_id: str, mrsi: float, test_date: str
) -> None:
    existing = conn.execute(
        "SELECT athlete_id FROM athlete_baselines WHERE athlete_id = ?", [athlete_id]
    ).fetchone()
    if not existing:
        conn.execute(
            "INSERT INTO athlete_baselines (athlete_id, baseline_mrsi, baseline_date) VALUES (?,?,?)",
            [athlete_id, mrsi, test_date],
        )


def run_pipeline(
    from_date: str = DEFAULT_FROM_DATE,
    db_path: str = "data/forceplate.db",
    dry_run: bool = False,
) -> dict:
    cfg = load_config()
    client = VALDClient()

    if dry_run:
        teams = client.get_teams()
        profiles = client.get_profiles()
        print(f"Teams: {[t.get('name', t) for t in teams]}")
        print(f"Athletes: {len(profiles)}")
        return {"teams": len(teams), "athletes": len(profiles)}

    conn = get_connection(db_path)
    init_schema(conn)

    raw_api_results = client.get_tests(from_date=from_date)

    # Flatten API results into rows
    rows = []
    for test in raw_api_results:
        test_id = test.get("id") or test.get("testId", "")
        athlete_id = test.get("profileId", "")
        athlete_name = test.get("profileName", "")
        position_abbr = test.get("position", "")
        test_date = test.get("recordedAt", "")[:10]  # ISO date
        full_pos, pos_group = resolve_position(
            position_abbr, cfg["position_map"], cfg["position_group_map"]
        )
        for result in test.get("results", []):
            rows.append({
                "test_id": test_id,
                "athlete_id": athlete_id,
                "athlete_name": athlete_name,
                "position": full_pos,
                "position_group": pos_group,
                "test_date": test_date,
                "metric_name": result.get("name", ""),
                "metric_value": result.get("value"),
                "metric_unit": result.get("unit", ""),
            })

    filtered = filter_target_metrics(rows, cfg["target_metrics"])
    new_rows = upsert_raw(conn, filtered)
    pivoted = pivot_tests(filtered)

    classified_count = 0
    flags: list[str] = []

    for test_id, test_data in pivoted.items():
        athlete_id = test_data["athlete_id"]
        position = test_data["position"]
        if position not in cfg["positions"]:
            continue  # skip unknown positions
        baseline = get_baseline(conn, athlete_id)
        prev_mrsi, days_since = get_prev_test(conn, athlete_id, test_data["test_date"])
        result = classify_test(
            test_metrics=test_data["metrics"],
            position=position,
            thresholds=cfg,
            baseline_mrsi=baseline,
            prev_mrsi=prev_mrsi,
            days_since_prev=days_since,
        )
        upsert_classified(
            conn, test_id, athlete_id, test_data["athlete_name"],
            position, test_data["position_group"], test_data["test_date"], result
        )
        mrsi = result.get("mrsi")
        if mrsi:
            set_baseline_if_missing(conn, athlete_id, mrsi, test_data["test_date"])
        if result["readiness_flag"] in ("red", "orange", "yellow"):
            flags.append(f"{test_data['athlete_name']}: {result['readiness_flag']}")
        classified_count += 1

    conn.close()
    summary = {
        "new_metric_rows": new_rows,
        "tests_classified": classified_count,
        "flags": flags,
    }
    print(f"Classified {classified_count} tests. {len(flags)} flags raised.")
    for f in flags:
        print(f"  FLAG: {f}")
    return summary
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_pipeline.py -v
```

Expected: 4 PASS

- [ ] **Step 5: Run full test suite**

```bash
pytest tests/ -v
```

Expected: all PASS

- [ ] **Step 6: Commit**

```bash
git add src/ingest/pipeline.py tests/test_pipeline.py
git commit -m "feat: ingest pipeline — pull, filter, pivot, classify, store"
```

---

## Task 11: CLI Entry Point

**Files:**
- Create: `run_pipeline.py`

- [ ] **Step 1: Implement `run_pipeline.py`**

```python
#!/usr/bin/env python3
"""
ForcePlate Decision System — Pipeline Entry Point

Usage:
  python run_pipeline.py                          # pull + classify
  python run_pipeline.py --dry-run                # list teams/athletes, no DB writes
  python run_pipeline.py --report                 # pull + classify + PDF/HTML
  python run_pipeline.py --from-date 2026-03-01   # override start date
  python run_pipeline.py --reset-baseline DB001   # reset one athlete baseline
  python run_pipeline.py --reset-all-baselines    # reset all baselines
"""
import argparse
import sys
from dotenv import load_dotenv

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="ForcePlate Decision System")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--from-date", default="2026-01-01")
    parser.add_argument("--reset-baseline", metavar="ATHLETE_ID")
    parser.add_argument("--reset-all-baselines", action="store_true")
    args = parser.parse_args()

    if args.reset_baseline or args.reset_all_baselines:
        from src.db import get_connection, init_schema
        conn = get_connection()
        init_schema(conn)  # ensure tables exist on fresh database
        if args.reset_all_baselines:
            conn.execute("DELETE FROM athlete_baselines")
            print("All baselines reset.")
        else:
            conn.execute("DELETE FROM athlete_baselines WHERE athlete_id = ?", [args.reset_baseline])
            print(f"Baseline reset for athlete: {args.reset_baseline}")
        conn.close()
        return

    from src.ingest.pipeline import run_pipeline
    summary = run_pipeline(from_date=args.from_date, dry_run=args.dry_run)

    if args.report and not args.dry_run:
        from src.report.pdf_report import generate_report
        generate_report()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Test dry-run manually (requires `.env`)**

```bash
python run_pipeline.py --dry-run
```

Expected: prints team name(s) and athlete count, exits cleanly.

- [ ] **Step 3: Commit**

```bash
git add run_pipeline.py
git commit -m "feat: CLI entry point with dry-run, report, baseline-reset flags"
```

---

## Task 12: Streamlit Dashboard — Roster View

**Files:**
- Create: `src/report/components/roster_table.py`
- Create: `src/report/dashboard.py`

- [ ] **Step 1: Implement `src/report/components/roster_table.py`**

```python
import pandas as pd
import streamlit as st

GROUP_COLORS = {"gold": "#FFD700", "purple": "#800080", "white": "#CCCCCC"}
FLAG_COLORS = {"green": "🟢", "yellow": "🟡", "orange": "🟠", "red": "🔴"}


def render_roster_table(df: pd.DataFrame) -> str | None:
    """Render color-coded roster table. Returns selected athlete_id or None."""
    display = df[["athlete_name", "position", "final_group", "readiness_flag",
                  "mrsi", "peak_power_bm_display", "edrfd_bm_display", "asymmetry_pct"]].copy()
    display.columns = ["Athlete", "Position", "Group", "Flag", "mRSI", "Pk Power/BM", "EDRFD/BM", "Asymmetry%"]
    display["Flag"] = display["Flag"].map(FLAG_COLORS).fillna("⚪")
    display["Group"] = display["Group"].str.upper()

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Group": st.column_config.TextColumn("Group"),
            "mRSI": st.column_config.NumberColumn(format="%.2f"),
            "Asymmetry%": st.column_config.NumberColumn(format="%.1f%%"),
        }
    )

    selected = st.selectbox(
        "Select athlete for profile view:",
        options=["— Select —"] + list(df["athlete_name"].unique()),
    )
    if selected != "— Select —":
        return df[df["athlete_name"] == selected]["athlete_id"].iloc[0]
    return None
```

- [ ] **Step 2: Implement `src/report/dashboard.py`**

```python
import streamlit as st
import pandas as pd
import duckdb
import yaml

from src.db import get_connection, init_schema
from src.report.components.roster_table import render_roster_table
from src.report.components.radar_chart import render_radar_chart
from src.report.components.phase_profile import render_phase_profile

st.set_page_config(page_title="ForcePlate Decision System", layout="wide")

@st.cache_resource
def get_conn():
    conn = get_connection()
    init_schema(conn)
    return conn

@st.cache_data(ttl=300)
def load_latest_tests(_conn) -> pd.DataFrame:
    return _conn.execute("""
        SELECT ca.*, rt.metric_value as peak_power_bm_display,
               rt2.metric_value as edrfd_bm_display
        FROM classified_athletes ca
        LEFT JOIN raw_tests rt ON ca.test_id = rt.test_id
            AND rt.metric_name = 'Peak Power / BM [W/kg]'
        LEFT JOIN raw_tests rt2 ON ca.test_id = rt2.test_id
            AND rt2.metric_name = 'Eccentric Deceleration RFD / BM [N/s/kg]'
        WHERE ca.test_date = (
            SELECT MAX(test_date) FROM classified_athletes ca2
            WHERE ca2.athlete_id = ca.athlete_id
        )
        ORDER BY ca.readiness_flag DESC, ca.athlete_name
    """).df()

@st.cache_data(ttl=300)
def load_athlete_history(_conn, athlete_id: str) -> pd.DataFrame:
    return _conn.execute("""
        SELECT test_date, mrsi, readiness_flag, final_group, p1p2_quadrant,
               prescription, clinical_notes, asymmetry_pct, ci_quartile
        FROM classified_athletes
        WHERE athlete_id = ?
        ORDER BY test_date DESC
        LIMIT 10
    """, [athlete_id]).df()

@st.cache_data(ttl=300)
def load_all_metrics_for_test(_conn, test_id: str) -> dict:
    rows = _conn.execute(
        "SELECT metric_name, metric_value FROM raw_tests WHERE test_id = ?", [test_id]
    ).fetchall()
    return {r[0]: r[1] for r in rows}

def main():
    conn = get_conn()
    st.title("ForcePlate Decision System — Football CMJ Dashboard")

    # Sidebar controls
    with st.sidebar:
        st.header("Filters")
        pos_filter = st.multiselect("Position Group", ["skill", "big"], default=["skill", "big"])
        show_white = st.checkbox("Show White Group athletes", value=True)

    df = load_latest_tests(conn)
    if df.empty:
        st.warning("No data yet. Run `python run_pipeline.py` to pull data.")
        return

    if pos_filter:
        df = df[df["position_group"].isin(pos_filter)]
    if not show_white:
        df = df[df["final_group"] != "white"]

    # Risk cluster alerts
    st.subheader("Risk Alerts")
    flagged = df[df["readiness_flag"].isin(["red", "orange"])]
    if not flagged.empty:
        for _, row in flagged.iterrows():
            color = "🔴" if row["readiness_flag"] == "red" else "🟠"
            st.warning(f"{color} **{row['athlete_name']}** ({row['position']}) — {row['readiness_flag'].upper()} flag | mRSI: {row['mrsi']:.2f} | Group: {row['final_group'].upper()}")
    else:
        st.success("No red/orange flags.")

    # Roster table
    st.subheader("Team Roster")
    selected_id = render_roster_table(df)

    # Individual athlete profile
    if selected_id:
        athlete_row = df[df["athlete_id"] == selected_id].iloc[0]
        test_id = conn.execute(
            "SELECT test_id FROM classified_athletes WHERE athlete_id = ? ORDER BY test_date DESC LIMIT 1",
            [selected_id]
        ).fetchone()[0]
        metrics = load_all_metrics_for_test(conn, test_id)
        history = load_athlete_history(conn, selected_id)

        st.divider()
        st.subheader(f"Athlete Profile: {athlete_row['athlete_name']} ({athlete_row['position']})")
        col1, col2, col3 = st.columns(3)
        col1.metric("Group", athlete_row["final_group"].upper())
        col2.metric("mRSI", f"{athlete_row['mrsi']:.2f}")
        col3.metric("Readiness", athlete_row["readiness_flag"].upper())

        with open("config/thresholds.yaml") as f:
            cfg = yaml.safe_load(f)

        tab1, tab2, tab3, tab4 = st.tabs(["Radar Chart", "Phase Profile", "Trend", "Prescription"])
        with tab1:
            render_radar_chart(metrics, athlete_row["position"], cfg)
        with tab2:
            render_phase_profile(metrics, athlete_row["position"], cfg)
        with tab3:
            if not history.empty:
                import plotly.graph_objects as go
                pos_t = cfg["positions"].get(athlete_row["position"], {})
                mrsi_t = pos_t.get("mrsi", {})
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=history["test_date"], y=history["mrsi"],
                    mode="lines+markers", name="mRSI", line=dict(color="royalblue", width=2)
                ))
                if mrsi_t:
                    fig.add_hline(y=mrsi_t["p75"], line_dash="dash", line_color="gold", annotation_text="P75 (Gold)")
                    fig.add_hline(y=mrsi_t["p25"], line_dash="dash", line_color="red", annotation_text="P25 (White)")
                fig.update_layout(title="mRSI Trend (last 10 tests)", xaxis_title="Date", yaxis_title="mRSI")
                st.plotly_chart(fig, use_container_width=True)
        with tab4:
            st.info(athlete_row.get("prescription") or "No prescription available.")
            if athlete_row.get("clinical_notes"):
                st.warning(f"Clinical Notes: {athlete_row['clinical_notes']}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Commit**

```bash
git add src/report/dashboard.py src/report/components/roster_table.py
git commit -m "feat: Streamlit dashboard roster view and athlete profile"
```

---

## Task 13: Dashboard Components — Radar Chart + Phase Profile

**Files:**
- Create: `src/report/components/radar_chart.py`
- Create: `src/report/components/phase_profile.py`

- [ ] **Step 1: Implement `src/report/components/radar_chart.py`**

```python
import plotly.graph_objects as go
import streamlit as st

RADAR_METRICS = [
    ("RSI-modified [m/s]", "mRSI", "mrsi"),
    ("Peak Power / BM [W/kg]", "Peak Power/BM", "peak_power_bm"),
    ("Eccentric Deceleration RFD / BM [N/s/kg]", "EDRFD/BM", "edrfd_bm"),
    ("Eccentric Peak Power / BM [W/kg]", "Ecc Pk Power/BM", "ecc_peak_power_bm"),
    ("Force at Zero Velocity / BM [N/kg]", "FV0/BM", None),
    ("Lower-Limb Stiffness [N/m]", "LL Stiffness", None),
]


def _percentile_rank(value: float, p25: float, p75: float) -> float:
    """Return 0–100 score: 50 = P50 (linear interpolation between P25 and P75)."""
    if value is None:
        return 50.0
    if value >= p75:
        return min(100.0, 50.0 + (value - p75) / (p75 - p25) * 50.0)
    elif value >= p25:
        return 50.0 * (value - p25) / (p75 - p25)
    else:
        return max(0.0, 50.0 * value / p25)


def render_radar_chart(metrics: dict, position: str, cfg: dict) -> None:
    pos_t = cfg["positions"].get(position, {})
    labels, scores = [], []

    for metric_key, label, threshold_key in RADAR_METRICS:
        val = metrics.get(metric_key)
        t = pos_t.get(threshold_key) if threshold_key else None
        if t and val is not None:
            score = _percentile_rank(val, t["p25"], t["p75"])
        else:
            score = 50.0
        labels.append(label)
        scores.append(score)

    fig = go.Figure(go.Scatterpolar(
        r=scores + [scores[0]],
        theta=labels + [labels[0]],
        fill="toself",
        line=dict(color="royalblue"),
        fillcolor="rgba(65, 105, 225, 0.2)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=[50] * (len(labels) + 1),
        theta=labels + [labels[0]],
        line=dict(color="orange", dash="dash"),
        name="P50 Reference",
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(range=[0, 100], tickvals=[25, 50, 75])),
        showlegend=True,
        title="Percentile Profile vs. Position Norms",
    )
    st.plotly_chart(fig, use_container_width=True)
```

- [ ] **Step 2: Implement `src/report/components/phase_profile.py`**

```python
import streamlit as st

PHASE_METRICS = {
    "Braking": [
        ("Eccentric Deceleration RFD / BM [N/s/kg]", "EDRFD/BM", "edrfd_bm"),
        ("Eccentric Peak Power / BM [W/kg]", "Ecc Pk Power/BM", "ecc_peak_power_bm"),
    ],
    "Propulsive": [
        ("Peak Power / BM [W/kg]", "Peak Power/BM", "peak_power_bm"),
        ("RSI-modified [m/s]", "mRSI", "mrsi"),
    ],
    "Landing": [
        ("Peak Landing Force / BM [N/kg]", "Pk Landing F/BM", None),
    ],
}

STATUS_COLORS = {"Deficit": "🔴", "Adequate": "🟡", "Strength": "🟢"}


def _phase_status(value: float | None, p25: float, p75: float) -> str:
    if value is None:
        return "Adequate"
    if value >= p75:
        return "Strength"
    if value >= p25:
        return "Adequate"
    return "Deficit"


def render_phase_profile(metrics: dict, position: str, cfg: dict) -> None:
    pos_t = cfg["positions"].get(position, {})
    cols = st.columns(len(PHASE_METRICS))

    for col, (phase, phase_metrics) in zip(cols, PHASE_METRICS.items()):
        with col:
            st.markdown(f"**{phase} Phase**")
            for metric_key, label, threshold_key in phase_metrics:
                val = metrics.get(metric_key)
                t = pos_t.get(threshold_key) if threshold_key else None
                if t:
                    status = _phase_status(val, t["p25"], t["p75"])
                else:
                    status = "Adequate"
                icon = STATUS_COLORS[status]
                val_str = f"{val:.1f}" if val is not None else "N/A"
                st.write(f"{icon} {label}: {val_str} ({status})")
```

- [ ] **Step 3: Verify dashboard launches**

```bash
streamlit run src/report/dashboard.py
```

Expected: dashboard opens in browser, roster table visible (may be empty if no data yet).

- [ ] **Step 4: Commit**

```bash
git add src/report/components/radar_chart.py src/report/components/phase_profile.py
git commit -m "feat: radar chart and phase profile dashboard components"
```

---

## Task 14: PDF/HTML Report Generator

**Files:**
- Create: `templates/weekly_report.html`
- Create: `src/report/pdf_report.py`

- [ ] **Step 1: Create `templates/weekly_report.html`**

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { font-family: Arial, sans-serif; margin: 20px; color: #222; }
  h1 { color: #003366; }
  h2 { color: #555; border-bottom: 1px solid #ccc; padding-bottom: 4px; }
  .gold { background: #FFD700; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
  .purple { background: #800080; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
  .white { background: #EEE; padding: 2px 8px; border-radius: 4px; }
  .flag-red { color: #CC0000; font-weight: bold; }
  .flag-orange { color: #FF8800; font-weight: bold; }
  .flag-yellow { color: #CCAA00; }
  .athlete-card { page-break-before: always; margin-top: 30px; }
  table { border-collapse: collapse; width: 100%; margin-top: 10px; }
  th, td { border: 1px solid #ccc; padding: 6px 10px; text-align: left; }
  th { background: #003366; color: white; }
  img { max-width: 500px; margin: 10px 0; }
  .summary-box { background: #f5f5f5; padding: 15px; border-radius: 6px; margin-bottom: 20px; }
</style>
</head>
<body>
<h1>Football CMJ Weekly Report — {{ report_date }}</h1>

<div class="summary-box">
  <h2>Team Summary</h2>
  <p>Athletes: <strong>{{ total_athletes }}</strong> |
     Gold: <strong>{{ gold_count }}</strong> |
     Purple: <strong>{{ purple_count }}</strong> |
     White: <strong>{{ white_count }}</strong></p>
  <p>Flags: Red: <strong>{{ red_count }}</strong> | Orange: <strong>{{ orange_count }}</strong> | Yellow: <strong>{{ yellow_count }}</strong></p>
</div>

{% if flagged_athletes %}
<h2>Risk Alerts</h2>
<table>
  <tr><th>Athlete</th><th>Position</th><th>Flag</th><th>mRSI</th><th>Group</th><th>Notes</th></tr>
  {% for a in flagged_athletes %}
  <tr>
    <td>{{ a.athlete_name }}</td>
    <td>{{ a.position }}</td>
    <td class="flag-{{ a.readiness_flag }}">{{ a.readiness_flag | upper }}</td>
    <td>{{ "%.2f" | format(a.mrsi) }}</td>
    <td><span class="{{ a.final_group }}">{{ a.final_group | upper }}</span></td>
    <td>{{ a.clinical_notes }}</td>
  </tr>
  {% endfor %}
</table>
{% endif %}

{% if movers %}
<h2>Group Changes Since Last Report</h2>
<table>
  <tr><th>Athlete</th><th>Previous Group</th><th>Current Group</th></tr>
  {% for m in movers %}
  <tr><td>{{ m.name }}</td><td>{{ m.prev }}</td><td>{{ m.curr }}</td></tr>
  {% endfor %}
</table>
{% endif %}

{% for athlete in athletes %}
<div class="athlete-card">
  <h2>{{ athlete.athlete_name }} — {{ athlete.position }} | <span class="{{ athlete.final_group }}">{{ athlete.final_group | upper }}</span></h2>
  {% if athlete.radar_img %}
  <img src="{{ athlete.radar_img }}" alt="Radar chart">
  {% endif %}
  <table>
    <tr><th>Metric</th><th>Value</th><th>Group</th><th>Readiness</th></tr>
    <tr>
      <td>mRSI</td><td>{{ "%.2f" | format(athlete.mrsi) }}</td>
      <td>{{ athlete.mrsi_group | upper }}</td>
      <td class="flag-{{ athlete.readiness_flag }}">{{ athlete.readiness_flag | upper }}</td>
    </tr>
    <tr><td>P1/P2 Quadrant</td><td colspan="3">{{ athlete.p1p2_quadrant }}</td></tr>
    <tr><td>CI Quartile</td><td colspan="3">Q{{ athlete.ci_quartile }}</td></tr>
    <tr><td>Asymmetry</td><td colspan="3">{{ "%.1f" | format(athlete.asymmetry_pct or 0) }}% — {{ athlete.asymmetry_flag }}</td></tr>
  </table>
  {% if athlete.prescription %}
  <p><strong>Prescription:</strong> {{ athlete.prescription }}</p>
  {% endif %}
  {% if athlete.clinical_notes %}
  <p class="flag-red"><strong>Clinical Notes:</strong> {{ athlete.clinical_notes }}</p>
  {% endif %}
</div>
{% endfor %}
</body>
</html>
```

- [ ] **Step 2: Implement `src/report/pdf_report.py`**

```python
import os
from datetime import date, datetime
from pathlib import Path

import duckdb
import pandas as pd
import plotly.graph_objects as go
import yaml
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from src.db import get_connection
from src.report.components.radar_chart import RADAR_METRICS, _percentile_rank

os.makedirs("reports", exist_ok=True)


def _export_radar_png(metrics: dict, position: str, cfg: dict, out_path: str) -> str | None:
    try:
        pos_t = cfg["positions"].get(position, {})
        labels, scores = [], []
        for metric_key, label, threshold_key in RADAR_METRICS:
            val = metrics.get(metric_key)
            t = pos_t.get(threshold_key) if threshold_key else None
            score = _percentile_rank(val, t["p25"], t["p75"]) if (t and val is not None) else 50.0
            labels.append(label)
            scores.append(score)
        fig = go.Figure(go.Scatterpolar(
            r=scores + [scores[0]], theta=labels + [labels[0]],
            fill="toself", line=dict(color="royalblue"),
        ))
        fig.update_layout(polar=dict(radialaxis=dict(range=[0, 100])))
        fig.write_image(out_path, width=500, height=400)
        return out_path
    except Exception:
        return None


def generate_report(db_path: str = "data/forceplate.db") -> str:
    conn = get_connection(db_path)
    with open("config/thresholds.yaml") as f:
        cfg = yaml.safe_load(f)

    df = conn.execute("""
        SELECT ca.*, rt.metric_value as peak_power_bm
        FROM classified_athletes ca
        LEFT JOIN raw_tests rt ON ca.test_id = rt.test_id
            AND rt.metric_name = 'Peak Power / BM [W/kg]'
        WHERE ca.test_date = (
            SELECT MAX(test_date) FROM classified_athletes ca2
            WHERE ca2.athlete_id = ca.athlete_id
        )
        ORDER BY ca.readiness_flag DESC, ca.athlete_name
    """).df()

    report_date = date.today().isoformat()
    athletes_data = []

    for _, row in df.iterrows():
        test_id = conn.execute(
            "SELECT test_id FROM classified_athletes WHERE athlete_id = ? ORDER BY test_date DESC LIMIT 1",
            [row["athlete_id"]]
        ).fetchone()[0]
        metrics = {r[0]: r[1] for r in conn.execute(
            "SELECT metric_name, metric_value FROM raw_tests WHERE test_id = ?", [test_id]
        ).fetchall()}
        radar_path = f"reports/radar_{row['athlete_id']}.png"
        img = _export_radar_png(metrics, row["position"], cfg, radar_path)
        athletes_data.append({**row.to_dict(), "radar_img": img})

    flagged = [a for a in athletes_data if a["readiness_flag"] in ("red", "orange")]

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("weekly_report.html")
    html_str = template.render(
        report_date=report_date,
        total_athletes=len(df),
        gold_count=len(df[df["final_group"] == "gold"]),
        purple_count=len(df[df["final_group"] == "purple"]),
        white_count=len(df[df["final_group"] == "white"]),
        red_count=len(df[df["readiness_flag"] == "red"]),
        orange_count=len(df[df["readiness_flag"] == "orange"]),
        yellow_count=len(df[df["readiness_flag"] == "yellow"]),
        flagged_athletes=flagged,
        athletes=athletes_data,
        movers=[],
    )

    html_path = f"reports/{report_date}_football_cmj_report.html"
    pdf_path = f"reports/{report_date}_football_cmj_report.pdf"

    Path(html_path).write_text(html_str, encoding="utf-8")
    HTML(filename=html_path).write_pdf(pdf_path)
    conn.close()
    print(f"Report written: {pdf_path}")
    return pdf_path
```

- [ ] **Step 3: Test report generation (requires data in DB)**

```bash
python run_pipeline.py --report
```

Expected: `reports/YYYY-MM-DD_football_cmj_report.pdf` created.

- [ ] **Step 4: Commit**

```bash
git add templates/weekly_report.html src/report/pdf_report.py
git commit -m "feat: Jinja2 + WeasyPrint PDF/HTML weekly report generator"
```

---

## Task 15: End-to-End Verification

- [ ] **Step 1: Dry-run API test**

```bash
python run_pipeline.py --dry-run
```

Expected: prints team name + athlete count (confirms auth + team ID).

- [ ] **Step 2: Full pipeline run**

```bash
python run_pipeline.py --from-date 2026-01-01
```

Expected: prints "Classified X tests. Y flags raised."

- [ ] **Step 3: Verify DB contents**

```python
import duckdb
conn = duckdb.connect("data/forceplate.db")
print(conn.execute("SELECT COUNT(*) FROM raw_tests").fetchone())
print(conn.execute("SELECT COUNT(*) FROM classified_athletes").fetchone())
print(conn.execute("SELECT COUNT(*) FROM athlete_baselines").fetchone())
print(conn.execute("SELECT final_group, COUNT(*) FROM classified_athletes GROUP BY 1").fetchall())
conn.close()
```

Expected: non-zero counts, groups distributed across gold/purple/white.

- [ ] **Step 4: Classification spot-check**

```python
import duckdb, yaml
conn = duckdb.connect("data/forceplate.db")
row = conn.execute("SELECT * FROM classified_athletes LIMIT 1").df().iloc[0]
print(row)
# Manually verify: athlete's mRSI vs. their position's P25/P75 thresholds matches mrsi_group
```

- [ ] **Step 5: Launch dashboard**

```bash
streamlit run src/report/dashboard.py
```

Expected: opens browser; roster table populated with athlete rows; click athlete → profile view loads.

- [ ] **Step 6: Generate report**

```bash
python run_pipeline.py --report
```

Expected: PDF opens; radar chart PNGs render; athlete cards populated.

- [ ] **Step 7: Run full test suite**

```bash
pytest tests/ -v
```

Expected: all PASS.

- [ ] **Step 8: Final commit**

```bash
git add -A
git commit -m "feat: end-to-end verification complete — pipeline, dashboard, PDF report"
```

---

## API Field Name Note

The exact VALD API JSON field names for test results (`results[].name`, `results[].value`, etc.) and test metadata (`profileId`, `recordedAt`, `position`) must be confirmed against actual API responses during Task 11 dry-run. If field names differ, update `src/ingest/pipeline.py` accordingly. The VALD API guide at `support.vald.com` documents the exact response schema.
