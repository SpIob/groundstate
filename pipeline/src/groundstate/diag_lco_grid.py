"""Diagnostic (NOT part of the G1 gate): LCO segment voltages on a finer x-grid.

Purpose: the benchmark's LCO voltage is a full 0->1 window average (3.49 V),
while the literature 3.9 V is a practical figure dominated by the high-x
cycling region. If CHGNet's segment voltages rise toward x=1 (e.g. the
2/3->1 segment lands near 3.9-4.1 V), the literature miss is mostly a
reference-basis effect; if the top segment is also ~3.5 V, it is model error.
The G1 verdict in benchmark.json is unchanged by this diagnostic either way.

Construction: 3x1x1 supercell of the RELAXED lco-x1 cell (12 atoms, 3 Li),
remove 0/1/2/3 Li -> x in {1, 2/3, 1/3, 0}, relax each with the manifest
settings, compute segment voltages. One arrangement per grid point (RQ-2
diagnostic cap), recorded as diagnostic output alongside the run.
"""
from __future__ import annotations

import json
import pathlib
import time

import torch

REPO = pathlib.Path(__file__).resolve().parents[3]
RUN = REPO / "pipeline" / "runs" / "run-20261021-t003-g1"

from chgnet.model.dynamics import AseAtomsAdaptor, CHGNetCalculator, StructOptimizer
from chgnet.model.model import CHGNet
from pymatgen.core import Structure

F = 96485.33212
MASS_LCO = 6.94 + 58.933194 + 2 * 15.999  # per LiCoO2 fu


def main() -> None:
    torch.manual_seed(0)
    chgnet = CHGNet.load(model_name="0.3.0", use_device="mps", verbose=False)
    relaxer = StructOptimizer(model=chgnet, optimizer_class="FIRE", use_device="mps")

    x1 = Structure.from_file(str(RUN / "structures" / "lco-x1-arr00.cif"))
    supercell = x1.copy()
    supercell.make_supercell([3, 1, 1])
    li_idx = [i for i, s in enumerate(supercell) if s.specie.symbol == "Li"]
    assert len(li_idx) == 3, f"expected 3 Li in supercell, got {len(li_idx)}"

    results = []
    energies = {}
    for n_remove, x in ((0, 1.0), (1, 2 / 3), (2, 1 / 3), (3, 0.0)):
        arr_id = f"diag-lco-x{round(x, 3)}/arr00".replace(".", "p")
        if x == 1.0:
            struct = supercell  # already relaxed as lco-x1 (re-check in supercell for consistency)
        else:
            struct = supercell.copy()
            struct.remove_sites(li_idx[:n_remove])
        t0 = time.monotonic()
        out = relaxer.relax(struct, fmax=0.05, steps=500, relax_cell=True,
                            ase_filter="FrechetCellFilter", verbose=False)
        final = out["final_structure"]
        atoms = AseAtomsAdaptor.get_atoms(final)
        atoms.calc = CHGNetCalculator(model=chgnet, use_device="mps")  # type: ignore[attr-defined]
        import numpy as np
        e = float(atoms.get_potential_energy())  # type: ignore[attr-defined]
        fmax_r = float(np.max(np.linalg.norm(atoms.get_forces(), axis=1)))  # type: ignore[attr-defined]
        energies[x] = e
        per_fu = e / 3.0
        results.append({
            "arrangement_id": arr_id, "x_per_fu": round(x, 4), "n_atoms": len(final),
            "energy_eV": e, "energy_eV_per_fu": per_fu,
            "max_residual_force_eV_A": fmax_r,
            "converged": fmax_r <= 0.05 * 1.001,
            "relax_seconds": round(time.monotonic() - t0, 1),
        })
        print(f"diag x={x:.3f}: E/fu = {per_fu:.4f} eV, fmax={fmax_r:.4f}, converged={fmax_r <= 0.05005}")

    e_li = json.loads((RUN / "relaxations" / "li-metal-arr00.json").read_text())
    e_li = e_li["energy_eV"] / e_li["n_li_in_cell"]
    segs = []
    for (xa, xb) in ((0.0, 1 / 3), (1 / 3, 2 / 3), (2 / 3, 1.0)):
        dx = xb - xa
        v = -((energies[xb] - energies[xa]) / 3.0 - dx * e_li) / dx
        seg = {"x_from": round(xa, 4), "x_to": round(xb, 4), "segment_voltage_V": round(v, 4),
               "capacity_mAh_g": round(dx * F / 3.6 / MASS_LCO, 1)}
        segs.append(seg)
        print(f"segment {xa:.2f}->{xb:.2f}: V = {v:.3f} V, cap = {seg['capacity_mAh_g']} mAh/g")

    doc = {
        "run_id": "run-20261021-t003-g1",
        "role": "diagnostic only — not part of the G1 gate or its verdict",
        "purpose": "separate reference-basis effect from model error for the LCO literature miss",
        "construction": "3x1x1 supercell of relaxed lco-x1-arr00, Li removed to x in {1, 2/3, 1/3, 0}; manifest settings",
        "E_Li_eV_per_atom": e_li,
        "points": results,
        "segment_voltages": segs,
        "note": "the full-window average from these points reproduces the 0->1 benchmark voltage by telescoping (same endpoints)",
    }
    (RUN / "diagnostic-lco-grid.json").write_text(json.dumps(doc, indent=2) + "\n")
    print(f"wrote {RUN / 'diagnostic-lco-grid.json'}")


if __name__ == "__main__":
    main()
