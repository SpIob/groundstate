"""Stage 2 (gs-relax-and-energy) for T-008: CHGNet relaxations for the
Li2FeSiO4 candidate (mp-18968) vs the LiFePO4 baseline (mp-19017), kickoff
2026-10-30 (Mico: Li2FeSiO4 vs LiFePO4 on predicted voltage).

Settings identical to run-20261021-t003-g1 (CHGNet v0.3.0, FIRE,
FrechetCellFilter, fmax 0.05 eV/A, 500 steps, mps) so the comparison is
like-for-like. Both materials' fully-lithiated (x_max) and fully-delithiated
(x=0) states relax in THIS run, plus the bcc Li reference — no energies are
borrowed across runs.

States per material: x_max (pulled structure as-is) and x=0 (all Li removed).
x_max = 1 Li/fu for LiFePO4, 2 Li/fu for Li2FeSiO4 — recorded from the pulled
composition, never hardcoded.

Outputs, under pipeline/runs/run-20261030-t008-lfs/:
  manifest.json                       written first, before any energy exists
  relaxations/<arrangement_id>.json   one per relaxed arrangement
  structures/<arrangement_id>.cif     final relaxed structures

RQ-2 note: Li2FeSiO4's Pmn2_1 cell has 8 Li sites per 4-fu cell (x_max = 2
Li/fu), so a full ordering enumeration is far larger than LFP's 24; same cap
as the benchmark and T-004 runs: exactly one arrangement per state (the
MP-drawn ordering for x_max, the vacancy-ordered empty framework for x=0),
cap recorded in the manifest.
"""
from __future__ import annotations

import datetime as dt
import importlib.metadata
import json
import pathlib
import subprocess
import time

import torch

REPO = pathlib.Path(__file__).resolve().parents[3]
PIPE = REPO / "pipeline"
RUN_ID = "run-20261030-t008-lfs"
RUN = PIPE / "runs" / RUN_ID

MATERIALS = [
    ("mp-18968", "lfs", "Li2FeSiO4", "candidate"),
    ("mp-19017", "lfp", "LiFePO4", "baseline"),
]

# Fixed settings, written into the manifest before any relaxation (skill rule).
# Identical to run-20261021-t003-g1 by design (like-for-like voltage comparison).
SETTINGS = {
    "model": "CHGNet",
    "model_version": "0.3.0",
    "optimizer": "FIRE",
    "ase_filter": "FrechetCellFilter",
    "fmax_eV_A": 0.05,
    "max_steps": 500,
    "relax_cell": True,
    "assign_magmoms": True,
    "device": "mps",
    "identical_settings_to": "run-20261021-t003-g1",
    "arrangements_policy": (
        "one arrangement per lithiation state: x_max uses the pulled MP structure "
        "as-is; x=0 removes all Li from the same cell (vacancy-ordered framework). "
        "RQ-2 cap recorded in manifest: LiFePO4 has 4 Li sites per 4-fu cell (24 "
        "orderings); Li2FeSiO4 Pmn2_1 has 8 Li sites per 4-fu cell (2 Li/fu, "
        "8!/(2!^4) = 2520 distinct arrangements by site-occupancy count); this run "
        "relaxes 1 per state, same cap as T-003/T-004."
    ),
    "li_reference": (
        "bcc Li, conventional 2-atom cell a=3.5093 A, relaxed with the same "
        "model/optimizer/fmax/cell relaxation. Never a database Li energy (D-rule)."
    ),
}


