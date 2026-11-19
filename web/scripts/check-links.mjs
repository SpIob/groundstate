// check-links: DESIGN.md R5 over dist/ - no third-party runtime requests.
// Every http(s):// or mailto: string in dist/ must appear in links.allow.txt.
// Also prints UNSET for any contact tile with no URL (PAGES.md P3); deploy is
// blocked on UNSET tiles, which the W2 audit enforces.
import { readdirSync, readFileSync, existsSync, statSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const webDir = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const distDir = join(webDir, "dist");
const allowPath = join(webDir, "links.allow.txt");

function walk(dir) {
  const out = [];
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) out.push(...walk(p));
    else out.push(p);
  }
  return out;
}

const failures = [];

// UNSET contact tiles (checked over source, so this works pre-build too).
const contactsTs = readFileSync(join(webDir, "src", "content", "contacts.ts"), "utf8");
const unset = [...contactsTs.matchAll(/id: "([^"]+)",\s*label: "[^"]+",\s*url: null/g)].map((m) => m[1]);
if (unset.length) {
  console.log(`UNSET contact tiles (${unset.length}): ${unset.join(", ")}`);
  console.log("Deploy is blocked while any tile is UNSET unless Mico removes it (PAGES.md P3).");
}

if (!existsSync(distDir)) {
  console.error("check-links: dist/ missing - run the build first.");
  process.exit(1);
}
if (!existsSync(allowPath)) {
  console.error(`check-links: ${relative(webDir, allowPath)} missing.`);
  process.exit(1);
}
const allowed = new Set(
  readFileSync(allowPath, "utf8")
    .split("\n")
    .map((l) => l.trim())
    .filter((l) => l && !l.startsWith("#")),
);

for (const f of walk(distDir)) {
  const text = readFileSync(f, "utf8");
  for (const m of text.matchAll(/https?:\/\/[^\s"'`)\]}>]+/g)) {
    const url = m[0].replace(/[.,;]+$/, "");
    if (!allowed.has(url)) {
      failures.push(`${relative(distDir, f)}: URL not in links.allow.txt: ${url}`);
    }
  }
  for (const m of text.matchAll(/mailto:([^\s"'`)\]}>]+)/g)) {
    const url = `mailto:${m[1]}`;
    if (!allowed.has(url) && !allowed.has(m[1])) {
      failures.push(`${relative(distDir, f)}: mailto not in links.allow.txt: ${url}`);
    }
  }
}

if (failures.length) {
  console.error(`\ncheck-links: ${failures.length} unallowed URL(s):`);
  for (const f of failures) console.error("  " + f);
  process.exit(1);
}
console.log("\ncheck-links: PASS (R5)");
