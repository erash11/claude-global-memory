# KeystoneOS Dashboard Design

## Purpose

The dashboard brings KeystoneOS to the surface as a daily operating screen. It should make active work, project state, graph availability, handoffs, and next actions visible without replacing the underlying command-line workflows.

## Approach

Add a `dashboard` command to `scripts/keystone.ps1`. The command reads the existing project registry, git summaries, latest handoff, latest intake, memory source summaries, and Graphify outputs, then writes a static local dashboard under `outputs/dashboard/`.

The MVP is generated HTML plus JSON data:

- `outputs/dashboard/index.html` is the visual surface.
- `outputs/dashboard/dashboard-data.json` is the machine-readable state packet.
- `outputs/dashboard/projects/<ProjectKey>.html` is the focused launch packet for one workstream.

No server is required. The file can be opened directly in a browser or linked from the morning routine.

## Screen Layout

The first viewport should be a compact workstation cockpit:

- Today: generated time, active project count, dirty repo count, latest handoff, latest intake.
- Project Switcher: one row/card per active project with status, git state, path, and suggested commands.
- Knowledge Map: Graphify availability, nodes, edges, communities, graph HTML/report links, Obsidian export path.
- Agent Launch Packet: project-specific resume/start/memory commands that work across Codex, Claude Code, and Gemini.
- Inbox/Triage: latest intake and handoff pointers.

Project launch packet pages should include project state, command snippets, startup checks, graph links, latest handoff, latest intake, and a link back to the main dashboard.

## Boundaries

- Do not create a full web app yet.
- Do not duplicate project source files into KeystoneOS.
- Do not require npm, a local server, or browser automation to generate the dashboard.
- Keep generated dashboard outputs ignored by git.

## Verification

- Add a fixture test proving `dashboard` writes `index.html` and `dashboard-data.json`.
- Assert the dashboard includes project names, git state, graph stats, commands, latest handoff, and latest intake.
- Assert each project page includes the project key, startup checks, launch commands, graph links, and handoff context.
- Run existing KeystoneOS tests to prove no command regressions.
