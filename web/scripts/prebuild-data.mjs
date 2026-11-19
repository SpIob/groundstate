// prebuild-data: copies promoted results/ into public/data/ at build time
// (docs/web/SCAFFOLD.md data flow). results/ is read-only here (post-G3 only).
// If docs/schemas ever lands (task T-005), validation wires in here and fails
// the build on a mismatch.
import { readdirSync, readFileSync, existsSync, mkdirSync, rmSync, copyFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const webDir = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const resultsDir = resolve(webDir, "..", "results");
const outDir = join(webDir, "public", "data");

if (!existsSync(join(resultsDir, "index.json"))) {
  console.error("prebuild-data: ../results/index.json not found; nothing promoted to results/ yet (post-G3 only).");
  process.exit(1);
}

rmSync(outDir, { recursive: true, force: true });
mkdirSync(outDir, { recursive: true });
const copied = ["index.json"];
copyFileSync(join(resultsDir, "index.json"), join(outDir, "index.json"));

const candidatesDir = join(resultsDir, "candidates");
if (existsSync(candidatesDir)) {
  mkdirSync(join(outDir, "candidates"), { recursive: true });
  for (const f of readdirSync(candidatesDir).filter((n) => n.endsWith(".json"))) {
    copyFileSync(join(candidatesDir, f), join(outDir, "candidates", f));
    copied.push(`candidates/${f}`);
  }
}
if (existsSync(join(resultsDir, "citations.json"))) {
  copyFileSync(join(resultsDir, "citations.json"), join(outDir, "citations.json"));
  copied.push("citations.json");
}

const schemasDir = resolve(webDir, "..", "docs", "schemas");
if (existsSync(schemasDir)) {
  console.warn("prebuild-data: docs/schemas exists but schema validation is not wired yet (task T-005).");
}

console.log(`prebuild-data: copied ${copied.length} file(s) -> public/data/`);
for (const f of copied) console.log(`  ${f}`);
