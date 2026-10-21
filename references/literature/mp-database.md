---
status: verified 2026-10-21 (T-002)
---
# Materials Project database and API

## Citation record
- id: mp-database
- type: database
- title: Materials Project database and Materials API (MAPI)
- authors: Materials Project (Lawrence Berkeley National Laboratory)
- year: UNVERIFIED (ongoing project; founding year not stated on pages opened)
- identifier: https://next-gen.materialsproject.org ; API https://api.materialsproject.org
- version: API 0.88.0rc4 (from live openapi.json on 2026-10-21); database release version UNVERIFIED (releases are date-based, e.g. YYYY.MM.DD, per mp-api docs)
- accessed_at: 2026-10-21
- verified: true
- verified_by: Researcher (Hermes), T-002 session — terms page fetched raw, API docs pages opened, live OpenAPI spec read, material pages opened

## Question this source was read for
T-002 criterion 1: confirm what the API exposes, its license and terms, and the official material IDs for the benchmark set.

## Claims
| Claim (paraphrase) | Locator | Number as printed (units, conditions) |
|---|---|---|
| License: downloading content means accepting Creative Commons Attribution 4.0; content may be copied, distributed, transmitted, adapted without specific permission, with attribution to Materials Project | legacy.materialsproject.org/terms, "License" section | CC BY 4.0 |
| API rate limits start at 25 requests/second | docs.materialsproject.org "Tips for Large Downloads" | 25/second |
| Automated scripts must not collect large fractions of the database and disseminate them; collecting large fractions for analysis and presenting processed results with attribution is allowed; large downloads should be coordinated by email | doc.docs.materialsproject.org "The Materials API", Security section | rule as stated |
| Electrode (battery) data is exposed via the API: GET /materials/insertion_electrodes/ and GET /materials/conversion_electrodes/ | live openapi.json (api.materialsproject.org, API 0.88.0rc4) | endpoints as listed; docs: battery IDs like mp-22526_Li, fields average_voltage, capacity_grav, stability_charge/discharge |
| Official material IDs for the benchmark set | legacy.materialsproject.org material pages (page titles) | mp-22526 = LiCoO2 (trigonal, R-3m); mp-19017 = LiFePO4 (orthorhombic, Pnma); mp-22584 = LiMn2O4 (cubic, Fd-3m) |
| API key required; keep it secret; account holder is responsible for violations | MAPI docs, "API keys" | rule as stated |

## Not shown by this source
The current database release identifier (not printed on the pages opened). Whether MP's computed electrode voltages are exported in bulk for redistribution (not checked; assume API-only, attribution-based use).

## How it bears on the current task
Confirms `references/data-sources.md`'s MP line: free API key via mp-api, CC BY 4.0 with attribution, electrode data available for a second benchmark comparison. The mp-15939 = LiMn2O4 guess that circulated earlier is WRONG (mp-15939 is SrAl2B2O7 per MP's own page); mp-22584 is the canonical cubic LiMn2O4 ID. Rate limits are generous relative to the pipeline's batch use, but the one-heavy-job rule still applies to local compute, not API calls.
