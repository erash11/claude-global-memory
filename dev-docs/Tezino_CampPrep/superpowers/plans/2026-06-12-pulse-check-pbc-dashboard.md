# Pulse Check PBC Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the staff-facing dashboard lead section into a morning pulse-check process behavior chart monitor.

**Architecture:** Extend the existing static dashboard pipeline instead of adding a new app. `scripts/build_dashboard_data.py` will emit a new top-level `pulse_monitor` contract from the existing retrospective weekly exposure and response panels. `scripts/build_dashboard_html.py` will lead with that contract and keep historical context below the fold.

**Tech Stack:** Python 3.14 standard library, CSV/JSON file transforms, static HTML with inline SVG, pytest/unittest tests.

---

## File Structure

- Modify `tests/fixtures/dashboard_data/weekly_exposure.csv` to add fixture rows for GPS session count, historical player-load guardrails, high-IMA/high-impact metrics, and Perch selected metrics.
- Modify `tests/fixtures/dashboard_data/response_panel.csv` to keep the current CMJ and IMTP fixture rows used by pulse metrics.
- Modify `tests/test_build_dashboard_data.py` with pulse-monitor JSON contract tests.
- Modify `scripts/build_dashboard_data.py` with focused helper functions:
  - `natural_process_limits(values)`
  - `metric_points_from_weekly(rows, metric_def)`
  - `metric_points_from_response(rows, metric_def)`
  - `build_pulse_metric(metric_def, weekly_rows, response_rows)`
  - `build_pulse_monitor(weekly_rows, response_rows, current_ramp, current_forceplate, live_baseline)`
- Modify `tests/test_build_dashboard_html.py` with Option A lead-section tests.
- Modify `scripts/build_dashboard_html.py` to render:
  - pulse-check hero/status strip
  - selected PBC chart grid
  - signal summary
  - existing historical/SPC sections below that lead section
- Regenerate `data/dashboard/dashboard_data.json` and `data/dashboard/index.html` with `python scripts\refresh_dashboard.py`.
- Update `docs/HANDOFF-2026-06-11-night.md`, `docs/NARRATIVE-PLAN.md`, and `AGENTS.md` only if the implementation changes the restart instructions or dashboard contract in a way not already covered by the spec.

---

### Task 1: Add Pulse-Monitor JSON Contract Tests

**Files:**
- Modify: `tests/fixtures/dashboard_data/weekly_exposure.csv`
- Modify: `tests/test_build_dashboard_data.py`
- Test: `tests/test_build_dashboard_data.py`

- [ ] **Step 1: Extend the weekly fixture with selected PBC source rows**

Add these rows to `tests/fixtures/dashboard_data/weekly_exposure.csv` under the header:

```csv
2024,2024,25,2024-06-17,2024-06-23,systemic,gps,session_count,count_distinct_activity,4.0,,,-45,-39,-23,-17,
2024,2024,25,2024-06-17,2024-06-23,systemic,gps,total_player_load,sum,840.0,,,-45,-39,-23,-17,
2024,2024,26,2024-06-24,2024-06-30,systemic,gps,session_count,count_distinct_activity,5.0,,,-38,-32,-16,-10,
2024,2024,26,2024-06-24,2024-06-30,systemic,gps,total_player_load,sum,1100.0,260.0,1.31,-38,-32,-16,-10,
2024,2024,26,2024-06-24,2024-06-30,foot_mechanical,gps,total_high_ima_avg,sum,22.0,,,,-38,-32,-16,-10,proxy_pending_thresholds
2024,2024,26,2024-06-24,2024-06-30,foot_mechanical,gps,impacts_high,sum,9.0,,,,-38,-32,-16,-10,proxy_pending_thresholds
2026,2026,23,2026-06-01,2026-06-07,systemic,gps,session_count,count_distinct_activity,3.0,,,-58,-52,,,
2026,2026,23,2026-06-01,2026-06-07,foot_mechanical,gps,total_high_ima_avg,sum,10.0,,,-58,-52,,,proxy_pending_thresholds
2026,2026,23,2026-06-01,2026-06-07,foot_mechanical,gps,impacts_high,sum,3.0,,,-58,-52,,,proxy_pending_thresholds
2026,2026,24,2026-06-08,2026-06-14,systemic,gps,total_player_load,sum,1137.515,712.475,2.676,-51,-47,,,
2026,2026,24,2026-06-08,2026-06-14,systemic,gps,session_count,count_distinct_activity,5.0,2.0,1.667,-51,-47,,,
2026,2026,24,2026-06-08,2026-06-14,foot_mechanical,gps,total_high_ima_avg,sum,48.0,38.0,4.8,-51,-47,,,proxy_pending_thresholds
2026,2026,24,2026-06-08,2026-06-14,foot_mechanical,gps,impacts_high,sum,15.0,12.0,5.0,-51,-47,,,proxy_pending_thresholds
2026,2026,24,2026-06-08,2026-06-14,foot_mechanical,perch,axial_reps_ge80,sum,12.0,-24.0,0.667,-51,-49,,,
2026,2026,24,2026-06-08,2026-06-14,foot_mechanical,perch,axial_tonnage_lb,sum,8513.5,-7577.3,1.058,-51,-49,,,
```

