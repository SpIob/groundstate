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
**Status: DECIDED (Mico, 2026-10-27): Option C — report Materials Project's value when available; candidates outside Materials Project's dataset carry an explicit "UNVERIFIED" gap instead of a computed number.** Materials Project's energy-above-hull is computed from its own DFT dataset. CHGNet (used for the actual screening in stages 2-3) produces energies on a different footing. Mixing the two without a stated rule risks a hull value that looks precise but isn't apples-to-apples.

- **A — Use Materials Project's own energy-above-hull as-is, for benchmark and known materials only:** Simple, defensible, no new hull math. Doesn't cover any candidate the pipeline finds that isn't already in Materials Project's dataset.
- **B — Build a CHGNet-referenced hull:** Recompute a formation-energy hull using CHGNet energies throughout (candidates and competing phases alike), so everything is internally consistent even for materials not in Materials Project's own hull. More work, and needs its own validation against the benchmark set before it's trusted.
- **C — Report Materials Project's value when available, flag `UNVERIFIED` otherwise:** Middle ground. No new hull-building now; candidates outside Materials Project's dataset get an explicit gap instead of a fabricated-looking number.

Decided: C (Mico, 2026-10-27, in session during T-005). Revisit B once the pipeline needs to screen materials Materials Project hasn't already characterized; until then no CHGNet/DFT hull mixing anywhere in the pipeline.

Operating sequence (noted by Mico, 2026-10-29): option C stays the operating mode — stage 4 reports MP's hull value whenever the material is in MP's dataset, and an explicit `UNVERIFIED` gap otherwise. The gap is also the tripwire: the first stage-4 record whose MP value is unavailable fires option B's revisit condition, and the agent stops and presents the option-B plan (CHGNet-referenced hull throughout, validated against the benchmark set before trusted) before any hull-building work starts. Option B is never mixed in silently. The two forms are machine-enforced in `pipeline/schemas/` and `pipeline/src/groundstate/validate_results.py` (T-007, 2026-10-29).

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

## D-009: Hosting target
**Status: DECIDED (Mico, 2026-10-22): Option B — Vercel.** Static `dist/` only, hash routes, so either works. Limits below are from memory and **UNVERIFIED**; `gs-web-deploy` opens the host's terms page and records them before any deploy.

- **A — GitHub Pages:** Repo is already on GitHub. Deploy is a workflow file in the repo. Custom domain through a `CNAME` file. Free for public repositories as I understand it. Fewer moving parts and one account.
- **B — Vercel:** Also free at the hobby level as I understand it, with preview deploys per push. A second account and dashboard to manage, and its free tier is written for personal non-commercial use, so check that against how Athena Studio is connected to the site.

Blocks: W-010 (deploy) only.

---

## D-010: Site font
**Status: DECIDED (Mico, 2026-10-22): Option D — find the original Dot Mincho 16 release.** The wireframe font is Canva's `DotMincho16Std`, a 16 px dot-matrix serif. Its web license is unknown, so it cannot be used as is. All licenses below are **UNVERIFIED** until Hermes opens the source (`gs-web-assets`). The wordmark and logo are images, so this choice does not affect them. Whatever is chosen must contain `← → › ‹ |`, or those glyphs become pixel SVGs.

- **A — DotGothic16:** Same family of idea (16 px dot-matrix, Latin glyphs), sans instead of serif. Closest to the pixel-art logo. Likely an open license.
- **B — Courier Prime or Cutive Mono:** Typewriter slab-serif monospace. Closest to the wireframe's serif silhouette and very cozy, but smooth outlines instead of pixels.
- **C — VT323:** The most literal CRT-terminal look. Thin at body size, so long paragraphs read harder.
- **D — Find the original Dot Mincho 16 release:** Exact match if a standalone release exists and allows web self-hosting. Needs a license search first.

Until a standalone, self-hostable release is found and its license is opened (`gs-web-assets`), builds use a system monospace fallback and are marked `font: provisional`. If the search finds no such release, stop and report back to Mico before falling back to A, B, or C. Blocks: final visual pass and deploy, not page building.

---

## D-011: Palette contrast
**Status: DECIDED (Mico, 2026-10-22): Option B — darker text tokens, same hues.** Measured from the wireframe (WCAG contrast ratios): green nav and titles on paper 3.15, orange labels 2.17, gray labels 2.32, paper-colored text on the green panel 3.3, on the orange panel 2.05, on gray 2.32, and orange "Electrolytes" on the green flyout 1.45. Dimmed rows fall to about 1.3. Body text is fine (black on paper, 20.0). Small text needs 4.5 to be comfortable for most readers.

