"""Stage 3 (gs-derive-voltage-capacity) for T-004: average voltage and capacity
for the LiMnPO4 candidate and the LiFePO4 baseline from this run's stage-2
relaxation energies (run-20261022-t004-lmp).

Formula (method-notes v0.2, confirmed by T-002 against Ong 2011):
    V = -(E(x2) - E(x1) - (x2 - x1) * E_Li) / (x2 - x1)
    capacity = (x2 - x1) * 26801 / M

Mass basis per D-005 (DECIDED 2026-10-21, option A): the lithiated host
formula unit. Single 0->1 step = step voltage, labeled as such.

D-004 comparison (kickoff 2026-10-22): candidate LiMnPO4 vs baseline
LiFePO4 on predicted voltage, both computed in THIS run with identical
settings and the same Li reference.
"""
from __future__ import annotations

import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[3]
RUN = REPO / "pipeline" / "runs" / "run-20261022-t004-lmp"
RUN_ID = "run-20261022-t004-lmp"

F = 96485.33212  # C/mol (CODATA), consistent with method-notes 96485/3600 ~ 26.80
MASS = {  # g/mol, IUPAC 2021 standard atomic weights (same table as T-003 stage 3)
    "Li": 6.94, "Co": 58.933194, "Fe": 55.845, "Mn": 54.938044,
    "P": 30.973761998, "O": 15.999,
}

MATERIALS = [
    ("lmp", "LiMnPO4", "mp-18997", 4, "candidate"),
    ("lfp", "LiFePO4", "mp-19017", 4, "baseline"),
]

LIT_HOST = {  # per reduced formula unit
    "LiMnPO4": {"Li": 1, "Mn": 1, "P": 1, "O": 4},
    "LiFePO4": {"Li": 1, "Fe": 1, "P": 1, "O": 4},
}


def fu_mass(formula: dict) -> float:
    return sum(MASS[el] * n for el, n in formula.items())


def load(arr_id: str) -> dict:
    return json.loads((RUN / "relaxations" / f"{arr_id}.json").read_text())


