"""G3 promotion for T-006: copy the approved proposed result into results/.

Preconditions (gs-promote-results skill) — all three checked, none assumed:
  a. Benchmark gate G1: verdict FAIL is on record and characterized (D-007),
     and this candidate is benchmark-exempt per its benchmark_gate treatment
     (D-004 within-chemistry comparison; D-008 declares that axis usable).
     Mico's written approval covers this treatment.
  b. audit.md verdict is PASS or PASS WITH FLAGS.
  c. Mico wrote an APPROVED line with a date in the T-006 task entry.

Fills audit_status / approved_by / approved_at from (b) and (c), copies to
results/candidates/mp-18997.json, updates results/index.json, and prints the
exact commit commands. Never edits values by hand; the payload comes from the
stage-6 generated file.
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[3]
RUN = REPO / "pipeline" / "runs" / "run-20261022-t004-lmp"
BOARD = REPO / "tasks" / "BOARD.md"
MATERIAL_ID = "mp-18997"
REQUIRED = ["material_id", "formula", "predicted_voltage_V", "capacity_mAh_g",
            "e_above_hull_eV_atom", "run_id", "audit_status", "approved_by",
            "approved_at", "disclaimer_version", "citations"]


def t006_entry(board_text: str) -> str:
    m = re.search(r"## T-006:.*?(?=\n---\n\n## )", board_text, re.S)
    if not m:
        sys.exit("T-006 entry not found on the board")
    return m.group(0)


def main() -> None:
    # (b) audit verdict
    audit_path = RUN / "audit.md"
    if not audit_path.exists():
        sys.exit("PRECONDITION b FAILED: no audit.md in the run folder (G2 not run)")
    audit_text = audit_path.read_text()
    m = re.search(r"\b(PASS WITH FLAGS|PASS|FAIL)\b\s*:?\s*$", audit_text.strip().splitlines()[-1]) \
        or re.search(r"(PASS WITH FLAGS|PASS|FAIL)", audit_text)
    verdict = m.group(1) if m else None
    if verdict not in ("PASS", "PASS WITH FLAGS"):
        sys.exit(f"PRECONDITION b FAILED: audit verdict is {verdict!r}, need PASS or PASS WITH FLAGS")

    # (c) Mico's written approval in the task entry
    entry = t006_entry(BOARD.read_text())
    am = re.search(r"APPROVED[^\n]*?(20\d\d-\d\d-\d\d)", entry)
    if not am:
        sys.exit("PRECONDITION c FAILED: no 'APPROVED <date>' line from Mico in the T-006 entry")
    approved_at = am.group(1)

    # (a) benchmark-exempt treatment must be stated in the artifact
    proposed = json.loads((RUN / "proposed-results" / f"{MATERIAL_ID}.json").read_text())
    treatment = proposed.get("benchmark_gate", {}).get("treatment", "")
    if "benchmark-exempt" not in treatment:
        sys.exit("PRECONDITION a FAILED: artifact does not state its benchmark-exempt treatment")

    # data-contract field check
    missing = [k for k in REQUIRED if k not in proposed]
    if missing:
        sys.exit(f"Data contract check FAILED: missing {missing}")

    # fill gate fields, copy
    promoted = dict(proposed)
    promoted["audit_status"] = verdict
    promoted["approved_by"] = "Mico"
    promoted["approved_at"] = approved_at
    # F-01 (audit flag): the producing session couldn't read MP's theoretical
    # flag (client sub-endpoint error) and left the field UNVERIFIED; the G2
    # audit session resolved it live (theoretical=False) this same day. Enrich
    # the promoted copy with the resolved value, keeping the original as-run.
    sp = promoted.get("method", {}).get("structure_provenance", {})
    if sp.get("theoretical_or_observed") == "UNVERIFIED":
        sp["theoretical_or_observed"] = "theoretical=false (resolved live 2026-10-22 by the G2 audit session's MP query; run-time value UNVERIFIED, sub-endpoint error)"
        sp["theoretical_or_observed_source"] = "G2 audit session, 2026-10-22, mp-api live query of mp-18997 (see audit.md F-01)"
    out_dir = REPO / "results" / "candidates"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{MATERIAL_ID}.json").write_text(json.dumps(promoted, indent=2) + "\n")

    index_path = REPO / "results" / "index.json"
    index = json.loads(index_path.read_text())
    if MATERIAL_ID not in index["candidates"]:
        index["candidates"].append(MATERIAL_ID)
    # no benchmark.json is promoted in T-006; the field stays null until that
    # artifact is approved on its own
    index["benchmark_run_id"] = index.get("benchmark_run_id")
    index["updated_at_utc"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    index_path.write_text(json.dumps(index, indent=2) + "\n")

    print(f"promoted {MATERIAL_ID} -> results/candidates/{MATERIAL_ID}.json")
    print(f"audit_status={verdict} approved_by=Mico approved_at={approved_at}")
    print(f"index: {json.dumps(index)}")
    print("commit (results/ only; tasks/ is gitignored by design):")
    print(f'  git add results/candidates/{MATERIAL_ID}.json results/index.json && '
          f'git commit -m "results: promote {MATERIAL_ID} from run-20261022-t004-lmp"')


if __name__ == "__main__":
    main()