- [ ] **Step 2: Write the failing contract test**

Append this test method to `BuildDashboardDataTests` in `tests/test_build_dashboard_data.py`:

```python
    def test_dashboard_payload_includes_pulse_monitor_contract(self):
        module = load_module()
        payload = module.build_dashboard_payload(FIXTURE)

        pulse = payload["pulse_monitor"]
        metric_ids = [metric["id"] for metric in pulse["metrics"]]

        self.assertEqual(pulse["guardrail_policy"]["historical_source"], "historical_guardrails")
        self.assertEqual(pulse["guardrail_policy"]["current_source"], "2026_provisional_limits")
        self.assertEqual(pulse["guardrail_policy"]["minimum_current_observations"]["session_metrics"], 5)
        self.assertEqual(pulse["guardrail_policy"]["minimum_current_observations"]["response_metrics"], 5)
        self.assertIn("gps_avg_player_load_per_session", metric_ids)
        self.assertIn("gps_high_ima_avg", metric_ids)
        self.assertIn("perch_axial_tonnage", metric_ids)
        self.assertIn("perch_heavy_axial_reps", metric_ids)
        self.assertIn("cmj_mrsi", metric_ids)
        self.assertIn("cmj_asymmetry", metric_ids)
        self.assertIn("imtp_pvf_bm", metric_ids)
        self.assertNotIn("gps_total_distance", metric_ids)

        avg_pl = next(metric for metric in pulse["metrics"] if metric["id"] == "gps_avg_player_load_per_session")
        self.assertEqual(avg_pl["label"], "Average player load per session")
        self.assertEqual(avg_pl["guardrail_source"], "historical_guardrails")
        self.assertEqual(avg_pl["current_observations"], 2)
        self.assertEqual(avg_pl["minimum_current_observations"], 5)
        self.assertEqual(avg_pl["latest_point"]["date"], "2026-06-14")
        self.assertAlmostEqual(avg_pl["latest_point"]["value"], 227.503, places=3)

        cmj = next(metric for metric in pulse["metrics"] if metric["id"] == "cmj_mrsi")
        self.assertEqual(cmj["guardrail_source"], "historical_guardrails")
        self.assertEqual(cmj["current_observations"], 2)
        self.assertEqual(cmj["minimum_current_observations"], 5)
```

- [ ] **Step 3: Run the test to verify RED**

Run:

```powershell
python -m pytest tests\test_build_dashboard_data.py::BuildDashboardDataTests::test_dashboard_payload_includes_pulse_monitor_contract -q -p no:cacheprovider
```

Expected:

```text
FAILED ... KeyError: 'pulse_monitor'
```

- [ ] **Step 4: Do not implement in this task**

Stop after the failing test is confirmed. Task 2 adds the implementation.

---

### Task 2: Implement Pulse-Monitor Data Builder

**Files:**
- Modify: `scripts/build_dashboard_data.py`
- Test: `tests/test_build_dashboard_data.py`

- [ ] **Step 1: Add metric definitions**

Add this constant after `LIVE_BASELINE` in `scripts/build_dashboard_data.py`:

