# Data contract

Status: implemented (T-005, 2026-10-27). JSON Schema files for every shape below live in `pipeline/schemas/`; validate with `pipeline/src/groundstate/validate_results.py --all`. This file stays the plain-language version every skill writes against. Schema rule: `required` = exactly the fields listed per shape (candidate records also require `result_type` and `statement` — evidence-rule essentials); anything a run or an audit records beyond that is legal enrichment and must stay optional. D-006 gap forms additionally require their `d006_*` fields through conditional (`allOf`) schema rules; legacy numeric-only hull records stay valid. `audit.md` stays free-form markdown (no schema). `stability-index.json` (run-level hull summary written by stage 4) is codified in `pipeline/schemas/stability-index.schema.json` though not described below.

## provenance.json (per candidate, in `pipeline/data/raw/<id>/`)
`material_id, formula, space_group, atoms_per_cell, source ("materials_project" | "literature"), database_version, retrieval_time_utc, client_version, query, theoretical_or_observed, citation_id (if source is literature)`

## manifest.json (per run, in `pipeline/runs/<run-id>/`)
`run_id, git_sha, package_versions, model_name, model_version, device, seeds, input_ids, created_at_utc`

## derived.json (per run)
`candidate_id, pairs: [{x1, x2, voltage_V, capacity_mAh_g, mass_basis}], formula_version, run_id`

Lithiation-state bounds: `x1`/`x2` are Li per reduced formula unit, schema-bounded 0 to 4 (T-008, 2026-10-30 — widened from 1 when the first multi-Li host, Li2FeSiO4 with a 0→2 window, validated; the pair's `label` names the window so per-material conventions stay explicit).

## stability.json (per candidate)
`material_id, e_above_hull_eV_atom, unit, source, database_version, retrieval_date, caveat`

D-006 (option C; operating sequence noted by Mico 2026-10-29): exactly one hull form per record. In MP's dataset: `e_above_hull_eV_atom` is a number (form `mp_value`). Outside it: the explicit gap — `e_above_hull_eV_atom: "UNVERIFIED"`, `d006_status: "unverified_gap"`, `source: "unverified_materials_project_miss"`, and a `d006_gap_reason` naming what was searched and not found (required in the gap form). Never a CHGNet or mixed CHGNet/DFT hull number. A gap is the tripwire for D-006 option B: stop and tell Mico before any CHGNet-referenced hull work starts. Records written before this amendment carry a numeric value and no `d006_status` and remain valid (legacy mp_value).

## benchmark.json (per benchmark run)
`run_id, settings, materials: [{material_id, predicted_V, reference_V, diff_V, reference_citation_id}], ordering_match: bool, verdict ("pass" | "fail" | "measurement_only")`

## audit.md (per artifact, free-form markdown)
A checks table (item, status), a list of unverifiable items, and one verdict line: `PASS`, `PASS WITH FLAGS`, or `FAIL`.

## results/candidates/<id>.json (public-facing, post-promotion)
`material_id, formula, predicted_voltage_V, capacity_mAh_g, e_above_hull_eV_atom, run_id, audit_status, approved_by, approved_at, disclaimer_version, citations: [citation_id, ...]`

Under D-006 option C, `e_above_hull_eV_atom` may be the literal `"UNVERIFIED"` gap; in that form `d006_status: "unverified_gap"` and a non-empty `d006_gap_reason` are required so the public record stays self-explanatory.

## results/index.json
`{ "candidates": [<id>, ...], "benchmark_run_id": "<run-id>", "updated_at_utc": "<timestamp>" }`

## results/citations.json (added by T-005, needed by the website's citations column)
`citations: [{id, type, title, authors, year, identifier, version, accessed_at, verified: true, verified_by}, ...]`
One entry per citation id used by promoted results (and by benchmark runs). Fields follow `references/CITATION_STANDARD.md`'s citation record. `verified` must be `true`: an entry whose source was never opened live never enters `results/`.

Every JSON file is valid JSON, UTF-8, and traces back to a `run_id` in `pipeline/runs/` — except `results/citations.json`, whose provenance is the `references/literature/` notes (its entries carry `verified_by` instead of a `run_id`).
