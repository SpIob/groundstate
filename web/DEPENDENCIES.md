# Dependencies

Every package, font, and tool used by `web/`, with license, source, and the
date each license/source was opened and verified. Allowlist:
`docs/web/SCAFFOLD.md`. Nothing gets added without Mico's approval.

## npm packages (installed 2026-10-27)

License text for each was read from the LICENSE file inside the published
npm tarball of the exact recorded version (not from registry metadata alone).

| Package | Version | License | Source (opened 2026-10-27) | License verified |
|---|---|---|---|---|
| react | 19.3.1 | MIT | https://github.com/react/react (registry repo URL; resolves live, HTTP 200) | tarball `package/LICENSE`: "MIT License, Copyright (c) Meta Platforms, Inc. and affiliates." |
| react-dom | 19.3.1 | MIT | https://github.com/react/react (same repo as react, registry metadata) | tarball `package/LICENSE`: MIT, Meta Platforms, Inc. and affiliates |
| vite | 8.3.5 | MIT | https://github.com/vitejs/vite | tarball `package/LICENSE.md`: "Vite is released under the MIT license" |
| typescript | 7.0.2 | Apache-2.0 | https://github.com/microsoft/TypeScript | tarball `package/LICENSE`: Apache License, Version 2.0 |
| @vitejs/plugin-react | 6.1.2 | MIT | https://github.com/vitejs/vite-plugin-react | tarball `package/LICENSE`: MIT, Evan You and Vite contributors |
| @types/react | 19.3.0 | MIT | https://github.com/DefinitelyTyped/DefinitelyTyped | tarball `react/LICENSE`: MIT, Microsoft Corporation |
| @types/react-dom | 19.3.0 | MIT | https://github.com/DefinitelyTyped/DefinitelyTyped | tarball `react-dom/LICENSE`: MIT, Microsoft Corporation |

Note on react/react-dom repo URLs: the npm registry records
`git+https://github.com/react/react.git` for both packages. That URL is live
(HTTP 200, 2026-10-27) and React's official homepage is https://react.dev/
(also opened 2026-10-27). The license check does not depend on the repo URL:
it was verified against the shipped tarball license text above.

Registry metadata fetch date: 2026-10-27 (registry.npmjs.org, dist-tags
latest for each). `npm ls --depth=0` lists exactly these 7 packages;
`npm install` reported 0 vulnerabilities.

## Fonts

| Font | Shipped file | License | Source | Date |
|---|---|---|---|---|
| JF Dot Shinonome Mincho 16 (The Electronic Font Open Laboratory /efont/; original BDF by Yasuyuki Furukawa) | `public/fonts/dot-shinonome-mincho-16.subset.woff2` (2,416 bytes; subset to ASCII + U+2190 + U+2192, bitmap/hinting tables dropped) | Public Domain | Font file supplied by Mico into `docs/web/design/assets-src/dot-mincho-16.ttf` (2026-11-17, chat-confirmed web-usable); license corroborated the same day against the font's own name table ("Public Domain"), the /efont/ project page (openlab.jp/efont/shinonome — "These fonts are in Public Domain. Share and Enjoy."), Japanese Wikipedia, and Gentoo packaging. Full record: `public/fonts/LICENSE-dot-shinonome-mincho-16.txt` | 2026-11-17 |

Not shipped, by rule: Canva's `DotMincho16Std` embedded in `Website_v3.pdf`
(web license unknown; never extracted — DESIGN.md section 3). This Shinonome
Mincho 16 is the owner-supplied, public-domain 16-dot Mincho that satisfies
D-010 option D's intent from W-003 on; `font: provisional` no longer applies.

## Tooling outside package.json

| Tool | Version | License | Source | Date |
|---|---|---|---|---|
| node | 26.10.0 | (runtime, preinstalled by Mico) | https://nodejs.org | 2026-10-27 |
| npm | 11.19.1 | (runtime, preinstalled by Mico) | https://nodejs.org | 2026-10-27 |
| fontTools (pyftsubset) | 4.60.2 | MIT ("MIT License, Copyright (c) 2017 Just van Rossum" read from the installed wheel's LICENSE; bundled third-party bits under LICENSE.external) | pypi.org/project/fonttools, installed into a scratch venv for the one-time subset; not a runtime dependency | 2026-11-17 |
| brotli | 1.2.1 | MIT ("Copyright (c) 2009, 2010, 2013-2016 by the Brotli Authors", permission notice read from the installed wheel's LICENSE) | pypi.org/project/brotli, same scratch venv; woff2 encoder for pyftsubset; not a runtime dependency | 2026-11-17 |

No optional tools (vitest, jsdom, headless browser) are installed. fontTools
and brotli live only in a scratch venv used to produce the font subset; the
site ships just the resulting woff2. SCAFFOLD.md lists both on the optional
tooling allowlist.
