# Decisions

Status: authoritative on what is and isn't decided. Only Mico moves a decision from OPEN to DECIDED. Agents that reach an OPEN decision stop, mark the task Blocked, and present the options here — they do not choose.

---

## D-001: Benchmark set membership
**Status: DECIDED.** LiCoO2, LiFePO4, LiMn2O4 (source: `references/plan/initial-plan.md`, Sept 25 2026). These are the trust check (gate G1) before any candidate ranking is used.

---

## D-002: Energy-above-hull cutoff — how stable counts as "stable enough to report"
**Status: DECIDED (Mico, 2026-10-21): Option A — strict, 0 to 25 meV/atom.**

Every candidate gets an energy-above-hull value (`/gs-stability-score`). Below some threshold it's worth taking seriously; above it, the material likely won't form or hold up as a bulk phase. Where that line sits is a judgment call.

- **A — Strict (0 to 25 meV/atom):** Matches common practice for "likely synthesizable" in materials-screening papers. Fewer candidates pass, but each is a safer bet.
- **B — Standard (0 to 50 meV/atom):** Wider net. Catches metastable phases that sometimes turn out synthesizable (temperature, doping, or kinetics can stabilize them), at the cost of more false positives to sort through later.
- **C — Report everything, flag by band:** Don't cut anyone. Label each candidate's hull value in bands (on-hull, low, moderate, high) and let the ranking, not a hard filter, do the work. Keeps the most information but pushes the judgment call downstream to whoever reads the report.

This also decides whether "efficient alternative" (D-004) can include a promising-but-metastable material at all.

---

## D-003: Benchmark pass/fail threshold
**Status: DECIDED (Mico, 2026-10-21): Option B — ±0.2–0.3 V as the gate; option C's relative-order check (LiCoO2 > LiMn2O4 > LiFePO4) reported alongside whenever it adds information.** The plan states the goal qualitatively: predict voltages "within a few tenths of a volt" for the three benchmark materials. Gate G1 needs a number to check against automatically.

- **A — ±0.1 V:** Tight. Matches high-quality DFT-vs-experiment agreement. CHGNet (an ML potential, not DFT) may not reliably hit this on all three materials — worth finding out, but worth knowing it's a stretch going in.
- **B — ±0.2–0.3 V:** What the plan's own wording ("a few tenths") suggests. More realistic for an ML-potential screen; still tight enough to catch a broken pipeline.
- **C — Ranking-only, no absolute threshold:** Pass means the three materials come out in the right relative order (LiCoO2 > LiMn2O4 > LiFePO4 in voltage, roughly), regardless of absolute error. Useful if the absolute numbers turn out to be systematically off in a way that's still useful for relative screening.

Options aren't exclusive — B could be the primary gate with C reported alongside it.

---

## D-004: What counts as an "efficient alternative" for v1 — candidate selection
**Status: DECIDED (Mico, 2026-10-21): Option A — beat a named baseline on a single metric.** The baseline material and the metric (voltage or capacity) get pinned at T-004 kickoff; the option's example baseline is LiFePO4, and D-002's 0–25 meV/atom band holds stability roughly equal. T-004 unblocks on this decision; it still needs Mico to name the first candidate (acceptance criterion 1). The flag below stands: a broad provisional pull list may bring a lighter provisional criterion back to Mico before any large pull.

- **A — Beat a named baseline on a single metric:** Pick one existing cathode (e.g., LiFePO4) and screen for candidates with higher predicted voltage or capacity, energy-above-hull held roughly equal or better. Simple to explain, easy to rank, but a one-axis win can hide a worse trade-off elsewhere (e.g., higher voltage but rarer elements).
- **B — Pareto screen across voltage, capacity, and stability:** No single baseline. Report the set of candidates where none is strictly better than another on all three axes. Closer to how materials screening papers actually present results, but a Pareto front from a handful of candidates isn't very informative yet — this pays off more once dozens are screened.
- **C — Constrain by practical criteria, then rank:** Filter first on things that matter for a real battery beyond the three computed properties (abundant elements, no cobalt or other flagged materials, known synthesis precedent from literature), then rank the survivors on voltage and capacity. Front-loads the "would anyone actually build this" question, at the cost of needing that criteria list defined now.

This can be revisited once a few dozen candidates exist and there's a real distribution to look at.

---

