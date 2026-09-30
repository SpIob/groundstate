---
status: UNVERIFIED — confirmed formulas, unconfirmed against literature by T-002
---
# Method notes: voltage, capacity, stability

## Average voltage
For a lithiation step from x1 to x2 Li per formula unit:

    V = -(E(x2) - E(x1) - (x2 - x1) * E_Li) / (x2 - x1)

E(x) is the relaxed total energy of the host at lithiation state x (eV per formula unit). E_Li is the relaxed energy of one Li atom in bulk Li metal, computed with the same model and settings (never taken from a database at different settings). V comes out in volts versus Li/Li+. Standard intercalation-voltage formula; T-002 confirms it against a primary source before the benchmark run relies on it.

## Capacity
    capacity (mAh/g) = (x2 - x1) * F / (3600 * M)

F is Faraday's constant (96485 C/mol); the combined constant 96485/3600 ≈ 26.80 is what's used in `/gs-derive-voltage-capacity`. M is the molar mass of the host formula unit in g/mol, on the basis decision D-005 confirms.

## Stability
Energy above hull, taken from Materials Project (`/gs-stability-score`), not recomputed unless decision D-006 says how. A zero-kelvin, kinetics-free number — it says nothing about whether the phase actually forms under real synthesis conditions.

## Open research questions
- **RQ-1:** Does CHGNet's accuracy hold evenly across the three benchmark chemistries, or does it favor one (e.g., layered oxides over polyanionic phases)? Find out from the benchmark run (T-003), not assumed beforehand.
- **RQ-2:** How many Li/vacancy arrangements per lithiation state are enough? Full enumeration is exact but explodes combinatorially for larger cells. A special quasirandom structure or a handful of representative orderings may suffice. `/gs-relax-and-energy` flags this per candidate rather than assuming an answer; if the count is large, it proposes a cap to Mico instead of silently truncating.
- **RQ-3:** Which magnetic/spin ordering should transition-metal ions be relaxed with (ferromagnetic, antiferromagnetic, high-spin/low-spin)? This can shift energies enough to matter for voltage. Unresolved; note whatever ordering CHGNet's defaults use and flag if it looks wrong on a benchmark material.

## Formula version
`v0.1` — first pass, T-002 confirms sources and may revise.
