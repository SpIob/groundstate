// Read-only loaders for /data/*.json (copied from ../results/ at prebuild by
// scripts/prebuild-data.mjs, schema-validated there since T-005). No math
// here: components print values exactly as stored (docs/web/SCAFFOLD.md data
// flow; gs-web-data-view "Never read pipeline/" - this fetches public/data
// only, which prebuild filled from results/).
import type { CandidateResult, CitationsFile, ResultsIndex } from "./types";

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(path);
  if (!res.ok) {
    throw new Error(`failed to load ${path}: ${res.status}`);
  }
  return (await res.json()) as T;
}

export function loadIndex(): Promise<ResultsIndex> {
  return fetchJson<ResultsIndex>("/data/index.json");
}

export function loadCandidate(id: string): Promise<CandidateResult> {
  return fetchJson<CandidateResult>(`/data/candidates/${encodeURIComponent(id)}.json`);
}

export function loadCitations(): Promise<CitationsFile> {
  return fetchJson<CitationsFile>("/data/citations.json");
}
