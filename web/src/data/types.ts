// Types mirror docs/DATA_CONTRACT.md (results/ section). Field-for-field.

export interface CandidateResult {
  material_id: string;
  formula: string;
  predicted_voltage_V: number;
  capacity_mAh_g: number;
  capacity_basis?: string;
  e_above_hull_eV_atom: number;
  run_id: string;
  audit_status: string;
  approved_by: string;
  approved_at: string;
  disclaimer_version: number;
  citations: string[];
  result_type?: string;
  statement?: string;
}

export interface ResultsIndex {
  candidates: string[];
  benchmark_run_id: string | null;
  updated_at_utc: string;
}

export interface CitationRecord {
  citation_id: string;
  title?: string;
  url?: string;
  [key: string]: unknown;
}