def main() -> None:
    RUN.mkdir(parents=True, exist_ok=True)
    (RUN / "relaxations").mkdir(exist_ok=True)
    (RUN / "structures").mkdir(exist_ok=True)

    # --- manifest FIRST: settings locked before any energy is computed ---
    git_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True
    ).stdout.strip()
    git_dirty = subprocess.run(
        ["git", "status", "--porcelain"], cwd=REPO, capture_output=True, text=True
    ).stdout.strip() != ""
    manifest = {
        "run_id": RUN_ID,
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "git_sha": git_sha,
        "git_dirty": git_dirty,
        "task": "T-008 (Li2FeSiO4 mp-18968 candidate vs LiFePO4 mp-19017 baseline on voltage; D-004 option A, kickoff 2026-10-30)",
        "package_versions": {
            p: importlib.metadata.version(p)
            for p in ("pymatgen", "mp_api", "ase", "chgnet", "torch")
        },
        "model_name": "CHGNet",
        "model_version": SETTINGS["model_version"],
        "device": "mps",
        "seeds": {"torch_manual_seed": 0, "note": "CHGNet inference is deterministic; seed recorded for completeness"},
        "input_ids": ["mp-18968", "mp-19017"],
        "input_provenance": (
            "pipeline/data/raw/<id>/provenance.json "
            "(stage 1, MP db 2026.09.28; mp-18968 pulled 2026-10-30 by "
            "stage1_pull_t008.py, named explicitly by Mico at kickoff; "
            "mp-19017 pulled by T-003 stage 1)"
        ),
        "settings": SETTINGS,
        "rq_flags": {
            "RQ-2": "arrangement cap: 1 per state (LFS Pmn2_1: 8 Li sites/4-fu cell; LFP: 4 Li sites/4-fu cell)",
            "RQ-3": "magnetic ordering: CHGNet internal magmom prediction (assign_magmoms=true); no explicit FM/AFM constraint",
        },
        "comparison": {
            "candidate": "mp-18968 Li2FeSiO4",
            "baseline": "mp-19017 LiFePO4",
            "metric": "predicted average voltage, full lithiation window of the host formula unit (D-004 option A; LFS window is 0->2 Li/fu, LFP 0->1 Li/fu)",
            "baseline_run_value_ref": "run-20261021-t003-g1 predicted 3.4239 V (0->1 window); this run re-relaxes the baseline for a within-run comparison",
        },
    }
    torch.manual_seed(0)
    (RUN / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"manifest written for {RUN_ID} (git {git_sha[:12]}, dirty={git_dirty})")

    from chgnet.model.dynamics import (
        AseAtomsAdaptor,
        CHGNetCalculator,
        StructOptimizer,
    )
    from chgnet.model.model import CHGNet
    from pymatgen.core import Lattice, Structure

    chgnet = CHGNet.load(model_name="0.3.0", use_device="mps", verbose=False)
    relaxer = StructOptimizer(model=chgnet, optimizer_class="FIRE", use_device="mps")

    def relax_one(arr_id: str, struct: Structure, meta: dict) -> None:
        t0 = time.monotonic()
        result = relaxer.relax(
            struct, fmax=SETTINGS["fmax_eV_A"], steps=SETTINGS["max_steps"],
            relax_cell=True, ase_filter="FrechetCellFilter", verbose=False,
        )
        secs = time.monotonic() - t0
        final = result["final_structure"]
        # Single-point recomputation on the exact saved structure: guarantees the
        # recorded energy/forces correspond to the CIF on disk (audit-friendly).
        atoms = AseAtomsAdaptor.get_atoms(final)
        atoms.calc = CHGNetCalculator(model=chgnet, use_device="mps")  # type: ignore[attr-defined]
        energy = float(atoms.get_potential_energy())  # type: ignore[attr-defined]
        import numpy as np
        fmax_res = float(np.max(np.linalg.norm(atoms.get_forces(), axis=1)))  # type: ignore[attr-defined]
        final.to(filename=str(RUN / "structures" / f"{arr_id}.cif"), fmt="cif")
        n_sites_li = meta.pop("n_li_in_cell")
        rec = {
            "arrangement_id": arr_id,
            "settings_ref": f"{RUN_ID}/manifest.json#settings",
            "n_li_in_cell": n_sites_li,
            **meta,
            "energy_eV": energy,
            "energy_eV_per_fu": energy / meta["n_formula_units_in_cell"],
            "energy_eV_per_atom": energy / len(final),
            "max_residual_force_eV_A": fmax_res,
            "converged": fmax_res <= SETTINGS["fmax_eV_A"] * 1.001,
            "relax_seconds": round(secs, 1),
            "structure_file": f"structures/{arr_id}.cif",
        }
        (RUN / "relaxations" / f"{arr_id}.json").write_text(json.dumps(rec, indent=2) + "\n")
        print(
            f"{arr_id}: E={energy:.4f} eV ({energy/len(final):.4f} eV/atom) "
            f"fmax={fmax_res:.4f} converged={rec['converged']} ({secs:.0f}s)"
        )

    # Li metal reference first (stage skill: same model and settings).
    li = Structure(Lattice.cubic(3.5093), ["Li", "Li"], [[0, 0, 0], [0.5, 0.5, 0.5]])
    relax_one(
        "li-metal-arr00", li,
        {"material_id": None, "formula": "Li", "state_x_per_fu": None,
         "n_formula_units_in_cell": 2.0, "n_li_in_cell": 2, "role": "li_reference"},
    )

    for mid, tag, formula, role in MATERIALS:
        pulled = Structure.from_file(str(PIPE / "data" / "raw" / mid / "structure.cif"))
        comp = pulled.composition.reduced_composition
        n_fu = len(pulled) / comp.num_atoms  # fu = reduced formula unit
        n_li_per_fu = comp.get_el_amt_dict().get("Li", 0)
        n_li_sites = int(round(pulled.composition.get_el_amt_dict().get("Li", 0)))

        # x = x_max: the pulled structure as-is (x_max from the composition).
        relax_one(
            f"{tag}-xmax-arr00", pulled,
            {"material_id": mid, "formula": formula, "state_x_per_fu": n_li_per_fu,
             "n_formula_units_in_cell": n_fu, "n_li_in_cell": n_li_sites,
             "role": role,
             "source_structure": f"data/raw/{mid}/structure.cif"},
        )

        # x = 0: remove all Li from the same cell.
        charged = pulled.copy()
        charged.remove_species(["Li"])
        relax_one(
            f"{tag}-x0-arr00", charged,
            {"material_id": mid, "formula": charged.composition.reduced_formula,
             "state_x_per_fu": 0.0, "n_formula_units_in_cell": n_fu, "n_li_in_cell": 0,
             "role": role,
             "source_structure": f"data/raw/{mid}/structure.cif (Li removed)"},
        )

    print("stage 2 complete")


if __name__ == "__main__":
    main()