```python
PULSE_METRICS = [
    {
        "id": "gps_avg_player_load_per_session",
        "label": "Average player load per session",
        "domain": "exposure",
        "source": "gps",
        "unit": "player load",
        "kind": "weekly_ratio",
        "numerator": "total_player_load",
        "denominator": "session_count",
        "minimum_current_observations": 5,
        "staff_prompt": "Discuss if average session load moves outside expected process behavior.",
    },
    {
        "id": "gps_high_ima_avg",
        "label": "High IMA average",
        "domain": "foot_mechanical",
        "source": "gps",
        "unit": "count",
        "kind": "weekly_metric",
        "metric": "total_high_ima_avg",
        "minimum_current_observations": 5,
        "staff_prompt": "Discuss if high-intensity movement exposure changes materially.",
    },
    {
        "id": "perch_axial_tonnage",
        "label": "Axial tonnage",
        "domain": "foot_mechanical",
        "source": "perch",
        "unit": "lb",
        "kind": "weekly_metric",
        "metric": "axial_tonnage_lb",
        "minimum_current_observations": 5,
        "staff_prompt": "Discuss if lower-body axial load moves outside expected process behavior.",
    },
    {
        "id": "perch_heavy_axial_reps",
        "label": "Heavy axial reps",
        "domain": "foot_mechanical",
        "source": "perch",
        "unit": "reps",
        "kind": "weekly_metric",
        "metric": "axial_reps_ge80",
        "minimum_current_observations": 5,
        "staff_prompt": "Discuss if heavy axial exposure changes materially.",
    },
    {
        "id": "cmj_mrsi",
        "label": "CMJ mRSI",
        "domain": "response",
        "source": "cmj",
        "unit": "ratio",
        "kind": "response_metric",
        "metric": "mrsi",
        "minimum_current_observations": 5,
        "staff_prompt": "Discuss if reactive strength behavior changes beyond routine variation.",
    },
    {
        "id": "cmj_asymmetry",
        "label": "CMJ asymmetry",
        "domain": "response",
        "source": "cmj",
        "unit": "%",
        "kind": "response_metric",
        "metric": "asymmetry_pct",
        "minimum_current_observations": 5,
        "staff_prompt": "Discuss if asymmetry changes beyond expected measurement noise.",
    },
    {
        "id": "imtp_pvf_bm",
        "label": "IMTP PVF/BM",
        "domain": "response",
        "source": "imtp",
        "unit": "N/kg",
        "kind": "response_metric",
        "metric": "Peak Vertical Force / BM",
        "minimum_current_observations": 5,
        "staff_prompt": "Discuss if maximal force output changes beyond expected process behavior.",
    },
]
```

- [ ] **Step 2: Add limit and point helpers**

Add these functions after `build_current_forceplate`:

```python
def natural_process_limits(values: list[float]) -> dict:
    numeric = [float(value) for value in values if value is not None]
    if not numeric:
        return {"center": None, "unpl": None, "lnpl": None}
    center = sum(numeric) / len(numeric)
    if len(numeric) < 2:
        return {"center": round(center, 4), "unpl": None, "lnpl": None}
    moving_ranges = [abs(numeric[index] - numeric[index - 1]) for index in range(1, len(numeric))]
    mr_bar = sum(moving_ranges) / len(moving_ranges)
    sigma = mr_bar / 1.128
    return {
        "center": round(center, 4),
        "unpl": round(center + 3 * sigma, 4),
        "lnpl": round(center - 3 * sigma, 4),
    }


def weekly_lookup(rows: list[dict], source: str, metric: str) -> dict[tuple[int, str], dict]:
    return {
        (row["ramp"], row["week_end"]): row
        for row in rows
        if row.get("source") == source and row.get("metric") == metric and row.get("week_end")
    }


def metric_points_from_weekly(rows: list[dict], metric_def: dict) -> list[dict]:
    if metric_def["kind"] == "weekly_ratio":
        numerator = weekly_lookup(rows, metric_def["source"], metric_def["numerator"])
        denominator = weekly_lookup(rows, metric_def["source"], metric_def["denominator"])
        points = []
        for key, num_row in numerator.items():
            denom_row = denominator.get(key)
            denom = denom_row.get("value") if denom_row else None
            if denom in (None, 0):
                continue
            points.append({
                "ramp": num_row["ramp"],
                "date": num_row["week_end"],
                "value": round(float(num_row["value"]) / float(denom), 4),
                "detail": num_row.get("detail"),
            })
        return sorted(points, key=lambda point: (point["ramp"], point["date"]))

    points = []
    for row in rows:
        if row.get("source") == metric_def["source"] and row.get("metric") == metric_def["metric"] and row.get("week_end"):
            points.append({
                "ramp": row["ramp"],
                "date": row["week_end"],
                "value": row.get("value"),
                "detail": row.get("detail"),
            })
    return sorted(points, key=lambda point: (point["ramp"], point["date"]))


def metric_points_from_response(rows: list[dict], metric_def: dict) -> list[dict]:
    points = []
    for row in rows:
        if row.get("source") == metric_def["source"] and row.get("metric") == metric_def["metric"] and row.get("date"):
            points.append({
                "ramp": row["ramp"],
                "date": row["date"],
                "value": row.get("value"),
                "detail": row.get("detail"),
            })
    return sorted(points, key=lambda point: (point["ramp"], point["date"]))
```

