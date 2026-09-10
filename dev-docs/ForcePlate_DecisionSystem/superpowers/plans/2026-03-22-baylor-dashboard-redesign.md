# Baylor Dashboard Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebrand the CMJ dashboard with Baylor University identity (green/gold), position-grouped roster, action-first athlete profile, and radar chart value labels.

**Architecture:** Template-first approach. Back up the old template, then work through Python changes (radar SVG colors + value labels, position grouping in render_dashboard), followed by full template rewrite (CSS + HTML restructure), then test updates. Each task is independently committable.

**Tech Stack:** Python, Jinja2, DuckDB, SVG, CSS, pytest

**Spec:** `docs/superpowers/specs/2026-03-22-baylor-dashboard-redesign-design.md`

---

### Task 1: Back Up Old Template

**Files:**
- Copy: `src/report/templates/dashboard.html.j2` → `src/report/templates/dashboard.html.j2.bak`

- [ ] **Step 1: Copy template to backup**

```bash
cp src/report/templates/dashboard.html.j2 src/report/templates/dashboard.html.j2.bak
```

- [ ] **Step 2: Verify backup exists**

```bash
diff src/report/templates/dashboard.html.j2 src/report/templates/dashboard.html.j2.bak
```

Expected: no differences (empty output).

- [ ] **Step 3: Commit**

```bash
git add src/report/templates/dashboard.html.j2.bak
git commit -m "chore: back up dashboard template before Baylor redesign"
```

---

### Task 2: Update Radar SVG Colors

**Files:**
- Modify: `src/report/html_dashboard.py:30-64` (color constants)
- Test: `tests/test_html_dashboard.py`

- [ ] **Step 1: Update test assertions for new colors**

In `tests/test_html_dashboard.py`, update the two color-dependent tests:

```python
# TestRadarSvgScoring class

def test_svg_color_polygon_fill(self):
    """Polygon fill color must match Baylor gold (#FECB0022)."""
    svg = self._svg_for({})
    assert "#FECB0022" in svg or "FECB00" in svg

def test_label_color_present(self):
    """Label color #7aab7a (Baylor muted green) must appear in the SVG."""
    svg = self._svg_for({})
    assert "#7aab7a" in svg
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_html_dashboard.py::TestRadarSvgScoring::test_svg_color_polygon_fill tests/test_html_dashboard.py::TestRadarSvgScoring::test_label_color_present -v
```

Expected: 2 FAIL

- [ ] **Step 3: Update color constants in html_dashboard.py**

Replace the color constant block at lines 51-63:

```python
# Colours — Baylor palette
_COL_BG = "#001a0d"
_COL_GRID = "#003a1a"
_COL_AXIS = "#1a4a2a"
_COL_POLY_FILL = "#FECB0022"
_COL_POLY_STROKE = "#FECB00"
_COL_LABEL = "#7aab7a"
# Normative P50 overlay (unchanged)
_COL_NORM_STROKE = "#ffffff"
_COL_NORM_FILL = "#ffffff0d"
# Team positional average overlay (unchanged)
_COL_TEAM_STROKE = "#f0a030"
_COL_TEAM_FILL = "#f0a03015"
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_html_dashboard.py::TestRadarSvgScoring -v
```

Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add src/report/html_dashboard.py tests/test_html_dashboard.py
git commit -m "feat: update radar SVG colors to Baylor green/gold palette"
```

---

### Task 3: Add Value Labels to Radar SVG

**Files:**
- Modify: `src/report/html_dashboard.py:96-266` (`render_radar_svg`)
- Test: `tests/test_html_dashboard.py`

- [ ] **Step 1: Write failing test for value labels**

Add a new test class in `tests/test_html_dashboard.py`:

```python
class TestRadarSvgValueLabels:
    """Radar SVG must include value labels at each axis vertex."""

    def _make_metrics(self):
        pos_cfg = CFG["positions"]["Defensive Back"]
        return {
            "Peak Power / BM": 67.4,
            "Eccentric Peak Force / BM": 2.5,
            "Eccentric Peak Power / BM": 24.1,
            "Jump Height (Imp-Mom)": 45.0,
            "RSI-modified": 0.74,
            "Flight Time:Contraction Time": 0.94,
        }

    def test_value_labels_present(self):
        """Each metric value should appear as text in the SVG."""
        svg = render_radar_svg(self._make_metrics(), "Defensive Back", CFG)
        assert "67.4" in svg     # Peak Power / BM (1 decimal)
        assert "0.74" in svg     # RSI-modified (2 decimal)
        assert "0.94" in svg     # FT:CT (2 decimal)
        assert "45.0" in svg     # Jump Ht (1 decimal)
        assert "24.1" in svg     # ECC Pw (1 decimal)

    def test_value_labels_absent_when_metric_missing(self):
        """Missing metrics should not produce value labels."""
        svg = render_radar_svg({}, "Defensive Back", CFG)
        # With no metrics, no numeric value labels should appear
        # (only axis labels and grid numbers)
        assert svg.strip().startswith("<svg")

    def test_value_label_formatting_two_decimals(self):
        """RSI-mod and FT:CT use 2 decimal places."""
        metrics = {"RSI-modified": 0.7, "Flight Time:Contraction Time": 0.9}
        svg = render_radar_svg(metrics, "Defensive Back", CFG)
        assert "0.70" in svg
        assert "0.90" in svg

    def test_value_label_formatting_one_decimal(self):
        """All other metrics use 1 decimal place."""
        metrics = {"Peak Power / BM": 67.0}
        svg = render_radar_svg(metrics, "Defensive Back", CFG)
        assert "67.0" in svg
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_html_dashboard.py::TestRadarSvgValueLabels -v
```

Expected: FAIL (no value labels in SVG yet)

- [ ] **Step 3: Implement value labels in render_radar_svg**

Add after the axis labels section (after the loop at ~line 241), before the legend:

```python
# ---- Value labels at each vertex -----------------------------------
_TWO_DECIMAL_KEYS = {"RSI-modified", "Flight Time:Contraction Time"}

