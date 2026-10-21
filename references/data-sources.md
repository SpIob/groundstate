# Data sources (v1)

Status: VERIFIED 2026-10-21 (task T-002). Every line below was confirmed by opening the source this session; citation notes live in `references/literature/` (ids: mp-database, batteryarchive). Corrections from the original draft are marked **[corrected]**.

## Materials Project
- Use: crystal structures, computed energies, energy above hull. Confirmed: precomputed insertion/conversion electrode data (average voltage, gravimetric capacity, stability of charged/discharged states) IS available through the API — endpoints `GET /materials/insertion_electrodes/` and `GET /materials/conversion_electrodes/` (API 0.88.0rc4, live OpenAPI).
- Access: free account and API key, used through the `mp-api` client. Key goes in `.env` as `MP_API_KEY`. Key must be kept secret; the account holder is responsible for violations.
- Site: https://materialsproject.org . API: https://api.materialsproject.org (Swagger at /docs).
- License and terms: CC BY 4.0 — content may be copied, distributed, transmitted, and adapted without specific permission, provided attribution is given to Materials Project (legacy.materialsproject.org/terms). No academic-use or non-commercial restriction found.
- Rate limits: start at 25 requests/second (docs, "Tips for Large Downloads"). Automated scripts must not collect large fractions of the database and disseminate them; collecting large fractions for analysis and presenting processed results with attribution is allowed — for large downloads, coordinate by email first (MAPI docs, Security).
- Database release naming: date-based releases (YYYY.MM.DD) selectable via mp-api's `db_version` parameter; current release confirmed by the first authenticated pull (task T-003, 2026-10-21): **2026.09.28**.
- Official material IDs for the benchmark set (from MP's own material pages): mp-22526 = LiCoO2 (R-3m), mp-19017 = LiFePO4 (Pnma), mp-22584 = LiMn2O4 (Fd-3m). **[corrected]** mp-15939 is NOT LiMn2O4 (it is SrAl2B2O7).
- Why it matters: MP publishes DFT electrode voltages, so they can serve as a second comparison for the benchmark alongside literature values, and they shape what "new" means for v1 (decision D-002, now DECIDED).

## BatteryArchive.org
- Use: cell-level cycling data from real batteries, in a standardized format, uploaded with permission from the generating institutions. Confirmed via study_summaries.html.
- Terms: no formal license on the opened page — a code of conduct instead: cite the original study's article and cite batteryarchive.org as the download source; per-dataset group policies may add constraints (linked per dataset).
- Likely relevance: later validation and the cell-level stage (PyBaMM, v2). Confirmed: nothing on the site maps to bulk cathode materials (no structures, no computed voltages) — not part of the v1 cathode screen.
- Site: https://www.batteryarchive.org

## Literature
- Open-access sources first (preprint servers, open-access journals). Record the DOI for every paper.
- Read each source through `/gs-lit-note`. Do not commit PDFs.
- Practical notes from T-002: MDPI and some Wiley/IOP pages block automated fetches (HTTP 403) but allow a real browser or direct PDF download; Europe PMC full-text XML works well for open-access papers. The 1997 PDFs at ceder.berkeley.edu use bitmap fonts that defeat text extraction — plan a human/microfilm read or use lineage-citing secondary sources for anything quoted from them.
