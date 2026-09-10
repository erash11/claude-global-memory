# The Monitor — transferred project context

Carried over from the Claude cloud project, Sept 2026. The repo root `CLAUDE.md` is the
operational instruction file and takes precedence for build details.

## What it is

"The Monitor" is a biweekly internal newsletter communicating the Applied Performance
department's work, methods, and value.

Audience is mixed: coaches, athletic administrators, and support staff. Not uniformly
technical, and that shapes every writing decision here.

## People

Eric Rash (Director of Applied Performance). Kenny Boyd is supervisor. Blake Wright is
the embedded PhD student leading B.A.I.R. research. Chris Ruf, Danny Davis, and
Dr. Andrew Gallucci are regular figures.

B.A.I.R. bridges Baylor's R1 research mission with athletic performance support across
14 varsity sports.

## Voice and attribution

Written in department voice ("we"). Signed "Baylor Applied Performance / B.A.I.R.
Initiative", never under Eric's name personally.

This was a deliberate correction: early drafts in first person were rejected, and "we"
is now the established standard.

## Writing rules (strict)

- No em dashes
- No corporate jargon
- Plain language throughout, non-negotiable even for technical topics, because the
  audience is mixed
- Department voice at all times

## Visual identity

Baylor brand system: green `#154734`, gold `#FFB81C`, warm paper background `#faf8f3`.
Editorial and magazine in feel, with a lab-report undertone. Typography is Fraunces
serif, IBM Plex Sans, JetBrains Mono.

Distribution is HTML email plus a PDF archive.

## Template system

One shared HTML scaffold with Jinja-style tokens, plus a section snippets library,
driven by two markdown input files (one per template type).

**Template A, "The People Issue"** (1st of the month): Staff Spotlight, From the Field,
Conference & Development, What's Next.

**Template B, "The Methods Issue"** (2nd of the month): Under the Hood, Tool of the
Trade, Research Corner, What's Next.

## Content workflow

Eric fills in bullet points and short answers in the markdown input files. Claude
generates polished prose from those inputs. The markdown files are the primary editorial
interface; do not bypass them.

## Deliverable package

`CLAUDE.md` (operational instructions), `SPEC.md` (full project spec),
`issue_template.html`, `section_snippets.html`, two markdown input files, `README.md`.
