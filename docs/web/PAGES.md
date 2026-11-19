# Groundstate web pages

Status: draft v1, from `design/Website_v3.pdf` plus Mico's v3 notes. Coordinates are in `DESIGN.md` section 4. All routes are hash routes (`#/...`) so the site works on any static host with no server rules.

## Domain registry (single source: `src/content/domains.ts`)
Status drives color, panel type, and icon. Order is fixed.

| Order | id | Label | Status | Children |
|---|---|---|---|---|
| 1 | `batteries` | Batteries | active | `cathodes` (active), `electrolytes` (planned) |
| 2 | `supercapacitors` | Supercapacitors | planned | none |
| 3 | `solar-absorbers` | Solar Absorbers | planned | none |
| 4 | `hydrogen-storage` | Hydrogen Storage | planned | none |
| 5 | `catalysts` | Catalysts | planned | none |
| 6 | `thermoelectrics` | Thermoelectrics | exploring | none |
| 7 | `wind-energy` | Wind Energy | exploring | none |
| 8 | `hydro-energy` | Hydro Energy | exploring | none |
| 9 | `geothermal-energy` | Geothermal Energy | exploring | none |

Panel by status: active leaf = content panel (green). Planned = orange panel, lightbulb icon, text `Oops! This domain is currently being planned!`. Exploring = gray panel, `?` icon, text `The team is currently exploring ideas for this domain!` (wireframe wording, kept verbatim, see A-5).

## Routes
`#/` Landing. `#/about`. `#/contacts`. `#/disclaimer`. `#/explore`. `#/explore/<domain>`. `#/explore/<domain>/<child>`. Unknown route: show Landing and nothing else (no 404 page).

## P1 Landing (`#/`)
No top nav. Centered column. Wireframe frame 1.
```
+------------------------------------------------+
|                                                |
|                 [logo mark]      y 23%-42%     |
|              [Groundstate wordmark] y 45%-56%  |
|                 Explore →        y 58%-62%     |
|                                                |
|        ABOUT | CONTACTS | DISCLAIMER y 86%-89% |
+------------------------------------------------+
```
`Explore →` links to `#/explore`, green. Footer links are green, uppercase, underlined, centered, `|` separators. Mark and wordmark are image assets (not live text).

## P2 About (`#/about`), frame 2
Top nav. Title row `← | About`. Text column holds copy slot `about` (justified paragraphs). Nothing else on the page.

## P3 Contacts (`#/contacts`), frame 3
Top nav. Title row `← | Contacts`. One row of six square tiles, order: X (bird glyph as drawn), Instagram, YouTube, TikTok, GitHub, Email. Each tile is one link with an accessible name (`GitHub`, not `link`). URLs and the mailto address come from `src/content/contacts.ts`, supplied by Mico. Never invent a handle or address. A tile with no URL renders unlinked and the build prints `UNSET`; deploy is blocked while any tile is `UNSET` unless Mico removes it.

## P4 Disclaimer (`#/disclaimer`), frame 4
Top nav. Title row `← | Disclaimer`. Warning-triangle icon centered above the text column. Copy slot `disclaimer`, then a last line `Disclaimer version <n>` taken from the copy file's `version` field. The `disclaimer_version` on candidate JSON must match it (see `gs-web-data-view`).

## P5 Explore index (`#/explore`), frame 5
Top nav. Title row `← | Explore`. Green rail on the left, domain list beside it in registry order, each row `Label ›`. Nothing is selected, so nothing is dimmed and no panel shows.

## P6 Batteries flyout (`#/explore/batteries`), frame 6
Selecting Batteries sets its chevron to `‹` and opens the flyout to its right: `Cathodes ›` and `Electrolytes`. Other rows stay normal, no dimming (D-011 DECIDED 2026-10-22, option B; the selected row is marked by `‹` and an underline, see DESIGN.md).

## P7 Cathodes panel (`#/explore/batteries/cathodes`), frame 7
The list shows `Cathodes ‹` and `Electrolytes`. The green content panel fills the right side and scrolls inside itself. Contents, top to bottom (structure DECIDED, D-012 option A, 2026-10-22):
1. Intro paragraph (copy slot `cathodes.intro`).
2. Benchmark: table of the three benchmark cathodes. Columns: material, predicted V, reference V, difference V, reference citation.
3. Candidates: table. Columns: formula, material id, predicted voltage (V), capacity (mAh/g), energy above hull (eV/atom), audit status, citations.
4. Method: short copy (slot `cathodes.method`).
5. One closing line stating values are computational estimates, the run id, and the disclaimer version.
Empty states (results are empty until M4): `No candidates have passed audit yet.` and `Benchmark has not been run yet.` Plain text inside the table region.
Data rules live in `gs-web-data-view`.

## P8 Planned panel, frame 8
Any planned domain or child (including Electrolytes). Orange panel, off-white pixel lightbulb, message below the icon.

## P9 Exploring panel, frame 9
Any exploring domain. Gray panel, off-white pixel `?`, message below the icon.

## Interaction (all instant, no animation)
- Selection state lives in the URL hash. Back button works. Deep links work.
- Click or Enter on a row selects it. Rows are real links or buttons, reachable by Tab, in list order. Hover does not open anything. (Amended 2026-11-02 per Mico's W-002 delta-audit disposition: "or Space" removed — rows are native links and Space does not activate them; Enter does, recorded as accepted.)
- `←` goes to Home on every sub-page.

## Assumptions to confirm (Mico)
- A-1 `›` shows on every domain row, because every row opens a panel. The wireframe drew it only on Batteries, Supercapacitors, Thermoelectrics; your v3 note says same-status domains get the same panels.
- A-2 Click opens the flyout; hover does not (works on touch and keyboard).
- A-3 `←` always routes Home.
- A-4 `Hydro Storage` is built as `Hydrogen Storage`, per your note that it is a typo.
- A-5 Exploring message says "The team", which reads as an organization. Kept verbatim; consider "Groundstate is" or "I am" to match the independent-enthusiast framing.
- A-6 Contact icons are inconsistent in the wireframe (line-art green for X, Instagram, YouTube, Mail; black fill for GitHub and TikTok). Supply one consistent set, or approve a redraw in a single style.
- A-7 Disclaimer carries a visible version line so candidate data can be matched to the wording it was published under.
