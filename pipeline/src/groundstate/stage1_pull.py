"""Stage 1 (gs-pull-mp-candidate): pull the three benchmark structures from
Materials Project.

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

# D-001 benchmark set; IDs verified by T-002 (references/data-sources.md).
MATERIALS = [
    ("mp-22526", "LiCoO2"),
    ("mp-19017", "LiFePO4"),
    ("mp-22584", "LiMn2O4"),
]

SUMMARY_FIELDS = ["material_id", "formula_pretty", "nsites", "symmetry", "energy_above_hull"]


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
    client_version = importlib.metadata.version("mp-api")
    with MPRester() as mpr:
        db_version = getattr(mpr, "db_version", None)
        for mid, _expected in MATERIALS:
            t_utc = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
            query = (
                f"mpr.materials.summary.search(material_ids=['{mid}'], "
                f"fields={SUMMARY_FIELDS}) + mpr.get_structure_by_material_id('{mid}')"
            )
            try:
                docs = mpr.materials.summary.search(material_ids=[mid], fields=SUMMARY_FIELDS)
            except Exception as exc:
                print(f"{mid}: restricted-field search failed ({type(exc).__name__}); retrying unfiltered")
                docs = mpr.materials.summary.search(material_ids=[mid])
            if not docs:
                sys.exit(f"{mid}: no summary doc returned")
            doc = docs[0]
            got = mpr.get_structure_by_material_id(mid)
            if isinstance(got, list):
                # Multiple entries (e.g. multipleICPDS settings) — keep the
                # conventional one, which MP indexes first.
                print(f"{mid}: structure query returned {len(got)} entries; using the first")
                struct = got[0]
            else:
                struct = got

            sym = field(doc, "symmetry")
            e_hull = field(doc, "energy_above_hull")
            if e_hull is None:
                try:
                    tdocs = mpr.materials.thermo.search(
                        material_ids=[mid], fields=["material_id", "energy_above_hull"]
                    )
                    e_hull = field(tdocs[0], "energy_above_hull")
                except Exception as exc:
                    print(f"{mid}: thermo fallback failed: {type(exc).__name__}: {exc}")

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
                "structure_file": "structure.cif",
            }
            (out / "provenance.json").write_text(json.dumps(prov, indent=2) + "\n")
            print(
                f"{mid}: {prov['formula']} {prov['space_group']} (#{prov['space_group_number']}) "
                f"{prov['atoms_per_cell']} atoms/cell, e_above_hull="
                f"{prov['energy_above_hull_eV_atom_as_reported']}, theoretical="
                f"{prov['theoretical_or_observed']}, db_version={prov['database_version']}"
            )

        print("--- verification re-query (skill check: same formula back) ---")
        ok = True
        for mid, expected in MATERIALS:
            saved = json.loads((RAW / mid / "provenance.json").read_text())
            docs = mpr.materials.summary.search(
                material_ids=[mid], fields=["material_id", "formula_pretty"]
            )
            got = docs[0].formula_pretty
            match = got == saved["formula"] == expected
            ok = ok and match
            print(f"{mid}: saved={saved['formula']} re-queried={got} expected={expected} match={match}")
        if not ok:
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