- [ ] **Step 3: Add signal and metric builders**

Add these functions after the point helpers:

```python
def classify_latest_signal(latest: dict | None, limits: dict) -> tuple[str, str | None]:
    if not latest or latest.get("value") is None:
        return "pending", None
    value = float(latest["value"])
    unpl = limits.get("unpl")
    lnpl = limits.get("lnpl")
    if unpl is not None and value > float(unpl):
        return "signal", "outside_limits"
    if lnpl is not None and value < float(lnpl):
        return "signal", "outside_limits"
    return "routine_variation", None


def build_pulse_metric(metric_def: dict, weekly_rows: list[dict], response_rows: list[dict]) -> dict:
    if metric_def["kind"] in {"weekly_metric", "weekly_ratio"}:
        points = metric_points_from_weekly(weekly_rows, metric_def)
    else:
        points = metric_points_from_response(response_rows, metric_def)

    historical_points = [point for point in points if point["ramp"] in {2023, 2024, 2025}]
    current_points = [point for point in points if point["ramp"] == 2026]
    current_observations = len(current_points)
    current_limits = natural_process_limits([point["value"] for point in current_points])
    historical_limits = natural_process_limits([point["value"] for point in historical_points])

    if current_observations >= metric_def["minimum_current_observations"]:
        guardrail_source = "2026_provisional_limits"
        limits = current_limits
    else:
        guardrail_source = "historical_guardrails"
        limits = historical_limits

    latest = current_points[-1] if current_points else None
    signal_state, signal_rule = classify_latest_signal(latest, limits)

    return {
        "id": metric_def["id"],
        "label": metric_def["label"],
        "domain": metric_def["domain"],
        "source": metric_def["source"],
        "unit": metric_def["unit"],
        "points": current_points,
        "center": limits["center"],
        "unpl": limits["unpl"],
        "lnpl": limits["lnpl"],
        "guardrail_source": guardrail_source,
        "minimum_current_observations": metric_def["minimum_current_observations"],
        "current_observations": current_observations,
        "latest_point": latest,
        "signal_state": signal_state,
        "signal_rule": signal_rule,
        "staff_prompt": metric_def["staff_prompt"],
    }


def build_pulse_monitor(
    weekly_rows: list[dict],
    response_rows: list[dict],
    current_ramp: dict,
    current_forceplate: dict,
    live_baseline: dict,
) -> dict:
    metrics = [
        build_pulse_metric(metric_def, weekly_rows, response_rows)
        for metric_def in PULSE_METRICS
    ]
    signals = [
        {
            "metric_id": metric["id"],
            "label": metric["label"],
            "signal_rule": metric["signal_rule"],
            "staff_prompt": metric["staff_prompt"],
        }
        for metric in metrics
        if metric["signal_state"] == "signal"
    ]
    return {
        "title": "Tezino Morning Pulse Check",
        "subtitle": "Selected process behavior charts for current summer ramp monitoring.",
        "guardrail_policy": {
            "historical_source": "historical_guardrails",
            "current_source": "2026_provisional_limits",
            "minimum_current_observations": {
                "session_metrics": 5,
                "response_metrics": 5,
            },
            "live_baseline_label": live_baseline.get("label"),
        },
        "source_freshness": [
            {"source": "GPS", "latest": current_ramp.get("data_through", {}).get("gps_sessions"), "label": "sessions"},
            {"source": "Perch", "latest": current_ramp.get("data_through", {}).get("perch_training_days"), "label": "training days"},
            {"source": "CMJ", "latest": current_forceplate.get("cmj", {}).get("date"), "label": "latest test"},
            {"source": "IMTP", "latest": current_forceplate.get("imtp", {}).get("date"), "label": "latest test"},
        ],
        "status": {
            "open_signals": len(signals),
            "metrics_tracked": len(metrics),
            "guardrail_mode": "hybrid_historical_then_2026",
        },
        "metrics": metrics,
        "signals": signals,
    }
```

