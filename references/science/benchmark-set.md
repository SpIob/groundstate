---
status: populated 2026-10-21 (task T-002) — every value backed by an opened source; see `references/literature/`
---
# Benchmark set (gate G1)

Materials (decision D-001, DECIDED): LiCoO2, LiFePO4, LiMn2O4.

| Material | Materials Project ID | Reference voltage (V vs Li/Li+) | Reference capacity (mAh/g) | Citation ID | Verified |
|---|---|---|---|---|---|
| LiCoO2 | mp-22526 | 3.9 | 274 | zhang-2022-lco | true |
| LiFePO4 | mp-19017 | 3.4 (others print 3.45) | 170 | wu-2014-lfp | true |
| LiMn2O4 | mp-22584 | 4.0 (Mn4+/Mn3+ couple; others print 4.1) | 148 | zhang-2022-lco; huang-2020-lmo; eriksson-2001 | true |

Provenance and basis:
- All three rows come from Zhang et al. 2022 (Rare Metals, DOI 10.1007/s12598-022-02070-6), Table 1, which lists the three materials side by side: theoretical capacity 274 / 170 / 148 mAh·g−1 and operating voltage 3.9 / 3.4 / 4.0 V vs. Li/Li+.
- LFP corroborated by Wu et al. 2014 (Nano-Micro Lett. 6(4):316–326, DOI 10.1007/s40820-014-0004-6, Introduction): 170 mAh g−1, 3.4 V vs. Li+/Li.
- LMO voltage corroborated by Huang et al. 2020 (Adv. Energy Mater., DOI 10.1002/aenm.202000997): the Mn4+/Mn3+ couple sits at about 4.0 V vs. Li+/Li. LMO capacity confirmed by derivation in Eriksson 2001: 26.8 Ah / 180.8 g/mol = 148 mAh/g.
- MP IDs are MP's own page titles (mp-22526, mp-19017, mp-22584); recorded in `references/literature/mp-database.md`.

Comparison rules for T-003 (gate G1, decision D-003: ±0.2–0.3 V gate; relative order reported alongside):
- These reference values are practical/operating or plateau figures, not computed equilibrium averages — treat them as approximate references inside the ±0.2–0.3 V band, and note the basis in `benchmark.json`.
- Where a computed value and a literature value disagree beyond the band, pull MP's computed electrode voltage for the same material (API `insertion_electrodes`, battery IDs mp-22526_Li, mp-19017_Li, mp-22584_Li) as a like-for-like second reference before calling the pipeline broken.
- Predicted relative order should come out LiCoO2 (3.9) ≈ LiMn2O4 (4.0) > LiFePO4 (3.4); LiCoO2 vs LiMn2O4 is within reference noise — the D-003 ordering check should treat those two as effectively tied.

Every reference value needs a citation entry in `references/literature/` (via `/gs-lit-note`), opened and checked, before `/gs-benchmark-run` can compare against it. Do not fill this table from memory. — Done for all three rows, 2026-10-21.
