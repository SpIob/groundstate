// check-data: gs-web-data-view verification for the P7 data panel (W-008).
// 1. Purity: no Math. / toFixed / .sort( anywhere in src/data or the table
//    components (skill step 3).
// 2. Fixture tests (skill step 9): web/tests/fixtures/ (each carries
//    "fixture": true, never copied into results/) are schema-validated and
//    driven through the same display mapping the panel uses; every displayed
//    string is compared to the JSON value string, character for character.
// 3. Negative schema tests: mini-schema must catch seeded defects.
// 4. Live gate over ../results/: traceability, schema validity, display order,
//    gate, citation resolution, disclaimer comparison (warnings where the
//    skill prescribes display-time handling).
// 5. dist scan: no fixture may reach dist/ (skill step 9).
// Runs inside `npm run check`, after the build, so the dist scan sees the
// shipped output.
import { readdirSync, readFileSync, existsSync, statSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { validate } from "./mini-schema.mjs";
import {
  EMPTY_CANDIDATES,
  benchmarkRegionText,
  candidateRows,
  citationCell,
  citationHref,
  closingLine,
  disclaimerMismatchNotes,
} from "../src/data/display.ts";
import { copyDisclaimer } from "../src/content/copy.disclaimer.ts";

const webDir = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const srcDir = join(webDir, "src");
const distDir = join(webDir, "dist");
const resultsDir = resolve(webDir, "..", "results");
const schemaDir = resolve(webDir, "..", "pipeline", "schemas");
const fixDir = join(webDir, "tests", "fixtures");

let failures = 0;
function ok(cond, msg) {
  if (cond) console.log(`ok: ${msg}`);
  else {
    failures += 1;
    console.error(`FAIL: ${msg}`);
  }
}
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
const readJson = (p) => JSON.parse(readFileSync(p, "utf8"));

// ---------- 1. purity (skill step 3) ----------
const purityFiles = [
  ...walk(join(srcDir, "data")),
  join(srcDir, "components", "DataTable.tsx"),
  join(srcDir, "components", "CathodesPanel.tsx"),
].filter((f) => existsSync(f));
const purityPatterns = [
  [/\bMath\./, "Math."],
  [/\btoFixed\b/, "toFixed"],
  [/\.sort\(/, ".sort("],
];
for (const f of purityFiles) {
  const text = readFileSync(f, "utf8");
  for (const [re, label] of purityPatterns) {
    if (re.test(text)) {
      failures += 1;
      console.error(`FAIL: purity: ${relative(webDir, f)} uses ${label} (gs-web-data-view step 3)`);
    }
  }
}
console.log(`ok: purity scan over ${purityFiles.length} file(s): no Math./toFixed/.sort(`);

// ---------- schemas ----------
const candidateSchema = readJson(join(schemaDir, "results-candidate.schema.json"));
const indexSchema = readJson(join(schemaDir, "results-index.schema.json"));
const citationsSchema = readJson(join(schemaDir, "results-citations.schema.json"));

// ---------- 2. fixtures ----------
const fixtureFiles = walk(fixDir);
ok(fixtureFiles.length > 0, `fixture directory has ${fixtureFiles.length} file(s)`);
for (const f of fixtureFiles) {
  ok(/"fixture"\s*:\s*true/.test(readFileSync(f, "utf8")), `${relative(fixDir, f)} carries "fixture": true`);
}

const fixIndex = readJson(join(fixDir, "fixture-index.json"));
const fixIndexEmpty = readJson(join(fixDir, "fixture-index-empty.json"));
const fixCitations = readJson(join(fixDir, "fixture-citations.json"));
const fixIds = ["mp-999901", "mp-999902", "mp-999903", "mp-999904"];
const fixCandidates = Object.fromEntries(fixIds.map((id) => [id, readJson(join(fixDir, `fixture-candidate-${id}.json`))]));

// 2a. fixtures are schema-legal (the marker field is legal enrichment) -
// except mp-999903, whose empty approved_by is exactly what the runtime gate
// exists for (schema minLength 1 already rejects it; asserted below as a
// negative case, per gs-web-data-view step 4's second layer).
const schemaLegalIds = fixIds.filter((id) => id !== "mp-999903");
const fixSchemaErrors = [
  ...validate(fixIndex, indexSchema, "fixture-index"),
  ...validate(fixIndexEmpty, indexSchema, "fixture-index-empty"),
  ...validate(fixCitations, citationsSchema, "fixture-citations"),
  ...schemaLegalIds.flatMap((id) => validate(fixCandidates[id], candidateSchema, id).map((e) => `${id}: ${e}`)),
];
ok(fixSchemaErrors.length === 0, `schema-legal fixtures validate against the T-005 schemas${fixSchemaErrors.length ? " - " + fixSchemaErrors.join("; ") : ""}`);
ok(
  validate(fixCandidates["mp-999903"], candidateSchema, "mp-999903").some((e) => /approved_by/.test(e)),
  "empty approved_by is rejected by the candidate schema (the gate is the second layer)",
);

// 2b. display mapping vs JSON value strings, character for character.
// Candidates are passed in the fixture index's order - the mapping must keep
// that order (never sorted).
const { rows, skipped } = candidateRows(fixIndex.candidates.map((id) => fixCandidates[id]), fixCitations.citations);
ok(rows.length === 2, `gate renders 2 of 4 fixture candidates (got ${rows.length})`);
ok(
  rows[0].material_id === "mp-999904" && rows[1].material_id === "mp-999901",
  "row order follows index order (fixture index lists 904 first) - never sorted",
);
for (const row of rows) {
  const c = fixCandidates[row.material_id];
  ok(row.formula === String(c.formula), `${c.material_id}: formula verbatim`);
  ok(row.predicted_voltage_V === String(c.predicted_voltage_V), `${c.material_id}: predicted voltage verbatim (${row.predicted_voltage_V})`);
  ok(row.capacity_mAh_g === String(c.capacity_mAh_g), `${c.material_id}: capacity verbatim (${row.capacity_mAh_g})`);
  ok(row.e_above_hull_eV_atom === String(c.e_above_hull_eV_atom), `${c.material_id}: hull verbatim (${row.e_above_hull_eV_atom})`);
  ok(row.audit_status === String(c.audit_status), `${c.material_id}: audit_status shown verbatim`);
  ok(row.run_id === String(c.run_id), `${c.material_id}: run_id verbatim`);
}
ok(rows[0].e_above_hull_eV_atom === "UNVERIFIED", "D-006 gap form prints the literal UNVERIFIED");
ok(
  rows[0].citations[0].id === "fixture-cite-1" &&
    rows[0].citations[0].href === "https://doi.org/10.1/fixture-a",
  "stored citation id resolves to a doi.org link built from the stored identifier",
);
ok(
  rows[0].citations[1].id === "fixture-cite-missing" && rows[0].citations[1].missing === true,
  "citation without a record is flagged missing (panel shows id + UNVERIFIED)",
);
ok(
  skipped.length === 2 &&
    skipped[0].id === "mp-999902" &&
    /not a passing value/.test(skipped[0].reason) &&
    skipped[1].id === "mp-999903" &&
    /approved_by/.test(skipped[1].reason),
  "gate skips audit-FAIL and empty-approved_by candidates with reasons",
);
ok(
  benchmarkRegionText(fixIndex) === "Benchmark has not been run yet.",
  "benchmark_run_id null prints the exact empty-state string",
);
ok(
  candidateRows([], fixCitations.citations).rows.length === 0,
  "empty index yields zero rows (panel prints the empty-state string)",
);
ok(
  EMPTY_CANDIDATES === "No candidates have passed audit yet.",
  "candidates empty-state string matches gs-web-data-view step 8 exactly",
);
let gapThrew = false;
try {
  benchmarkRegionText({ ...fixIndex, benchmark_run_id: "run-x" });
} catch {
  gapThrew = true;
}
ok(gapThrew, "a non-null benchmark_run_id with no benchmark shape fails loudly (contract gap, never invented content)");
const cl = closingLine(fixIndex, rows);
ok(
  cl === "Run id(s): run-20261119-w008-fixture, run-20261119-w008-fixture-b. Results updated 2026-11-19T00:00:00+00:00.",
  "closing line carries run ids (index order, deduped) and updated_at_utc verbatim",
);
ok(!cl.includes("Benchmark run id:"), "closing line omits benchmark_run_id while it is null (region states it)");
const mismatchNotes = disclaimerMismatchNotes(rows, copyDisclaimer.version);
ok(
  mismatchNotes.length === 1 &&
    mismatchNotes[0] === "Li2FixtureSiO4 is published under disclaimer version 2.",
  'disclaimer mismatch note reads "published under disclaimer version <x>" with the stored x',
);
ok(
  disclaimerMismatchNotes([rows[1]], copyDisclaimer.version).length === 0,
  "matching disclaimer version produces no note",
);
ok(
  citationHref({ identifier: "DOI 10.1/x" }) === "https://doi.org/10.1/x" &&
    citationHref({ identifier: "URL https://a.b/c" }) === "https://a.b/c" &&
    citationHref({ identifier: "https://a.b" }) === "https://a.b" &&
    citationHref({ identifier: "print-only" }) === null,
  "identifier forms resolve: DOI / URL / bare URL / unlinked",
);
ok(citationCell("fixture-cite-1", fixCitations.citations).missing === false, "existing citation record resolves");

// ---------- 3. negative schema tests (mini-schema must catch) ----------
const pass = fixCandidates["mp-999901"];
const seeded = [
  [{ ...pass, predicted_voltage_V: "3.4239" }, "type"],
  [{ ...pass, e_above_hull_eV_atom: "UNVERIFIED" }, "D-006 conditional required fields"],
  [{ ...pass, audit_status: "MAYBE" }, "enum"],
  [{ ...pass, run_id: "t003" }, "pattern"],
  [{ ...pass, citations: [] }, "minItems"],
  [{ ...pass, statement: "" }, "minLength"],
  [{ ...pass, disclaimer_version: 0 }, "minimum"],
  [{ ...pass }, "required (statement removed)"],
];
seeded[7][0] = { ...seeded[7][0] };
delete seeded[7][0].statement;
for (const [bad, label] of seeded) {
  ok(validate(bad, candidateSchema, "seeded").length > 0, `mini-schema catches seeded defect: ${label}`);
}
ok(
  validate({ ...fixIndex, benchmark_run_id: "not-a-run-id" }, indexSchema, "seeded").length > 0,
  "mini-schema catches seeded defect: index benchmark_run_id pattern",
);
let unsupportedThrew = false;
try {
  validate({ ...pass }, { ...candidateSchema, minProperties: 2 }, "seeded");
} catch (e) {
  unsupportedThrew = /unsupported keyword/.test(String(e));
}
ok(unsupportedThrew, "mini-schema throws on a keyword it does not implement (never silently bypasses)");

// ---------- 4. live gate over ../results/ ----------
const liveIndex = readJson(join(resultsDir, "index.json"));
for (const id of liveIndex.candidates) {
  ok(
    existsSync(join(resultsDir, "candidates", `${id}.json`)),
    `results traceability: index entry ${id} has a candidate file`,
  );
}
const liveCandidates = liveIndex.candidates.map((id) => readJson(join(resultsDir, "candidates", `${id}.json`)));
const liveCitationsFile = readJson(join(resultsDir, "citations.json"));
const liveSchemaErrors = [
  ...validate(liveIndex, indexSchema, "index.json"),
  ...validate(liveCitationsFile, citationsSchema, "citations.json"),
  ...liveCandidates.flatMap((c) => validate(c, candidateSchema, c.material_id).map((e) => `${c.material_id}: ${e}`)),
];
ok(liveSchemaErrors.length === 0, `live results/ validate against the T-005 schemas${liveSchemaErrors.length ? " - " + liveSchemaErrors.join("; ") : ""}`);
const live = candidateRows(liveCandidates, liveCitationsFile.citations);
console.log(`live render order (index order): ${live.rows.map((r) => `${r.formula} ${r.material_id} = ${r.predicted_voltage_V} V`).join(" | ")}`);
for (const s of live.skipped) {
  console.warn(`check-data: WARNING live candidate ${s.id} will not render: ${s.reason}`);
}
const liveUnresolved = live.rows.flatMap((r) =>
  r.citations.filter((c) => c.missing).map((c) => `${r.material_id} cites ${c.id}`),
);
if (liveUnresolved.length) {
  console.warn(`check-data: WARNING live citations with no record (render as id + UNVERIFIED): ${liveUnresolved.join(", ")}`);
}
const liveMismatch = disclaimerMismatchNotes(live.rows, copyDisclaimer.version);
if (liveMismatch.length) {
  console.warn(`check-data: WARNING disclaimer version mismatch: ${liveMismatch.join(" | ")}`);
}
try {
  console.log(`live benchmark region: "${benchmarkRegionText(liveIndex)}"`);
} catch (e) {
  failures += 1;
  console.error(`FAIL: live index benchmark state: ${e.message}`);
}
console.log(`live closing line: ${closingLine(liveIndex, live.rows)} Disclaimer version ${copyDisclaimer.version}.`);

// ---------- 5. dist scan (skill step 9) ----------
if (existsSync(distDir)) {
  let fixtureHits = 0;
  for (const f of walk(distDir)) {
    const rel = relative(distDir, f);
    if (/fixture/i.test(rel)) {
      failures += 1;
      console.error(`FAIL: fixture file reached dist/: ${rel}`);
      fixtureHits += 1;
      continue;
    }
    if (/"fixture"\s*:\s*true/.test(readFileSync(f, "utf8"))) {
      failures += 1;
      console.error(`FAIL: fixture marker found in dist/: ${rel}`);
      fixtureHits += 1;
    }
  }
  if (fixtureHits === 0) console.log("ok: no fixture reached dist/");
} else {
  console.log("dist scan skipped: dist/ missing (run after the build for the full check)");
}

if (failures > 0) {
  console.error(`\ncheck-data: ${failures} failure(s)`);
  process.exit(1);
}
console.log("\ncheck-data: PASS (purity, fixtures, negative schema tests, live gate, dist scan)");