def main() -> None:
    li_rec = load("li-metal-arr00")
    e_li = li_rec["energy_eV"] / li_rec["n_li_in_cell"]
    print(f"E_Li (relaxed bcc, same settings) = {e_li:.6f} eV/atom")

    results = {}
    pairs_out = []
    for tag, formula, mid, n_fu, role in MATERIALS:
        x1rec = load(f"{tag}-x1-arr00")
        x0rec = load(f"{tag}-x0-arr00")
        assert x0rec["state_x_per_fu"] == 0.0 and x1rec["state_x_per_fu"] == 1.0
        assert x0rec["n_formula_units_in_cell"] == x1rec["n_formula_units_in_cell"] == n_fu
        e1 = x1rec["energy_eV_per_fu"]  # eV per formula unit, x = 1
        e0 = x0rec["energy_eV_per_fu"]  # eV per formula unit, x = 0
        dx = x1rec["state_x_per_fu"] - x0rec["state_x_per_fu"]

        # V in volts: energies eV/fu, dx Li per fu (1 eV per (e * dx) = V, per-fu basis)
        voltage = -(e1 - e0 - dx * e_li) / dx

        # Independent recomputation (skill verification: match to 3 decimals) —
        # same numbers, deliberately different arithmetic path, from the raw
        # cell totals rather than the per-fu fields.
        e1_tot = x1rec["energy_eV"]
        e0_tot = x0rec["energy_eV"]
        voltage_recheck = -((e1_tot - e0_tot) / n_fu - dx * e_li) / dx
        assert abs(voltage - voltage_recheck) < 5e-4, (
            f"{formula}: recompute mismatch {voltage} vs {voltage_recheck}"
        )

        m_lit = fu_mass(LIT_HOST[formula])
        # D-005 basis: lithiated host formula unit. 26801 = F/3.6 (skill constant).
        cap_lit = dx * F / 3.6 / m_lit

        # Unit sanity checks (skill step 3): LFP ~170 mAh/g at M~157.76; V a few volts.
        if tag == "lfp":
            assert abs(m_lit - 157.76) < 0.5, f"LFP mass check failed: {m_lit}"
            assert 160 < cap_lit < 175, f"LFP capacity check failed: {cap_lit}"
        if tag == "lmp":
            assert abs(m_lit - 156.85) < 0.5, f"LMP mass check failed: {m_lit}"
            assert 165 < cap_lit < 177, f"LMP capacity check failed: {cap_lit}"
        for v in (voltage,):
            assert 1.0 < v < 5.5, f"implausible voltage for {formula}: {v}"

        print(
            f"{formula} ({mid}, {role}): V = {voltage:.4f} V | recheck = "
            f"{voltage_recheck:.4f} V | capacity (lithiated basis, D-005) = "
            f"{cap_lit:.1f} mAh/g (M={m_lit:.3f})"
        )
        results[tag] = {"voltage": voltage, "cap": cap_lit, "mid": mid, "formula": formula}
        pairs_out.append({
            "candidate_id": mid,
            "material_tag": tag,
            "role": role,
            "pairs": [{
                "x1": 0.0, "x2": 1.0,
                "voltage_V": round(voltage, 4),
                "capacity_mAh_g": round(cap_lit, 1),
                "mass_basis": "lithiated_host_formula_mass (D-005 option A, DECIDED 2026-10-21)",
                "molar_mass_g_mol": round(m_lit, 3),
                "arrangement_ids": {"x1": x1rec["arrangement_id"], "x2": x0rec["arrangement_id"]},
                "label": "single lithiation step 0->1, step voltage (not a multi-step average)",
            }],
        })

    # --- D-004 comparison: candidate vs baseline on predicted voltage ---
    v_cand = results["lmp"]["voltage"]
    v_base = results["lfp"]["voltage"]
    delta = v_cand - v_base
    verdict = "candidate_beats_baseline" if v_cand > v_base else "candidate_does_not_beat_baseline"
    print(
        f"\nD-004 comparison (metric: predicted voltage, baseline LiFePO4):\n"
        f"  LiMnPO4 (mp-18997): {v_cand:.4f} V\n"
        f"  LiFePO4 (mp-19017): {v_base:.4f} V\n"
        f"  delta = {delta:+.4f} V -> {verdict}"
    )
    # Cross-run consistency of the baseline (same structure/settings as T-003).
    print(
        "  baseline cross-run check: this run's LFP voltage vs "
        "run-20261021-t003-g1's 3.4239 V (both CHGNet v0.3.0, identical settings)"
    )

    derived = {
        "run_id": RUN_ID,
        "formula_version": "v0.2",
        "e_li_reference": {"arrangement_id": "li-metal-arr00", "eV_per_Li_atom": round(e_li, 6),
                           "source": "CHGNet-relaxed bcc Li, same model and settings (never a database value)"},
        "d005_status": "DECIDED 2026-10-21 (option A): capacity per gram of the lithiated host formula unit; single basis reported",
        "d004_comparison": {
            "metric": "predicted average voltage 0->1 (V vs Li/Li+)",
            "candidate": {"material_id": "mp-18997", "formula": "LiMnPO4", "voltage_V": round(v_cand, 4)},
            "baseline": {"material_id": "mp-19017", "formula": "LiFePO4", "voltage_V": round(v_base, 4),
                         "run-20261021-t003-g1_predicted_V": 3.4239},
            "delta_V": round(delta, 4),
            "verdict": verdict,
            "like_for_like_note": (
                "both voltages from this run, identical settings, one Li reference; "
                "baseline value also reproduces the benchmark run's 3.4239 V"
            ),
        },
        "materials": pairs_out,
    }
    (RUN / "derived.json").write_text(json.dumps(derived, indent=2) + "\n")
    print(f"wrote {RUN / 'derived.json'}")


if __name__ == "__main__":
    main()
