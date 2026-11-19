# web/ scaffold (target layout, created by `gs-web-setup` after M5 opens)

Nothing here is created now. `web/` stays frozen until `docs/ROADMAP.md` M5 reads Open (D-013). Stack is the decided one: React + TypeScript + Vite, static, no server, no database. Pages are tiny, so if Mico later wants it lighter still, plain TypeScript + Vite is a drop-in swap; that is not proposed now.

## Tree
```
web/
  README.md              replaces the frozen stub when M5 opens
  DEPENDENCIES.md        every package, font, tool: license, source URL, date opened
  links.allow.txt        every outbound URL allowed in dist/ (R5)
  package.json, package-lock.json, tsconfig.json, vite.config.ts, index.html
  public/
    fonts/               subset woff2 + LICENSE file per family
    assets/              logo, wordmark, pixel icons (SVG preferred) + ASSETS.md manifest
    data/                GIT-IGNORED. Copied from ../results/ at prebuild. Never edited by hand.
  src/
    main.tsx, App.tsx, router.ts        hash router, hand-written, no library
    styles/tokens.css                   the ONLY file allowed to contain color literals
    styles/base.css, layout.css, components.css
    components/          Nav, TitleRow, TextBlock, ContactTile, DomainList, Flyout,
                         Panel, PlaceholderPanel, DataTable
    pages/               Landing, About, Contacts, Disclaimer, Explore
    content/             domains.ts, contacts.ts, status-messages.ts,
                         copy.about.ts, copy.disclaimer.ts, copy.cathodes.ts
    data/                types.ts (mirrors docs/DATA_CONTRACT.md), loaders.ts (read-only, no math)
  scripts/               prebuild-data.mjs, check-look.mjs, check-budget.mjs, check-links.mjs
  tests/fixtures/        made-up data for display tests only, each file marked "fixture": true
```
Design reference (wireframes, extracted assets) stays in `docs/web/design/`. It is not copied into `web/` and never shipped.

## npm scripts
`dev`, `build`, `preview`, `typecheck`, `prebuild` (runs prebuild-data), `check:look` (DESIGN.md section 6 R1 to R10), `check:budget` (R11), `check:links` (R5), `check` (typecheck, all check:*, build). Every check exits non-zero on violation and prints the rule id.

## Dependency allowlist (all free and open source; license opened and recorded before install)
- Runtime: `react`, `react-dom`.
- Dev: `vite`, `@vitejs/plugin-react`, `typescript`, `@types/react`, `@types/react-dom`.
- Optional dev: `vitest` + `jsdom` for display tests.
- Optional tooling outside `package.json`: `fonttools` + `brotli` (Python) to subset fonts to woff2; a headless browser for screenshots only if one is already installed (do not download a second browser just for this).
- Not allowed: router libraries, UI or CSS frameworks, icon libraries, animation libraries, state libraries, markdown parsers, analytics, anything with a paid tier or account requirement. Anything not on this list needs Mico's approval.

## Data flow
`results/` (post-G3 only) -> `prebuild-data.mjs` copies `index.json`, `candidates/*.json`, and `citations.json` (if present) into `public/data/` -> `loaders.ts` fetches `/data/...` at runtime -> components print values exactly as stored. The site never reads `pipeline/`. If JSON Schemas exist (task T-005), prebuild validates against them and fails the build on a mismatch.

## Hosting (D-009, decided: Vercel)
Static `dist/` only, hash routes, no SPA rewrite rules needed. Deploying `dist/` to Vercel and DNS are Mico's dashboard steps; Hermes cannot do them. Before any deploy, `gs-web-deploy` opens Vercel's terms and records how the hobby plan's personal non-commercial use reads against the site's setup, and stops for Mico if it is not clearly fine.

## Root `.gitignore` addition
`web/public/data/`
