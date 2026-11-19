# Asset manifest — web/public/assets/ (+ public/fonts/)

Every shipped asset with its source, author, license, date, derivation, and
FINAL/STOPGAP status. Rule (gs-web-assets): an asset with no source record
cannot ship. Sources are Mico's originals in `docs/web/design/assets-src/`
(FINAL tier); the extracted stopgaps in `docs/web/design/assets-extracted/`
were never used.

## Conversion (W-003, 2026-11-17 — Mico's decision)

Mico's decision for this task: **convert to flat token-colored rect-SVGs.**
His 12 supplied PNGs are anti-aliased raster (300–3200 distinct colors, no
clean pixel grid — edge-alignment and box-downsample tests found none), so
the skill's zero-diff rect-SVG verification could not apply verbatim; instead
each PNG was quantized to the site's token palette and emitted as a
`shape-rendering: crispEdges` rect-SVG on the art's native pixel grid
(horizontal run-merge + vertical merge, so shapes follow the original exactly
with flat token fills). Each SVG's `viewBox` is tightened to the art's own
pixel bounds (canvas padding dropped); icon-x and icon-tiktok are additionally
**centroid-recentered** (viewBox enlarged/shifted so the ink mass — not the
ink bbox — sits at the art's center; measured 2026-11-17 after Mico noticed
optical off-centering; all ink covered, no clipping). This is a redraw of smoothed exports
into flat token color — **approved by Mico 2026-11-17 in chat** after seeing
the per-asset candidate preview (native/÷2/÷4 grids; native chosen for
fidelity). All files ≤ 12.4 KB (budget: any single image ≤ 20 KB).

Color mapping (baked fills = token values from `src/styles/tokens.css`;
each asset has exactly one display context):

| Asset | Source color(s) | Shipped fill(s) | Context |
|---|---|---|---|
| logo-mark | dark `#04382b` + green `#44a14f` families | `#083529` (--ink-green) + `#4f9e58` (--green) | Landing, on paper |
| wordmark | green `#519d5a` family | `#4f9e58` (--green) | Landing h1, on paper |
| icon-x / instagram / youtube / tiktok / email | mid-green or near-black line art | `#f9faf5` (--paper) | contact tiles (ink-green fill) |
| icon-github | green body `#4f9e58` + black accents | `#f9faf5` body + `#083529` accents | contact tiles |
| icon-warning | paper-matched fill `#fdfdf3` + green outline `#50a955` | `#f9faf5` fill + `#4f9e58` outline (as drawn: outline carries the shape on paper) | Disclaimer page |
| icon-lightbulb / icon-question | paper-colored art `#f9faf5` | `#083529` (--ink-green) per the D-011 amendment (panel text and icons) | planned (orange) / exploring (gray) panels |

If a token value ever changes, regenerate from `docs/web/design/assets-src/`
and update this table (the conversion is a stdlib script; its steps are
recorded in `tasks/archive/W-003.md`).

## Files

| File | Source (docs/web/design/assets-src/) | Author | License | Date | Derivation | Status |
|---|---|---|---|---|---|---|
| logo-mark.svg | logo-mark.png (512×512, RGBA transparent) | Mico | owner's own art, (c) Groundstate / Mico Arenga | 2026-11-17 | flat token rect-SVG, native grid, 160 rects, 9,694 B | FINAL |
| wordmark.svg | wordmark.png (1024×512, RGBA transparent) | Mico | owner's own art | 2026-11-17 | flat token rect-SVG, native grid, 191 rects, 11,615 B | FINAL |
| icon-x.svg | icon-x.png (256×256) | Mico | owner's own art | 2026-11-17 | flat token rect-SVG, 61 rects, 3,686 B | FINAL |
| icon-instagram.svg | icon-instagram.png (256×256) | Mico | owner's own art | 2026-11-17 | flat token rect-SVG, 84 rects, 5,079 B | FINAL |
| icon-youtube.svg | icon-youtube.png (256×256) | Mico | owner's own art | 2026-11-17 | flat token rect-SVG, 41 rects, 2,536 B | FINAL |
| icon-tiktok.svg | icon-tiktok.png (256×256) | Mico | owner's own art | 2026-11-17 | flat token rect-SVG, 52 rects, 3,176 B (source's chromatic edge glow flattens to one token — accepted with the conversion decision) | FINAL |
| icon-github.svg | icon-github.png (256×256) | Mico | owner's own art | 2026-11-17 | flat token rect-SVG, 198 rects, 11,809 B | FINAL |
| icon-email.svg | icon-email.png (256×256) | Mico | owner's own art | 2026-11-17 | flat token rect-SVG, 89 rects, 5,320 B | FINAL |
| icon-warning.svg | icon-warning.png (256×256) | Mico | owner's own art | 2026-11-17 | flat token rect-SVG, 206 rects, 12,335 B | FINAL |
| icon-lightbulb.svg | icon-lightbulb.png (256×256) | Mico | owner's own art | 2026-11-17 | flat token rect-SVG, 65 rects, 3,904 B | FINAL |
| icon-question.svg | icon-question.png (256×256) | Mico | owner's own art | 2026-11-17 | flat token rect-SVG, 22 rects, 1,407 B | FINAL |

`public/favicon.svg` (site root, referenced by index.html): Mico-made
favicon.svg (32×32 viewBox, Affinity export embedding a 28×32 one-bit PNG),
ships byte-for-byte as supplied — 2 colors (transparent + green `#519d5a`),
hard pixel edges — 1,004 B. FINAL.

Brand-logo note (intake-spec A-6 rule): the X, Instagram, YouTube, TikTok and
GitHub marks were converted (not redrawn) from Mico's supplied art with the
shape fidelity recorded above, and the conversion result was put in front of
Mico for approval before shipping, per the "never redrawn without Mico's
approval of the result" rule.

## Fonts (public/fonts/)

| File | Source | Author/license | Date | Derivation | Status |
|---|---|---|---|---|---|
| dot-shinonome-mincho-16.subset.woff2 (2,416 B) | Mico-supplied `dot-mincho-16.ttf` (JF Dot Shinonome Mincho 16, The Electronic Font Open Laboratory; original BDF by Yasuyuki Furukawa) | Public Domain (full record + evidence trail: `public/fonts/LICENSE-dot-shinonome-mincho-16.txt`) | 2026-11-17 | pyftsubset 4.60.2: UnicodeSet U+0020-007E + U+2190 + U+2192, bitmap-strike/hinting tables dropped, woff2 via brotli 1.2.1 | FINAL |
| LICENSE-dot-shinonome-mincho-16.txt | (this repo, W-003) | — | 2026-11-17 | license record + provenance | FINAL |

Missing from the font (verified): `‹ ›` (U+2039/U+203A) — drawn instead as
pixel SVGs (`src/components/Chevron.tsx`, dot map extracted 1px-exact from
wireframe v3-05; DESIGN.md section 3's prescribed fallback).

## Not shipped

- `docs/web/design/assets-extracted/*` — STOPGAP tier, never used (W-003 had
  the owner's originals).
- Canva's `DotMincho16Std` embedded in `Website_v3.pdf` — web license
  unknown; never extracted (DESIGN.md section 3).
- The original PNG/TTf files stay in `docs/web/design/assets-src/` as the
  conversion sources; they are not copied into `web/` and never ship.
