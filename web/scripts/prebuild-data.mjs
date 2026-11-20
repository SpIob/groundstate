// prebuild-data: copies promoted results/ into public/data/ at build time
// (docs/web/SCAFFOLD.md data flow). results/ is read-only here (post-G3 only).
// Since T-005 the copies are validated against the JSON Schemas in
// ../pipeline/schemas/ (task W-008; gs-web-data-view step 2): the build FAILS
// on any mismatch. Validation uses web/scripts/mini-schema.mjs - keyword-exact,
// throws on any schema keyword it does not implement. Gate/citation/disclaimer
// warnings print per gs-web-data-view steps 4, 6, 7.
import { readdirSync, readFileSync, existsSync, mkdirSync, rmSync, copyFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { validate } from "./mini-schema.mjs";
import { gateCandidate, citationCell } from "../src/data/display.ts";
import { copyDisclaimer } from "../src/content/copy.disclaimer.ts";

const webDir = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const resultsDir = resolve(webDir, "..", "results");
const schemaDir = resolve(webDir, "..", "pipeline", "schemas");
const outDir = join(webDir, "public", "data");

function loadSchema(name) {
  const p = join(schemaDir, name);
  if (!existsSync(p)) {
    console.error(`prebuild-data: schema ${name} not found at ${p} - cannot validate results/ (T-005).`);
    process.exit(1);
  }
  return JSON.parse(readFileSync(p, "utf8"));
}

if (!existsSync(join(resultsDir, "index.json"))) {
  console.error("prebuild-data: ../results/index.json not found; nothing promoted to results/ yet (post-G3 only).");
  process.exit(1);
}

rmSync(outDir, { recursive: true, force: true });
mkdirSync(outDir, { recursive: true });
const copied = ["index.json"];
copyFileSync(join(resultsDir, "index.json"), join(outDir, "index.json"));

const candidatesDir = join(resultsDir, "candidates");
const candidateFiles = [];
if (existsSync(candidatesDir)) {
  mkdirSync(join(outDir, "candidates"), { recursive: true });
  for (const f of readdirSync(candidatesDir).filter((n) => n.endsWith(".json"))) {
    copyFileSync(join(candidatesDir, f), join(outDir, "candidates", f));
    copied.push(`candidates/${f}`);
    candidateFiles.push(f);
  }
}
const hasCitations = existsSync(join(resultsDir, "citations.json"));
if (hasCitations) {
  copyFileSync(join(resultsDir, "citations.json"), join(outDir, "citations.json"));
  copied.push("citations.json");
}

// ---- schema validation (fail the build on mismatch) ----
const indexSchema = loadSchema("results-index.schema.json");
const candidateSchema = loadSchema("results-candidate.schema.json");
const citationsSchema = hasCitations ? loadSchema("results-citations.schema.json") : null;

const schemaErrors = [];
const index = JSON.parse(readFileSync(join(resultsDir, "index.json"), "utf8"));
schemaErrors.push(...validate(index, indexSchema, "index.json").map((e) => `index.json: ${e}`));
for (const f of candidateFiles) {
  const c = JSON.parse(readFileSync(join(candidatesDir, f), "utf8"));
  schemaErrors.push(...validate(c, candidateSchema, f).map((e) => `candidates/${f}: ${e}`));
}
const citations = hasCitations ? JSON.parse(readFileSync(join(resultsDir, "citations.json"), "utf8")) : null;
if (citationsSchema && citations) {
  schemaErrors.push(...validate(citations, citationsSchema, "citations.json").map((e) => `citations.json: ${e}`));
}
if (schemaErrors.length > 0) {
  console.error(`prebuild-data: results/ failed T-005 schema validation (${schemaErrors.length} error(s)); build stopped.`);
  for (const e of schemaErrors) console.error(`  ${e}`);
  process.exit(1);
}

// ---- gs-web-data-view warnings (do not block: the display handles each) ----
const records = candidateFiles.map((f) => JSON.parse(readFileSync(join(candidatesDir, f), "utf8")));
const citationRecords = citations ? citations.citations : [];
for (const c of records) {
  const reason = gateCandidate(c);
  if (reason) console.warn(`prebuild-data: WARNING candidate ${c.material_id} will not render: ${reason} (gate, gs-web-data-view step 4)`);
  for (const id of c.citations) {
    const cell = citationCell(id, citationRecords);
    if (cell.missing) {
      console.warn(`prebuild-data: WARNING candidate ${c.material_id} cites "${id}" which has no record in citations.json; it renders as "${id} (UNVERIFIED)" (step 6)`);
    }
  }
  if (c.disclaimer_version !== copyDisclaimer.version) {
    console.warn(`prebuild-data: WARNING candidate ${c.material_id} disclaimer_version ${c.disclaimer_version} != copy.disclaimer.version ${copyDisclaimer.version}; the panel states "published under disclaimer version ${c.disclaimer_version}" (step 7)`);
  }
}

console.log(`prebuild-data: copied ${copied.length} file(s) -> public/data/ (schema-validated)`);
for (const f of copied) console.log(`  ${f}`);