- [ ] **Step 4: Wire `pulse_monitor` into the payload**

In `build_dashboard_payload`, replace the direct return with local variables and include `pulse_monitor`.

Use this pattern:

```python
    current_ramp = build_current_ramp(kpis)
    current_forceplate = build_current_forceplate(response)
    live_baseline = build_live_baseline(weekly)

    return {
        "schema_version": 1,
        "generated_on": date.today().isoformat(),
        "project": {
            "athlete": "Devonte Tezino",
            "audience": "performance_staff",
            "frame": "SPC live monitor with historical warning references",
        },
        "current_ramp": current_ramp,
        "current_forceplate": current_forceplate,
        "live_baseline": live_baseline,
        "pulse_monitor": build_pulse_monitor(weekly, response, current_ramp, current_forceplate, live_baseline),
        "warning_references": build_warning_references(kpis),
        "spc_validation": build_spc_validation(spc_summary),
        "series": {
            "weekly_exposure": compact_weekly(weekly),
            "response": compact_response(response),
            "spc_signal_points": compact_spc_points(spc_points),
        },
        "caveats": [
            "First four weeks of June 2026 selected as the live baseline; limits are provisional until the four-week window is complete.",
            "FC26 P1 is estimated as 2026-07-29 until the calendar is confirmed.",
            "Catapult tier-2 acceleration and HSR thresholds for a 290 lb DL are pending.",
            "Catapult tier-2 proxy rows remain review prompts, not locked foot-specific thresholds.",
            "SPC validation supports change detection, not a strong injury-prediction claim.",
        ],
    }
```

- [ ] **Step 5: Run the focused tests to verify GREEN**

Run:

```powershell
python -m pytest tests\test_build_dashboard_data.py -q -p no:cacheprovider
```

Expected:

```text
5 passed
```

- [ ] **Step 6: Commit the data contract**

Run:

```powershell
git add scripts\build_dashboard_data.py tests\test_build_dashboard_data.py tests\fixtures\dashboard_data\weekly_exposure.csv
git commit -m "feat: add pulse monitor data contract"
```

Expected: commit succeeds. If the repo has unrelated unstaged changes, leave them unstaged.

---

### Task 3: Add Option A HTML Tests

**Files:**
- Modify: `tests/test_build_dashboard_html.py`
- Test: `tests/test_build_dashboard_html.py`

- [ ] **Step 1: Write the failing HTML lead-section test**

Add this test method to `BuildDashboardHtmlTests`:

```python
    def test_dashboard_html_leads_with_morning_pulse_check(self):
        data_module = load_module("build_dashboard_data_for_pulse_html", DATA_SCRIPT)
        html_module = load_module("build_dashboard_html_pulse", HTML_SCRIPT)
        payload = data_module.build_dashboard_payload(FIXTURE)

        html = html_module.render_dashboard(payload)
        first_chart_index = html.index("pulse-chart-grid")
        warning_index = html.index("Historical Warning References")

        self.assertIn("Tezino Morning Pulse Check", html)
        self.assertIn("Selected process behavior charts for current summer ramp monitoring.", html)
        self.assertIn("Average player load per session", html)
        self.assertIn("CMJ mRSI", html)
        self.assertIn("IMTP PVF/BM", html)
        self.assertIn("Historical guardrails", html)
        self.assertIn("2026 provisional limits", html)
        self.assertLess(first_chart_index, warning_index)
```

