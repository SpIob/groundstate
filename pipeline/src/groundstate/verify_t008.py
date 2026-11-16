"""Determinism + cross-run verification for run-20261030-t008-lfs (T-008).

Checks (gs-relax-and-energy / gs-derive-voltage-capacity verification):
1. Re-relax the candidate's x_max arrangement from the raw CIF in a fresh
   process and compare the single-point energy to the stored one
   (skill bar: within 1 meV per atom).
2. Compare this run's baseline LFP x_max energy to run-20261021-t003-g1's
   stored value (same structure, same settings -> should match).
3. Hand-recompute both voltages from the stored relaxation JSONs and compare
   to derived.json (bar: match to 3 decimals).
"""
from __future__ import annotations

import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[3]
PIPE = REPO / "pipeline"
RUN = PIPE / "runs" / "run-20261030-t008-lfs"
PREV = PIPE / "runs" / "run-20261021-t003-g1"

# --- checks 2 and 3 first (no model needed) ---
lfs_xmax = json.loads((RUN / "relaxations" / "lfs-xmax-arr00.json").read_text())
lfp_xmax = json.loads((RUN / "relaxations" / "lfp-xmax-arr00.json").read_text())
prev_lfp_x1 = json.loads((PREV / "relaxations" / "lfp-x1-arr00.json").read_text())
derived = json.loads((RUN / "derived.json").read_text())

d_cross = abs(lfp_xmax["energy_eV_per_atom"] - prev_lfp_x1["energy_eV_per_atom"])
print(f"check 2 (cross-run baseline x_max energy): this run {lfp_xmax['energy_eV_per_atom']:.10f} "
      f"vs T-003 {prev_lfp_x1['energy_eV_per_atom']:.10f} eV/atom -> delta {d_cross*1000:.4f} meV/atom")

li = json.loads((RUN / "relaxations" / "li-metal-arr00.json").read_text())
e_li = li["energy_eV"] / li["n_li_in_cell"]
n_fu = 4.0  # both structures are 4 reduced-fu cells (32 atoms / 8-atom fu, 28 / 7)
for tag, mid, dx_mate in (("lfs", "mp-18968", 2.0), ("lfp", "mp-19017", 1.0)):
    x1 = json.loads((RUN / "relaxations" / f"{tag}-xmax-arr00.json").read_text())
    x0 = json.loads((RUN / "relaxations" / f"{tag}-x0-arr00.json").read_text())
    dx = x1["state_x_per_fu"] - x0["state_x_per_fu"]
    assert dx == dx_mate, f"{tag}: window {dx} != expected {dx_mate}"
    v_hand = -((x1["energy_eV"] - x0["energy_eV"]) / n_fu - dx * e_li) / dx
    v_stored = derived["materials"][0 if tag == "lfs" else 1]["pairs"][0]["voltage_V"]
    ok = abs(v_hand - v_stored) < 5e-4
    print(f"check 3 ({tag} voltage hand-recompute, window 0->{dx:g}): {v_hand:.4f} "
          f"vs stored {v_stored:.4f} -> match={ok}")

# --- check 1: fresh re-relaxation of the candidate x_max arrangement ---
import torch
torch.manual_seed(0)
from chgnet.model.dynamics import AseAtomsAdaptor, CHGNetCalculator, StructOptimizer
from chgnet.model.model import CHGNet
from pymatgen.core import Structure

chgnet = CHGNet.load(model_name="0.3.0", use_device="mps", verbose=False)
relaxer = StructOptimizer(model=chgnet, optimizer_class="FIRE", use_device="mps")
pulled = Structure.from_file(str(PIPE / "data" / "raw" / "mp-18968" / "structure.cif"))
result = relaxer.relax(pulled, fmax=0.05, steps=500, relax_cell=True,
                       ase_filter="FrechetCellFilter", verbose=False)
atoms = AseAtomsAdaptor.get_atoms(result["final_structure"])
atoms.calc = CHGNetCalculator(model=chgnet, use_device="mps")  # type: ignore[attr-defined]
e_rerun = float(atoms.get_potential_energy())  # type: ignore[attr-defined]
d_relax = abs(e_rerun - lfs_xmax["energy_eV"]) / len(atoms)
print(f"check 1 (candidate x_max re-relax determinism): stored {lfs_xmax['energy_eV']:.6f} eV, "
      f"rerun {e_rerun:.6f} eV -> delta {d_relax*1000:.4f} meV/atom "
      f"(bar: <= 1.0) -> {'PASS' if d_relax <= 0.001 else 'FAIL'}")
