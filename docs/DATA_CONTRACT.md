# Data contract

Status: draft (JSON Schema files land in task T-005, once real output shapes exist). This is the plain-language version every skill writes against.

## provenance.json (per candidate, in `pipeline/data/raw/<id>/`)
`material_id, formula, space_group, atoms_per_cell, source ("materials_project" | "literature"), database_version, retrieval_time_utc, client_version, query, theoretical_or_observed, citation_id (if source is literature)`

## manifest.json (per run, in `pipeline/runs/<run-id>/`)
`run_id, git_sha, package_versions, model_name, model_version, device, seeds, input_ids, created_at_utc`

## derived.json (per run)
`candidate_id, pairs: [{x1, x2, voltage_V, capacity_mAh_g, mass_basis}], formula_version, run_id`

## stability.json (per candidate)
`material_id, e_above_hull_eV_atom, unit, source, database_version, retrieval_date, caveat`

## benchmark.json (per benchmark run)
`run_id, settings, materials: [{material_id, predicted_V, reference_V, diff_V, reference_citation_id}], ordering_match: bool, verdict ("pass" | "fail" | "measurement_only")`

## audit.md (per artifact, free-form markdown)
A checks table (item, status), a list of unverifiable items, and one verdict line: `PASS`, `PASS WITH FLAGS`, or `FAIL`.

## results/candidates/<id>.json (public-facing, post-promotion)
`material_id, formula, predicted_voltage_V, capacity_mAh_g, e_above_hull_eV_atom, run_id, audit_status, approved_by, approved_at, disclaimer_version, citations: [citation_id, ...]`

## results/index.json
`{ "candidates": [<id>, ...], "benchmark_run_id": "<run-id>", "updated_at_utc": "<timestamp>" }`

Every JSON file is valid JSON, UTF-8, and traces back to a `run_id` in `pipeline/runs/`.
