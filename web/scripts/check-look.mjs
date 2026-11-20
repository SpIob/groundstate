// check-look: machine-checks DESIGN.md section 6, hard rules R1-R10, over
// src/ (and dist/ when present), plus R12 (svg wrappers labeled or
// presentational; audit flag 3 disposition). Every violation prints its rule
// id and exits non-zero. R10 (contrast) runs and reports failing pairs; under
// the DECIDED set-B text tokens a real failure blocks the build.
// Rule text: docs/web/DESIGN.md. Token table is parsed from tokens.css so the
// check can never drift from the one file allowed to hold color literals.
import { readdirSync, readFileSync, existsSync, statSync } from "node:fs";
import { dirname, extname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const webDir = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const srcDir = join(webDir, "src");
const distDir = join(webDir, "dist");
const tokensPath = join(srcDir, "styles", "tokens.css");

const failures = [];
const known = [];
function fail(rule, msg) {
  failures.push(`[${rule}] ${msg}`);
}
function flag(rule, msg) {
  known.push(`[${rule}] ${msg}`);
}

// ---------- gather files ----------
function walk(dir) {
  const out = [];
  if (!existsSync(dir)) return out;
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) out.push(...walk(p));
    else out.push(p);
  }
  return out;
}
const srcFiles = walk(srcDir);
const distFiles = existsSync(distDir) ? walk(distDir) : [];
const cssFiles = srcFiles.filter((f) => extname(f) === ".css");
const codeFiles = srcFiles.filter((f) => [".ts", ".tsx", ".js", ".mjs"].includes(extname(f)));
const read = (p) => readFileSync(p, "utf8");

