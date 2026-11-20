// Types mirror docs/DATA_CONTRACT.md (results/ section), field-for-field.
// Required = the contract's field lists (candidates also require result_type
// and statement - evidence-rule essentials). Enrichment the contract names
// (capacity_basis, d006_status, d006_gap_reason) is optional. No invented
// fields: anything else a promoted record carries (d004_comparison, method,
// ...) is enrichment the site never reads, so it stays untyped here.

export interface CandidateResult {
  material_id: string;
  formula: string;
  predicted_voltage_V: number;
  capacity_mAh_g: number;
  // D-006 option C: MP's number when available, else the literal gap.
  e_above_hull_eV_atom: number | "UNVERIFIED";
  run_id: string;
  audit_status: "PASS" | "PASS WITH FLAGS" | "FAIL";
  approved_by: string;
  approved_at: string;
  disclaimer_version: number;
  citations: string[];
  // Optional enrichment named by the contract:
  result_type?: string;
  statement?: string;
  capacity_basis?: string;
  d006_status?: "mp_value" | "unverified_gap";
  d006_gap_reason?: string;
}

export interface ResultsIndex {
  candidates: string[];
  benchmark_run_id: string | null;
  updated_at_utc: string;
}

export interface CitationRecord {
  id: string;
  type: "paper" | "database" | "dataset" | "software";
  title: string;
  authors: string | string[];
  year: number | "UNVERIFIED";
  identifier: string;
  version: string;
  accessed_at: string;
  verified: true;
  verified_by: string;
}

export interface CitationsFile {
  citations: CitationRecord[];
}
