// check-budget: DESIGN.md section 8 size budgets over dist/.
// initial JS 100 KB gzip, CSS 10 KB gzip, fonts 60 KB total, any single image
// 20 KB, first load excluding fonts 250 KB gzip. Exits non-zero on violation.
import { readdirSync, readFileSync, existsSync, statSync } from "node:fs";
import { dirname, extname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { gzipSync } from "node:zlib";

const webDir = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const distDir = join(webDir, "dist");

const BUDGETS = {
  jsInitialKb: 100,
  cssTotalKb: 10,
  fontsTotalKb: 60,
  singleImageKb: 20,
  firstLoadNoFontsKb: 250,
};

if (!existsSync(distDir)) {
  console.error("check-budget: dist/ missing - run the build first.");
  process.exit(1);
}

function walk(dir) {
  const out = [];
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) out.push(...walk(p));
    else out.push(p);
  }
  return out;
}
const files = walk(distDir);
const gz = (p) => gzipSync(readFileSync(p)).length;
const kb = (n) => n / 1024;

const js = files.filter((f) => extname(f) === ".js");
const css = files.filter((f) => extname(f) === ".css");
const fonts = files.filter((f) => [".woff", ".woff2", ".ttf", ".otf"].includes(extname(f)));
const images = files.filter((f) => [".png", ".svg", ".jpg", ".jpeg", ".gif", ".webp", ".ico"].includes(extname(f)));
const html = files.filter((f) => extname(f) === ".html");

const failures = [];
const notes = [];

// Initial JS: dist has no lazy chunks (single-page shell, no dynamic imports),
// so every JS file counts as initial.
const jsGzTotal = js.reduce((s, f) => s + gz(f), 0);
notes.push(`js: ${js.length} file(s), ${kb(jsGzTotal).toFixed(1)} KB gzip`);
if (kb(jsGzTotal) > BUDGETS.jsInitialKb) {
  failures.push(`initial JS ${kb(jsGzTotal).toFixed(1)} KB gzip > ${BUDGETS.jsInitialKb} KB`);
}

const cssGzTotal = css.reduce((s, f) => s + gz(f), 0);
notes.push(`css: ${css.length} file(s), ${kb(cssGzTotal).toFixed(1)} KB gzip`);
if (kb(cssGzTotal) > BUDGETS.cssTotalKb) {
  failures.push(`CSS total ${kb(cssGzTotal).toFixed(1)} KB gzip > ${BUDGETS.cssTotalKb} KB`);
}

const fontBytes = fonts.reduce((s, f) => s + statSync(f).size, 0);
notes.push(`fonts: ${fonts.length} file(s), ${kb(fontBytes).toFixed(1)} KB raw`);
if (kb(fontBytes) > BUDGETS.fontsTotalKb) {
  failures.push(`fonts total ${kb(fontBytes).toFixed(1)} KB > ${BUDGETS.fontsTotalKb} KB`);
}

for (const f of images) {
  const size = statSync(f).size;
  if (kb(size) > BUDGETS.singleImageKb) {
    failures.push(`image ${relative(distDir, f)} ${kb(size).toFixed(1)} KB > ${BUDGETS.singleImageKb} KB`);
  }
}
notes.push(`images: ${images.length} file(s), max ${images.length ? kb(Math.max(...images.map((f) => statSync(f).size))).toFixed(1) : 0} KB raw`);

// First load excluding fonts: all JS + CSS + HTML + images, gzip.
const firstLoad = [...js, ...css, ...html, ...images].reduce((s, f) => s + gz(f), 0);
notes.push(`first load (no fonts): ${kb(firstLoad).toFixed(1)} KB gzip`);
if (kb(firstLoad) > BUDGETS.firstLoadNoFontsKb) {
  failures.push(`first load ${kb(firstLoad).toFixed(1)} KB gzip > ${BUDGETS.firstLoadNoFontsKb} KB`);
}

for (const n of notes) console.log("  " + n);
if (failures.length) {
  console.error(`\ncheck-budget: ${failures.length} budget(s) exceeded:`);
  for (const f of failures) console.error("  " + f);
  process.exit(1);
}
console.log("\ncheck-budget: PASS (R11)");
