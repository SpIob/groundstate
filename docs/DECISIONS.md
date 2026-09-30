# Decisions

Status: authoritative on what is and isn't decided. Only Mico moves a decision from OPEN to DECIDED. Agents that reach an OPEN decision stop, mark the task Blocked, and present the options here — they do not choose.

---

## D-001: Benchmark set membership
**Status: DECIDED.** LiCoO2, LiFePO4, LiMn2O4 (source: `references/plan/initial-plan.md`, Sept 25 2026). These are the trust check (gate G1) before any candidate ranking is used.

---

## D-002: Energy-above-hull cutoff — how stable counts as "stable enough to report"
**Status: OPEN.**

Every candidate gets an energy-above-hull value (`/gs-stability-score`). Below some threshold it's worth taking seriously; above it, the material likely won't form or hold up as a bulk phase. Where that line sits is a judgment call.

- **A — Strict (0 to 25 meV/atom):** Matches common practice for "likely synthesizable" in materials-screening papers. Fewer candidates pass, but each is a safer bet.
- **B — Standard (0 to 50 meV/atom):** Wider net. Catches metastable phases that sometimes turn out synthesizable (temperature, doping, or kinetics can stabilize them), at the cost of more false positives to sort through later.
- **C — Report everything, flag by band:** Don't cut anyone. Label each candidate's hull value in bands (on-hull, low, moderate, high) and let the ranking, not a hard filter, do the work. Keeps the most information but pushes the judgment call downstream to whoever reads the report.

This also decides whether "efficient alternative" (D-004) can include a promising-but-metastable material at all.

---

## D-003: Benchmark pass/fail threshold
**Status: OPEN.** The plan states the goal qualitatively: predict voltages "within a few tenths of a volt" for the three benchmark materials. Gate G1 needs a number to check against automatically.

- **A — ±0.1 V:** Tight. Matches high-quality DFT-vs-experiment agreement. CHGNet (an ML potential, not DFT) may not reliably hit this on all three materials — worth finding out, but worth knowing it's a stretch going in.
- **B — ±0.2–0.3 V:** What the plan's own wording ("a few tenths") suggests. More realistic for an ML-potential screen; still tight enough to catch a broken pipeline.
- **C — Ranking-only, no absolute threshold:** Pass means the three materials come out in the right relative order (LiCoO2 > LiMn2O4 > LiFePO4 in voltage, roughly), regardless of absolute error. Useful if the absolute numbers turn out to be systematically off in a way that's still useful for relative screening.

Options aren't exclusive — B could be the primary gate with C reported alongside it.

---

## D-004: What counts as an "efficient alternative" for v1 — candidate selection
**Status: OPEN.** This decides which materials the pipeline pulls once past the benchmark set. It's the main energy-domain-research-direction call for v1.

- **A — Beat a named baseline on a single metric:** Pick one existing cathode (e.g., LiFePO4) and screen for candidates with higher predicted voltage or capacity, energy-above-hull held roughly equal or better. Simple to explain, easy to rank, but a one-axis win can hide a worse trade-off elsewhere (e.g., higher voltage but rarer elements).
- **B — Pareto screen across voltage, capacity, and stability:** No single baseline. Report the set of candidates where none is strictly better than another on all three axes. Closer to how materials screening papers actually present results, but a Pareto front from a handful of candidates isn't very informative yet — this pays off more once dozens are screened.
- **C — Constrain by practical criteria, then rank:** Filter first on things that matter for a real battery beyond the three computed properties (abundant elements, no cobalt or other flagged materials, known synthesis precedent from literature), then rank the survivors on voltage and capacity. Front-loads the "would anyone actually build this" question, at the cost of needing that criteria list defined now.

This can be revisited once a few dozen candidates exist and there's a real distribution to look at.

---

## D-005: Capacity mass basis
**Status: OPEN, but narrow.** Theoretical gravimetric capacity is almost always reported per gram of the active material's own formula mass — not per gram of a full cell or electrode. That's the near-universal convention.

- **A — Confirm the convention (formula mass of the host material only):** Fast, matches how the benchmark literature values were almost certainly computed, keeps `/gs-derive-voltage-capacity` and the benchmark comparison (D-003) on the same basis.
- **B — Something else:** State it if there's a reason to deviate (e.g., a full-cell or electrode-composite basis for a later, more applied stage). Not needed for v1's cathode-only screen, but flag now if the long-term plan wants it.

Recommendation: A. Needs a one-line confirmation, not a debate.

---

## D-006: Hull-mixing rule
**Status: OPEN.** Materials Project's energy-above-hull is computed from its own DFT dataset. CHGNet (used for the actual screening in stages 2-3) produces energies on a different footing. Mixing the two without a stated rule risks a hull value that looks precise but isn't apples-to-apples.

- **A — Use Materials Project's own energy-above-hull as-is, for benchmark and known materials only:** Simple, defensible, no new hull math. Doesn't cover any candidate the pipeline finds that isn't already in Materials Project's dataset.
- **B — Build a CHGNet-referenced hull:** Recompute a formation-energy hull using CHGNet energies throughout (candidates and competing phases alike), so everything is internally consistent even for materials not in Materials Project's own hull. More work, and needs its own validation against the benchmark set before it's trusted.
- **C — Report Materials Project's value when available, flag `UNVERIFIED` otherwise:** Middle ground. No new hull-building now; candidates outside Materials Project's dataset get an explicit gap instead of a fabricated-looking number.

Recommendation: start with C, revisit B once the pipeline needs to screen materials Materials Project hasn't already characterized.

---

## Adding a decision
New fork → append a `D-0XX` section here in this same shape: status, context, lettered options with real trade-offs, a recommendation if there's a clear one. An agent proposes; only Mico decides.