## D-005: Capacity mass basis
**Status: DECIDED (Mico, 2026-10-21): Option A — the convention is confirmed.** Theoretical gravimetric capacity is reported per gram of the lithiated host formula unit (the active material's own formula mass) — the basis of the Eriksson 2001 worked example and of MP's `capacity_grav`. Full-cell or electrode-composite bases stay out of v1; revisit only if a later, more applied stage needs them.

- **A — Confirm the convention (formula mass of the host material only):** Fast, matches how the benchmark literature values were almost certainly computed, keeps `/gs-derive-voltage-capacity` and the benchmark comparison (D-003) on the same basis.
- **B — Something else:** State it if there's a reason to deviate (e.g., a full-cell or electrode-composite basis for a later, more applied stage). Not needed for v1's cathode-only screen, but flag now if the long-term plan wants it.

Recommendation: A. Confirmed by Mico 2026-10-21 — no further action.

---

## D-006: Hull-mixing rule
**Status: OPEN.** Materials Project's energy-above-hull is computed from its own DFT dataset. CHGNet (used for the actual screening in stages 2-3) produces energies on a different footing. Mixing the two without a stated rule risks a hull value that looks precise but isn't apples-to-apples.

- **A — Use Materials Project's own energy-above-hull as-is, for benchmark and known materials only:** Simple, defensible, no new hull math. Doesn't cover any candidate the pipeline finds that isn't already in Materials Project's dataset.
- **B — Build a CHGNet-referenced hull:** Recompute a formation-energy hull using CHGNet energies throughout (candidates and competing phases alike), so everything is internally consistent even for materials not in Materials Project's own hull. More work, and needs its own validation against the benchmark set before it's trusted.
- **C — Report Materials Project's value when available, flag `UNVERIFIED` otherwise:** Middle ground. No new hull-building now; candidates outside Materials Project's dataset get an explicit gap instead of a fabricated-looking number.

Recommendation: start with C, revisit B once the pipeline needs to screen materials Materials Project hasn't already characterized.

---

## D-007: G1 benchmark result — LCO misses the D-003 gate; what happens to gate G1 (PROPOSED by Runner session, 2026-10-21, task T-003)
**Status: DECIDED (Mico, 2026-10-21): Option A — record as a characterized limitation; gate G1 stays exactly as decided (option B, ±0.3 V, with the ordering check alongside).** The limitation text is recorded in `references/science/method-notes.md`; Co-rich candidate results carry a widened uncertainty label until the model question is revisited. Option B's investigation (RQ-3 spin/magnetic hypothesis) may become a future task; not opened now. T-003 stands closed with its FAIL verdict — the gate did its job.

Run-20261021-t003-g1 verdict: **FAIL** on the D-003 option B gate (±0.3 V). LiFePO4 (+0.024 V) and LiMn2O4 (−0.015 V) pass comfortably; LiCoO2 is −0.408 V vs the literature 3.9 V (−0.298 V vs MP's own computed 0→1 DFT value of 3.790 V, which is inside the band). The option C ordering check also fails: predicted order is LiMn2O4 (3.99) > LiCoO2 (3.49) > LiFePO4 (3.42), while the reference says LCO ≈ LMO > LFP — CHGNet puts the Co redox ~0.5 V below the Mn redox.

A diagnostic x-grid on relaxed LCO (segment voltages 3.730 / 3.523 / 3.219 V for 0→⅓→⅔→1) rules out the reference-basis explanation: every window sits low, so the offset is chemistry-correlated model error for the Co redox couple, not a mismatch between "practical" literature voltages and computed averages. Capacities, energies, relaxations, and bookkeeping all verified clean — the pipeline did its job; the model is the limit. This is exactly what gate G1 exists to catch, and it caught it before any candidate was ranked.

- **A — Accept as a characterized limitation, keep G1 strict (recommended):** Record "CHGNet v0.3.0 voltages carry a chemistry-correlated offset up to ~0.4–0.5 V for layered Co oxides; polyanionic (Fe) and spinel (Mn) chemistries verified within ~0.03 V" in the method notes. G1 stays as decided (the gate did its job; the artifact records the FAIL and the audit). Candidate results touching Co-rich chemistries carry a widened uncertainty label until the model question is revisited. No method change, no rerun.
- **B — Try to fix the model behavior, then rerun G1:** Investigate the Co offset (leading unverified hypothesis: spin/magnetic-ordering treatment per RQ-3; CHGNet's internal magmoms may misrepresent Co³⁺/Co⁴⁺), possibly with explicit magnetic configurations or a per-chemistry calibration. Only path that could genuinely restore absolute accuracy for Co chemistries — but it is a method change (invalidates current outputs until G1 reruns), and calibrating on the 3-material benchmark set risks overfitting the very gate meant to catch errors.
- **C — Relax the gate (e.g. ±0.5 V, or gate against MP's computed values rather than literature):** Re-labels this run PASS. Cheapest, but it permanently weakens the broken-pipeline detector for every future chemistry, and MP-gating only works for materials MP has already computed — which undermines the point of screening anything new. Recommended against.

If A: T-003 can close as Done with verdict FAIL recorded (the gate ran, the result is trustworthy, the trust finding is the deliverable). If B: keep T-003 open, open an RQ-4 investigation task. If C: D-003 itself would need reopening.

---

## Adding a decision
New fork → append a `D-0XX` section here in this same shape: status, context, lettered options with real trade-offs, a recommendation if there's a clear one. An agent proposes; only Mico decides.
