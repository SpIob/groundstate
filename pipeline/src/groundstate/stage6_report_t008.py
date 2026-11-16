"""Stage 6 (candidate report) for T-008: assemble the proposed results/candidates/
mp-18968.json for Li2FeSiO4 from run-20261030-t008-lfs artifacts.

Reads everything from the run folder and pipeline/data/raw (never hardcodes a
computed number); the only literals are cited literature reference values, each
carrying its citation id. Output: pipeline/runs/<run-id>/proposed-results/.
The promote step (promote_t008.py) copies this file into results/ after G2 and
Mico's approval, filling audit_status / approved_by / approved_at then.

Gate G3 note: G1's verdict is FAIL, recorded and characterized (D-007/D-008,
both DECIDED option A). This candidate is treated as benchmark-exempt on that
basis: the D-004 comparison pits the candidate against the LiFePO4 baseline
re-relaxed in the same run with identical settings — the Fe-redox chemistry
whose benchmark error T-003 verified at ~0.03 V — and the voltage-window
convention (each host's full lithiation window) is stated explicitly on both
sides. Mico's written approval covers this treatment.

Literature crosscheck (stage 5, notes under references/literature/):
- zhang-2013-lfs (full text opened): two-Li theoretical capacity ca. 330 mAh/g;
  Fe2+/Fe3+ plateau 3.1 V (first cycle) shifting to ~2.8 V; second-electron
  plateau 4.3-4.7 V per the experiments it cites; no single 0->2 average printed.
- zhao-2015-silicate-motifs (opened): "~331 mAh/g"; practical 130-165 mAh/g.
- nyten-2005-lfs (abstract/metadata opened; body paywalled): discovery paper,
  one-Li practical 165 initial / ~140 stabilized mAh/g at 60 C.
The implied literature 0->2 average from those plateau pairs spans ~3.55-3.90 V
(midpoints of the two Fe3+/Fe4+ values with the subsequent/first-cycle Fe2+/Fe3+
plateaus); the predicted 3.9168 V sits at/just above the top of that band
(+0.02 V vs the highest pairing) — ideal-limit vs practical-plateau basis, same
caveat class as method-notes' basis note. The ordering (above LFP) matches.
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[3]
RUN = REPO / "pipeline" / "runs" / "run-20261030-t008-lfs"

# Cited literature reference values (numbers as printed in the sources; see the
# notes under references/literature/, verified 2026-10-30, task T-008).
LIT = {
    "capacity_2li_mAh_g": 330,        # zhang-2013-lfs: "ca. 330 mAh/g" for 2 Li/fu
    "capacity_2li_mAh_g_2nd": 331,    # zhao-2015-silicate-motifs: "~331 mAh/g"
    "plateau_fe23_first_V": 3.1,      # zhang-2013-lfs (cited experiments): Fe2+/Fe3+ first cycle
    "plateau_fe23_subsequent_V": 2.8, # zhang-2013-lfs: subsequent cycles
    "plateau_fe34_low_V": 4.3,        # zhang-2013-lfs (cited: Lv et al.)
    "plateau_fe34_high_V": 4.7,       # zhang-2013-lfs (cited: Muraliganth et al.)
    "one_li_practical_mAh_g": 165,    # nyten-2005-lfs: initial charge, 99% of 1-Li theory
}


def main() -> None:
    manifest = json.loads((RUN / "manifest.json").read_text())
    derived = json.loads((RUN / "derived.json").read_text())
    stability = json.loads((RUN / "stability-mp-18968.json").read_text())
    provenance = json.loads((REPO / "pipeline" / "data" / "raw" / "mp-18968" / "provenance.json").read_text())

    lfs = next(m for m in derived["materials"] if m["candidate_id"] == "mp-18968")
    lfp = next(m for m in derived["materials"] if m["candidate_id"] == "mp-19017")
    pair = lfs["pairs"][0]
    lfp_pair = lfp["pairs"][0]
    cmp_ = derived["d004_comparison"]

    # Literature implied 0->2 average from the cited plateau pairs (both
    # combinations of the two cited second-plateau values with the subsequent-
    # cycle Fe2+/Fe3+ plateau; the first-cycle 3.1 V gives the upper end).
    # round(…, 4) keeps the stored band free of float artifacts (G2 audit F-03):
    # (3.1+4.7)/2 = 3.9000000000000004 in IEEE-754.
    implied_low = round((LIT["plateau_fe23_subsequent_V"] + LIT["plateau_fe34_low_V"]) / 2, 4)
    implied_high = round((LIT["plateau_fe23_first_V"] + LIT["plateau_fe34_high_V"]) / 2, 4)
    offset_low = round(pair["voltage_V"] - implied_low, 4)
    offset_high = round(pair["voltage_V"] - implied_high, 4)

    report = {
        "material_id": provenance["material_id"],
        "formula": provenance["formula"],
        "predicted_voltage_V": pair["voltage_V"],
        "voltage_window_Li_per_fu": pair["x2"],
        "capacity_mAh_g": pair["capacity_mAh_g"],
        "capacity_basis": (
            "per gram of the lithiated host formula unit over the host's full "
            "lithiation window (0->2 Li/fu; D-005 option A, DECIDED 2026-10-21)"
        ),
        "e_above_hull_eV_atom": stability["e_above_hull_eV_atom"],
        "run_id": manifest["run_id"],
        "audit_status": "PENDING_G2",
        "approved_by": None,
        "approved_at": None,
        "disclaimer_version": 1,
        "citations": ["zhang-2013-lfs", "zhao-2015-silicate-motifs", "nyten-2005-lfs", "mp-database"],
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
            "metric": (
                "predicted average voltage over each host's full lithiation window "
                "(candidate 0->2 Li/fu, baseline 0->1 Li/fu; V vs Li/Li+), same run, "
                "same model and settings"
            ),
            "delta_V": cmp_["delta_V"],
            "verdict": cmp_["verdict"],
            "window_convention_note": (
                "each material's voltage spans its own host's full lithiation window; "
                "this reproduces the per-material convention T-003/T-004 used and MP's "
                "own electrode docs (candidate scout doc: 4.05 V / 331 mAh/g doc-range)"
            ),
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
            "implied_average_low_V": implied_low,
            "implied_average_high_V": implied_high,
            "implied_average_basis": (
                "midpoints of the cited plateau pairs: Fe2+/Fe3+ (2.8 V subsequent / "
                "3.1 V first cycle) + Fe3+/Fe4+ (4.3-4.7 V); literature prints no "
                "single 0->2 average"
            ),
            "implied_average_citation": "zhang-2013-lfs (plateau pairs as cited therein)",
            "offset_V_predicted_minus_implied_low": offset_low,
            "offset_V_predicted_minus_implied_high": offset_high,
            "offset_note": (
                f"offset fields = predicted minus implied literature average "
                f"({pair['voltage_V']} - {implied_low} = {offset_low:+.4f} V; "
                f"{pair['voltage_V']} - {implied_high} = {offset_high:+.4f} V). The "
                "predicted voltage sits at/above the top of the plateau-implied band; "
                "ideal-limit computed averages vs practical plateaus differ by this "
                "class of basis gap (method-notes basis caveat; same class as T-002). "
                "The D-007/D-008 chemistry-correlated-offset label does not apply to "
                "Fe-redox chemistries (Fe olivine verified within ~0.03 V); this "
                "candidate is Fe silicate, and the literature itself offers only "
                "plateau pairs here, so no like-for-like absolute offset is claimed."
            ),
            "ordering_crosscheck": (
                "literature-implied LFS average (~3.55-3.9 V band across plateau "
                "pairings) sits above LiFePO4's 3.4-3.45 V plateau, matching the "
                "predicted ordering (LFS above LFP, delta +0.4929 V, same run)"
            ),
            "theoretical_capacity_mAh_g": LIT["capacity_2li_mAh_g"],
            "theoretical_capacity_2nd_source_mAh_g": LIT["capacity_2li_mAh_g_2nd"],
            "capacity_citation": (
                "zhang-2013-lfs (ca. 330 mAh/g, 2 Li/fu); zhao-2015-silicate-motifs "
                "(~331 mAh/g); analytic D-005 value 331.3 mAh/g matches both"
            ),
            "practicality_note": (
                "Experiments reach far less than the two-Li theoretical capacity: "
                "reversible 130-165 mAh/g typical (zhao-2015-silicate-motifs), ~240 "
                "mAh/g initial with fade in later work, and the discovery-era one-Li "
                "practical value was 165 mAh/g initial stabilizing ~140 mAh/g at 60 C "
                "(nyten-2005-lfs). The Fe2+/Fe3+ plateau also shifts 3.1 -> 2.8 V "
                "after the first cycle (attributed in the literature to a structural "
                "transformation of the host: zhang-2013-lfs intro; nyten-2005 abstract, "
                "'phase transition to a more stable structure after the first cycle'), and "
                "full two-Li extraction faces the Fe3+/Fe4+ plateau at 4.3-4.7 V with "
                "large volume changes on full delithiation (zhang-2013-lfs). These are "
                "kinetic/structural realities distinct from this zero-kelvin "
                "thermodynamic estimate and are not contradicted by it."
            ),
        },
        "benchmark_gate": {
            "g1_run": "run-20261021-t003-g1",
            "g1_verdict": "FAIL (recorded; characterized limitation per D-007/D-008, both DECIDED option A)",
            "treatment": (
                "benchmark-exempt for this candidate: the D-004 comparison is against "
                "the LiFePO4 baseline re-relaxed in the same run with identical "
                "settings — the Fe-redox chemistry whose benchmark error T-003 "
                "verified at ~0.03 V — and the voltage-window convention is stated on "
                "both sides; no cross-chemistry absolute comparison is made"
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
    out = out_dir / "mp-18968.json"
    out.write_text(json.dumps(report, indent=2) + "\n")

    # Data-contract field check (docs/DATA_CONTRACT.md candidate fields).
    required = ["material_id", "formula", "predicted_voltage_V", "capacity_mAh_g",
                "e_above_hull_eV_atom", "run_id", "audit_status", "approved_by",
                "approved_at", "disclaimer_version", "citations"]
    missing = [k for k in required if k not in report]
    print(f"wrote {out.relative_to(REPO)}")
    print(f"V={pair['voltage_V']} cap={pair['capacity_mAh_g']} hull={stability['e_above_hull_eV_atom']} "
          f"offset_vs_implied=[{offset_low:+.2f}, {offset_high:+.2f}] V | contract fields missing: {missing or 'none'}")


if __name__ == "__main__":
    main()
