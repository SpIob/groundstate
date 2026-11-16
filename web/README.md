# web/

The Groundstate website source: React + TypeScript + Vite, static, no server,
no database. Built by task W-002 (`/gs-web-setup`); specs live in `docs/web/`
(`DESIGN.md`, `PAGES.md`, `SCAFFOLD.md`), the work queue on `tasks/BOARD.md`.

## What lives here

- `src/` — pages, components, styles. `src/styles/tokens.css` is the only
  file allowed to contain color literals (DESIGN.md R3).
- `scripts/` — `prebuild-data.mjs` (copies `../results/` into
  `public/data/` at build time) and the machine checks for the hard rules
  (DESIGN.md section 6): `check-look` (R1–R10, plus R12 for svg wrappers),
  `check-budget` (R11), `check-links` (R5).
- `links.allow.txt` — every outbound URL allowed in `dist/`.
- `DEPENDENCIES.md` — every package/font/tool with license and source;
  the allowlist is `docs/web/SCAFFOLD.md`. Nothing gets added without
  Mico's approval.
- `public/data/` — git-ignored. Copied from `../results/` at prebuild,
  never edited by hand. `citations.json` comes along the same way: every
  entry traces to a verified `references/literature/` note (T-005), and
  `src/data/loaders.ts` fetches it for the data panel (task W-008).

## Commands

```
npm install        # allowlisted packages only (see DEPENDENCIES.md)
npm run dev        # dev server
npm run check      # typecheck + check:look + build + check:budget + check:links
```

`npm run check` must pass before any hand-off to audit (gate W2). It exits
non-zero on any hard-rule violation and prints the rule id. Two classes of
findings are reported as known failures instead of blocking, by design:
vendor-bundle string constants inside React's runtime (R1) and the two
panel-contrast pairs D-011 decided to accept (R10).

The font stack is provisional (D-010 option D): fallback monospace until the
Dot Mincho 16 license is verified and the subset woff2 lands in
`public/fonts/` (task W-003).
