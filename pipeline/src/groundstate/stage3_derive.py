"""Stage 3 (gs-derive-voltage-capacity): average voltage + capacity from the
stage-2 relaxation energies of run-20261021-t003-g1.

Formula (method-notes v0.2, confirmed by T-002 against Ong 2011):
    V = -(E(x2) - E(x1) - (x2 - x1) * E_Li) / (x2 - x1)
    capacity = (x2 - x1) * F / (3600 * M)

D-005 is OPEN, so both mass bases are reported and labeled:
  - lithiated_host_formula_mass   (Eriksson 2001 worked example; MP's own
    capacity_grav uses this basis too — used for the benchmark comparison)
  - delithiated_host_formula_mass (reported alongside only)
"""
from __future__ import annotations

import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[3]
RUN = REPO / "pipeline" / "runs" / "run-20261021-t003-g1"
RUN_ID = "run-20261021-t003-g1"

F = 96485.33212  # C/mol (CODATA), consistent with method-notes 96485/3600 ~ 26.80
MASS = {  # g/mol, IUPAC 2021 standard atomic weights
    "Li": 6.94, "Co": 58.933194, "Fe": 55.845, "Mn": 54.938044,
    "P": 30.973761998, "O": 15.999,
}

MATERIALS = [
    ("lco", "LiCoO2", "mp-22526", 1),
    ("lfp", "LiFePO4", "mp-19017", 4),
    ("lmo", "LiMn2O4", "mp-22584", 6),
]


def fu_mass(formula: dict) -> float:
    return sum(MASS[el] * n for el, n in formula.items())


def load(arr_id: str) -> dict:
    return json.loads((RUN / "relaxations" / f"{arr_id}.json").read_text())


def main() -> None:
    e_li = load("li-metal-arr00")["energy_eV"] / load("li-metal-arr00")["n_li_in_cell"]
    print(f"E_Li (relaxed bcc, same settings) = {e_li:.6f} eV/atom")

    pairs_out = []
    for tag, formula, mid, n_fu in MATERIALS:
        x1rec = load(f"{tag}-x0-arr00")
        x2rec = load(f"{tag}-x1-arr00")
        assert x1rec["state_x_per_fu"] == 0.0 and x2rec["state_x_per_fu"] == 1.0
        e0 = x1rec["energy_eV_per_fu"]  # eV per formula unit, x = 0
        e1 = x2rec["energy_eV_per_fu"]  # eV per formula unit, x = 1
        dx = x2rec["state_x_per_fu"] - x1rec["state_x_per_fu"]

        # V in volts: energies eV/fu, dx Li per fu (1 eV per (e * dx) = V, per-fu basis)
        voltage = -(e1 - e0 - dx * e_li) / dx

        # masses per formula unit
        lit_host = {"LiCoO2": {"Li": 1, "Co": 1, "O": 2},
                    "LiFePO4": {"Li": 1, "Fe": 1, "P": 1, "O": 4},
                    "LiMn2O4": {"Li": 1, "Mn": 2, "O": 4}}[formula]
        delit_host = {k: v for k, v in lit_host.items() if k != "Li"}
        m_lit = fu_mass(lit_host)
        m_delit = fu_mass(delit_host)

        # mAh/g: F/(3.6*M) = 26801/M — the skill's constant (96485 C/mol / 3.6)
        cap_lit = dx * F / 3.6 / m_lit
        cap_delit = dx * F / 3.6 / m_delit

        # Unit sanity checks (skill step 3): LFP ~170 mAh/g at M~157.76; V a few volts.
        if tag == "lfp":
            assert abs(m_lit - 157.76) < 0.5, f"LFP mass check failed: {m_lit}"
            assert 160 < cap_lit < 175, f"LFP capacity check failed: {cap_lit}"
        for v in (voltage,):
            assert 1.0 < v < 5.5, f"implausible voltage for {formula}: {v}"

        print(
            f"{formula} ({mid}): V = {voltage:.4f} V | capacity(lithiated basis) = "
            f"{cap_lit:.1f} mAh/g (M={m_lit:.3f}) | capacity(delithiated basis) = "
            f"{cap_delit:.1f} mAh/g (M={m_delit:.3f})"
        )
        pairs_out.append({
            "candidate_id": mid,
            "material_tag": tag,
            "pairs": [{
                "x1": 0.0, "x2": 1.0,
                "voltage_V": round(voltage, 4),
                "capacity_mAh_g_lithiated_basis": round(cap_lit, 1),
                "capacity_mAh_g_delithiated_basis": round(cap_delit, 1),
                "mass_basis_benchmark_comparison": "lithiated_host_formula_mass",
                "molar_mass_g_mol": round(m_lit, 3),
                "arrangement_ids": {"x1": x1rec["arrangement_id"], "x2": x2rec["arrangement_id"]},
                "label": "single lithiation step 0->1, step voltage (not a multi-step average)",
            }],
        })

    derived = {
        "run_id": RUN_ID,
        "formula_version": "v0.2",
        "e_li_reference": {"arrangement_id": "li-metal-arr00", "eV_per_Li_atom": round(e_li, 6),
                           "source": "CHGNet-relaxed bcc Li, same model and settings (never a database value)"},
        "d005_status": "OPEN — both mass bases reported and labeled; benchmark comparison uses the lithiated basis (matches Eriksson 2001 worked example and MP capacity_grav)",
        "materials": pairs_out,
    }
    (RUN / "derived.json").write_text(json.dumps(derived, indent=2) + "\n")
    print(f"wrote {RUN / 'derived.json'}")


if __name__ == "__main__":
    main()
