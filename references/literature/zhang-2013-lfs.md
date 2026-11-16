---
status: verified 2026-10-30 (T-008, stage-5 cross-check for run-20261030-t008-lfs)
---
# Insights into electrochemical performance of Li2FeSiO4 from first-principles calculations

## Citation record
- id: zhang-2013-lfs
- type: paper
- title: Insights into electrochemical performance of Li2FeSiO4 from first-principles calculations
- authors: P. Zhang, Y. Zheng, S. Yu, S.Q. Wu, Y.H. Wen, Z.Z. Zhu, Y. Yang
- year: 2013
- identifier: DOI 10.1016/j.electacta.2013.07.190
- version: Electrochimica Acta 111 (2013) 172-178
- accessed_at: 2026-10-30
- verified: true
- verified_by: Researcher (Hermes), T-008 session — accepted-manuscript full text opened live at sciencedirect.com (PII S0013468613014758, HTTP 200); bibliographic identity cross-checked against the Crossref record for the DOI (title, authors, journal, volume 111, pages 172-178 matched)

## Question this source was read for
Stage-5 cross-check for candidate Li2FeSiO4 (mp-18968, run-20261030-t008-lfs): the literature voltage reference (Fe2+/Fe3+ and Fe3+/Fe4+ redox plateaus) and the theoretical-capacity basis for the two-Li window.

## Claims
| Claim (paraphrase) | Locator | Number as printed (units, conditions) |
|---|---|---|
| Extraction of two Li ions per formula unit is possible in principle for Li2MSiO4, producing a high capacity | §1 Introduction | "ca. 330 mAh/g" |
| Li2FeSiO4 shows a shift of the voltage plateau (Fe2+/Fe3+) between first and subsequent cycles, attributed to a structural transformation | §1 Introduction | 3.1 V -> 2.8 V (first vs subsequent charge cycles) |
| Experimental multi-electron (initial charge) plateaus: two plateaus observed in prior experiments, values differing between groups | §1 Introduction (citing Muraliganth et al.; Lv et al.) | 3.1 V and 4.7 V (Muraliganth); 3.1 V and 4.3 V (Lv) |
| For P2_1/n-cycl, further Li extraction beyond ~1.5 Li/fu predicted possible; Pmn2_1-cycl cannot give a stable FeSiO4 end member | §3.1-3.2, Fig. 2 discussion | ~1.5 Li per f.u. (P2_1/n-cycl) |
| Fully delithiated Li2FeSiO4 -> FeSiO4: P2_1/n end member energetically unstable; cycled polymorphs reach 17-23% volume expansion on full delithiation | §3.2, Fig. 6 | 3% (P2_1/n), 23% (Pmn2_1-cycl), 17% (P2_1/n-cycl) |
| Oxygen release from Li0.5FeSiO4 energetically impossible (Delta E ~ -1.038 eV) | §3.2 | -1.038 eV (GGA, 0 K) |

## Not shown by this source
No single 0->2 average voltage is printed as a number anywhere in the text: calculated voltages live in Figure 3 (per-polymorph, per-step profile), which the accepted-manuscript text does not transcribe. No experimental capacity number of its own — experimental values are quoted from the cited works (Muraliganth, Lv). No Fe2+/Fe3+ plateau value for the Pmn2_1 polymorph specifically (experiments cover several as-prepared polymorphs).

## How it bears on the current task
This is a first-principles (VASP, PBE+U, U-J = 4.0 eV) study of the same material the pipeline just predicted — the closest like-for-like crosscheck class available (computed vs computed, both at 0 K, versus experimental plateau ranges). Its printed numbers support three report fields: (1) two-Li theoretical capacity ca. 330 mAh/g — the run's 331.3 mAh/g (analytic, D-005 basis) matches; (2) the Fe2+/Fe3+ plateau is ~3.1 V (first cycle) shifting to ~2.8 V, and the second-electron plateau sits at ~4.3-4.7 V per the cited experiments — so a full 0->2 average implied by these plateaus spans roughly (3.1+4.3)/2 = 3.7 V to (2.8+4.7)/2 = 3.75 V depending on pairing, i.e. the predicted 3.9168 V sits 0.17-0.22 V above the plateau-implied average — a known pattern for ideal-limit computed averages versus practical plateaus (same caveat class as T-002's basis note); (3) the ordering question: no LFP comparison is printed here, but the plateau-implied LFS average (~3.7-3.75 V) sits above LiFePO4's 3.4-3.45 V plateau, consistent with the run's candidate_beats_baseline verdict. The structural caveats (plateau shift, Li/Fe site exchange, P2_1/n end-member instability, possible O2 loss limits at full delithiation) are kinetic/structural-reality limits distinct from the zero-kelvin thermodynamic estimate and are not contradicted by it.
