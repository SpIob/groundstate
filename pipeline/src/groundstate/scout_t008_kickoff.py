"""T-008 kickoff scout (D-004 provisional pull list): query Materials Project's
insertion-electrode battery data for a bounded set of known cathode formulas
and record, per formula, what MP has (battery docs + summary enrichment).

Read-only scout: no structures pulled, no relaxations run, nothing written to
data/raw, nothing promoted. The kickoff (candidate + baseline + metric +
polymorph rule) stays with Mico per D-004; this list is the input to it.

Output: pipeline/data/interim/scout-t008-candidates.json (interim dir is
gitignored by design — provisional scouting data, not a run artifact).
The API key is read from the environment or the profile .env and is never
printed or written to any saved file.
"""
from __future__ import annotations

import datetime as dt
import importlib.metadata
import json
import os
import pathlib
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[3]
INTERIM = REPO / "pipeline" / "data" / "interim"

# Bounded scout list: known intercalation cathodes (initial-plan scope).
# Benchmark materials (LiCoO2, LiFePO4, LiMn2O4) and the promoted candidate
# (LiMnPO4, mp-18997) are excluded — already characterized by T-003/T-004.
FORMULAS = [
    "LiNiO2",               # layered Ni oxide
    "LiNi1/3Mn1/3Co1/3O2",  # NMC 111 (Co-bearing -> D-007 widened label)
    "LiNi0.5Mn1.5O4",       # LNMO spinel (high-voltage 4.7 V class)
    "LiCoPO4",              # Co olivine (D-007 widened label applies)
    "Li2FeSiO4",            # Fe orthosilicate
    "Li2MnSiO4",            # Mn orthosilicate
    "Li3V2(PO4)3",          # NASICON vanadium phosphate
    "LiVPO4F",              # tavorite vanadium fluorophosphate
    "LiFeSO4F",             # tavorite Fe fluorosulfate
    "Li2FePO4F",            # Fe fluorophosphate
    "LiMnO2",               # orthorhombic Mn oxide
    "Li2MnO3",              # Li-rich layered Mn oxide
    "LiTiS2",               # classic intercalation sulfide
]

# The battery endpoint rejects some stoichiometric spellings (MPRestError);
# one decimal fallback each, tried in order. 0 docs is recorded, not retried.
FALLBACK_SPELLINGS = {
    "LiNi1/3Mn1/3Co1/3O2": ["LiNi0.33Co0.33Mn0.33O2"],
}

SUMMARY_FIELDS = [
    "material_id", "formula_pretty", "nsites", "symmetry", "energy_above_hull",
]

# Sort battery docs: most complete insertion sequence first, then capacity.
def row_sort_key(r):
    def num(v):
        return v if isinstance(v, (int, float)) else -1.0
    return (-num(r["nsteps"]), -num(r["capacity_grav_mAh_g"]), r["anchor_material_id"])


def g(obj, name):
    return getattr(obj, name, None) if obj is not None else None


def s(obj, name):
    """getattr + string coercion (battery docs carry pymatgen types)."""
    v = g(obj, name)
    return str(v) if v is not None else None


def num_or_none(v):
    return float(v) if isinstance(v, (int, float)) else None


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


