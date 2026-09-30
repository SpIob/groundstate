---
status: authoritative — transcribed verbatim from Groundstate_Initial_Project_Plan.pdf (Mico's own document, Sept 25 2026)
---
# Groundstate — Initial Project Plan & Roadmap

Prepared by Jan Mico M. Arenga (Mico) — groundstate.science — September 25, 2026

## Mission

Groundstate is an AI-orchestrated pipeline that screens materials for efficient, theoretically grounded alternatives to current energy resources. It gathers and processes known information from credible sources, and pairs that with atomic-scale simulation, to rank candidate materials before anyone touches a lab bench. The project starts with batteries. The long-term goal is to extend the same approach to other energy resources as the pipeline and its validation record mature.

## About the author

I'm not an energy scientist. I'm an independent AI enthusiast who wants to contribute to the energy scene. Everything Groundstate produces is a computational estimate meant to help narrow down candidates, not a validated experimental result. Check the cited sources and consult domain experts before relying on anything here.

## Scope

Active now: battery cathode materials — average voltage, capacity, and stability, screened against known intercalation compounds.

Long-term goal: extend the same screen-then-validate approach to other materials-driven energy domains (see Roadmap). Domains that need a fundamentally different kind of simulation, such as wind, hydro, or geothermal, stay flagged as exploratory until an approach exists.

## Architecture

Two decoupled halves, kept in one repository so the science and the site stay in sync.

- **Pipeline (local, offline).** Python code run in batches on Mico's M5 MacBook. Pulls candidate structures, relaxes and screens them, and writes results plus citations to JSON files.
- **Website (static).** React + TypeScript + Vite, reading the JSON output. No server, no database. Hosted free on GitHub Pages or Vercel, at groundstate.science.

This costs nothing to host and uses no local compute while people browse. The tradeoff: visitors see published results, not on-demand simulation. A private lab-mode API (local FastAPI over Tailscale) is a possible later addition for Mico's own use.

## Toolchain (zero-budget)

| Layer | Tools | Role |
|---|---|---|
| Data & structures | Materials Project API, pymatgen, ASE | Crystal structures, formation energies, battery-electrode data |
| ML potentials | CHGNet, MACE-MP-0 | Fast, near-DFT energy and force estimates for screening |
| DFT (spot-checks) | GPAW, Quantum ESPRESSO, PySCF | Accurate validation on the top few candidates only |
| Molecules | xtb, RDKit | Electrolytes and solvent candidates |
| Dynamics | LAMMPS, ASE MD | Ion diffusion in solid electrolytes |
| Cell-level | PyBaMM | Full-cell behavior from material parameters (v2) |

All free and open-source. System limit: DFT stays under roughly 20-30 atoms per cell on 24 GB of RAM, so ML potentials carry the bulk of the screening.

## V1 workflow: battery cathodes

1. Pull candidate structures from Materials Project and the literature.
2. Relax each structure with CHGNet and compute energies at different lithiation states.
3. Derive average voltage from lithiated/delithiated energy differences, and capacity from composition.
4. Score stability using energy above hull from Materials Project data.
5. Rank candidates, cross-check the top few against published papers.
6. Publish a report per candidate with the supporting evidence and citations.

**Benchmark:** the pipeline should rank known performers (LiCoO2, LiFePO4, LiMn2O4) sensibly and predict voltages within a few tenths of a volt. That's the trust check before ranking unfamiliar candidates.

## Roadmap

Domains are grouped by how ready the current simulation approach is to handle them.

| Domain | Status | Notes |
|---|---|---|
| Batteries (cathodes) | ACTIVE | V1 focus. Materials Project + CHGNet screening pipeline. |
| Batteries (electrolytes) | PLANNED | xtb/RDKit-based screening once cathode pipeline is validated. |
| Supercapacitors | PLANNED | Same materials-screening approach; connects to prior work on Bagong Enerhiya. |
| Solar absorbers | PLANNED | Band-gap and stability screening; reuses the DFT spot-check layer. |
| Hydrogen storage / catalysts | PLANNED | Adsorption-energy screening; more compute-heavy per candidate. |
| Thermoelectrics | EXPLORING | Approach not yet scoped. |
| Wind / hydro / geothermal | EXPLORING | Not materials-driven in the same way; needs a different simulation strategy. |

## Website pages (v1)

- **Home.** Scope statement, per-domain status badges, and the author disclaimer.
- **Candidate explorer.** Sortable table plus a voltage-vs-capacity plot for screened cathodes; each candidate opens its stability data and sources.
- **Benchmark.** Predicted vs. reference voltages for known materials — the credibility page.
- **Method.** Pipeline steps, tools used, and known limitations.
- **Roadmap.** Every energy domain, marked Active, Planned, or Exploring.

## Immediate next steps (as originally written)

Before any simulation work begins, the first pass is establishing the project's shell and identity:

1. Project scaffold. Repository structure (`pipeline/` and `web/`), environment setup, and dependency installation.
2. Website interface UI. The five pages above, built as a static React + Vite site reading placeholder JSON.
3. Brand logo. A mark for Groundstate to carry across the site, GitHub repo, and any future write-ups.

The battery-screening pipeline itself (structure pulls, CHGNet relaxation) follows once the scaffold is in place.

> **Reprioritized for this build (Sept 30, 2026):** brand logo and wireframes (`docs/ROADMAP.md` M0) are already drafted separately. Mico's instruction for this scaffolding task moved the website UI build after the pipeline works end to end once — see `docs/ROADMAP.md` and root `AGENTS.md`. The scope and toolchain above are unchanged.
