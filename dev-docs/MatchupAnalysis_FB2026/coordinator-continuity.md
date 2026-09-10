# Coordinator continuity — whose 2025 tape to read

A team that hired a new coordinator does not run its old scheme any more. When the
routine falls back to 2025 data, using the opponent's own 2025 numbers is wrong for any
side of the ball that changed hands. Read the coordinator's 2025 team instead.

This is the logic the Week 1 Auburn analysis already used for Baylor: Joe Klanderman
came from Kansas State, so Kansas State's 2025 defense predicted Baylor's 2026 defense
better than Baylor's own 2025 numbers under Matt Powledge.

Reference file: `~/DEV/CFB_Victory_Model/matchup/coordinators_2026.json`
Researched and web-verified 2026-09-05. Re-verify if a coordinator is fired in-season
or play-calling changes hands.

## Where each side of the ball points

| Team | Offense reads | Defense reads | What changed |
|---|---|---|---|
| Auburn | **South Florida 2025** | Auburn 2025 | New HC Golesh, OC Joel Gordon followed from USF. Durkin retained on defense. |
| Prairie View A&M | Prairie View 2025 | Prairie View 2025 | No change. FCS, so data is thin regardless. |
| Louisiana Tech | Louisiana Tech 2025 *(partial)* | Louisiana Tech 2025 | Nathan Young promoted internally after Franklin retired. Expect more run-oriented. |
| Colorado | **Sacramento State 2025** *(partial)* | Colorado 2025 *(partial)* | Brennan Marion brings the Go-Go from Sac State. Marve promoted internally but was Va Tech's DC 22-24. |
| Arizona State | Arizona State 2025 | Arizona State 2025 | No change. Dillingham may take a larger play-calling role. |
| TCU | **UConn 2025** | TCU 2025 | Gordon Sammis hired from UConn after Briles left for South Carolina. |
| Kansas | **Penn State 2025** | Kansas 2025 | Kotelnicki returns from Penn State. He also ran KU's offense 2021-23. |
| UCF | UCF 2025 | UCF 2025 | No change. Frost may be the real play caller on offense. |
| Iowa State | **no proxy exists** | **Washington State 2025** | Full turnover. Rogers from WSU with DC Bobbit. OC Roehl was in the NFL in 2025. |
| BYU | BYU 2025 | BYU 2025 *(partial)* | Poppinga promoted internally after Hill left for Michigan; says he carries over much of Hill's system. |
| Texas Tech | Texas Tech 2025 | Texas Tech 2025 | No change. Both extended through 2028. |
| Houston | Houston 2025 | Houston 2025 | No change. |
| **Baylor** | Baylor 2025 | **Kansas State 2025** | Spavital unchanged, 3rd year. Klanderman in from K-State; Aranda has given up defensive play-calling. |

Bold means the proxy is a different team, so the script pulls that team's 2025 data.

## Proxy quality
- **direct** — clean read, same coordinator running his own scheme somewhere else.
- **partial** — expect scheme drift. Internal promotions and coordinators with a
  different scheme history land here. Hedge the language.
- **none** — no usable college proxy. Iowa State's OC was in the NFL in 2025. Describe
  the background qualitatively and attach no rates to it.

## How the script uses it
`scheme_proxies()` builds a `scheme_reference` block into every bundle, naming the
coordinator, whether he is new, who calls plays, and which team's 2025 data applies per
side. When `basis` is `"2025"` and a proxy is a different team, the script also pulls
that team's 2025 season stats, advanced stats and last two GameOnPaper games into a
`proxy_2025` block.

When `basis` is `"2026"` the proxy pull is skipped deliberately: the team's own 2026
games already show the new coordinator's scheme. `scheme_reference` still rides along so
the doc can name the coordinator and flag a first-year scheme on a small sample.

An FCS proxy such as Sacramento State returns empty CFBD advanced stats. The script
writes a `warning` on that proxy entry and the doc is instructed to lean on the
GameOnPaper boxes and scheme description rather than invent rates.

## Cost
Two proxy teams at 3 CFBD calls each is the normal case, so a Monday run with proxies is
about 21 calls instead of 15. Only happens while `basis` is 2025, roughly the first
three or four weeks.

## Maintenance
If a coordinator is fired or play-calling shifts mid-season, edit
`coordinators_2026.json` directly. The script reads it fresh on every run, so no code
change is needed.