- **A — Exact wireframe colors:** Looks exactly as drawn. Small text in green, orange, and gray is hard to read for many people. The check script reports every failing pair but does not block the build.
- **B — Darker text tokens, same hues:** Green text `#3a8045` (4.6), orange text `#b0541a` (4.85), gray text `#6f6f6f` (4.79). Fills and the rail keep the wireframe colors. Rows are not dimmed; the selected row is marked by `‹` and an underline. Very close visually, passes AA for text.
- **B2 — B plus ink-green text on the orange and gray panels:** Text inside those panels becomes `#083529` (6.3 on orange, 5.56 on gray) instead of paper-colored. Passes everywhere, but the panels look less airy than drawn.

Decided option B: text uses `--green-text #3a8045`, `--orange-text #b0541a`, `--gray-text #6f6f6f`; fills and the rail keep the wireframe colors; rows are not dimmed — the selected row is marked by `‹` and an underline. B2 is not used. The set-A default above is superseded. Blocks: nothing; it is a one-file token switch.

---

## D-011 Amendment (Mico, 2026-10-29): Panel text and icons use --ink-green
**Status: DECIDED.** Supersedes the panel-text portion of option B above. Text and icons placed on the colored fills (green, orange, gray panels) render in `--ink-green` (`#083529`) instead of `--paper`. The fills themselves do not change. This covers panel body text, panel headings, links and underlines inside panels, the Cathodes/Electrolytes sub-nav inside its green sub-panel, and the pixel icons on the panels.

Measured contrast ratios (from token values):
- Ink-green on green fill: `#083529` on `#4f9e58` = 4.10:1 — **below 4.5**, listed as known residual; not "large text" (font-size < 24px / not 18.66px bold). [Corrected 2026-11-02 per Mico's W-002 delta-audit disposition: the recorded 4.16 was inaccurate — the value recomputable from the token hexes is 4.10 (recomputed twice, independently, in the 2026-10-30 delta audit); the amendment itself stands unchanged.]
- Ink-green on orange fill: `#083529` on `#f29d64` = 6.24:1 — passes.
- Ink-green on gray fill: `#083529` on `#a6a6a6` = 5.56:1 — passes.

Implementation: token system only (no hardcoded hex). `tokens.css` gains `--panel-text: var(--ink-green)` and panel styles reference it. Any future "large text" exemption in an audit must show the computed font size meeting WCAG definition (24px, or 18.66px bold).

---

## D-012: Cathodes panel structure and table columns
**Status: DECIDED (Mico, 2026-10-22): Option A — full columns, stacked sections.** The wireframe shows an intro paragraph and an empty 3-column table. `DATA_CONTRACT.md` has more fields than three columns hold, and Mico's v3 note puts Method and Benchmark inside the panel.

- **A — Full columns, stacked sections:** Intro, Benchmark, Candidates, Method, closing line. Candidates table shows formula, material id, voltage, capacity, energy above hull, audit status, citations. Complete, wide, scrolls sideways on small screens. This is the default in `PAGES.md`.
- **B — Three columns as drawn:** Material, Result (voltage, capacity, hull in one cell), Evidence (audit status and citations). Matches the wireframe, but packs numbers together and is harder to scan.
- **C — Three columns plus row expand:** Same as B, selecting a row reveals the full record under it. Instant, no animation. More clicks, but compact.

Blocks: `gs-web-data-view` only.

---

## D-008: Voltage offset seen on Mn-olivine too — scope of the D-007 limitation (PROPOSED by Runner session, 2026-10-22, task T-004)
**Status: DECIDED (Mico, 2026-10-22): Option A — record as a characterized limitation.** The limitation text in `references/science/method-notes.md` is extended to cover Mn olivine: chemistry-correlated offsets up to ~0.4–0.5 V seen on layered Co oxides AND Mn olivine; Fe olivine and Mn spinel verified within ~0.03 V; relative rankings within one chemistry usable, absolute cross-chemistry comparisons not. No method change, no rerun; candidate reports carry the offset context. Option B's investigation may become a future RQ-4 task once several candidates exist and the offset pattern is better sampled.

T-004's candidate run (run-20261022-t004-lmp) predicts olivine LiMnPO4 (mp-18997) at 3.6865 V, while the literature Mn3+/Mn2+ plateau is ~4.1 V (multiple open web sources this session; to be written up as a `/gs-lit-note` in the candidate's stage-5 pass, not yet a verified citation). The relative result — LiMnPO4 above LiFePO4 — matches the literature ordering, and stability is exactly equal (both 0.0 meV/atom). But the absolute offset, −0.41 V, is nearly the size of LiCoO2's −0.41 V from T-003. D-007's wording ("polyanionic Fe and spinel Mn verified within ~0.03 V") implicitly treated the offset as a layered-Co-oxide problem; T-004 shows a polyanionic Mn chemistry carries it too. The D-004 within-chemistry comparison is unaffected: candidate and baseline share the olivine structure, model, and settings.

