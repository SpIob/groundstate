"""Stage 1 (gs-pull-mp-candidate) for T-004: pull the first non-benchmark
candidate, LiMnPO4 (kickoff 2026-10-22: LiMnPO4 vs LiFePO4 on voltage).

The kickoff names the like-for-like polymorph: olivine (Pnma), the same
structure as the LiFePO4 baseline mp-19017. Skill step 3: list every polymorph
the formula returns (ID, space group, atoms per cell, energy above hull),
record the listing, then pull the named one — Pnma, LiMnPO4, 28 atoms/cell,
lowest energy above hull if several qualify.

Writes pipeline/data/raw/<material_id>/{structure.cif, provenance.json}.
The API key is read from the environment or the Hermes profile .env and is
never printed or written to any saved file.
"""
from __future__ import annotations

import datetime as dt
import importlib.metadata
import json
import os
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[3]
RAW = REPO / "pipeline" / "data" / "raw"
RUN_ID = "run-20261022-t004-lmp"
RUN = REPO / "pipeline" / "runs" / RUN_ID

FORMULA = "LiMnPO4"
PICK_RULE = (
    "kickoff 2026-10-22 (Mico, task T-004): olivine Pnma like the LiFePO4 "
    "baseline mp-19017; among Pnma LiMnPO4 entries with 28 atoms/cell take the "
    "lowest energy_above_hull; ties -> stop and ask Mico."
)
SUMMARY_FIELDS = [
    "material_id", "formula_pretty", "nsites", "symmetry",
    "energy_above_hull",
]


def load_key() -> None:
    if os.environ.get("MP_API_KEY"):
        return
    env = pathlib.Path.home() / ".hermes" / "profiles" / "groundstate" / ".env"
    for line in env.read_text().splitlines():
        line = line.strip()
        if line.startswith("MP_API_KEY="):
            os.environ["MP_API_KEY"] = line.split("=", 1)[1].strip().strip("\"'")
            return
    sys.exit("MP_API_KEY not found in environment or profile .env")


def field(obj, name, default=None):
    return getattr(obj, name, default) if obj is not None else default