- [ ] **Step 2: Run the test to verify RED**

Run:

```powershell
python -m pytest tests\test_build_dashboard_html.py::BuildDashboardHtmlTests::test_dashboard_html_leads_with_morning_pulse_check -q -p no:cacheprovider
```

Expected:

```text
FAILED ... ValueError: substring not found
```

The exact failure can be an assertion failure if `pulse-chart-grid` exists after implementation from a prior attempt. The required red condition is that the current HTML does not satisfy the Option A lead-section contract.

---

### Task 4: Implement Option A Static HTML Lead Section

**Files:**
- Modify: `scripts/build_dashboard_html.py`
- Test: `tests/test_build_dashboard_html.py`

- [ ] **Step 1: Add guardrail and signal formatters**

Add these helper functions after `fmt_pct`:

```python
def guardrail_label(value: Any) -> str:
    labels = {
        "historical_guardrails": "Historical guardrails",
        "2026_provisional_limits": "2026 provisional limits",
    }
    return labels.get(str(value), esc(value))


def signal_state_label(value: Any) -> str:
    labels = {
        "pending": "Data pending",
        "routine_variation": "Routine variation",
        "signal": "Process signal",
    }
    return labels.get(str(value), esc(value))
```

- [ ] **Step 2: Add the pulse metric card renderer**

Add this function after `kpi_card`:

```python
def render_pulse_metric_card(metric: dict[str, Any]) -> str:
    latest = metric.get("latest_point") or {}
    value = latest.get("value")
    unit = metric.get("unit")
    unit_suffix = "" if unit in (None, "", "ratio") else f" {esc(unit)}"
    point_rows = []
    for point in metric.get("points", [])[-8:]:
        point_rows.append(
            f"<span class='spark-point' title='{esc(point.get('date'))}: {fmt_number(point.get('value'), 2)}'></span>"
        )
    return f"""
      <article class="pulse-card {css_class(metric.get("signal_state"))}">
        <div class="pulse-card-topline">
          <h3>{esc(metric.get("label"))}</h3>
          <span>{signal_state_label(metric.get("signal_state"))}</span>
        </div>
        <div class="pulse-latest">{fmt_number(value, 2)}{unit_suffix}</div>
        <div class="pulse-meta">
          <span>{esc(latest.get("date"))}</span>
          <span>{guardrail_label(metric.get("guardrail_source"))}</span>
        </div>
        <div class="pbc-limits">
          <span>Center {fmt_number(metric.get("center"), 2)}</span>
          <span>UNPL {fmt_number(metric.get("unpl"), 2)}</span>
          <span>LNPL {fmt_number(metric.get("lnpl"), 2)}</span>
        </div>
        <div class="sparkline" aria-label="{esc(metric.get("label"))} current points">{"".join(point_rows)}</div>
        <p class="pulse-prompt">{esc(metric.get("staff_prompt"))}</p>
      </article>"""
```

- [ ] **Step 3: Add the pulse monitor section renderer**

Add this function before `render_current_ramp`:

```python
def render_pulse_monitor(pulse: dict[str, Any]) -> str:
    status = pulse.get("status", {})
    freshness = pulse.get("source_freshness", [])
    freshness_cards = "\n".join(
        kpi_card(item.get("source"), esc(item.get("latest")), esc(item.get("label")))
        for item in freshness
    )
    metric_cards = "\n".join(render_pulse_metric_card(metric) for metric in pulse.get("metrics", []))
    signals = pulse.get("signals", [])
    if signals:
        signal_items = "\n".join(
            f"<li><strong>{esc(signal.get('label'))}</strong>: {esc(signal_label(signal.get('signal_rule')))}. {esc(signal.get('staff_prompt'))}</li>"
            for signal in signals
        )
    else:
        signal_items = "<li>No process signals in the selected current metrics.</li>"
    return f"""
    <section class="pulse-hero" aria-labelledby="pulse-title">
      <div class="pulse-heading">
        <div>
          <h1 id="pulse-title">{esc(pulse.get("title"))}</h1>
          <p>{esc(pulse.get("subtitle"))}</p>
        </div>
        <div class="pulse-status">
          <strong>{fmt_number(status.get("open_signals"))}</strong>
          <span>open signals</span>
        </div>
      </div>
      <div class="pulse-freshness">{freshness_cards}</div>
      <div id="pulse-chart-grid" class="pulse-chart-grid">{metric_cards}</div>
      <div class="pulse-signal-summary">
        <h2>Signal Summary</h2>
        <ul>{signal_items}</ul>
      </div>
    </section>"""
```

