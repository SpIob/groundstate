# Glossary

Status: draft.

| Term | Meaning here |
|---|---|
| Cathode | The positive electrode of a Li-ion cell. v1 screens cathode materials. |
| Intercalation | Li ions inserting into and leaving a host crystal without destroying its framework. |
| Lithiation state | How much Li the host holds, written as x in Li_x(host). |
| Average voltage | Voltage of the lithiation step from x1 to x2, in volts versus Li/Li+. |
| Gravimetric capacity | Charge stored per gram of material, in mAh/g. The mass basis is decision D-005. |
| Energy above hull | Energy per atom above the lowest-energy mix of competing phases, in eV per atom. Zero means on the hull. |
| ML potential | A trained model that predicts energies and forces (here CHGNet), used instead of full DFT for screening. |
| DFT | Density functional theory. Accurate and expensive. Used only for spot checks. |
| Candidate | A material moving through the pipeline. |
| Run | One execution of pipeline stages, stored in `pipeline/runs/<run-id>/` with a manifest. |
| Gate | A check that must pass before work moves on. G1 benchmark, G2 evidence audit, G3 promotion. |
| Promotion | Copying audited, approved output into `results/`. |
| Role | A job description an agent takes on (`docs/ROSTER.md`). |
| UNVERIFIED | Not opened and checked in this session. |