def main() -> None:
    load_key()
    from mp_api.client import MPRester

    RAW.mkdir(parents=True, exist_ok=True)
    RUN.mkdir(parents=True, exist_ok=True)
    client_version = importlib.metadata.version("mp-api")

    with MPRester() as mpr:
        db_version = getattr(mpr, "db_version", None)

        # --- skill step 3: list every polymorph for the formula ---
        docs = mpr.materials.summary.search(formula=FORMULA, fields=SUMMARY_FIELDS)
        if not docs:
            sys.exit(f"{FORMULA}: no summary docs returned")
        listing = []
        for d in docs:
            sym = field(d, "symmetry")
            listing.append({
                "material_id": str(field(d, "material_id")),
                "formula": field(d, "formula_pretty"),
                "space_group": field(sym, "symbol", "UNVERIFIED"),
                "space_group_number": field(sym, "number", "UNVERIFIED"),
                "nsites": field(d, "nsites", "UNVERIFIED"),
                "energy_above_hull_eV_atom": field(d, "energy_above_hull", "UNVERIFIED"),
            })
        listing.sort(key=lambda r: (
            r["energy_above_hull_eV_atom"]
            if isinstance(r["energy_above_hull_eV_atom"], float) else 9e9,
            r["material_id"],
        ))
        (RUN / "polymorphs-limpo.json").write_text(json.dumps({
            "run_id": RUN_ID,
            "formula": FORMULA,
            "retrieved_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "database_version": db_version if db_version else "UNVERIFIED",
            "n_polymorphs": len(listing),
            "polymorphs": listing,
            "pick_rule": PICK_RULE,
        }, indent=2) + "\n")
        print(f"{FORMULA}: {len(listing)} polymorphs (db {db_version})")
        for r in listing:
            eh = r["energy_above_hull_eV_atom"]
            eh_s = f"{eh * 1000:.1f} meV/atom" if isinstance(eh, float) else str(eh)
            print(f"  {r['material_id']}: {r['space_group']} (#{r['space_group_number']}), "
                  f"{r['nsites']} atoms, {eh_s}")

        # --- apply the kickoff's pick rule deterministically ---
        eligible = [r for r in listing
                    if r["space_group"] == "Pnma"
                    and r["formula"] == FORMULA
                    and r["nsites"] == 28
                    and isinstance(r["energy_above_hull_eV_atom"], float)]
        if not eligible:
            sys.exit("no Pnma 28-atom LiMnPO4 entry found — kickoff pick rule cannot be applied")
        if len(eligible) > 1 and eligible[0]["energy_above_hull_eV_atom"] == eligible[1]["energy_above_hull_eV_atom"]:
            sys.exit("hull tie between eligible Pnma entries — stopping for Mico per skill")
        mid = eligible[0]["material_id"]
        print(f"pick rule -> {mid} "
              f"({eligible[0]['energy_above_hull_eV_atom'] * 1000:.1f} meV/atom)")

        # --- pull the picked entry (same call pattern as stage1_pull.py) ---
        t_utc = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        query = (
            f"mpr.materials.summary.search(formula='{FORMULA}', fields={SUMMARY_FIELDS}) "
            f"[pick_rule] + mpr.materials.summary.search(material_ids=['{mid}'], "
            f"fields={SUMMARY_FIELDS}) + mpr.get_structure_by_material_id('{mid}')"
        )
        doc = mpr.materials.summary.search(material_ids=[mid], fields=SUMMARY_FIELDS)[0]
        got = mpr.get_structure_by_material_id(mid)
        if isinstance(got, list):
            print(f"{mid}: structure query returned {len(got)} entries; using the first")
            struct = got[0]
        else:
            struct = got

        sym = field(doc, "symmetry")
        e_hull = field(doc, "energy_above_hull")

        theoretical = None
        try:
            mdocs = mpr.materials.search(material_ids=[mid], fields=["material_id", "theoretical"])
            theoretical = field(mdocs[0], "theoretical")
        except Exception as exc:
            print(f"{mid}: theoretical flag unavailable: {type(exc).__name__}")

        out = RAW / mid
        out.mkdir(parents=True, exist_ok=True)
        struct.to(filename=str(out / "structure.cif"), fmt="cif")

        prov = {
            "material_id": str(field(doc, "material_id", mid)),
            "formula": field(doc, "formula_pretty", "UNVERIFIED"),
            "space_group": field(sym, "symbol", "UNVERIFIED"),
            "space_group_number": field(sym, "number", "UNVERIFIED"),
            "atoms_per_cell": len(struct),
            "source": "materials_project",
            "database_version": db_version if db_version else "UNVERIFIED",
            "retrieval_time_utc": t_utc,
            "client_version": client_version,
            "query": query,
            "theoretical_or_observed": (
                "theoretical"
                if theoretical is True
                else "experimentally_observed" if theoretical is False else "UNVERIFIED"
            ),
            "energy_above_hull_eV_atom_as_reported": (
                float(e_hull) if e_hull is not None else "UNVERIFIED"
            ),
            "candidate_for": "T-004 (LiMnPO4 vs LiFePO4 on voltage; baseline mp-19017)",
            "polymorph_pick_rule": PICK_RULE,
            "n_polymorphs_listed": len(listing),
            "polymorph_listing_file": f"{RUN_ID}/polymorphs-limpo.json",
            "structure_file": "structure.cif",
        }
        (out / "provenance.json").write_text(json.dumps(prov, indent=2) + "\n")
        print(
            f"{mid}: {prov['formula']} {prov['space_group']} (#{prov['space_group_number']}) "
            f"{prov['atoms_per_cell']} atoms/cell, e_above_hull="
            f"{prov['energy_above_hull_eV_atom_as_reported']}, theoretical="
            f"{prov['theoretical_or_observed']}, db_version={prov['database_version']}"
        )

        # --- verification re-query (skill check: same formula back) ---
        saved = json.loads((out / "provenance.json").read_text())
        docs2 = mpr.materials.summary.search(
            material_ids=[mid], fields=["material_id", "formula_pretty"]
        )
        got_formula = docs2[0].formula_pretty
        match = got_formula == saved["formula"] == FORMULA
        print(f"re-query: saved={saved['formula']} re-queried={got_formula} match={match}")
        if not match:
            sys.exit("re-query verification failed")

    key = os.environ.get("MP_API_KEY", "")
    leaked = [
        str(p)
        for p in RAW.rglob("*")
        if p.is_file() and key and key in p.read_text(errors="ignore")
    ]
    print("key-leak check over data/raw:", "CLEAN" if not leaked else f"LEAKED in {leaked}")
    if leaked:
        sys.exit(1)


if __name__ == "__main__":
    main()
