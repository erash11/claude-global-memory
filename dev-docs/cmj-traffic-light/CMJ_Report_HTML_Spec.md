# CMJ Traffic Light Report — HTML Template Spec

**Purpose:** This is the visual and functional specification for the HTML report that `generate_report.py` produces. Claude Code should use this document to build the Jinja2 template (`templates/report_template.html`) so the production output matches the approved mockup exactly.

**Reference file:** `cmj_report.html` (mockup, included in repo root)

---

## Constraint: Self-Contained HTML

The final report is a single `.html` file with all CSS and JavaScript inline. No external stylesheets, no CDN links, no separate JS files. It must open and function correctly in any modern browser with no internet connection. This is non-negotiable because the file gets emailed as an attachment.

**Font handling for production:** The mockup loads Google Fonts (DM Sans, Bebas Neue) via CDN. The production template should embed a `@font-face` fallback stack so the report still looks good offline. Use this stack:

```css
font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
/* For display/heading elements: */
font-family: 'Bebas Neue', Impact, 'Arial Narrow', sans-serif;
```

If you can base64-encode the font files inline, do it. If the file size gets too large (over 500KB for fonts alone), use the fallback stack only and skip the embed.

---

## Color System

Every color in the report is defined as a CSS custom property on `:root`. The Jinja2 template must preserve this exact palette.

```css
:root {
  /* Baylor brand */
  --baylor-green: #003015;
  --baylor-gold: #FFB81C;

  /* Background layers (dark theme) */
  --bg: #0A0F0D;
  --surface: #111916;
  --surface-2: #182420;
  --border: #1E2E28;

  /* Text */
  --text: #E8EDE9;
  --text-muted: #7A8E82;

  /* Traffic light: Green */
  --green: #22C55E;
  --green-bg: rgba(34,197,94,0.08);
  --green-border: rgba(34,197,94,0.2);

  /* Traffic light: Yellow */
  --yellow: #FACC15;
  --yellow-bg: rgba(250,204,21,0.08);
  --yellow-border: rgba(250,204,21,0.2);

  /* Traffic light: Red */
  --red: #EF4444;
  --red-bg: rgba(239,68,68,0.08);
  --red-border: rgba(239,68,68,0.2);
}
```

Each traffic light color has three variants: the solid color (for text and indicator dots), a translucent background tint (8% opacity, used for card/pill backgrounds), and a translucent border (20% opacity). This creates the layered glow effect throughout the report.

---

## Layout Sections (Top to Bottom)

### 1. Header

A full-width bar with a gradient background fading from `--baylor-green` at the top to `--bg` at the bottom. Contains a subtle radial gold glow in the upper right corner (decorative only, done with a `::before` pseudo-element).

**Left side:**
- Logo block: 42x42px square with `--baylor-gold` background, rounded 8px corners, containing "BU" in Bebas Neue at 22px, colored `--baylor-green`
- Title: "CMJ Fatigue Traffic Light Report" in Bebas Neue, 28px, `--baylor-gold`, letter-spacing 2px
- Subtitle: "Baylor Volleyball — Applied Performance" in 12px, `--text-muted`

**Right side (metadata):**
- Three items separated by 24px gaps, each preceded by a small gold dot (4px circle)
- Item 1: Session date (e.g., "February 18, 2025")
- Item 2: Session label (e.g., "Post-Practice Assessment")
- Item 3: Data source ("ForceDecks")

**Jinja2 variables needed:** `{{ report_date }}`, `{{ session_label }}`, `{{ data_source }}`

### 2. Summary Bar

A horizontal bar with `--surface` background containing three equally-sized cards. Each card shows the count of athletes in that traffic light zone.

Each card contains:
- A circular icon (44x44px, border-radius 50%) with the zone's background/border tint and a symbol: checkmark (✓) for green, exclamation (!) for yellow, X mark (✕) for red
- A label in 12px uppercase with 1px letter-spacing (e.g., "GREEN — FULL GO")
- A count in Bebas Neue at 26px, colored with the zone's solid color

