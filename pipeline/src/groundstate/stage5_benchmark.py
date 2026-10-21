"""Assemble benchmark.json for run-20261021-t003-g1 (gate G1) from the run's
stage outputs. Applies decision D-003: option B gate (|predicted - literature|
<= 0.3 V for all three) with option C's relative-order check reported alongside.
Also records MP's computed electrode voltages as the like-for-like second
reference (method-notes basis caveat / benchmark-set comparison rules).
"""
from __future__ import annotations

import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[3]
RUN = REPO / "pipeline" / "runs" / "run-20261021-t003-g1"
RUN_ID = "run-20261021-t003-g1"

# D-003 option B gate and option C ordering check
GATE_ABS_V = 0.3
# Literature references from references/science/benchmark-set.md (T-002, verified)
REFS = {
    "lco": {"mid": "mp-22526", "lit_V": 3.9, "lit_cap": 274.0,
            "citation": "zhang-2022-lco",
            "mp_pair_V": 3.789750783333332, "mp_battery": "mp-aaaabhik_Li (pair Li(CoO2)3->LiCoO2 window 0->0.25; 0->1 average 3.7898)"},
    "lfp": {"mid": "mp-19017", "lit_V": 3.4, "lit_cap": 170.0,
            "citation": "wu-2014-lfp",
            "mp_pair_V": 3.499170160833334, "mp_battery": "mp-aaaabcdl_Li (pair FePO4->LiFePO4, window 0->1)"},
    "lmo": {"mid": "mp-22584", "lit_V": 4.0, "lit_cap": 148.0,
            "citation": "zhang-2022-lco; huang-2020-lmo; eriksson-2001",
            "mp_pair_V": 3.839347458333333, "mp_battery": "mp-aaaabhkq_Li adj_pair[0] MnO2->LiMn2O4, window 0->1"},
}


