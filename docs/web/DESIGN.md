# Groundstate web design spec

Status: draft v1, derived from `design/Website_v3.pdf` (9 frames, 1024.5 x 576 pt). Values below were measured from the PDF, not eyeballed. Decided 2026-10-22: D-011 option B (set B text tokens, set A fills and rail, no dimming) and D-010 option D (original Dot Mincho 16 if a self-hostable release exists; fallback stack and `font: provisional` until the license is verified and the woff2 lands).

## 1. Intent
An old-school terminal, but cozy and natural rather than cold: off-white "paper", pixel greens, a pixel-art logo, a monospace-feeling pixel font. Flat, hard-edged, instant. If a choice is not covered here, pick the plainer, flatter, more terminal-like option and note it in the worklog.

## 2. Color tokens
Wireframe values are set A; set B is the AA-safe alternative. **DECIDED (D-011, 2026-10-22): option B — text uses the set B tokens; fills, rail, and backgrounds keep set A. No dimming (see the dimming note below).** Tokens stay in one CSS file so a future change remains a one-file change.

| Token | A (wireframe) | B (AA-safe) | Use |
|---|---|---|---|
| `--paper` | `#f9faf5` | same | page background; also text on filled panels |
| `--green` | `#4f9e58` | same | fills (panel, rail), underlines, icons |
| `--green-text` | `#4f9e58` | `#3a8045` | nav, title row, small text in green |
| `--ink-green` | `#083529` | same | icon tiles, scrollbar track, focus outline |
| `--ink` | `#000000` | same | body paragraphs |
| `--orange` | `#f29d64` | same | "planned" panel fill |
| `--orange-text` | `#f29557` | `#b0541a` | "planned" domain labels |
| `--gray` | `#a6a6a6` | same | "exploring" panel fill |
| `--gray-text` | `#a6a6a6` | `#6f6f6f` | "exploring" domain labels |
| `--dim-green` | `#8bbe90` | same | non-selected rows while a panel is open |
| `--dim-orange` | `#f6dbc5` | same | same, planned rows |
| `--dim-gray` | `#dfe0dd` | same | same, exploring rows |

Only these colors may appear in shipped CSS. No opacity-based dimming (use the dim tokens), no gradients, no shadows, no alpha overlays.

Dimming: the wireframe fades every non-selected Explore row while a panel is open. Under set A, do that with the `--dim-*` tokens. Under set B, do not dim: non-selected rows keep their normal text color, and the selected row is marked by `‹` and an underline. The dim tokens are then unused.

Measured contrast of set A (WCAG): green on paper 3.15, orange text on paper 2.17, gray text on paper 2.32, paper on green panel 3.3, paper on orange panel 2.05, paper on gray panel 2.32, orange text on green flyout 1.45, dimmed rows about 1.26 to 2.0. Black on paper is 20.0. Set B text colors measure: green 4.6, orange 4.85, gray 4.79. Option B2 for panels: ink-green text on the orange fill measures 6.3, on gray 5.56. See D-011. D-011 is DECIDED (2026-10-22): option B.

