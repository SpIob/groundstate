# Roadmap (this repo's build-out, not the energy-domain roadmap)

Status: draft. The energy-domain roadmap (which domain opens after batteries) lives in `references/plan/initial-plan.md` and is a separate, later decision.

| Milestone | What | Status |
|---|---|---|
| M0 | Brand mark and wireframe drafts (`Website_v1-v3.pdf`) | In progress, tracked outside this repo's task board for now |
| M1 | This scaffold: repo structure, `AGENTS.md`, project skills, references, Hermes profile setup | In progress (this task) |
| M2 | Pipeline environment verified; data sources and benchmark reference voltages confirmed | Not started — T-001, T-002 |
| M3 | Benchmark gate G1 passing for LiCoO2, LiFePO4, LiMn2O4 | Not started — T-003, blocked on decision D-003 |
| M4 | First non-benchmark candidate screened, audited, and promoted to `results/` | Not started — blocked on decision D-004 |
| M5 | Website built (React + TypeScript + Vite, reading `results/` JSON) and deployed to groundstate.science | **Frozen.** Do not start `web/` before this milestone. Wireframes from M0 are the starting design reference when it opens. |

Reorder note: the initial plan listed the website UI as an immediate next step, second only to the scaffold. Mico's instruction for this task moves it after the pipeline works end to end once — build the thing that produces real data before building the interface that shows it.