def main() -> None:
    manifest = json.loads((RUN / "manifest.json").read_text())
    derived = json.loads((RUN / "derived.json").read_text())
    by_tag = {m["material_tag"]: m for m in derived["materials"]}

    rows = []
    for tag in ("lco", "lfp", "lmo"):
        ref = REFS[tag]
        pair = by_tag[tag]["pairs"][0]
        v = pair["voltage_V"]
        cap = pair["capacity_mAh_g_lithiated_basis"]
        stab = json.loads((RUN / f"stability-{ref['mid']}.json").read_text())
        x1 = json.loads((RUN / "relaxations" / f"{tag}-x1-arr00.json").read_text())
        rows.append({
            "material_id": ref["mid"],
            "formula": {"lco": "LiCoO2", "lfp": "LiFePO4", "lmo": "LiMn2O4"}[tag],
            "predicted_V": v,
            "reference_V": ref["lit_V"],
            "diff_V": round(v - ref["lit_V"], 4),
            "reference_citation_id": ref["citation"],
            "reference_basis": "literature practical/operating or plateau voltage (approximate reference per method-notes basis caveat)",
            "within_gate": abs(v - ref["lit_V"]) <= GATE_ABS_V,
            "predicted_capacity_mAh_g": cap,
            "reference_capacity_mAh_g": ref["lit_cap"],
            "capacity_diff_mAh_g": round(cap - ref["lit_cap"], 1),
            "capacity_mass_basis": "lithiated host formula mass (D-005 OPEN: delithiated basis also recorded in derived.json)",
            "mp_computed_reference_V": round(ref["mp_pair_V"], 4),
            "mp_computed_diff_V": round(v - ref["mp_pair_V"], 4),
            "mp_reference_source": ref["mp_battery"],
            "e_above_hull_eV_atom": stab["e_above_hull_eV_atom"],
            "converged": x1["converged"],
            "arrangement_ids": pair["arrangement_ids"],
        })

    # D-003 option C: ordering check. benchmark-set rule: LCO vs LMO treated as
    # effectively tied in the reference (3.9 ~ 4.0); LFP strictly lowest.
    v_by_tag = {t: by_tag[t]["pairs"][0]["voltage_V"] for t in ("lco", "lfp", "lmo")}
    lfp_lowest = v_by_tag["lfp"] < v_by_tag["lco"] and v_by_tag["lfp"] < v_by_tag["lmo"]
    top_tie_ok = abs(v_by_tag["lco"] - v_by_tag["lmo"]) <= GATE_ABS_V  # within reference noise band
    ordering_match = bool(lfp_lowest and top_tie_ok)
    strict_order = sorted(v_by_tag, key=v_by_tag.get, reverse=True)

    gate_pass = all(r["within_gate"] for r in rows)
    verdict = "pass" if gate_pass else "fail"

    doc = {
        "run_id": RUN_ID,
        "created_from": "stages 1-4 outputs in this run folder; see manifest.json for settings and versions",
        "settings": manifest["settings"],
        "gate": {
            "decision": "D-003 option B: |predicted - literature| <= 0.3 V for all three materials",
            "ordering_check": "D-003 option C alongside: LCO~LMO tied (reference noise), LFP strictly lowest",
            "abs_threshold_V": GATE_ABS_V,
        },
        "materials": rows,
        "ordering_match": ordering_match,
        "ordering_details": {
            "predicted_strict_order_high_to_low": strict_order,
            "lfp_strictly_lowest": lfp_lowest,
            "lco_lmo_gap_V": round(abs(v_by_tag["lco"] - v_by_tag["lmo"]), 4),
            "tied_top_treatment": "LCO vs LMO treated as tied per references/science/benchmark-set.md",
        },
        "verdict": verdict,
        "verdict_rationale": "",
        "flags": [
            "RQ-1 answered for this run: CHGNet accuracy is NOT even across chemistries - LFP and LMO are within 0.03 V of literature; LCO is 0.41 V low vs literature (0.30 V low vs MP's own DFT, inside the band).",
            "LCO gap is NOT explained by the reference-basis caveat: a diagnostic x-grid on the relaxed cell (diagnostic-lco-grid.json) gives segment voltages 3.730 / 3.523 / 3.219 V for 0->1/3, 1/3->2/3, 2/3->1 - the profile slopes down with x as expected, but every segment sits below the literature window, so the offset is chemistry-correlated (model-level) rather than a basis artifact; RQ-1 answer sharpened. Candidate mechanism for later investigation: Co3+/Co4+ spin/magnetic-ordering treatment (RQ-3) - unverified hypothesis, not run here.",
            "LMO energy above hull is 45.0 meV/atom (MP GGA_GGA+U_R2SCAN, db 2026.09.28) - above D-002's strict 25 meV band; D-002 governs candidate screening, benchmark membership is D-001 and unaffected.",
            "MP thermo endpoint returns multiple thermo types; the canonical GGA_GGA+U_R2SCAN value was selected explicitly and cross-checked against the summary doc (all three materials match).",
            "Arrangements: one per lithiation state (RQ-2 cap recorded in manifest); capacities are exact by construction, so capacity columns verify the bookkeeping, not model accuracy.",
            "D-005 OPEN: capacity mass basis 'lithiated host formula mass' used for comparison (matches Eriksson 2001 worked example); delithiated basis recorded alongside in derived.json.",
        ],
    }
    fails = [r["material_id"] for r in rows if not r["within_gate"]]
    doc["verdict_rationale"] = (
        f"D-003 option B gate {'PASS' if gate_pass else 'FAIL'}: "
        + ", ".join(f"{r['formula']} {r['diff_V']:+.2f} V" for r in rows)
        + f". Outside band: {fails if fails else 'none'}. Ordering check (option C): "
        f"{'match' if ordering_match else 'mismatch'}."
    )
    (RUN / "benchmark.json").write_text(json.dumps(doc, indent=2) + "\n")

    print("G1 benchmark table (run-20261021-t003-g1)")
    print(f"{'material':10} {'pred V':>7} {'lit V':>6} {'diff':>7} {'gate':>5} {'MP V':>7} {'MPdiff':>7} {'cap':>7} {'capref':>7}")
    for r in rows:
        print(f"{r['formula']:10} {r['predicted_V']:7.3f} {r['reference_V']:6.2f} "
              f"{r['diff_V']:+7.3f} {'ok' if r['within_gate'] else 'MISS':>5} "
              f"{r['mp_computed_reference_V']:7.3f} {r['mp_computed_diff_V']:+7.3f} "
              f"{r['predicted_capacity_mAh_g']:7.1f} {r['reference_capacity_mAh_g']:7.1f}")
    print(f"ordering_match={ordering_match} (strict predicted order: {' > '.join(strict_order)})")
    print(f"VERDICT: {verdict.upper()} — {doc['verdict_rationale']}")


if __name__ == "__main__":
    main()