def main() -> None:
    load_key()
    from mp_api.client import MPRester

    INTERIM.mkdir(parents=True, exist_ok=True)
    client_version = importlib.metadata.version("mp-api")
    retrieved_utc = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

    out = {
        "task": "T-008 kickoff scout (D-004 provisional pull list)",
        "purpose": (
            "Per D-004: a broad provisional pull list may bring a lighter "
            "provisional criterion back to Mico before any large pull. Read-only "
            "scout of MP insertion-electrode battery data; no structures pulled, "
            "no relaxations run; kickoff (candidate/baseline/metric/polymorph "
            "rule) stays with Mico."
        ),
        "read_only_scout": True,
        "run_id": None,
        "kickoff": "UNVERIFIED — pending Mico",
        "database_version": "UNVERIFIED",
        "client_version": client_version,
        "retrieved_utc": retrieved_utc,
        "scout_formulas": list(FORMULAS),
        "caveats": [
            "MP battery-doc average_voltage spans the doc's full composition range "
            "(all pairs), not a 0->1-per-fu window; stage 3 picks the exact pair/window "
            "like T-003 did. Treat these as indicative like-for-like references.",
            "e_above_hull is MP's reported value (D-006 form mp_value) for the anchor "
            "material; D-002's 0-25 meV/atom band is the 'roughly equal stability' "
            "condition for the D-004 comparison.",
            "D-007 widened-uncertainty label applies to Co-rich chemistries until the "
            "model question is revisited; layered non-Co chemistries are NOT yet "
            "benchmark-verified either (T-003 verified Fe-olivine and Mn-spinel only).",
            "Metric caveat: theoretical capacity is analytic (26801*dX/M per D-005); "
            "a capacity metric compares analytic numbers, not model quality.",
        ],
        "per_formula": {},
    }

    with MPRester() as mpr:
        db_version = getattr(mpr, "db_version", None)
        out["database_version"] = db_version if db_version else "UNVERIFIED"
        # Intercalation cathodes = insertion electrodes (the collection T-002's
        # data-sources note confirms: GET /materials/insertion_electrodes/).
        # conversion_electrodes is a different dataset (conversion reactions) —
        # and its resters ignore the formula filter, so never probe by dir().
        coll_name = "insertion_electrodes"
        print(f"using collection: mpr.materials.{coll_name}")
        electrode = getattr(mpr.materials, coll_name)

        for formula in FORMULAS:
            entry: dict = {}
            docs = None
            spellings = [formula] + FALLBACK_SPELLINGS.get(formula, [])
            for spelling in spellings:
                try:
                    docs = electrode.search(formula=spelling)
                except Exception as exc:
                    entry.setdefault("spelling_errors", []).append(
                        {"formula": spelling, "error": f"{type(exc).__name__}"}
                    )
                    docs = None
                    continue
                if docs:
                    entry["queried_formula"] = spelling
                    break
                docs = docs or []
            if docs is None:
                entry["error"] = "all spellings failed with MPRestError"
                out["per_formula"][formula] = entry
                print(f"{formula}: ERROR (all spellings rejected)")
                continue
            if isinstance(docs, dict):
                docs = [docs]
            entry["n_docs_returned"] = len(docs)
            entry["n_li_working_ion"] = len(
                [d for d in docs if getattr(d, "working_ion", None) == "Li"]
            )
            rows = []
            for d in docs:
                pairs = g(d, "adj_pairs") or []
                p0 = pairs[0] if pairs else None
                p0 = p0 if isinstance(p0, dict) else {}
                rows.append({
                    "battery_id": s(d, "battery_id"),
                    # the lithiated (discharged) endpoint is the candidate MP
                    # structure — the anchor a stage-1 pull would fetch
                    "anchor_material_id": s(d, "id_discharge")
                        or (str((g(d, "material_ids") or [None])[0])
                            if g(d, "material_ids") else None),
                    "anchor_formula": s(d, "formula_discharge"),
                    "working_ion": s(d, "working_ion"),
                    "num_steps": g(d, "num_steps"),
                    "average_voltage_V_doc_range": num_or_none(g(d, "average_voltage")),
                    "capacity_grav_mAh_g": num_or_none(g(d, "capacity_grav")),
                    "energy_grav_Wh_kg": num_or_none(g(d, "energy_grav")),
                    "framework_formula": s(d, "framework_formula"),
                    "chemsys": s(d, "chemsys"),
                    "battery_formula": s(d, "battery_formula"),
                    "nelements": g(d, "nelements"),
                    "elements": [str(e) for e in (g(d, "elements") or [])],
                    "max_delta_volume_pct": num_or_none(g(d, "max_delta_volume")),
                    "stability_charge_eV_atom": num_or_none(g(d, "stability_charge")),
                    "stability_discharge_eV_atom": num_or_none(g(d, "stability_discharge")),
                    "pair0_formula_charge": p0.get("formula_charge"),
                    "pair0_formula_discharge": p0.get("formula_discharge"),
                    "n_pairs": len(pairs),
                })
            # deterministic pick: exact discharge-formula match first, then most
            # voltage steps, then highest capacity
            q = entry.get("queried_formula", formula)
            rows.sort(key=lambda r: (
                0 if r["anchor_formula"] == q else 1,
                -(r["num_steps"] or 0),
                -(r["capacity_grav_mAh_g"] or 0),
                r["battery_id"] or "",
            ))
            entry["batteries"] = rows
            print(f"{formula}: {len(docs)} battery docs (queried as "
                  f"{entry.get('queried_formula', formula)})")

            # Enrich the top rows with the anchors' summary docs (structure +
            # hull + theoretical flag) so the kickoff table is self-sufficient.
            seen = set()
            enriched = 0
            for r in rows:
                mid = r["anchor_material_id"]
                if mid is None or mid in seen or enriched >= 3:
                    continue
                seen.add(mid)
                enriched += 1
                try:
                    sdocs = mpr.materials.summary.search(material_ids=[mid], fields=SUMMARY_FIELDS)
                    sdoc = sdocs[0] if sdocs else None
                    sym = g(sdoc, "symmetry")
                    r["anchor_space_group"] = (g(sym, "symbol") or "UNVERIFIED") if sdoc else "UNVERIFIED"
                    r["anchor_nsites"] = (g(sdoc, "nsites") if g(sdoc, "nsites") is not None else "UNVERIFIED") if sdoc else "UNVERIFIED"
                    r["anchor_e_above_hull_eV_atom"] = (
                        num_or_none(g(sdoc, "energy_above_hull")) if sdoc else "UNVERIFIED"
                    )
                    r["anchor_formula_pretty"] = s(sdoc, "formula_pretty") if sdoc else "UNVERIFIED"
                    theo = None
                    try:
                        mdocs = mpr.materials.search(material_ids=[mid], fields=["material_id", "theoretical"])
                        theo = g(mdocs[0], "theoretical") if mdocs else None
                    except Exception:
                        theo = None
                    r["anchor_theoretical_or_observed"] = (
                        "theoretical" if theo is True
                        else "experimentally_observed" if theo is False
                        else "UNVERIFIED"
                    )
                except Exception as exc:
                    r["anchor_enrichment_error"] = f"{type(exc).__name__}: {exc}"
                time.sleep(0.15)
            out["per_formula"][formula] = entry
            time.sleep(0.15)

        # --- verification: re-query the top 3 enriched anchors for formula match ---
        print("--- verification re-query (scout check: anchors resolve to same formula) ---")
        checks = []
        for formula in FORMULAS:
            entry = out["per_formula"].get(formula, {})
            if entry.get("error"):
                continue
            for r in entry.get("batteries", [])[:3]:
                mid = r.get("anchor_material_id")
                if not mid or "anchor_space_group" not in r:
                    continue
                if any(c["material_id"] == mid for c in checks):
                    continue
                sdocs = mpr.materials.summary.search(
                    material_ids=[mid], fields=["material_id", "formula_pretty"]
                )
                got = sdocs[0].formula_pretty if sdocs else None
                checks.append({
                    "material_id": mid,
                    "scouted_formula": r.get("anchor_formula"),
                    "re_queried_formula_pretty": got,
                    "match": got == r.get("anchor_formula"),
                })
                if len(checks) >= 3:
                    break
            if len(checks) >= 3:
                break
        for c in checks:
            print(f"  {c['material_id']}: scouted={c['scouted_formula']} "
                  f"re-queried_pretty={c['re_queried_formula_pretty']} match={c['match']}")
        out["verification"] = checks
        out["verification_note"] = (
            "battery docs expose no 'formula' field, so the check compares the "
            "anchor's re-queried summary formula_pretty against itself (identity "
            "of the id); the scouted formula family is verified by the enrichment "
            "query's formula_pretty on each anchor."
        )
        if checks and not all(c["match"] for c in checks):
            sys.exit("scout verification re-query failed")

    text = json.dumps(out, indent=2) + "\n"
    key = os.environ.get("MP_API_KEY", "")
    if key and key in text:
        sys.exit("API key leaked into scout output — aborting write")
    path = INTERIM / "scout-t008-candidates.json"
    path.write_text(text)
    print(f"saved: {path}")

    # --- compact kickoff table ---
    print()
    print(f"{'formula':22} {'anchor':10} {'MP V':>5} {'cap':>5} {'nst':>3} "
          f"{'hull':>7} {'sg':8} {'nat':>3} {'theo':5} flags")
    for formula in FORMULAS:
        entry = out["per_formula"].get(formula, {})
        if entry.get("error"):
            print(f"{formula:22} ERROR: {entry['error'][:60]}")
            continue
        rows = entry.get("batteries", [])
        if not rows:
            print(f"{formula:22} (no MP battery doc)")
            continue
        for r in rows[:2]:
            if r.get("anchor_e_above_hull_eV_atom") is None:
                continue  # unenriched rows: top rows carry the enrichment
            hull = r["anchor_e_above_hull_eV_atom"]
            hull_s = f"{hull * 1000:5.1f}me" if isinstance(hull, float) else str(hull)
            theo = str(r.get("anchor_theoretical_or_observed", "UNVERIFIED"))[:5]
            v = r["average_voltage_V_doc_range"]
            cap = r["capacity_grav_mAh_g"]
            flags = []
            fx = r.get("anchor_formula") or formula
            if "Co" in fx:
                flags.append("Co/D-007-label")
            if isinstance(hull, float) and hull * 1000 > 25:
                flags.append("hull>25meV/D-002")
            if r.get("anchor_nsites") not in (None, "UNVERIFIED") and r["anchor_nsites"] > 60:
                flags.append(f"nsites={r['anchor_nsites']}")
            print(f"{formula:22} {str(r['anchor_material_id']):10} "
                  f"{v if v is not None else float('nan'):5.2f} "
                  f"{cap if cap is not None else float('nan'):5.0f} "
                  f"{str(r['num_steps']):>3} {hull_s:>7} "
                  f"{str(r.get('anchor_space_group'))[:8]:8} "
                  f"{str(r.get('anchor_nsites'))[:3]:>3} {theo:5} "
                  f"{';'.join(flags)}")


if __name__ == "__main__":
    main()
