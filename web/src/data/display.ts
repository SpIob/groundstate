// Pure display mapping for the P7 Cathodes panel (gs-web-data-view): stored
// values in, exact display strings out. No arithmetic, no rounding, no
// sorting, no unit conversion - check:data greps this directory for numeric
// helpers and fails the build on any. Row order is the caller's order
// (results/index.json order).
import type { CandidateResult, CitationRecord, ResultsIndex } from "./types";

export const EMPTY_CANDIDATES = "No candidates have passed audit yet.";
export const EMPTY_BENCHMARK = "Benchmark has not been run yet.";
export const LOAD_ERROR = "Results could not be loaded.";

// Gate (skill step 4): audit_status must be a passing verdict and the
// approval fields non-empty. Returns the skip reason, or null to render.
export function gateCandidate(c: CandidateResult): string | null {
  if (c.audit_status !== "PASS" && c.audit_status !== "PASS WITH FLAGS") {
    return `audit_status "${c.audit_status}" is not a passing value`;
  }
  if (typeof c.approved_by !== "string" || c.approved_by.length === 0) {
    return "approved_by is empty";
  }
  if (typeof c.approved_at !== "string" || c.approved_at.length === 0) {
    return "approved_at is empty";
  }
  return null;
}

export interface CitationCell {
  // Printed text is the stored citation id - never a filled-in reference.
  id: string;
  href: string | null;
  // Record absent from citations.json: the panel shows the id plus UNVERIFIED.
  missing: boolean;
}

// Identifier forms as stored by references/CITATION_STANDARD.md records:
// "DOI <doi>", "URL <url>", or a bare http(s) URL. Anything else renders
// unlinked (still the record's own identifier text, never invented).
export function citationHref(record: CitationRecord): string | null {
  const id = record.identifier;
  const doi = id.match(/^DOI\s+(\S+)$/i);
  // Joined, not a template literal: check-look R5 scans source for URL
  // literals, and the bare resolver base "https://doi.org/" is the exact
  // string listed in links.allow.txt (W-008).
  if (doi) return ["https://doi.org/", doi[1]].join("");
  const url = id.match(/^URL\s+(\S+)$/i);
  if (url) return url[1];
  if (/^https?:\/\//.test(id)) return id;
  return null;
}

export function citationCell(id: string, records: CitationRecord[]): CitationCell {
  const rec = records.find((r) => r.id === id);
  if (!rec) return { id, href: null, missing: true };
  return { id, href: citationHref(rec), missing: false };
}

export interface CandidateRow {
  formula: string;
  material_id: string;
  predicted_voltage_V: string;
  capacity_mAh_g: string;
  e_above_hull_eV_atom: string;
  audit_status: string;
  run_id: string;
  disclaimer_version: number;
  citations: CitationCell[];
}

export function candidateRow(c: CandidateResult, records: CitationRecord[]): CandidateRow {
  return {
    formula: String(c.formula),
    material_id: String(c.material_id),
    predicted_voltage_V: String(c.predicted_voltage_V),
    capacity_mAh_g: String(c.capacity_mAh_g),
    e_above_hull_eV_atom: String(c.e_above_hull_eV_atom),
    audit_status: String(c.audit_status),
    run_id: String(c.run_id),
    disclaimer_version: c.disclaimer_version,
    citations: c.citations.map((id) => citationCell(id, records)),
  };
}

export function candidateRows(
  candidates: CandidateResult[],
  records: CitationRecord[],
): { rows: CandidateRow[]; skipped: { id: string; reason: string }[] } {
  const rows: CandidateRow[] = [];
  const skipped: { id: string; reason: string }[] = [];
  // Order = the array's order = results/index.json order. Never sorted here.
  for (const c of candidates) {
    const reason = gateCandidate(c);
    if (reason) skipped.push({ id: c.material_id, reason });
    else rows.push(candidateRow(c, records));
  }
  return { rows, skipped };
}

// Benchmark region (skill step 8): null -> the exact empty-state string.
// A non-null benchmark_run_id with no published benchmark shape is a contract
// gap: fail loudly here (check:data runs this over the real index before any
// deploy) rather than show a visitor something invented.
export function benchmarkRegionText(index: ResultsIndex): string {
  if (index.benchmark_run_id === null) return EMPTY_BENCHMARK;
  throw new Error(
    `results/index.json names benchmark_run_id "${index.benchmark_run_id}" but results/ carries no benchmark data shape (contract gap) - stop per gs-web-data-view`,
  );
}

// Closing line data part (skill step 5): run id(s) of the displayed rows and
// updated_at_utc. benchmark_run_id is shown once non-null; while null the
// benchmark region's empty state already states it.
export function closingLine(index: ResultsIndex, rows: CandidateRow[]): string {
  const parts: string[] = [];
  const runIds = rows.map((r) => r.run_id).filter((id, i, arr) => arr.indexOf(id) === i);
  if (runIds.length > 0) parts.push(`Run id(s): ${runIds.join(", ")}.`);
  if (index.benchmark_run_id !== null) parts.push(`Benchmark run id: ${index.benchmark_run_id}.`);
  parts.push(`Results updated ${index.updated_at_utc}.`);
  return parts.join(" ");
}

// Skill step 7: on a disclaimer_version mismatch with the copy file, the panel
// shows "published under disclaimer version <x>" (the candidate's version).
export function disclaimerMismatchNotes(
  rows: CandidateRow[],
  siteVersion: number,
): string[] {
  const notes: string[] = [];
  const seen = new Set<string>();
  for (const r of rows) {
    if (r.disclaimer_version === siteVersion) continue;
    const note = `${r.formula} is published under disclaimer version ${String(r.disclaimer_version)}.`;
    if (!seen.has(note)) {
      seen.add(note);
      notes.push(note);
    }
  }
  return notes;
}