- [ ] **Step 4: Add CSS for the pulse section**

Inside the `<style>` block, add:

```css
    .pulse-hero {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      box-shadow: var(--shadow);
      padding: 22px;
      margin: 22px 0;
    }
    .pulse-heading {
      display: flex;
      justify-content: space-between;
      gap: 20px;
      align-items: flex-start;
      margin-bottom: 16px;
    }
    .pulse-heading h1 {
      font-size: clamp(2rem, 4vw, 3.4rem);
      line-height: 0.98;
    }
    .pulse-heading p {
      color: var(--muted);
      margin-top: 8px;
      max-width: 760px;
    }
    .pulse-status {
      min-width: 140px;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px;
      text-align: center;
      background: var(--surface-soft);
    }
    .pulse-status strong {
      display: block;
      font-size: 2rem;
    }
    .pulse-status span {
      color: var(--muted);
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .pulse-freshness {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
      margin-bottom: 16px;
    }
    .pulse-chart-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }
    .pulse-card {
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      background: #fff;
    }
    .pulse-card.signal {
      border-color: #ffd0cc;
      background: var(--red-bg);
    }
    .pulse-card-topline {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: flex-start;
    }
    .pulse-card-topline span {
      color: var(--accent-strong);
      font-size: 0.76rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .pulse-latest {
      font-size: 2rem;
      font-weight: 760;
      margin-top: 10px;
    }
    .pulse-meta,
    .pbc-limits {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      color: var(--muted);
      font-size: 0.86rem;
      margin-top: 6px;
    }
    .sparkline {
      display: flex;
      align-items: end;
      gap: 4px;
      height: 28px;
      margin-top: 12px;
    }
    .spark-point {
      display: inline-block;
      width: 18px;
      height: 18px;
      border-radius: 999px;
      background: var(--accent);
    }
    .pulse-prompt {
      color: var(--muted);
      margin-top: 10px;
      font-size: 0.9rem;
    }
    .pulse-signal-summary {
      margin-top: 16px;
      padding: 14px 16px;
      background: var(--surface-soft);
      border: 1px solid #d5e2d7;
      border-radius: 8px;
    }
    .pulse-signal-summary h2 {
      margin-bottom: 8px;
    }
```

Also update the mobile media query to include:

```css
      .pulse-heading { display: block; }
      .pulse-status { margin-top: 14px; }
      .pulse-freshness, .pulse-chart-grid { grid-template-columns: 1fr; }
```

- [ ] **Step 5: Lead the page with `render_pulse_monitor`**

In `render_dashboard`, replace the current top `<header class="topbar">...</header>` block with the existing generated date metadata retained in a smaller topbar, then render the pulse monitor before caveats:

```python
    <header class="topbar">
      <div>
        <p class="frame">Generated {esc(generated)} for {esc(project.get("audience"))}</p>
      </div>
    </header>
    {render_pulse_monitor(payload.get("pulse_monitor", {}))}
    {render_caveats(payload.get("caveats", []))}
```

Keep the existing `render_current_ramp`, `render_current_forceplate`, `render_live_baseline`, `render_warning_references`, `render_spc_validation`, and `render_charts` calls after caveats for now.

- [ ] **Step 6: Run the focused HTML tests**

Run:

```powershell
python -m pytest tests\test_build_dashboard_html.py -q -p no:cacheprovider
```

Expected:

```text
4 passed
```

- [ ] **Step 7: Commit the HTML lead section**

Run:

```powershell
git add scripts\build_dashboard_html.py tests\test_build_dashboard_html.py
git commit -m "feat: lead dashboard with pulse check monitor"
```

Expected: commit succeeds. If generated `data/dashboard/index.html` is modified later, leave it for Task 5.

---

### Task 5: Refresh Artifacts And Update Handoff

