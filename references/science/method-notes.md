---
status: VERIFIED 2026-10-21 — both formulas confirmed against primary sources by T-002 (see `references/literature/ong-2011.md`, `references/literature/eriksson-2001.md`)
---
# Method notes: voltage, capacity, stability

## Average voltage
For a lithiation step from x1 to x2 Li per formula unit:

    V = -(E(x2) - E(x1) - (x2 - x1) * E_Li) / (x2 - x1)

E(x) is the relaxed total energy of the host at lithiation state x (eV per formula unit). E_Li is the relaxed energy of one Li atom in bulk Li metal, computed with the same model and settings (never taken from a database at different settings). V comes out in volts versus Li/Li+.

Confirmed: Ong et al. 2011 (Energy Environ. Sci., DOI 10.1039/c1ee01782a), Eq. (1): V = −[E(AnH) − E(An−xH) − x·E(A)] / (x·e), total energies from DFT, V vs. the alkali-metal anode — identical expression with A=Li and a per-mole basis (e→F). Origin: Ceder group's average-voltage method (Aydinol et al., J. Power Sources 68 (1997) 664; the PDF's embedded bitmap fonts defeated text extraction this session, so it is cited for lineage, not quoted). pymatgen 2026.9.24 `InsertionVoltagePair` (apps/battery/insertion_battery.py) implements the same energy-difference construction with per-formula-unit normalization.

## Capacity
    capacity (mAh/g) = (x2 - x1) * F / (3600 * M)

F is Faraday's constant (96485 C/mol); the combined constant 96485/3600 ≈ 26.80 is what's used in `/gs-derive-voltage-capacity`. M is the molar mass of the host formula unit in g/mol, on the basis decision D-005 confirms.

Confirmed: Eriksson 2001 PhD thesis (Uppsala, DiVA diva2:160906), ch. 2.3: "96487 coulombs (or 26.8 Ah)" per gram equivalent weight (Faraday's first law), with the worked example LiMn2O4: 26.8/180.8 g/mol = 148 mAh/g. The worked example also fixes the basis: the host formula's own molar mass — confirmed as the standard by decision D-005 (DECIDED 2026-10-21): capacity is per gram of the lithiated host formula unit.

## Stability
Energy above hull, taken from Materials Project (`/gs-stability-score`), not recomputed unless decision D-006 says how. A zero-kelvin, kinetics-free number — it says nothing about whether the phase actually forms under real synthesis conditions. Cutoff now DECIDED (D-002): report as passing when 0 to 25 meV/atom.

## Benchmark outcome (gate G1, run-20261021-t003-g1 — recorded per D-007, DECIDED 2026-10-21)
**Known limitation, characterized by T-003:** CHGNet v0.3.0 voltages carry a chemistry-correlated offset. Polyanionic Fe (LiFePO4: +0.024 V) and spinel Mn (LiMn2O4: −0.015 V) match literature within ~0.03 V; layered Co oxide (LiCoO2) runs ~0.4 V low vs literature (−0.298 V vs MP's own computed 0→1 value) and ~0.5 V below the predicted Mn redox. A diagnostic x-grid (segment voltages 3.730 / 3.523 / 3.219 V) rules out the reference-basis explanation — the offset is model-level. Consequences for screening:
- Relative rankings within one chemistry are usable; cross-chemistry comparisons involving Co-rich materials are not, until this is revisited.
- Any candidate result touching Co-rich chemistries carries a widened uncertainty label (rule per D-007 option A).
- Capacities are analytic (26801·Δx/M) and were benchmark-exact; model risk is confined to voltages and (for non-MP materials) stability.

## Open research questions
- **RQ-1 (answered by T-003):** No — CHGNet's accuracy does NOT hold evenly across the three chemistries. Fe (polyanionic) and Mn (spinel) land within ~0.03 V of literature; Co (layered oxide) runs ~0.4 V low. See "Benchmark outcome" above; consequence rule per D-007.
- **RQ-2:** How many Li/vacancy arrangements per lithiation state are enough? Full enumeration is exact but explodes combinatorially for larger cells. A special quasirandom structure or a handful of representative orderings may suffice. `/gs-relax-and-energy` flags this per candidate rather than assuming an answer; if the count is large, it proposes a cap to Mico instead of silently truncating.
- **RQ-3:** Which magnetic/spin ordering should transition-metal ions be relaxed with (ferromagnetic, antiferromagnetic, high-spin/low-spin)? This can shift energies enough to matter for voltage. Unresolved; note whatever ordering CHGNet's defaults use and flag if it looks wrong on a benchmark material.

## Reference-value basis caveat (added by T-002)
Literature "operating voltage" figures (e.g. 3.9 V for LiCoO2) are practical cell averages; computed equilibrium voltages are ideal-limit numbers. The benchmark comparison (T-003, D-003 gate ±0.2–0.3 V) must treat literature values as approximate references, and MP's computed electrode voltages (available via the API) as a second, like-for-like comparison.

## Formula version
`v0.2` — T-002 confirmed both formulas against primary sources; wording and basis notes updated. No formula content changed.