for i, (_label, metric_key, _cfg_key) in enumerate(_AXES):
    value = metrics.get(metric_key)
    if value is None:
        continue
    # Format: 2 decimals for RSI-mod and FT:CT, 1 decimal otherwise
    if metric_key in _TWO_DECIMAL_KEYS:
        val_str = f"{value:.2f}"
    else:
        val_str = f"{value:.1f}"
    # Position: slightly outward from the polygon point
    px, py = _polar(scores[i], i)
    angle_deg = i * (360.0 / _N_AXES) - 90.0
    angle_rad = math.radians(angle_deg)
    offset = 12
    vx = px + offset * math.cos(angle_rad)
    vy = py + offset * math.sin(angle_rad)
    # Text anchor
    if vx < _CX - 5:
        anchor = "end"
    elif vx > _CX + 5:
        anchor = "start"
    else:
        anchor = "middle"
    lines.append(
        f'  <text x="{vx:.1f}" y="{vy:.1f}" '
        f'fill="{_COL_POLY_STROKE}" font-size="9" font-weight="700" '
        f'text-anchor="{anchor}" dominant-baseline="middle">'
        f'{val_str}</text>'
    )
```

Note: `_TWO_DECIMAL_KEYS` should be defined as a module-level constant near the other radar constants. `scores` is already computed earlier in the function — the value labels use the polygon vertex positions.

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_html_dashboard.py::TestRadarSvgValueLabels -v
```

Expected: all PASS

- [ ] **Step 5: Run full radar test suite**

```bash
python -m pytest tests/test_html_dashboard.py::TestRadarSvgStructure tests/test_html_dashboard.py::TestRadarSvgScoring tests/test_html_dashboard.py::TestRadarSvgValueLabels -v
```

Expected: all PASS

- [ ] **Step 6: Commit**

```bash
git add src/report/html_dashboard.py tests/test_html_dashboard.py
git commit -m "feat: add value labels to radar SVG at each axis vertex"
```

---

### Task 4: Add Position Grouping to render_dashboard

**Files:**
- Modify: `src/report/html_dashboard.py:780-854` (`render_dashboard`)
- Test: `tests/test_html_dashboard.py`

- [ ] **Step 1: Write failing test for position grouping**

Add to `tests/test_html_dashboard.py`:

```python
class TestPositionGrouping:
    """render_dashboard must pass position_groups to the template."""

    def test_position_groups_in_html(self, tmp_path):
        """HTML output should contain position group headers."""
        db_path = str(tmp_path / "test.db")
        conn = get_connection(db_path)
        init_schema(conn)
        _seed_db(conn)
        output = tmp_path / "report.html"
        render_dashboard(conn, output, open_browser=False)
        conn.close()
        html = output.read_text(encoding="utf-8")
        assert "Defensive Back" in html

    def test_position_group_order(self):
        """POSITION_ORDER must list skill positions before big positions."""
        from src.report.html_dashboard import POSITION_ORDER
        db_idx = POSITION_ORDER.index("Defensive Back")
        ol_idx = POSITION_ORDER.index("Offensive Line")
        assert db_idx < ol_idx
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_html_dashboard.py::TestPositionGrouping -v
```

Expected: FAIL (POSITION_ORDER not defined, template doesn't have group headers yet)

- [ ] **Step 3: Add POSITION_ORDER constant and update render_dashboard**

Add module-level constant near the top of `html_dashboard.py`:

```python
# Position display order: skill positions first, then big, then special teams
POSITION_ORDER = [
    "Defensive Back", "Linebacker", "Wide Receiver", "Running Back",
    "Quarterback", "Tight End", "Defensive Line", "Offensive Line",
    "Special Teams", "Kicker/Punter",
]
```

Update `render_dashboard()` — after building the `athletes` list and `group_counts`, add position grouping:

```python
# Build position groups for template
from collections import OrderedDict
pos_groups_dict: dict[str, list] = {}
for a in athletes:
    pos = a["position"]
    if pos not in pos_groups_dict:
        pos_groups_dict[pos] = []
    pos_groups_dict[pos].append(a)

position_groups = []
for pos_name in POSITION_ORDER:
    if pos_name in pos_groups_dict:
        position_groups.append({
            "position_name": pos_name,
            "athletes": pos_groups_dict[pos_name],
            "count": len(pos_groups_dict[pos_name]),
        })
# Catch any positions not in POSITION_ORDER
for pos_name, pos_athletes in pos_groups_dict.items():
    if pos_name not in POSITION_ORDER:
        position_groups.append({
            "position_name": pos_name,
            "athletes": pos_athletes,
            "count": len(pos_athletes),
        })
```

Update the `template.render()` call to include `position_groups`:

```python
html = template.render(
    athletes=athletes,
    position_groups=position_groups,
    group_counts=group_counts,
    report_date=str(date.today()),
    team_name="Baylor Football",
    total_count=len(athletes),
)
```

Note: `team_name` changes from `"Football Team"` to `"Baylor Football"`.

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_html_dashboard.py::TestPositionGrouping -v
```

Expected: first test may still fail until template is updated (Task 5). Second test should PASS.

- [ ] **Step 5: Commit**

```bash
git add src/report/html_dashboard.py tests/test_html_dashboard.py
git commit -m "feat: add POSITION_ORDER and position grouping to render_dashboard"
```

---

### Task 5: Rewrite Dashboard Template — Roster View

**Files:**
- Modify: `src/report/templates/dashboard.html.j2:1-375` (everything up to profile views)

This is the largest task. Rewrite the CSS and roster HTML to use the Baylor palette and position-grouped layout.

- [ ] **Step 1: Rewrite CSS reset, base, and layout**

Replace lines 7-17 (reset & base):

```css
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background: #001a0d;
  color: #f0f0e8;
  line-height: 1.5;
}
a { color: #FECB00; text-decoration: none; }
a:hover { text-decoration: underline; }
```

- [ ] **Step 2: Rewrite team header CSS**

Replace the `.team-header` block with the Baylor header:

```css
.team-header {
  background: linear-gradient(135deg, #003015 0%, #001a0d 100%);
  border-bottom: 3px solid #FECB00;
  padding: 20px 32px;
  position: relative;
  overflow: hidden;
}
.team-header::before {
  content: '';
  position: absolute; top: 0; right: 0; bottom: 0; width: 200px;
  background: repeating-linear-gradient(
    -45deg, transparent, transparent 8px,
    #FECB0010 8px, #FECB0010 10px
  );
}
.team-header-inner {
  display: flex; justify-content: space-between; align-items: center;
  position: relative; z-index: 1; max-width: 1400px; margin: 0 auto;
}
.team-header-left { display: flex; align-items: center; gap: 16px; }
.bu-logo {
  width: 48px; height: 48px; border-radius: 50%;
  background: #FECB00; display: flex; align-items: center; justify-content: center;
  font-weight: 900; color: #003015; font-size: 18px; letter-spacing: -1px;
  box-shadow: 0 0 20px #FECB0040;
}
.team-title { font-size: 1.5rem; font-weight: 800; color: #FECB00; letter-spacing: 2px; text-transform: uppercase; }
.team-subtitle { font-size: 0.8rem; color: #7aab7a; letter-spacing: 1px; }
.team-header .meta { color: #7aab7a; font-size: 0.82rem; text-align: right; }
```

- [ ] **Step 3: Update alert strip, tabs, and card CSS**

Alert strip — change background to `#1a0a0a`, keep red left border. No structural change.

Tabs:
```css
.tab {
  display: inline-block; padding: 6px 14px; border-radius: 20px;
  font-size: 0.8rem; font-weight: 600; cursor: pointer;
  background: #002a12; color: #7aab7a; border: 1px solid #003a1a;
  transition: background 0.15s, color 0.15s;
}
.tab:hover { background: #003a1a; color: #FECB00; }
.tab.active { background: #003a1a; color: #FECB00; border-color: #FECB0060; }
```

Sort select: `background: #002a12; color: #f0f0e8; border: 1px solid #003a1a;`

Cards:
```css
.card {
  background: linear-gradient(180deg, #002a12 0%, #001a0d 100%);
  border: 1px solid #003a1a; border-radius: 10px;
  padding: 16px; cursor: pointer;
  transition: all 0.2s;
  display: flex; flex-direction: column; gap: 10px;
}
.card:hover { border-color: #FECB00; transform: translateY(-2px); box-shadow: 0 4px 20px #FECB0015; }
```

Card metric values: `color: #FECB00;`
Card metric labels: `color: #5a8a5a;`
Card footer: `color: #5a8a5a;`

Readiness dots — add glow and pulse:
```css
.dot-green  { background: #5adf7a; box-shadow: 0 0 6px #5adf7a80; }
.dot-yellow { background: #f0c040; box-shadow: 0 0 6px #f0c04080; }
.dot-orange { background: #cc7733; box-shadow: 0 0 6px #cc773380; }
.dot-red    { background: #ff4444; box-shadow: 0 0 6px #ff444480; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
```

Badge colors — update DEVELOPMENTAL:
```css
.badge-developmental { color: #90a0ff; background: #0d0d1e; border: 1px solid #3a3a8e50; }
.badge-movement { color: #7aab7a; background: #0a1a0a; border: 1px solid #2a5a2a; font-size: 0.55rem; }
```

- [ ] **Step 4: Add position group CSS**

```css
.pos-group { margin-bottom: 28px; }
.pos-header {
  display: flex; align-items: center; gap: 12px; margin-bottom: 14px;
  padding-bottom: 8px; border-bottom: 2px solid #FECB0040;
}
.pos-label {
  font-size: 0.75rem; font-weight: 800; letter-spacing: 2px;
  text-transform: uppercase; color: #FECB00;
}
.pos-count {
  font-size: 0.7rem; color: #7aab7a;
  background: #003015; padding: 2px 10px; border-radius: 10px;
  border: 1px solid #FECB0030;
}
.pos-stripe {
  flex: 1; height: 2px;
  background: linear-gradient(90deg, #FECB0040, transparent);
}
```

- [ ] **Step 5: Rewrite roster HTML structure**

Replace the header HTML with Baylor header:

```html
<div class="team-header">
  <div class="team-header-inner">
    <div class="team-header-left">
      <div class="bu-logo">BU</div>
      <div>
        <div class="team-title">{{ team_name }}</div>
        <div class="team-subtitle">CMJ Force Plate Dashboard</div>
      </div>
    </div>
    <div class="meta">
      <div>{{ report_date }}</div>
      <div>{{ total_count }} Athletes</div>
    </div>
  </div>
</div>
```

Replace the flat `#card-grid` with position-grouped layout:

```html
{% for pg in position_groups %}
<div class="pos-group" data-position="{{ pg.position_name }}">
  <div class="pos-header">
    <span class="pos-label">{{ pg.position_name }}s</span>
    <span class="pos-count">{{ pg.count }} athlete{{ 's' if pg.count != 1 }}</span>
    <div class="pos-stripe"></div>
  </div>
  <div class="card-grid">
    {% for a in pg.athletes %}
    <div class="card {% if a.readiness_flag == 'red' %}flag-red{% elif a.readiness_flag == 'orange' %}flag-orange{% endif %}"
         data-group="{{ a.group_css_class }}"
         data-id="{{ a.athlete_id }}"
         data-name="{{ a.athlete_name }}"
         data-mrsi="{{ a.mrsi | default(0) }}"
         data-power="{{ a.rel_power_bm | default(0) }}"
         data-readiness-rank="{{ a.readiness_rank }}"
         onclick="showProfile('{{ a.athlete_id }}')">
      <!-- same card interior as current, with Baylor styling -->
      <div class="card-top">
        <div class="card-name">{{ a.athlete_name }}</div>
        <span class="dot dot-{{ a.readiness_flag | default('green') }}"></span>
      </div>
      <div class="card-badges">
        <span class="badge badge-{{ a.group_css_class }}">{{ a.display_group }}</span>
        <span class="badge badge-movement">{{ a.movement_type }}</span>
      </div>
      <div class="card-metrics">
        <div class="card-metric-cell">
          <div class="card-metric-label">Power</div>
          <div class="card-metric-value">
            {% if a.rel_power_bm is not none %}{{ "%.1f" | format(a.rel_power_bm) }}{% else %}&mdash;{% endif %}
            <span class="card-metric-unit">W/kg</span>
          </div>
        </div>
        <div class="card-metric-cell">
          <div class="card-metric-label">Asym</div>
          <div class="card-metric-value">
            {% if a.asymmetry_pct is not none %}{{ "%.1f" | format(a.asymmetry_pct) }}{% else %}&mdash;{% endif %}
            <span class="card-metric-unit">%</span>
          </div>
        </div>
        <div class="card-metric-cell">
          <div class="card-metric-label">mRSI</div>
          <div class="card-metric-value">
            {% if a.mrsi is not none %}{{ "%.2f" | format(a.mrsi) }}{% else %}&mdash;{% endif %}
          </div>
        </div>
      </div>
      <div class="card-footer">
        <span>{{ a.position | default("—") }}{% if a.body_weight_kg is not none %} &bull; {{ "%.1f" | format(a.body_weight_kg) }} kg{% endif %}</span>
      </div>
    </div>
    {% endfor %}
  </div>
</div>
{% endfor %}
```

**Important:** Preserve the outer `<div id="roster-view" class="container">` wrapper — tests assert `"roster-view" in html` and `showRoster()` JS depends on it. Change CSS selector from `#card-grid` to `.card-grid` (class, not ID) since there are now multiple grids.

- [ ] **Step 6: Update filter/sort JS for position groups**

The filter JS must now operate across multiple `.card-grid` containers and hide empty position groups:

```javascript
/* Filter tabs */
document.querySelectorAll('.tab').forEach(function(tab) {
  tab.addEventListener('click', function() {
    var group = tab.dataset.group;
    document.querySelectorAll('.card').forEach(function(card) {
      card.style.display = (group !== 'all' && card.dataset.group !== group) ? 'none' : '';
    });
    // Hide position groups with no visible cards
    document.querySelectorAll('.pos-group').forEach(function(pg) {
      var visibleCards = pg.querySelectorAll('.card');
      var anyVisible = Array.prototype.some.call(visibleCards, function(c) {
        return c.style.display !== 'none';
      });
      pg.style.display = anyVisible ? '' : 'none';
    });
    document.querySelectorAll('.tab').forEach(function(t) {
      t.classList.remove('active');
    });
    tab.classList.add('active');
  });
});

/* Sort — reorders cards within each position group */
var sortSelect = document.getElementById('sort-select');
if (sortSelect) {
  sortSelect.addEventListener('change', function(e) {
    var field = e.target.value;
    document.querySelectorAll('.card-grid').forEach(function(grid) {
      var cards = Array.prototype.slice.call(grid.querySelectorAll('.card'));
      cards.sort(function(a, b) {
        if (field === 'name') return (a.dataset.name || '').localeCompare(b.dataset.name || '');
        if (field === 'mrsi') return parseFloat(b.dataset.mrsi || 0) - parseFloat(a.dataset.mrsi || 0);
        if (field === 'power') return parseFloat(b.dataset.power || 0) - parseFloat(a.dataset.power || 0);
        if (field === 'readiness') return parseInt(a.dataset.readinessRank || 4) - parseInt(b.dataset.readinessRank || 4);
        return 0;
      });
      cards.forEach(function(c) { grid.appendChild(c); });
    });
  });
}
```

- [ ] **Step 7: Run integration tests**

```bash
python -m pytest tests/test_html_dashboard.py::test_render_dashboard_creates_file tests/test_html_dashboard.py::test_render_dashboard_empty_db tests/test_html_dashboard.py::TestPositionGrouping -v
```

Expected: all PASS

- [ ] **Step 8: Commit**

```bash
git add src/report/templates/dashboard.html.j2
git commit -m "feat: rewrite roster view with Baylor branding and position groups"
```

---

### Task 6: Rewrite Dashboard Template — Profile View

**Files:**
- Modify: `src/report/templates/dashboard.html.j2:378-559` (profile view section)

- [ ] **Step 1: Update profile panel CSS**

Add/update profile-specific CSS for Baylor palette:

```css
.panel {
  background: linear-gradient(180deg, #002a12 0%, #001a0d 100%);
  border: 1px solid #003a1a; border-radius: 10px;
  padding: 16px; margin-bottom: 16px;
}
.panel-title {
  font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 1px; color: #FECB00; margin-bottom: 12px;
}

/* Action panel — new */
.action-panel {
  background: linear-gradient(180deg, #002a12 0%, #001a0d 100%);
  border: 1px solid #003a1a; border-radius: 10px;
  padding: 20px; margin-bottom: 16px;
}
.prescription-callout {
  border-left: 3px solid #FECB00;
  padding: 10px 16px; margin-bottom: 12px;
  background: #003a1a30; border-radius: 0 6px 6px 0;
}
.prescription-callout .panel-title { margin-bottom: 6px; }
.prescription-text { font-size: 0.9rem; color: #f0f0e8; }
.clinical-notes { font-size: 0.82rem; color: #7aab7a; white-space: pre-wrap; margin-bottom: 12px; }
.sw-pills { display: flex; gap: 6px; flex-wrap: wrap; }
.sw-pill {
  display: inline-block; padding: 3px 10px; border-radius: 12px;
  font-size: 0.7rem; font-weight: 600;
}
.sw-pill-strength { color: #5adf7a; background: #1a3a1a; border: 1px solid #2a7a3a; }
.sw-pill-weakness { color: #ff6666; background: #3a1a1a; border: 1px solid #7a2a2a; }

/* Key metrics — Baylor */
.km-cell {
  background: #001a0d; border: 1px solid #003a1a; border-radius: 6px;
  padding: 8px 10px; text-align: center;
}
.km-label { font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.5px; color: #5a8a5a; margin-bottom: 2px; }
.km-value { font-size: 1.1rem; font-weight: 700; color: #FECB00; }
.km-unit  { font-size: 0.65rem; color: #4a6a4a; }

/* Phase badges — keep semantic colors */
.ph-strong    { background: #1a3a1a; color: #5adf7a; }
.ph-monitor   { background: #2a2a1a; color: #f0c040; }
.ph-deficit   { background: #3a1a1a; color: #ff6666; }
.ph-high-risk { background: #4a1a1a; color: #ff4444; }

.phase-metric-name { color: #7aab7a; }
.phase-metric-value { font-weight: 600; color: #f0f0e8; }

/* Movement strategy */
.movement-label { font-size: 1.2rem; font-weight: 700; color: #FECB00; margin-bottom: 6px; }
.movement-desc  { font-size: 0.82rem; color: #7aab7a; margin-bottom: 12px; }
.movement-stat-label { font-size: 0.65rem; text-transform: uppercase; color: #5a8a5a; }
.movement-stat-value { font-size: 1rem; font-weight: 700; color: #f0f0e8; }

/* Trend strip */
.trend-cell {
  background: #001a0d; border: 1px solid #003a1a; border-radius: 6px;
  padding: 10px; text-align: center;
}
.trend-label { font-size: 0.65rem; text-transform: uppercase; color: #5a8a5a; margin-bottom: 4px; }
.trend-values { font-size: 0.8rem; color: #7aab7a; }
.trend-delta  { font-size: 0.9rem; font-weight: 700; margin-top: 2px; }
.trend-up   { color: #5adf7a; }
.trend-down { color: #ff6666; }
.trend-none { color: #4a6a4a; }

/* Profile header + back link */
.back-link { color: #FECB00; }
.profile-header h2 { font-size: 1.5rem; font-weight: 700; color: #f0f0e8; }
.profile-header .profile-meta { color: #7aab7a; font-size: 0.82rem; }
.flag-banner {
  background: #3a1a1a; border: 1px solid #ff6666; border-radius: 6px;
  padding: 10px 16px; margin-bottom: 16px; color: #ff6666; font-size: 0.85rem;
}
```

- [ ] **Step 2: Rewrite profile HTML — action-first reorder**

For each athlete profile, replace the panel order with:

```html
<div id="athlete-{{ a.athlete_id }}" class="profile-view container" style="display:none;">

  <span class="back-link" onclick="showRoster()">&larr; Back to roster</span>

  {% if a.has_flags %}
  <div class="flag-banner">
    {{ a.clinical_notes | default("Flagged — clinical review required", true) }}
  </div>
  {% endif %}

  <!-- Header -->
  <div class="profile-header">
    <div class="profile-header-left">
      <h2>{{ a.athlete_name }}</h2>
      <span class="badge badge-{{ a.group_css_class }}">{{ a.display_group }}</span>
      <span class="badge badge-movement">{{ a.movement_type }}</span>
    </div>
    <div class="profile-meta">
      {{ a.position | default("—") }} &bull;
      {% if a.body_weight_kg is not none %}{{ "%.1f" | format(a.body_weight_kg) }} kg &bull; {% endif %}
      {{ a.test_date | default("—") }}
    </div>
  </div>

  <!-- ROW 1: Action Panel (prescription + clinical + strengths/weaknesses) -->
  <div class="action-panel">
    <div class="prescription-callout">
      <div class="panel-title">Prescription</div>
      <div class="prescription-text">{{ a.prescription | default("No prescription assigned.", true) }}</div>
    </div>
    {% if a.clinical_notes %}
    <div class="clinical-notes">{{ a.clinical_notes }}</div>
    {% endif %}
    <div class="sw-pills">
      {% for s in a.strengths %}
      <span class="sw-pill sw-pill-strength">+ {{ s }}</span>
      {% endfor %}
      {% for w in a.weaknesses %}
      <span class="sw-pill sw-pill-weakness">- {{ w }}</span>
      {% endfor %}
    </div>
  </div>

  <!-- ROW 2: Radar + Trend -->
  <div class="two-col">
    <div class="panel radar-panel">
      <div class="panel-title">Team Percentile Profile</div>
      {{ a.radar_svg | safe }}
    </div>
    <div class="panel">
      <div class="panel-title">Trend vs Baseline
        {% if not a.baseline_established %}
        <span style="font-size:0.7rem; color:#f0a030; margin-left:8px; font-weight:400; text-transform:none;">
          Establishing baseline ({{ a.baseline_test_count }}/4 tests)
        </span>
        {% endif %}
      </div>
      <div class="trend-strip-vertical">
        {% for t in a.trend %}
        <div class="trend-cell">
          <div class="trend-label">{{ t.label }}</div>
          {% if t.direction == "none" %}
          <div class="trend-values">No baseline</div>
          <div class="trend-delta trend-none">&mdash;</div>
          {% else %}
          <div class="trend-values">
            {{ "%.2f" | format(t.prior) }} &rarr; {{ "%.2f" | format(t.current) }}
          </div>
          <div class="trend-delta {% if t.direction == 'up' %}trend-up{% else %}trend-down{% endif %}">
            {% if t.direction == "up" %}&#9650;{% else %}&#9660;{% endif %}
            {{ "%.1f" | format(t.delta_pct) }}%
          </div>
          {% endif %}
        </div>
        {% endfor %}
      </div>
    </div>
  </div>

  <!-- ROW 3: Phase Profile + Movement Strategy -->
  <div class="two-col">
    <div class="panel">
      <div class="panel-title">Phase Profile</div>
      <div class="phase-cols">
        <div>
          <div class="phase-col-title">Braking</div>
          <span class="ph-badge {{ a.phase_braking.badge_css }}">{{ a.phase_braking.status }}</span>
          {% for pm in a.phase_braking.metrics %}
          <div class="phase-metric">
            <span class="phase-metric-name">{{ pm.label }}</span>
            <span class="phase-metric-value">
              {% if pm.value is not none %}{{ "%.1f" | format(pm.value) }}{% else %}&mdash;{% endif %}
            </span>
          </div>
          {% endfor %}
        </div>
        <div>
          <div class="phase-col-title">Propulsive</div>
          <span class="ph-badge {{ a.phase_propulsive.badge_css }}">{{ a.phase_propulsive.status }}</span>
          {% for pm in a.phase_propulsive.metrics %}
          <div class="phase-metric">
            <span class="phase-metric-name">{{ pm.label }}</span>
            <span class="phase-metric-value">
              {% if pm.value is not none %}{{ "%.1f" | format(pm.value) }}{% else %}&mdash;{% endif %}
            </span>
          </div>
          {% endfor %}
        </div>
        <div>
          <div class="phase-col-title">Landing</div>
          <span class="ph-badge {{ a.phase_landing.badge_css }}">{{ a.phase_landing.status }}</span>
          {% for pm in a.phase_landing.metrics %}
          <div class="phase-metric">
            <span class="phase-metric-name">{{ pm.label }}</span>
            <span class="phase-metric-value">
              {% if pm.value is not none %}{{ "%.1f" | format(pm.value) }}{% else %}&mdash;{% endif %}
            </span>
          </div>
          {% endfor %}
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-title">Movement Strategy</div>
      <div class="movement-label">{{ a.movement_type }}</div>
      <div class="movement-desc">{{ a.movement_desc }}</div>
      <div class="movement-stats">
        <div>
          <div class="movement-stat-label">Ecc Duration</div>
          <div class="movement-stat-value">
            {% if a.ecc_duration is not none %}{{ "%.0f" | format(a.ecc_duration * 1000) }} ms{% else %}&mdash;{% endif %}
          </div>
        </div>
        <div>
          <div class="movement-stat-label">CM Depth</div>
          <div class="movement-stat-value">
            {% if a.cm_depth is not none %}{{ "%.1f" | format(a.cm_depth | abs) }} cm{% else %}&mdash;{% endif %}
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ROW 4: Key Metrics -->
  <div class="panel">
    <div class="panel-title">Key Metrics</div>
    <div class="key-metrics-grid">
      {% for m in a.key_metrics %}
      <div class="km-cell">
        <div class="km-label">{{ m.label }}</div>
        <div class="km-value">
          {% if m.value is not none %}
            {% if m.label in ["RSI-modified", "FT:CT"] %}{{ "%.2f" | format(m.value) }}{% else %}{{ "%.1f" | format(m.value) }}{% endif %}
          {% else %}&mdash;{% endif %}
        </div>
        {% if m.unit %}<div class="km-unit">{{ m.unit }}</div>{% endif %}
      </div>
      {% endfor %}
    </div>
  </div>

</div>
```

Note: The key-metrics-grid should be `grid-template-columns: repeat(5, 1fr)` for the 2×5 layout.

```css
.key-metrics-grid {
  display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px;
}
@media (max-width: 800px) { .key-metrics-grid { grid-template-columns: repeat(2, 1fr); } }
```

The trend strip in the right column uses a vertical stack:

```css
.trend-strip-vertical {
  display: flex; flex-direction: column; gap: 8px;
}
```

- [ ] **Step 3: Run full test suite**

```bash
python -m pytest tests/test_html_dashboard.py -v
```

Expected: all PASS. Key assertions to verify:
- `test_render_dashboard_creates_file`: "Test Player" in html, "roster-view" in html, "ELITE CONCENTRIC" in html
- `test_render_dashboard_empty_db`: "No data" in html

- [ ] **Step 4: Commit**

```bash
git add src/report/templates/dashboard.html.j2
git commit -m "feat: rewrite profile view with action-first layout and Baylor styling"
```

---

### Task 7: Generate Report and Visual Verification

**Files:**
- No code changes — verification only

- [ ] **Step 1: Run full test suite**

```bash
python -m pytest -v
```

Expected: all 114+ tests PASS (original 114 + new tests from Tasks 3-4)

- [ ] **Step 2: Generate new dashboard from existing DB**

```bash
python run_pipeline.py --report-only
```

Expected: Opens `reports/2026-03-22_team_dashboard.html` in browser. Verify:
- Baylor green background
- Gold "BU" logo + "BAYLOR FOOTBALL" header
- Position-grouped roster (DBs together, WRs together, etc.)
- Gold metric values on cards
- Pulsing red dots on flagged athletes
- Clicking a card opens the action-first profile view
- Prescription + strengths/weaknesses at top of profile
- Radar chart with gold polygon and value labels
- Filter tabs hide/show cards and empty position groups
- Sort works within each position group

- [ ] **Step 3: Commit any final fixes**

```bash
git add -A
git commit -m "fix: address visual verification issues in Baylor dashboard"
```

Only if Step 2 revealed issues that need fixing.