**Files:**
- Modify: `data/dashboard/dashboard_data.json`
- Modify: `data/dashboard/index.html`
- Modify: `docs/HANDOFF-2026-06-11-night.md`
- Modify: `docs/NARRATIVE-PLAN.md`
- Modify: `AGENTS.md`
- Test: full test suite

- [ ] **Step 1: Refresh generated artifacts**

Run:

```powershell
python scripts\refresh_dashboard.py
```

Expected:

```text
dashboard_data.json: wrote data\dashboard\dashboard_data.json
index.html: wrote data\dashboard\index.html
Dashboard refresh complete:
  data\dashboard\dashboard_data.json
  data\dashboard\index.html
```

- [ ] **Step 2: Verify the JSON readback**

Run:

```powershell
@'
import json
from pathlib import Path
payload = json.loads(Path("data/dashboard/dashboard_data.json").read_text())
pulse = payload["pulse_monitor"]
print(pulse["title"])
print([metric["id"] for metric in pulse["metrics"]])
print(pulse["status"])
'@ | python -
```

Expected includes:

```text
Tezino Morning Pulse Check
gps_avg_player_load_per_session
cmj_mrsi
imtp_pvf_bm
```

- [ ] **Step 3: Verify the HTML readback**

Run:

```powershell
Select-String -Path data\dashboard\index.html -Pattern 'Tezino Morning Pulse Check|pulse-chart-grid|Average player load per session|Historical Warning References'
```

Expected: all four patterns are present, with `pulse-chart-grid` appearing before `Historical Warning References`.

- [ ] **Step 4: Update docs**

Update `docs/HANDOFF-2026-06-11-night.md` current state with:

```markdown
The dashboard now leads with the Pulse Check First layout. The top section is driven by
`pulse_monitor` in `data/dashboard/dashboard_data.json` and shows selected process behavior
metrics before historical warning context.
```

Update `docs/NARRATIVE-PLAN.md` Phase 4 with:

```markdown
- [x] Pulse Check First redesign: the static dashboard now leads with selected process
      behavior chart panels for average player load per session, high-IMA/high-impact GPS
      exposure, Perch axial load, CMJ, and IMTP.
```

Update `AGENTS.md` current milestone with:

```markdown
The staff-facing dashboard lead section is now `Tezino Morning Pulse Check`, driven by the
`pulse_monitor` JSON contract. Historical 2024/2025 context remains secondary.
```

- [ ] **Step 5: Run full verification**

Run:

```powershell
python -m pytest tests -q -p no:cacheprovider
```

Expected:

```text
18 passed
```

The exact pass count may be higher if additional tests were added before this task. There must be zero failures.

- [ ] **Step 6: Commit generated artifacts and docs**

Run:

```powershell
git add data\dashboard\dashboard_data.json data\dashboard\index.html docs\HANDOFF-2026-06-11-night.md docs\NARRATIVE-PLAN.md AGENTS.md
git commit -m "chore: refresh pulse check dashboard artifacts"
```

Expected: commit succeeds. Leave unrelated upstream sync artifacts unstaged unless they are intentionally part of this dashboard checkpoint.

---

## Final Verification

Run:

```powershell
python scripts\refresh_dashboard.py
python -m pytest tests -q -p no:cacheprovider
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8765/data/dashboard/index.html -TimeoutSec 3
```

Expected:

- Refresh exits 0.
- Test suite exits 0.
- Local dashboard server returns HTTP 200 if the server is still running.
- `data/dashboard/index.html` contains `Tezino Morning Pulse Check`.
- `data/dashboard/index.html` contains `pulse-chart-grid`.
- `data/dashboard/index.html` contains `Average player load per session`.
- `data/dashboard/index.html` still contains `Historical Warning References` below the pulse section.

---

## Spec Coverage Review

- Option A Pulse Check First layout: Tasks 3 and 4.
- Selected metrics and total-distance exclusion: Tasks 1 and 2.
- Hybrid historical-to-2026 guardrail rule: Tasks 1 and 2.
- Morning pulse-check status strip and source freshness: Tasks 2 and 4.
- Historical context below the fold: Task 4.
- Tests and full verification: Tasks 1, 3, and 5.
- No new scheduling, acute:chronic, React app, or source extraction: preserved by file scope.