// ---------- tokens (R3) ----------
const tokenCss = read(tokensPath);
const tokens = new Map();
for (const m of tokenCss.matchAll(/--([a-z-]+):\s*(#[0-9a-fA-F]{3,8})\b/g)) {
  tokens.set(m[1], m[2].toLowerCase());
}
const allowedLiterals = new Set(tokens.values());
if (allowedLiterals.size === 0) fail("R3", "no color tokens found in tokens.css - token table parse failed");

// ---------- R1: no animation/motion ----------
// Scope: src/ files and dist/ CSS are wholly ours and are failed hard. dist/
// JS contains React's runtime string constants (its CSS property lists mention
// "transition", its scheduler references requestAnimationFrame); no motion
// executes on the site, but a static check cannot prove that from a vendor
// bundle, so those hits are reported as known, not failing (same pattern as
// the R10 set-A precedent in DESIGN.md).
const r1Patterns = [
  [/transition\s*:/i, "transition property"],
  [/animation\s*:/i, "animation property"],
  [/@keyframes\b/i, "@keyframes"],
  [/scroll-behavior\s*:\s*smooth/i, "scroll-behavior: smooth"],
  [/will-change\s*:/i, "will-change"],
  [/\brequestAnimationFrame\b/, "requestAnimationFrame"],
  [/\bsetInterval\s*\(/, "setInterval (visuals must be instant)"],
];
for (const f of [...cssFiles, ...codeFiles]) {
  const text = read(f);
  for (const [re, label] of r1Patterns) {
    if (re.test(text)) fail("R1", `${relative(webDir, f)}: ${label}`);
  }
}
for (const f of distFiles) {
  if (extname(f) === ".css") {
    const text = read(f);
    for (const [re, label] of r1Patterns) {
      if (re.test(text)) fail("R1", `${relative(webDir, f)}: ${label}`);
    }
  } else if (extname(f) === ".js") {
    const text = read(f);
    for (const [re, label] of r1Patterns) {
      if (re.test(text)) flag("R1", `${relative(webDir, f)}: ${label} (inside the vendor bundle's string constants; verify no site code triggers it)`);
    }
  }
}

// ---------- R2: no softness/opacity ----------
const r2Patterns = [
  [/border-radius\s*:\s*(?!0(?:\s|;|}|$))/i, "non-zero border-radius"],
  [/box-shadow\s*:/i, "box-shadow"],
  [/text-shadow\s*:/i, "text-shadow"],
  [/\bfilter\s*:/i, "filter"],
  [/backdrop-filter\s*:/i, "backdrop-filter"],
  [/(linear|radial|conic)-gradient\s*\(/i, "gradient function"],
  [/opacity\s*:\s*(0?\.\d+)/i, "opacity below 1 on text"],
];
for (const f of cssFiles) {
  const text = read(f);
  for (const [re, label] of r2Patterns) {
    const m = text.match(re);
    if (m) fail("R2", `${relative(webDir, f)}: ${label}`);
  }
}

// ---------- R3: every color literal is a token ----------
for (const f of srcFiles) {
  if (f === tokensPath) continue;
  if (![".css", ".ts", ".tsx"].includes(extname(f))) continue;
  const text = read(f);
  for (const m of text.matchAll(/#[0-9a-fA-F]{3,8}\b/g)) {
    fail("R3", `${relative(webDir, f)}: color literal ${m[0]} outside tokens.css`);
  }
}

// ---------- R4: exactly one font family, local only ----------
// W-003 (2026-11-17): the single self-hosted family ships via @font-face, whose
// font-family descriptor DEFINES the family (CSS custom properties do not work
// inside @font-face). The descriptor is therefore checked as the definition,
// not as a second family: exactly one @font-face family, it must equal the
// first family named in the --font token, and every OTHER font-family
// declaration must go through var(--font).
const fontFamilies = new Set();
const fontFaceFamilies = new Set();
for (const f of cssFiles) {
  const text = read(f);
  const withoutFontFace = text.replace(/@font-face\s*{[^}]*}/g, (block) => {
    const m = block.match(/font-family\s*:\s*([^;]+);/);
    if (m) fontFaceFamilies.add(m[1].trim().replace(/^["']|["']$/g, ""));
    return "";
  });
  for (const m of withoutFontFace.matchAll(/font-family\s*:\s*([^;]+);/g)) fontFamilies.add(m[1].trim());
}
for (const fam of fontFamilies) {
  if (!fam.includes("var(--font)")) fail("R4", `var(--font)-only rule broken: literal font-family "${fam}"`);
}
if (fontFamilies.size === 0) fail("R4", "no font-family rule found (expected exactly one, via var(--font))");
if (fontFamilies.size > 1) fail("R4", `${fontFamilies.size} distinct font-family values (must be exactly 1)`);
if (fontFaceFamilies.size > 1) {
  fail("R4", `${fontFaceFamilies.size} distinct @font-face families (must be exactly 1): ${[...fontFaceFamilies].join(", ")}`);
}
if (fontFaceFamilies.size === 1) {
  const fontToken = (tokenCss.match(/--font\s*:\s*([^;]+);/) || [])[1];
  const firstFamily = fontToken
    ? (fontToken.match(/["']?([^"',]+)["']?/) || [])[1]?.trim()
    : undefined;
  if (!firstFamily) {
    fail("R4", "--font token not found in tokens.css");
  } else {
    const defined = [...fontFaceFamilies][0];
    if (defined.toLowerCase() !== firstFamily.toLowerCase()) {
      fail("R4", `@font-face family "${defined}" does not match the first family in --font ("${firstFamily}")`);
    }
  }
}
const allSrc = [...srcFiles, ...distFiles].map((f) => [f, read(f)]);
for (const [f, text] of allSrc) {
  if (/fonts\.googleapis\.com|fonts\.gstatic\.com|use\.typekit\.net/i.test(text)) {
    fail("R4", `${relative(webDir, f)}: third-party font host`);
  }
}

// ---------- R5: no third-party runtime requests ----------
const allowPath = join(webDir, "links.allow.txt");
const allowedUrls = new Set(
  existsSync(allowPath)
    ? read(allowPath).split("\n").map((l) => l.trim()).filter((l) => l && !l.startsWith("#"))
    : [],
);
for (const [f, text] of allSrc) {
  for (const m of text.matchAll(/https?:\/\/[^\s"'`)\]}>]+/g)) {
    const url = m[0].replace(/[.,;]+$/, "");
    if (!allowedUrls.has(url)) {
      fail("R5", `${relative(webDir, f)}: URL not in links.allow.txt: ${url}`);
    }
  }
}
// R5's job here: every URL appearing in src/ or dist/ must be listed in
// links.allow.txt (outbound copy links and the site's own domain). The
// allowlist's contents are audited by the W2 audit.

// ---------- R7: allowlist only in package.json ----------
const pkg = JSON.parse(read(join(webDir, "package.json")));
const ALLOW = new Set([
  "react", "react-dom",
  "vite", "@vitejs/plugin-react", "typescript", "@types/react", "@types/react-dom",
  "vitest", "jsdom",
]);
for (const section of ["dependencies", "devDependencies"]) {
  for (const name of Object.keys(pkg[section] ?? {})) {
    if (!ALLOW.has(name)) fail("R7", `package.json ${section}: "${name}" is not on the SCAFFOLD.md allowlist`);
  }
}

// ---------- R8: no lorem ipsum / TODO / DRAFT in dist ----------
for (const [f, text] of allSrc.filter(([f]) => f.startsWith(distDir))) {
  if (/lorem ipsum/i.test(text)) fail("R8", `${relative(webDir, f)}: "lorem ipsum"`);
  if (/\bTODO\b|DRAFT/i.test(text)) fail("R8", `${relative(webDir, f)}: TODO/DRAFT string`);
}

// ---------- W-008: no test fixture may reach dist/ ----------
// gs-web-data-view step 9: fixtures live in web/tests/fixtures/ (marker
// "fixture": true) and must never ship. check:data re-runs this over dist/
// after the build; this keeps it enforced whenever dist/ exists.
for (const [f, text] of allSrc.filter(([f]) => f.startsWith(distDir))) {
  if (/"fixture"\s*:\s*true/.test(text) || /fixture/i.test(relative(distDir, f))) {
    fail("W-008", `${relative(webDir, f)}: test fixture reached dist/ (gs-web-data-view step 9)`);
  }
}

// ---------- R6: pixel images crisp ----------
for (const f of srcFiles.filter((f) => extname(f) === ".tsx")) {
  const text = read(f);
  for (const m of text.matchAll(/<img\b[^>]*>/g)) {
    const tag = m[0];
    if (!/image-rendering|pixelated|pixel-img|pixel-icon/i.test(tag)) {
      fail("R6", `${relative(webDir, f)}: <img> without pixelated/crisp class`);
    }
  }
}

// ---------- R12: every svg wrapper is labeled or presentational ----------
// W-002 audit flag 3, Mico disposition 2026-10-29 (FIX: sweep all pixel
// icons; rule = role="img"+aria-label, or explicit aria-hidden="true" when
// decorative). Static over src/ — JSX props compile to plain attributes, so
// the opening tag shows exactly what the DOM gets. Verified live in a browser
// during the 2026-10-30 delta pass (all rendered svgs comply); this keeps it.
for (const f of srcFiles.filter((f) => extname(f) === ".tsx")) {
  const text = read(f);
  for (const m of text.matchAll(/<svg\b[^>]*>/g)) {
    const tag = m[0];
    const labeled = /\brole\s*=\s*["']img["']/.test(tag) && /\baria-label\s*=/.test(tag);
    const presentational = /\baria-hidden\s*=\s*["']true["']/.test(tag);
    if (!labeled && !presentational) {
      fail("R12", `${relative(webDir, f)}: svg without role="img"+aria-label and without aria-hidden="true"`);
    }
  }
}

// ---------- R9: nav string and domain order match PAGES.md ----------
const navTs = read(join(srcDir, "components", "Nav.tsx"));
const navMatch = [...navTs.matchAll(/label: "([^"]+)"/g)].map((m) => m[1]);
const navExpected = ["Home", "Explore", "About", "Contacts", "Disclaimer"];
if (JSON.stringify(navMatch) !== JSON.stringify(navExpected)) {
  fail("R9", `nav order ${JSON.stringify(navMatch)} != PAGES.md ${JSON.stringify(navExpected)}`);
}
const domainsTs = read(join(srcDir, "content", "domains.ts"));
const domainOrder = [...domainsTs.matchAll(/id: "([a-z-]+)"/g)].map((m) => m[1]);
const domainExpected = [
  "batteries", "supercapacitors", "solar-absorbers", "hydrogen-storage", "catalysts",
  "thermoelectrics", "wind-energy", "hydro-energy", "geothermal-energy",
];
const orderedIds = domainOrder.filter((id) => domainExpected.includes(id));
if (JSON.stringify(orderedIds) !== JSON.stringify(domainExpected)) {
  fail("R9", `domain registry order mismatch: ${JSON.stringify(orderedIds)}`);
}

// ---------- R10: contrast of DECIDED token pairs ----------
function lum(hex) {
  const c = hex.replace("#", "");
  const n = c.length === 3 ? c.split("").map((x) => x + x).join("") : c;
  const [r, g, b] = [0, 2, 4].map((i) => {
    let v = parseInt(n.slice(i, i + 2), 16) / 255;
    return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
function ratio(a, b) {
  const [l1, l2] = [lum(a), lum(b)].sort((x, y) => y - x);
  return (l1 + 0.05) / (l2 + 0.05);
}
const t = (name) => {
  const v = tokens.get(name.replace(/^--/, ""));
  if (!v) fail("R3", `token ${name} missing from tokens.css`);
  return v;
};
// Pairs DECIDED by D-011 option B (text on paper, contact tiles) plus the
// D-011 amendment (2026-10-29): panel text/icons are --ink-green on the
// set-A fills. Orange and gray pass as hard gates; all must pass.
const setBpairs = [
  ["--green-text", "--paper", 4.5, "nav/title/small green text on paper"],
  ["--orange-text", "--paper", 4.5, "planned domain labels on paper"],
  ["--gray-text", "--paper", 4.5, "exploring domain labels on paper"],
  ["--ink", "--paper", 4.5, "body text on paper"],
  ["--paper", "--ink-green", 4.5, "paper text on contact tiles"],
  ["--ink-green", "--orange", 4.5, "panel text on orange panel (D-011 amendment)"],
  ["--ink-green", "--gray", 4.5, "panel text on gray panel (D-011 amendment)"],
];
for (const [fg, bg, min, label] of setBpairs) {
  const f = t(fg), b = t(bg);
  if (!f || !b) continue;
  const r = ratio(f, b);
  if (r < min) fail("R10", `${label}: ${f} on ${b} = ${r.toFixed(2)} < ${min}`);
  else console.log(`R10 ok: ${label} ${r.toFixed(2)} >= ${min}`);
}
// D-011 option B rejected B2, but the D-011 amendment (2026-10-29) moved
// panel text/icons to --ink-green on all fills. The one residual below-4.5
// pair in the amended system stays reported-but-not-blocking, with its
const knownPairs = [
  ["--ink-green", "--green", 4.5, "panel text on green panel (D-011 amendment; known residual, below 4.5)"],
];
for (const [fg, bg, min, label] of knownPairs) {
  const f = t(fg), b = t(bg);
  if (!f || !b) continue;
  const r = ratio(f, b);
  if (r < min) flag("R10", `${label}: ${f} on ${b} = ${r.toFixed(2)} < ${min}`);
  else console.log(`R10 ok: ${label} ${r.toFixed(2)} >= ${min}`);
}

// ---------- report ----------
if (known.length) {
  console.log("\nKnown failures (reported, not blocking):");
  for (const k of known) console.log("  " + k);
}
if (failures.length) {
  console.error(`\ncheck-look: ${failures.length} violation(s):`);
  for (const f of failures) console.error("  " + f);
  process.exit(1);
}
console.log("\ncheck-look: PASS (R1-R10, R12)");