**Jinja2 variables needed:** `{{ green_count }}`, `{{ yellow_count }}`, `{{ red_count }}`

### 3. Athlete Grid

The main content area. Each athlete is rendered as a row. Rows are stacked vertically with 10px gaps. Each row has a staggered fade-in animation (40ms delay per row).

#### Collapsed Row (default state)

A three-column grid: `260px | 1fr | 300px`

**Column 1 — Athlete Identity:**
- Traffic light dot: 14px circle, solid fill matching overall color, with a `box-shadow: 0 0 8px` glow in the same color
- Name: "#[number] [name]" in 15px, font-weight 600
- Position: below name in 12px, `--text-muted`

**Column 2 — Metric Pills:**
- A flex-wrap row of six small pills, one per metric
- Each pill shows the metric short label and the percent change value
- Pill styling: 6px 12px padding, 6px border-radius, 12px font size, colored background/border/text matching that metric's individual color assignment
- Percent change values show a "+" prefix for positive values, no prefix for negative. One decimal place always.

**Column 3 — Status:**
- Status badge: pill-shaped (20px border-radius), 11px uppercase bold text with 1px letter-spacing, colored per overall zone
- Green badge text: "Full Go"
- Yellow badge text: "Modified"
- Red badge text: "Restricted"
- Short description text in 12px `--text-muted` next to the badge: "No restrictions" / "Reduce max-effort jumps" / "Recovery-focused only"

**Hover state:** Border color shifts to `rgba(255,184,28,0.25)` with a faint gold outer glow.

#### Expanded Row (toggled on click)

When clicked, the row gets an `expanded` class and reveals a detail panel spanning all three columns below the main row content.

**Left half — Detail Metric Cards:**
A 3-column sub-grid of six cards (one per metric). Each card contains:
- Metric full label in 11px uppercase `--text-muted` (e.g., "Jump Height", "RSI-modified")
- Pre → Post values with units (e.g., "28.4 cm → 27.6 cm")
- Percent change in the metric's color, bold, with +/- sign

**Right half — Practice Recommendations:**
- Heading: "PRACTICE RECOMMENDATIONS" in Bebas Neue, 15px, `--baylor-gold`, 1.5px letter-spacing
- List of action items, each prefixed with a gold arrow character (→)
- Items are separated by 1px `--border` bottom borders
- Content is pulled from config based on the athlete's overall color

**Jinja2 loop structure:**
```
{% for athlete in athletes %}
  <!-- render collapsed row with athlete.name, athlete.number, athlete.position -->
  <!-- render metric pills from athlete.metrics dict -->
  <!-- render status badge from athlete.overall_color -->
  <!-- render expandable detail panel -->
{% endfor %}
```

**Data shape the template expects per athlete:**
```python
{
    "name": "Avery Mitchell",
    "number": "4",
    "position": "Outside Hitter",
    "overall_color": "green",           # "green", "yellow", or "red"
    "status_label": "Full Go",          # from config recommendations
    "status_short": "No restrictions",  # from config recommendations
    "recommendations": [                # list of strings from config
        "Full practice participation, no restrictions",
        "Normal jump volume and intensity permitted",
        ...
    ],
    "metrics": [                        # ordered list, one per metric
        {
            "key": "jump_height",
            "short_label": "Jump Ht",
            "full_label": "Jump Height",
            "unit": "cm",
            "pre_value": 28.4,
            "post_value": 27.6,
            "pct_change": -2.8,
            "color": "green"            # individual metric color
        },
        ...
    ]
}
```

### 4. Legend Section

A rounded card (`--surface` background, `--border` border, 12px radius) containing threshold reference information.

**Title:** "THRESHOLD REFERENCE" in Bebas Neue, 15px, `--text-muted`, 1.5px letter-spacing

**Three-column grid** with one column per zone:

