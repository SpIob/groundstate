---
status: verified 2026-10-22 (T-006, stage-5 cross-check for run-20261022-t004-lmp)
---
# Phase Diagram of Lix(MnyFe1-y)PO4 (0 ≤ x, y ≤ 1)

## Citation record
- id: yamada-2001-lmp
- type: paper
- title: Phase Diagram of Lix(MnyFe1−y)PO4 (0 ⩽ x, y ⩽ 1)
- authors: Atsuo Yamada, Yoshihiro Kudo, Kuang-Yu Liu
- year: 2001
- identifier: DOI 10.1149/1.1401083
- version: J. Electrochem. Soc. 148 (10) A1153
- accessed_at: 2026-10-22
- verified: true
- verified_by: Researcher (Hermes), T-006 session — full article page opened live at iopscience.iop.org (HTTP 200, 372 KB); citation_* meta tags on the page matched title, authors, journal, volume, pages, DOI

## Question this source was read for
Stage-5 cross-check for candidate LiMnPO4 (mp-18997, run-20261022-t004-lmp): the literature Mn3+/Mn2+ plateau voltage used in D-008, and the capacity basis.

## Claims
| Claim (paraphrase) | Locator | Number as printed (units, conditions) |
|---|---|---|
| "the two-phase Mn3+/Mn2+ redox region with a potential of 4.1 V" vs. Li/Li+ | Abstract; restated in Introduction ("the position of the Mn3+/Mn2+ couple, 4.1 V vs. Li/Li+") | 4.1 V vs. Li/Li+ (room-temperature olivine phase diagram) |
| LiMnPO4 shows an open-circuit voltage of 4.1 V (two-phase region I, 0 ⩽ x ⩽ 0.6 for y = 0.6 composition) | Discussion of Lix(Mn0.6Fe0.4)PO4 mechanism | OCV 4.1 V |
| Theoretical capacity of the M3+/M2+ one-electron redox of LixMPO4 | Introduction | 170 mAh/g |
| Pure LiMnPO4: OCV 4.1 V observed, but capacity "much smaller than the theoretical value of 170 mAh/g" with large polarization; 4.1 V capacity not achieved without Fe at the 4c site (Padhi et al. results) | Discussion | practical capacity far below 170 mAh/g (no number printed for pure LMP) |
| Mn-rich compositions (y > 0.8) unsuitable due to Jahn-Teller phase instability near MnPO4 | Abstract; Discussion | no number (phase-stability statement) |

## Not shown by this source
No computed/DFT voltage for LiMnPO4 (experimental determination only — OCV and galvanostatic curves). No single 0→1 average voltage printed as a number; the 4.1 V is the two-phase plateau potential. No practical capacity value for pure LiMnPO4 is given, only that it is far below theoretical.

## How it bears on the current task
This is the primary literature basis for the ~4.1 V Mn3+/Mn2+ plateau: the run's predicted 3.6865 V sits ~0.41 V below it (the D-008 offset finding, now DECIDED as a characterized limitation). The paper's own practical caveats (large polarization, Fe coexistence needed, Jahn-Teller instability) are kinetic/electrode-engineering limits, distinct from the computed zero-kelvin thermodynamic result — the candidate report must not read the predicted stability as contradicting these known practical obstacles. Capacity: predicted 170.9 mAh/g vs. this source's 170 mAh/g theoretical (same one-Li-per-formula basis).
