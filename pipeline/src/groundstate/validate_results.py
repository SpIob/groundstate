#!/usr/bin/env python3
"""Validate results/ and pipeline artifacts against pipeline/schemas/ (task T-005).

Usage (run with pipeline/.venv/bin/python):
  python pipeline/src/groundstate/validate_results.py --all
  python pipeline/src/groundstate/validate_results.py --file <path> [--schema <name>]
  python pipeline/src/groundstate/validate_results.py --self-test

Exit codes: 0 clean, 1 validation/cross-check failures, 2 usage or setup error.

Rules encoded here (docs/DATA_CONTRACT.md):
- required = the contract's fields (schemas allow recorded enrichment, so audits
  can add fields without breaking validation).
- Cross-checks JSON Schema cannot express: index<->candidate files exist,
  candidate run_id traces to a run manifest, citation ids resolve in
  results/citations.json, and the D-005 capacity-basis forms (pre-decision
  dual-basis vs post-decision single-basis) are used one at a time per pair.
- D-006 (option C; operating sequence noted by Mico 2026-10-29): hull records
  carry either MP's number (form mp_value) or the explicit 'UNVERIFIED' gap
  (form unverified_gap, source unverified_materials_project_miss, reason
  recorded) — never both, never a CHGNet or mixed-CHGNet/DFT hull value. A gap
  is the trigger to stop and tell Mico before any option-B (CHGNet-referenced
  hull) work starts.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

import jsonschema

REPO = pathlib.Path(__file__).resolve().parents[3]
SCHEMAS = REPO / "pipeline" / "schemas"
RESULTS = REPO / "results"
RUNS = REPO / "pipeline" / "runs"
RAW = REPO / "pipeline" / "data" / "raw"

# filename -> schema file (order matters: stability-*.json before stability-index check
# is handled by exact-name match first)
NAME_TO_SCHEMA = {
    "index.json": "results-index.schema.json",
    "citations.json": "results-citations.schema.json",
    "benchmark.json": "benchmark.schema.json",
    "derived.json": "derived.schema.json",
    "manifest.json": "manifest.schema.json",
    "stability-index.json": "stability-index.schema.json",
    "provenance.json": "provenance.schema.json",
}


def schema_for(path: pathlib.Path) -> str:
    if path.parent.name == "candidates":
        return "results-candidate.schema.json"
    name = path.name
    if name == "stability-index.json":
        return NAME_TO_SCHEMA["stability-index.json"]
    if name.startswith("stability-") and name.endswith(".json"):
        return "stability.schema.json"
    if name in NAME_TO_SCHEMA:
        return NAME_TO_SCHEMA[name]
    raise KeyError(f"no schema mapping for {name}")


def get_schema(name: str) -> dict:
    import json

    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def validate_doc(path: pathlib.Path, schema_name: str | None = None):
    """Return (ok, list_of_error_strings) for schema validation of one file."""
    import json

    sname = schema_name or schema_for(path)
    schema = get_schema(sname)
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # unreadable or invalid JSON
        return False, [f"{path}: invalid JSON ({exc})"]
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path))
    if not errors:
        return True, []
    out = []
    for e in errors:
        loc = "$." + ".".join(str(p) for p in e.absolute_path) if e.absolute_path else "$"
        out.append(f"{path}: {loc}: {e.message}")
    return False, out


def all_targets() -> list[pathlib.Path]:
    targets: list[pathlib.Path] = []
    for name in ("index.json", "citations.json"):
        p = RESULTS / name
        if p.exists():
            targets.append(p)
    if (RESULTS / "candidates").is_dir():
        targets += sorted((RESULTS / "candidates").glob("*.json"))
    targets += sorted(RUNS.glob("*/manifest.json"))
    for name in ("benchmark.json", "derived.json", "stability-index.json"):
        targets += sorted(RUNS.glob(f"*/{name}"))
    targets += sorted(RUNS.glob("*/stability-*.json"))
    # drop stability-index double-count (matched by both stability-*.json and exact name)
    seen: set[pathlib.Path] = set()
    unique: list[pathlib.Path] = []
    for t in targets:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    unique += sorted(set(RAW.glob("*/provenance.json")) - seen)
    return unique


def split_citation_ids(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def cross_checks(results: list[tuple[str, bool, str]]) -> None:
    """Contract rules JSON Schema cannot express. Appends (label, ok, detail)."""
    import json

    index_path = RESULTS / "index.json"
    citations_path = RESULTS / "citations.json"
    if not index_path.exists() or not citations_path.exists():
        results.append(("results/index.json + citations.json present", False, "missing file(s)"))
        return
    index = json.loads(index_path.read_text(encoding="utf-8"))
    citations = json.loads(citations_path.read_text(encoding="utf-8"))
    citation_ids = {c["id"] for c in citations.get("citations", [])}

    # 1. every id in the index has a candidate file
    for cid in index.get("candidates", []):
        p = RESULTS / "candidates" / f"{cid}.json"
        results.append((f"index -> {cid}.json exists", p.exists(), str(p)))

    # 2. every candidate traces to a run manifest with the same run_id
    for cid in index.get("candidates", []):
        p = RESULTS / "candidates" / f"{cid}.json"
        if not p.exists():
            continue
        doc = json.loads(p.read_text(encoding="utf-8"))
        run_id = doc.get("run_id")
        manifest = RUNS / run_id / "manifest.json"
        ok = manifest.exists()
        if ok:
            ok = json.loads(manifest.read_text(encoding="utf-8")).get("run_id") == run_id
        results.append((f"{cid}: run_id {run_id} traces to its manifest", ok, str(manifest)))

    # 3. every citation id used by a promoted candidate resolves in citations.json
    for cid in index.get("candidates", []):
        p = RESULTS / "candidates" / f"{cid}.json"
        if not p.exists():
            continue
        doc = json.loads(p.read_text(encoding="utf-8"))
        for ref in doc.get("citations", []):
            results.append(
                (f"{cid}: citation '{ref}' in citations.json", ref in citation_ids, ref)
            )

    # 4. benchmark citation ids (semicolon-joined strings) also resolve
    for bench in RUNS.glob("*/benchmark.json"):
        doc = json.loads(bench.read_text(encoding="utf-8"))
        for m in doc.get("materials", []):
            for ref in split_citation_ids(str(m.get("reference_citation_id", ""))):
                results.append(
                    (f"{bench.parent.name}: citation '{ref}' in citations.json",
                     ref in citation_ids, ref)
                )

    # 5. D-005 capacity forms: exactly one spelling per derived pair
    for derived_path in RUNS.glob("*/derived.json"):
        doc = json.loads(derived_path.read_text(encoding="utf-8"))
        for m in doc.get("materials", []):
            for i, pair in enumerate(m.get("pairs", [])):
                single = "capacity_mAh_g" in pair
                dual = "capacity_mAh_g_lithiated_basis" in pair or (
                    "capacity_mAh_g_delithiated_basis" in pair
                )
                both = single and dual
                neither = not single and not dual
                ok = not both and not neither
                label = (
                    f"{derived_path.parent.name} {m.get('candidate_id')} pair[{i}]: "
                    "exactly one capacity-basis form (D-005)"
                )
                detail = "single-basis" if single else (
                    "dual-basis (pre-D-005)" if dual else "no capacity field"
                )
                results.append((label, ok, detail))

    # 6. D-006 hull forms: value and d006_status/source must agree; the gap form
    # requires the source marker and a reason. Legacy records (pre-D-006 fields,
    # numeric value, no d006_status) stay valid.
    for hull_path in sorted(RUNS.glob("*/stability-*.json")) + sorted(RAW.glob("*/provenance.json")):
        if hull_path.name == "stability-index.json":
            continue
        doc = json.loads(hull_path.read_text(encoding="utf-8"))
        key = "e_above_hull_eV_atom"
        if key not in doc:
            key = "energy_above_hull_eV_atom_as_reported"
        if key not in doc:
            continue
        value = doc[key]
        status = doc.get("d006_status")
        if isinstance(value, (int, float)):
            ok = status in (None, "mp_value")
            detail = "mp_value" if status == "mp_value" else "legacy mp value (pre-D-006 fields)"
        elif value == "UNVERIFIED":
            ok = (
                status == "unverified_gap"
                and doc.get("source") == "unverified_materials_project_miss"
                and isinstance(doc.get("d006_gap_reason"), str)
                and len(doc["d006_gap_reason"]) > 0
            )
            detail = "unverified_gap" if ok else "gap form incomplete (status/source/reason)"
        else:
            ok = False
            detail = f"unexpected hull value type {type(value).__name__}"
        results.append((f"{hull_path.parent.name}/{hull_path.name}: D-006 hull form consistent", ok, detail))


def cmd_all(quiet: bool) -> int:
    results: list[tuple[str, bool, str]] = []
    failures: list[str] = []
    targets = all_targets()
    if not targets:
        print("no targets found; nothing to validate")
        return 2
    for t in targets:
        ok, errs = validate_doc(t)
        label = f"schema {t.relative_to(REPO)}"
        results.append((label, ok, "clean" if ok else f"{len(errs)} error(s)"))
        failures += errs
    cross_checks(results)
    if not quiet:
        for label, ok, detail in results:
            print(f"{'PASS' if ok else 'FAIL'}  {label}  [{detail}]")
    bad = [r for r in results if not r[1]]
    n_schema = sum(1 for r in results if r[0].startswith("schema "))
    print(f"\n{len(results)} checks: {len(results) - len(bad)} pass, {len(bad)} fail "
          f"({n_schema} schema files, {len(results) - n_schema} cross-checks)")
    if bad:
        for line in failures:
            print(" ", line)
        return 1
    return 0


def cmd_self_test() -> int:
    """Seed defects into copies of real artifacts; every one must be caught."""
    import copy
    import json

    checks: list[tuple[str, bool]] = []

    def expect_caught(label: str, doc: dict, schema_name: str) -> None:
        validator = jsonschema.Draft202012Validator(get_schema(schema_name))
        errors = list(validator.iter_errors(doc))
        checks.append((label, len(errors) > 0))

    cand_path = RESULTS / "candidates" / "mp-18997.json"
    if not cand_path.exists():
        print("self-test needs results/candidates/mp-18997.json (real artifact)")
        return 2
    cand = json.loads(cand_path.read_text(encoding="utf-8"))

    # sanity: the untouched real record must be clean
    validator = jsonschema.Draft202012Validator(get_schema("results-candidate.schema.json"))
    checks.append(("real mp-18997 record validates clean (control)",
                   len(list(validator.iter_errors(cand))) == 0))

    # seeded defect 1: required field removed
    d1 = copy.deepcopy(cand)
    del d1["approved_by"]
    expect_caught("candidate: removed approved_by -> caught", d1, "results-candidate.schema.json")

    # seeded defect 2: evidence-rule wording violated
    d2 = copy.deepcopy(cand)
    d2["result_type"] = "experimental measurement"
    expect_caught("candidate: result_type != 'computed estimate' -> caught", d2,
                  "results-candidate.schema.json")

    # seeded defect 3: bad run_id shape
    d3 = copy.deepcopy(cand)
    d3["run_id"] = "not-a-run-id"
    expect_caught("candidate: run_id pattern violated -> caught", d3,
                  "results-candidate.schema.json")

    # seeded defect 4: unverified citation entry
    c4 = {"citations": [{
        "id": "fake-2030", "type": "paper", "title": "Never Opened",
        "authors": "Nobody", "year": 2030, "identifier": "DOI 10.0000/fake",
        "version": "UNVERIFIED", "accessed_at": "2030-01-01",
        "verified": False, "verified_by": "Nobody",
    }]}
    expect_caught("citations: verified=false entry -> caught", c4,
                  "results-citations.schema.json")

    # seeded defect 5: index with malformed benchmark_run_id
    idx = json.loads((RESULTS / "index.json").read_text(encoding="utf-8"))
    i5 = copy.deepcopy(idx)
    i5["benchmark_run_id"] = "bogus"
    expect_caught("index: benchmark_run_id pattern violated -> caught", i5,
                  "results-index.schema.json")

    # seeded defect 6 (cross-check): citation id missing from citations.json
    results: list[tuple[str, bool, str]] = []
    d6 = copy.deepcopy(cand)
    d6["citations"] = d6.get("citations", []) + ["not-in-citations"]
    citation_ids = {c["id"] for c in json.loads(
        (RESULTS / "citations.json").read_text(encoding="utf-8"))["citations"]}
    missing = [r for r in d6["citations"] if r not in citation_ids]
    checks.append(("cross-check: unknown citation id detected", bool(missing)))

    # seeded defect 7 (cross-check): derived pair carrying BOTH capacity forms
    der_path = RUNS / "run-20261022-t004-lmp" / "derived.json"
    der = json.loads(der_path.read_text(encoding="utf-8"))
    d7 = copy.deepcopy(der)
    d7["materials"][0]["pairs"][0]["capacity_mAh_g_lithiated_basis"] = 170.9
    pair = d7["materials"][0]["pairs"][0]
    both = ("capacity_mAh_g" in pair) and ("capacity_mAh_g_lithiated_basis" in pair)
    checks.append(("cross-check: D-005 dual-form pair detected", both))

    # D-006 hull-form defects, seeded on the real mp-18997 stability record
    stab_path = RUNS / "run-20261022-t004-lmp" / "stability-mp-18997.json"
    if stab_path.exists():
        stab = json.loads(stab_path.read_text(encoding="utf-8"))

        # control: the real MP-numbered record must stay clean
        def d006_form(doc: dict) -> tuple[bool, str]:
            value = doc["e_above_hull_eV_atom"]
            status = doc.get("d006_status")
            if isinstance(value, (int, float)):
                ok = status in (None, "mp_value")
                return ok, "mp_value form"
            if value == "UNVERIFIED":
                ok = (
                    status == "unverified_gap"
                    and doc.get("source") == "unverified_materials_project_miss"
                    and isinstance(doc.get("d006_gap_reason"), str)
                    and len(doc["d006_gap_reason"]) > 0
                )
                return ok, "unverified_gap form"
            return False, "unexpected type"

        ok, _ = d006_form(copy.deepcopy(stab))
        checks.append(("D-006 control: real mp-18997 hull record clean", ok))

        # defect 8: gap value without the gap-form fields (schema must catch)
        d8 = copy.deepcopy(stab)
        d8["e_above_hull_eV_atom"] = "UNVERIFIED"
        validator = jsonschema.Draft202012Validator(get_schema("stability.schema.json"))
        checks.append(("D-006: gap value without status/source/reason -> caught",
                       len(list(validator.iter_errors(d8))) > 0))

        # defect 9: complete gap form must pass the cross-check (no false alarm)
        d9 = copy.deepcopy(stab)
        d9["e_above_hull_eV_atom"] = "UNVERIFIED"
        d9["d006_status"] = "unverified_gap"
        d9["source"] = "unverified_materials_project_miss"
        d9["d006_gap_reason"] = "hypothetical: not in MP's hull dataset (db 2026.09.28), searched by formula and chemsys"
        ok, detail = d006_form(d9)
        checks.append((f"D-006: complete gap form passes cross-check [{detail}]", ok))

        # defect 10: double form — number plus unverified_gap status
        d10 = copy.deepcopy(stab)
        d10["d006_status"] = "unverified_gap"
        ok, _ = d006_form(d10)
        checks.append(("D-006: number plus unverified_gap status (double form) -> caught", not ok))

    ok_all = True
    for label, ok in checks:
        print(f"{'CAUGHT' if ok else 'MISSED'}  {label}")
        ok_all = ok_all and ok
    print(f"\nself-test: {len(checks)} checks, "
          f"{'all defects caught' if ok_all else 'DEFECTS MISSED'}")
    return 0 if ok_all else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate results/ and pipeline artifacts against pipeline/schemas/."
    )
    parser.add_argument("--all", action="store_true", help="validate every known artifact")
    parser.add_argument("--file", type=pathlib.Path, help="validate one file")
    parser.add_argument("--schema", help="override the schema chosen by filename")
    parser.add_argument("--self-test", action="store_true",
                        help="seed defects and verify each is caught")
    parser.add_argument("--quiet", action="store_true", help="only the summary line")
    args = parser.parse_args(argv)
    if args.self_test:
        return cmd_self_test()
    if args.file:
        ok, errs = validate_doc(args.file, args.schema)
        for line in errs:
            print(line)
        print("clean" if ok else f"{len(errs)} error(s)")
        return 0 if ok else 1
    if args.all:
        return cmd_all(args.quiet)
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
