# Roadmap (this repo's build-out, not the energy-domain roadmap)

Status: draft. The energy-domain roadmap (which domain opens after batteries) lives in `references/plan/initial-plan.md` and is a separate, later decision.

| Milestone | What | Status |
|---|---|---|
| M0 | Brand mark and wireframe drafts (`Website_v1-v3.pdf`) | In progress — v3 wireframe and extracted reference assets now in `docs/web/design/`; final logo and wordmark originals still with Mico |
| M1 | This scaffold: repo structure, `AGENTS.md`, project skills, references, Hermes profile setup | Done — scaffold, skills by role (incl. `skills/web/`), references, and profile configured |
| M2 | Pipeline environment verified; data sources and benchmark reference voltages confirmed | Done — T-001, T-002 |
| M3 | Benchmark gate G1 passing for LiCoO2, LiFePO4, LiMn2O4 | Done — T-003 ran and was audited; the LCO miss is a characterized limitation (D-007), gate G1 unchanged |
| M4 | First non-benchmark candidate screened, audited, and promoted to `results/` | Done — T-004 screened LiMnPO4, T-006 closed it out (2026-10-22): 4.1 V plateau cross-check verified (Yamada 2001, Zaghib 2013), fresh-session G2 audit PASS WITH FLAGS 33/34, Mico approved, promoted to `results/candidates/mp-18997.json` (commit 0f121b2); D-008 offset carried in the record |
| M5 | Website built (React + TypeScript + Vite, reading `results/` JSON) and deployed to groundstate.science | Open — M4 closed 2026-10-22, so per D-013 (DECIDED: option A, keep the order) the freeze on `web/` lifts and M5 opens. The design spec is ready in `docs/web/` (`DESIGN.md`, `PAGES.md`, `SCAFFOLD.md`; wireframes and reference assets in `docs/web/design/`); W-002 unblocks once W-001's remaining decisions (D-009 hosting, D-010 font, D-011 palette, D-012 columns) are made. |

Reorder note: the initial plan listed the website UI as an immediate next step, second only to the scaffold. Mico's instruction for this task moves it after the pipeline works end to end once — build the thing that produces real data before building the interface that shows it.
