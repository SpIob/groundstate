# Data sources (v1)

Status: UNVERIFIED. Written from general knowledge. Task T-002 opens each source and confirms every line, or corrects it.

## Materials Project
- Use: crystal structures, computed energies, energy above hull. Possibly precomputed insertion-electrode data (voltage, capacity). Confirm what the current API exposes.
- Access: free account and API key, used through the `mp-api` client. Key goes in `.env` as `MP_API_KEY`.
- Site: https://materialsproject.org . API page: https://next-gen.materialsproject.org/api
- To confirm: license and terms of use, rate limits, database release naming, and whether electrode data is available through the API.
- Why it matters: if Materials Project already publishes DFT electrode voltages, they can serve as a second comparison for the benchmark and shape what "new" means for v1 (decision D-002).

## BatteryArchive.org
- Use: cell-level cycling data from real batteries.
- Likely relevance: later validation and the cell-level stage (PyBaMM, v2). Probably not part of the v1 cathode screen.
- Site: https://www.batteryarchive.org
- To confirm: what data it holds, its terms, and whether any of it maps to bulk cathode materials.

## Literature
- Open-access sources first (preprint servers, open-access journals). Record the DOI for every paper.
- Read each source through `/gs-lit-note`. Do not commit PDFs.
