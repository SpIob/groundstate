"""Verification for run-20261021-t003-g1 (gs-relax-and-energy / gs-derive checks):
1. volume sanity: pulled vs relaxed cell volumes (lithiation should swell the cell)
2. determinism: re-relax lco-x1-arr00, energy must match within 1 meV/atom
3. hand-recompute one voltage (LFP) from stored energies, match to 3 decimals
"""
from __future__ import annotations

import json
import pathlib

import torch

REPO = pathlib.Path(__file__).resolve().parents[3]
RUN = REPO / "pipeline" / "runs" / "run-20261021-t003-g1"
PIPE = REPO / "pipeline"

from pymatgen.core import Structure

print("1) volume check (A^3; pulled -> relaxed, per formula unit where useful)")
rows = [
    ("li-metal-arr00", None),
    ("lco-x1-arr00", "mp-22526"), ("lco-x0-arr00", None),
    ("lfp-x1-arr00", "mp-19017"), ("lfp-x0-arr00", None),
    ("lmo-x1-arr00", "mp-22584"), ("lmo-x0-arr00", None),
]
for arr, raw_mid in rows:
    rec = json.loads((RUN / "relaxations" / f"{arr}.json").read_text())
    rel = Structure.from_file(str(RUN / "structures" / f"{arr}.cif"))
    if raw_mid:
        raw = Structure.from_file(str(PIPE / "data" / "raw" / raw_mid / "structure.cif"))
        raw_v = raw.volume / rec["n_formula_units_in_cell"]
        src = "pulled"
    elif rec.get("role") == "li_reference":
        raw_v, src = 3.5093**3 / 2, "constructed"
    else:
        # x=0 starts from the pulled x=1 cell minus Li; compare against pulled x=1 per fu
        tag = arr.split("-")[0]
        raw_mid = {"lco": "mp-22526", "lfp": "mp-19017", "lmo": "mp-22584"}[tag]
        raw = Structure.from_file(str(PIPE / "data" / "raw" / raw_mid / "structure.cif"))
        raw_v, src = raw.volume / rec["n_formula_units_in_cell"], "pulled-x1-minus-Li"
    rel_v = rel.volume / rec["n_formula_units_in_cell"]
    print(f"  {arr}: {src} {raw_v:.2f} -> relaxed {rel_v:.2f} A^3/fu ({100*(rel_v-raw_v)/raw_v:+.1f}%)")

print("2) determinism: re-relax lco-x1-arr00 (same settings)")
from chgnet.model.model import CHGNet
from chgnet.model.dynamics import StructOptimizer
torch.manual_seed(0)
chgnet = CHGNet.load(model_name="0.3.0", use_device="mps", verbose=False)
relaxer = StructOptimizer(model=chgnet, optimizer_class="FIRE", use_device="mps")
pulled = Structure.from_file(str(PIPE / "data" / "raw" / "mp-22526" / "structure.cif"))
out = relaxer.relax(pulled, fmax=0.05, steps=500, relax_cell=True,
                    ase_filter="FrechetCellFilter", verbose=False)
re_e = float(out["final_structure"].to(fmt="json")) if False else None
# single-point energy on the rerun final structure, same protocol as stage 2
from chgnet.model.dynamics import AseAtomsAdaptor, CHGNetCalculator
import numpy as np
atoms = AseAtomsAdaptor.get_atoms(out["final_structure"])
atoms.calc = CHGNetCalculator(model=chgnet, use_device="mps")  # type: ignore[attr-defined]
re_energy = float(atoms.get_potential_energy())  # type: ignore[attr-defined]
saved = json.loads((RUN / "relaxations" / "lco-x1-arr00").with_suffix(".json").read_text())
d = abs(re_energy - saved["energy_eV"]) / len(out["final_structure"]) * 1000
print(f"  saved E={saved['energy_eV']:.6f} eV, rerun E={re_energy:.6f} eV -> diff {d:.4f} meV/atom (limit 1.0)")

print("3) hand-recompute LFP voltage from stored energies")
e0 = json.loads((RUN / "relaxations" / "lfp-x0-arr00.json").read_text())
e1 = json.loads((RUN / "relaxations" / "lfp-x1-arr00.json").read_text())
eli = json.loads((RUN / "relaxations" / "li-metal-arr00.json").read_text())
e_li_hand = eli["energy_eV"] / eli["n_li_in_cell"]
v_hand = -((e1["energy_eV"] / 4 - e0["energy_eV"] / 4) - 1.0 * e_li_hand) / 1.0
derived = json.loads((RUN / "derived.json").read_text())
v_stored = [p["voltage_V"] for m in derived["materials"] if m["material_tag"] == "lfp" for p in m["pairs"]][0]
print(f"  hand: {v_hand:.6f} V | stored: {v_stored:.4f} V | match to 3 decimals: {round(v_hand,3) == round(v_stored,3)}")