## 3. Type
- One family via `--font`, self-hosted woff2, Latin subset, `font-display: swap`. Fallback stack ends in `ui-monospace, monospace`. D-010 is DECIDED (option D, 2026-10-22): use the fallback stack only until the Dot Mincho 16 license is verified and the subset woff2 sits in `public/fonts`; mark `font: provisional` in the worklog until then.
- Never load fonts from a third-party host. Never extract or reuse the font embedded in the PDF (Canva's `DotMincho16Std`; license for web use unknown, treat as not usable).
- If a pixel font is chosen, use sizes that are multiples of its design grid (16 px grid: 16, 32) for crisp edges.
- Sizes (desktop, starting points): nav 16 px, title row 24 px, body 18 px, line-height 1.7, table text 16 px.
- Body paragraphs are **justified** in the wireframe. Keep `text-align: justify` for About, Disclaimer, and panel intros.
- Nav and footer links are uppercase. Titles and domain names are Title Case.

## 4. Layout (reference frame 1024 x 576, values in % of frame)
- **Top nav** (all pages except Landing): text at x 1.2%, y 1.7% to 4.4%. Text: `HOME | EXPLORE | ABOUT | CONTACTS | DISCLAIMER`, green, no underline, `|` separators in green. Underline on hover and focus only.
- **Title row**: x 5.6%, y about 16%. Format: `← | Title`. `←` is a link to Home.
- **Text column** (About, Disclaimer): left 11%, width 77.5%.
- **Explore rail**: vertical rule 5 pt wide (0.5%), x 8.6%, y 22.5% to 94.8% (height 72%), color `--green`.
- **Explore list**: x 10.7%, rows spaced 9.5% of frame height (about 55 pt).
- **Flyout** (Batteries submenu): green fill, starts right of the Batteries row, about 24% wide, 2 rows.
- **Content panel** (Cathodes): x 22.2% to 94.5%, y 26% to 94.8%.
- **Placeholder panel** (planned/exploring): x 28.9% to 94.4%, y 27.4% to 94.4%. Icon centered, text centered under it.
- **Contact tiles**: 6 tiles, 13.3% wide each, 1.9% gap, first tile at x 5.6%, tops at y 37.3%. Tile fill `--ink-green`. All six tiles must sit on one baseline (the wireframe has 2 to 4 pt of hand-placement jitter; do not reproduce it).
Layout is fluid with `max-width: 1200px`, centered. No fixed pixel positioning.

## 5. Components
| Component | Rule |
|---|---|
| Link | Green text. Hover and focus: underline. Focus also gets a 2 px `--ink-green` outline. Instant. |
| Domain row | Label plus `›` (collapsed) or `‹` (open). Color by status: active green, planned orange, exploring gray. Status is also exposed as text (visually hidden `, active` / `, planned` / `, exploring`). |
| Flyout | Green fill, `--paper` text, rows `Cathodes ›` and `Electrolytes`. Electrolytes is planned status. |
| Panel | Flat fill, no border radius, no border, internal scroll when content is taller than the panel. |
| Scrollbar | `scrollbar-color: --paper --ink-green` (thumb, track). No custom JS scrollbars. |
| Table | 1 px `--paper` grid lines on the green panel, no zebra, no hover color. |
| Pixel images | `image-rendering: pixelated`, integer scale only, never blurred. Prefer SVG made of `<rect>`s with `shape-rendering: crispEdges`. |

## 6. Hard rules (machine-checked by `npm run check:look`, re-run by the Auditor)
- R1 No `transition`, `animation`, `@keyframes`, `scroll-behavior: smooth`, `will-change`, or JS-driven motion (`requestAnimationFrame` loops, `setInterval` for visuals) in `src/` or `dist/`.
- R2 No `border-radius` (except `0`), `box-shadow`, `text-shadow`, `filter`, `backdrop-filter`, gradient functions, `opacity` below 1 on text.
- R3 Every color literal in shipped CSS is in the token table above.
- R4 Exactly one font family token. All font files local. No `fonts.googleapis.com` or any third-party font URL anywhere.
- R5 No third-party runtime requests. Every `http(s)://` string in `dist/` is either the site's own domain or an outbound link in copy (contacts, citations), and is listed in `web/links.allow.txt`.
- R6 All pixel images carry `image-rendering: pixelated` or are crisp-edges SVG.
- R7 No UI framework, CSS framework, icon library, animation library, or analytics package in `package.json` (see `docs/web/SCAFFOLD.md` allowlist).
- R8 No `lorem ipsum` and no `TODO`/`DRAFT` copy strings in `dist/`.
- R9 Nav string, title-row format, and domain list order match `docs/web/PAGES.md` exactly.
- R10 Contrast. Under set B every text/background pair meets 4.5 (3.0 for text of 24 px or larger and for UI graphics). Under set A the check still runs and prints every failing pair as a known failure instead of failing the build, so the look stays exact while the cost stays visible.
- R11 Size budgets (section 8) hold.

## 7. Responsive (the wireframe is desktop only; these are defaults, Mico may change them)
- Below 900 px: tiles wrap to 3 per row; panel moves below the Explore list instead of beside it; text column widens to 90%.
- Below 560 px: tiles 2 per row; top nav wraps onto two lines. No hamburger menu (removed in v3 on purpose).

## 8. Accessibility and budgets
- Semantic HTML: `nav`, `main`, one `h1` per page, real `table` with `th`, `lang="en"`. Alt text on logo and every icon. Keyboard reachable everywhere, visible focus. Color never the only carrier of status.
- Budgets (proposed, Mico may adjust): initial JS 100 KB gzip, CSS 10 KB gzip, fonts 60 KB total, any single image 20 KB, first load excluding fonts 250 KB gzip.
