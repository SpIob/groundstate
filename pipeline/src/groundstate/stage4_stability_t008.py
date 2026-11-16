"""Stage 4 (gs-stability-score) for T-008: energy above hull from Materials
Project for the Li2FeSiO4 candidate (mp-18968), with the skill's second-query
verification. Baseline LiFePO4's stability is already on record from T-003
(0.0 meV/atom, db 2026.09.28) and mp-18968's stage-1 provenance reports 0.0.

Cutoffs are decision D-002's (0-25 meV/atom strict band); this script records
values only. Competing phases: MP's thermo doc does not return them -> UNVERIFIED.
D-006 form: mp_value (mp-18968 is in MP's dataset; scout + stage 1 both
reported a numeric hull value), so no gap fields are written.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[3]
RUN = REPO / "pipeline" / "runs" / "run-20261030-t008-lfs"

MATERIALS = [("mp-18968", "Li2FeSiO4")]
CAVEAT = (
    "Zero-kelvin computed value (DFT, Materials Project); ignores kinetics and "
    "entropy. Says nothing about whether the phase actually forms under real "
    "synthesis conditions."
)


def load_key() -> None:
    if os.environ.get("MP_API_KEY"):
        return
    env = pathlib.Path.home() / ".hermes" / "profiles" / "groundstate" / ".env"
    for line in env.read_text().splitlines():
        if line.startswith("MP_API_KEY="):
            os.environ["MP_API_KEY"] = line.split("=", 1)[1].strip().strip("\"'")
            return
    sys.exit("MP_API_KEY not found")


def main() -> None:
    load_key()
    from mp_api.client import MPRester

    results = {}
    retrieval_date = dt.datetime.now(dt.timezone.utc).date().isoformat()
    with MPRester() as mpr:
        db_version = getattr(mpr, "db_version", None) or "UNVERIFIED"
        for mid, formula in MATERIALS:
            # query 1: thermo doc, explicitly the canonical corrected set
            # (GGA_GGA+U_R2SCAN = what MP material pages and summary report).
            tdocs = mpr.materials.thermo.search(material_ids=[mid])
            by_type = {str(d.thermo_type): float(d.energy_above_hull) for d in tdocs}
            canonical = "GGA_GGA+U_R2SCAN"
            v1 = by_type[canonical]
            # query 2 (skill verification): independent summary-doc query
            sdoc = mpr.materials.summary.search(material_ids=[mid], fields=["material_id", "energy_above_hull"])[0]
            v2 = float(sdoc.energy_above_hull)
            match = abs(v1 - v2) < 1e-9
            # cross-check against stage-1 provenance (third recorded value)
            prov = json.loads((REPO / "pipeline" / "data" / "raw" / mid / "provenance.json").read_text())
            v3 = prov["energy_above_hull_eV_atom_as_reported"]
            rec = {
                "material_id": mid,
                "formula": formula,
                "e_above_hull_eV_atom": v1,
                "thermo_type": canonical,
                "unit": "eV/atom",
                "source": "materials_project (thermo doc, double-queried)",
                "database_version": db_version,
                "retrieval_date": retrieval_date,
                "second_query_value": v2,
                "second_query_match": match,
                "stage1_provenance_value": v3,
                "alternate_thermo_values": by_type,
                "competing_phases": "UNVERIFIED (not returned by the installed client's thermo doc)",
                "d002_band_0_25_meV": "within" if v1 * 1000 <= 25 else "above",
                "baseline_reference": {
                    "material_id": "mp-19017",
                    "e_above_hull_eV_atom": 0.0,
                    "source_ref": "run-20261021-t003-g1/stability-mp-19017.json (db 2026.09.28)",
                },
                "caveat": CAVEAT,
            }
            (RUN / f"stability-{mid}.json").write_text(json.dumps(rec, indent=2) + "\n")
            results[mid] = rec
            print(f"{mid} {formula}: {v1*1000:.1f} meV/atom | 2nd query match={match} "
                  f"| stage1 match={abs(v1-v3)<1e-9} | db={db_version} | "
                  f"D-002 band: {rec['d002_band_0_25_meV']}")
    (RUN / "stability-index.json").write_text(json.dumps(
        {"run_id": "run-20261030-t008-lfs", "materials": {k: v["e_above_hull_eV_atom"] for k, v in results.items()},
         "database_version": db_version, "retrieval_date": retrieval_date}, indent=2) + "\n")


if __name__ == "__main__":
    main()