- **A — Record as a characterized limitation (recommended):** Extend the method-notes limitation text to "chemistry-correlated offsets up to ~0.4–0.5 V seen on layered Co oxides AND Mn olivine; Fe olivine and Mn spinel verified within ~0.03 V; relative rankings within one chemistry usable; absolute cross-chemistry comparisons not." No method change, no rerun; candidate reports carry the offset context.
- **B — Investigate before more candidates (would become RQ-4):** e.g. spin/magnetic-ordering treatment for Mn2+/Mn3+ (CHGNet magmoms) or per-chemistry calibration. Only path to restored absolute accuracy, but a method change that invalidates current outputs until G1 reruns.
- **C — Widen the D-003 gate:** Recommended against, same reasoning as D-007 option C.

Recommendation: A now; keep B in mind as a future RQ-4 task once several candidates exist and the offset pattern is better sampled.

---

## Adding a decision
New fork → append a `D-0XX` section here in this same shape: status, context, lettered options with real trade-offs, a recommendation if there's a clear one. An agent proposes; only Mico decides.

---

## D-013: When does M5 (the website) open?
**Status: DECIDED (Mico, 2026-10-22): Option A — keep the order; M5 opens after M4 closes.** `web/` stays frozen until the first non-benchmark candidate is screened, audited, and promoted to `results/`, so the site builds against a settled data shape.

- **A — Keep the order (open M5 after M4):** The site launches showing real data. No UI work gets thrown away if the data shape shifts. Nothing visible exists until the pipeline works.
- **B — Open M5 now, build everything:** Parallel progress, and the site can be reviewed early with honest empty states. Risk: the data contract is still draft and schemas (T-005) are not written, so the data panel may need rework. Two agent roles running at once also uses more of the free-tier quota.
- **C — Open a shell-only slice now:** Landing, About, Contacts, Disclaimer, and the Explore shell with the planned and exploring panels need no pipeline data. Defer `gs-web-data-view` until M4. Gets most of the look done early, keeps the data work in its original order.

Blocks: W-002 onward until M4 closes and M5 opens (`docs/ROADMAP.md` M5 row).

Numbering note: this question was drafted as D-008 alongside the website fork's specs, but the T-004 Mn-olivine proposal took D-008 first (recorded in `tasks/BOARD.md` and `docs/WORKLOG.md` on 2026-10-22), so it renumbers to D-013 and every reference to it is updated. Only Mico renumbers or retires decision numbers.

---

## D-014: Should the site publish the G1 benchmark table? (PROPOSED by Web Builder session, 2026-11-19, task W-008)
**Status: PROPOSED — open for Mico.**

Context: PAGES.md P7 item 2 lists a benchmark table (material, predicted V, reference V, difference V, reference citation) as a permanent panel element, with the empty state `Benchmark has not been run yet.` until results exist. But the `results/` contract defines no benchmark shape — `benchmark.json` lives only in `pipeline/runs/` — and the live `results/index.json` carries `benchmark_run_id: null`. G1 did run (T-003): verdict **FAIL** on the D-003 gate (LiCoO2 −0.408 V; ordering check also failed), recorded as a characterized limitation per D-007, gate unchanged. W-008 therefore ships the benchmark region as the empty state and stops there: rendering the table from anything but promoted `results/` would break the data-view rules, and publishing a FAIL-verdict table is a science-presentation call, not a build detail.

- **A — Leave the empty state:** the benchmark stays run-internal (visible in the run folder and in each candidate's `benchmark_gate` enrichment). The site never shows a table that failed its own gate. Zero work.
- **B — Promote benchmark.json into `results/`** (new contract shape + index field + promotion pass) and render the three-material table with the D-007 framing: a line stating the LCO miss is a characterized chemistry-correlated offset (D-007/D-008), so the panel shows the honest trust check including its failure. Most transparent; needs a small contract change and approved framing copy (W-004).
- **C — Prose only:** a short approved line stating the benchmark ran and how its outcome is framed (no table, no schema change).

Recommendation: B at launch — the benchmark table is the trust story of the whole screen — but only with Mico-approved framing copy, so A is the safe default until then. Blocks nothing today: the region is built and the empty state is per spec.