Each column has:
- A small colored dot (10px circle)
- Zone label in 13px bold, colored per zone (e.g., "Green — Full Participation")
- Description in 12px `--text-muted` explaining the criteria

**Legend text (hardcoded or from config):**
- Green: "Fatigue within expected training response. Force production and jump strategy preserved. 0-1 metrics outside green range."
- Yellow: "Manageable fatigue present. Early changes in jump strategy or force expression. 2-3 metrics in yellow or 1 red metric."
- Red: "Significant neuromuscular fatigue. Suppressed force production and slower movement strategy. 2+ red metrics or 3+ metrics at yellow or above."

### 5. Footer

Centered text in 11px `--text-muted` with a top border:

"Baylor Athletics Applied Performance | B.A.I.R. Initiative | Green = Go · Yellow = Be Smart · Red = Protect Tomorrow"

---

## Interactive Behavior (JavaScript)

The only interactive behavior is click-to-expand on athlete rows. This must work with inline JavaScript since the file is self-contained.

**Implementation:**
- Each `.athlete-row` has a click event listener
- Clicking toggles the CSS class `expanded` on that row
- The `.athlete-detail` div inside the row is hidden by default (`display: none`) and shown when the parent has the `expanded` class (`display: block`)
- The expanded row gets a brighter gold border (`rgba(255,184,28,0.35)`)
- Only one behavior needed. No accordion (multiple rows can be open simultaneously).

**Animation:**
- Each athlete row fades in on page load with a `fadeUp` keyframe animation (opacity 0 to 1, translateY 12px to 0, 0.4s ease)
- Rows are staggered by 40ms using `animation-delay` based on their index

---

## Responsive Breakpoints

The report should function on tablets (coaching staff may open the email on an iPad).

**At 1100px and below:**
- Athlete row grid collapses to two columns: `220px | 1fr`
- Status section moves to a new row spanning full width, with a top border instead of left border
- Detail metric sub-grid becomes 2 columns instead of 3

**At 768px and below:**
- Athlete row grid becomes single column
- Athlete identity section gets a bottom border instead of right border
- Summary bar stacks vertically
- Legend grid becomes single column
- Detail grid (metrics + recommendations) becomes single column
- Detail metric sub-grid stays at 2 columns
- Horizontal padding reduces from 40px to 20px

---

## Print Styles

Add a `@media print` block that:
- Forces white background, dark text
- Expands all athlete rows (remove `display: none` on detail panels)
- Removes hover effects and animations
- Hides the "Click to expand" instruction text
- Sets all traffic light colors to print-safe versions (ensure contrast on white)

---

## Unpaired Athletes

If an athlete has pre-practice data but no post-practice data (or vice versa), they cannot be scored. The template should handle this with a separate section below the main grid:

- Section title: "UNPAIRED TESTS" in the same style as other section titles
- Each unpaired athlete shown as a muted row with their name, position, and a note: "Missing [pre/post] test data — excluded from analysis"
- No traffic light, no metrics, no recommendations

**Jinja2 variable:** `{{ unpaired_athletes }}` (list of dicts with `name`, `number`, `position`, `missing` field)

---

## File the Template Expects from Python

The `generate_report.py` script should call Jinja2 with a context dict shaped like this:

```python
context = {
    "report_date": "February 18, 2025",
    "session_label": "Post-Practice Assessment",
    "data_source": "ForceDecks",
    "green_count": 8,
    "yellow_count": 4,
    "red_count": 2,
    "athletes": [ ... ],           # list of athlete dicts (see shape above)
    "unpaired_athletes": [ ... ],  # list of unpaired athlete dicts
    "legend": {                    # from config
        "green": { "label": "...", "description": "..." },
        "yellow": { "label": "...", "description": "..." },
        "red": { "label": "...", "description": "..." },
    },
    "footer_text": "Baylor Athletics Applied Performance | B.A.I.R. Initiative | Green = Go · Yellow = Be Smart · Red = Protect Tomorrow"
}
```
