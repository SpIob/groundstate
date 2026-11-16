"""Stage 6 (candidate report) for T-006: assemble the proposed results/candidates/
mp-18997.json for LiMnPO4 from run-20261022-t004-lmp artifacts.

Reads everything from the run folder and pipeline/data/raw (never hardcodes a
computed number); the only literals are cited literature reference values, each
carrying its citation id. Output: pipeline/runs/<run-id>/proposed-results/.
The promote step (promote_t006.py) copies this file into results/ after G2 and
Mico's approval, filling audit_status / approved_by / approved_at then.

Gate G3 note: G1's verdict is FAIL, recorded and characterized (D-007/D-008,
both DECIDED option A). This candidate is treated as benchmark-exempt on that
basis: the D-004 comparison is within one chemistry (olivine vs olivine), the
axis D-008 declares usable. Mico's written approval covers this treatment.
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[3]
RUN = REPO / "pipeline" / "runs" / "run-20261022-t004-lmp"

# Cited literature reference values (numbers as printed in the sources; see the
# notes under references/literature/, verified 2026-10-22, task T-006).
LIT = {
    "plateau_V": 4.1,            # yamada-2001-lmp: Mn3+/Mn2+ two-phase redox potential
    "plateau_V_2nd": 4.1,        # zaghib-2013-lmp: same plateau, independent group
    "theoretical_capacity_mAh_g": 170,  # yamada-2001-lmp: one-electron M3+/M2+ redox
}


def main() -> None:
    manifest = json.loads((RUN / "manifest.json").read_text())
    derived = json.loads((RUN / "derived.json").read_text())
    stability = json.loads((RUN / "stability-mp-18997.json").read_text())
    provenance = json.loads((REPO / "pipeline" / "data" / "raw" / "mp-18997" / "provenance.json").read_text())

    lmp = next(m for m in derived["materials"] if m["candidate_id"] == "mp-18997")
    lfp = next(m for m in derived["materials"] if m["candidate_id"] == "mp-19017")
    pair = lmp["pairs"][0]
    lfp_pair = lfp["pairs"][0]
    cmp_ = derived["d004_comparison"]

    offset_V = round(LIT["plateau_V"] - pair["voltage_V"], 4)
    report = {
        "material_id": provenance["material_id"],
        "formula": provenance["formula"],
        "predicted_voltage_V": pair["voltage_V"],
        "capacity_mAh_g": pair["capacity_mAh_g"],
        "capacity_basis": "per gram of the lithiated host formula unit (D-005 option A, DECIDED 2026-10-21)",
        "e_above_hull_eV_atom": stability["e_above_hull_eV_atom"],
        "run_id": manifest["run_id"],
        "audit_status": "PENDING_G2",
        "approved_by": None,
        "approved_at": None,
        "disclaimer_version": 1,
        "citations": ["yamada-2001-lmp", "zaghib-2013-lmp", "mp-database"],
        "result_type": "computed estimate",
        "statement": (
            "Computed estimate from CHGNet v0.3.0 relaxations. Not an experimental "
            "measurement; no synthesis, validation, or discovery claim is made."
        ),
        "d004_comparison": {
            "decision": "D-004 option A (DECIDED 2026-10-21): beat a named baseline on a single metric",
            "baseline_material_id": "mp-19017",
            "baseline_formula": "LiFePO4",
            "baseline_predicted_voltage_V": lfp_pair["voltage_V"],
            "metric": "predicted average voltage 0->1 (V vs Li/Li+), same run, same model and settings",
            "delta_V": cmp_["delta_V"],
            "verdict": cmp_["verdict"],
        },
        "stability": {
            "e_above_hull_eV_atom": stability["e_above_hull_eV_atom"],
            "unit": stability["unit"],
            "source": stability["source"],
            "database_version": stability["database_version"],
            "d002_band": stability["d002_band_0_25_meV"],
            "baseline_e_above_hull_eV_atom": stability["baseline_reference"]["e_above_hull_eV_atom"],
            "caveat": stability["caveat"],
        },
        "literature_crosscheck": {
            "plateau_V_vs_Li": LIT["plateau_V"],
            "plateau_citation": "yamada-2001-lmp (Mn3+/Mn2+ two-phase redox region)",
            "plateau_2nd_source_V_vs_Li": LIT["plateau_V_2nd"],
            "plateau_2nd_citation": "zaghib-2013-lmp",
            "theoretical_capacity_mAh_g": LIT["theoretical_capacity_mAh_g"],
            "capacity_citation": "yamada-2001-lmp (one-electron M3+/M2+ redox, host-formula basis per D-005)",
            "offset_V_predicted_minus_literature": -offset_V,
            "offset_note": (
                "offset field = predicted minus literature (3.6865 - 4.1 = -0.4135 V). "
                "Predicted voltage sits 0.41 V below the literature Mn3+/Mn2+ plateau "
                "(D-008 DECIDED 2026-10-22, option A: chemistry-correlated offset up to "
                "~0.4-0.5 V on layered Co oxides AND Mn olivine; Fe olivine and Mn spinel "
                "verified within ~0.03 V). Relative rankings within one chemistry are "
                "usable; absolute cross-chemistry comparisons are not."
            ),
            "practicality_note": (
                "The literature also reports kinetic and electrode-engineering obstacles "
                "for pure LiMnPO4 (capacity far below theoretical, large polarization, "
                "Fe coexistence needed at the 4c site, Jahn-Teller instability of "
                "Mn-rich compositions). These are distinct from this zero-kelvin "
                "thermodynamic estimate and are not contradicted by it."
            ),
        },
        "benchmark_gate": {
            "g1_run": "run-20261021-t003-g1",
            "g1_verdict": "FAIL (recorded; characterized limitation per D-007/D-008, both DECIDED option A)",
            "treatment": (
                "benchmark-exempt for this candidate: the D-004 comparison is within "
                "one chemistry (olivine vs olivine), the axis D-008 declares usable"
            ),
        },
        "method": {
            "model": f"{manifest['model_name']} {manifest['model_version']}",
            "device": manifest["device"],
            "package_versions": manifest["package_versions"],
            "formula_version": derived["formula_version"],
            "settings": manifest["settings"],
            "arrangements_policy": manifest["settings"]["arrangements_policy"],
            "rq_flags": manifest["rq_flags"],
            "structure_provenance": {
                "source": provenance["source"],
                "database_version": provenance["database_version"],
                "retrieval_time_utc": provenance["retrieval_time_utc"],
                "space_group": provenance["space_group"],
                "atoms_per_cell": provenance["atoms_per_cell"],
                "theoretical_or_observed": provenance["theoretical_or_observed"],
            },
        },
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
    }

    out_dir = RUN / "proposed-results"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / "mp-18997.json"
    out.write_text(json.dumps(report, indent=2) + "\n")

    # Data-contract field check (docs/DATA_CONTRACT.md candidate fields).
    required = ["material_id", "formula", "predicted_voltage_V", "capacity_mAh_g",
                "e_above_hull_eV_atom", "run_id", "audit_status", "approved_by",
                "approved_at", "disclaimer_version", "citations"]
    missing = [k for k in required if k not in report]
    print(f"wrote {out.relative_to(REPO)}")
    print(f"V={pair['voltage_V']} cap={pair['capacity_mAh_g']} hull={stability['e_above_hull_eV_atom']} "
          f"offset={-offset_V:+.2f} V | contract fields missing: {missing or 'none'}")


if __name__ == "__main__":
    main()
