# Citation and provenance standard

Status: authoritative. Applies to every reference note, every output file, and every public claim.

## Citation record
Each source gets one record. Fields:

| Field | Meaning |
|---|---|
| `id` | Short stable key, for example `aydinol-1997` or `mp-database` |
| `type` | `paper`, `database`, `dataset`, or `software` |
| `title` | Exact title or database name |
| `authors` | First author plus "et al." is enough |
| `year` | Publication or release year |
| `identifier` | DOI for papers. URL for databases, datasets, software. |
| `version` | Database release, software version, or commit. `UNVERIFIED` if unknown. |
| `accessed_at` | UTC date the source was opened |
| `verified` | `true` only if someone opened the source and the title, year, and identifier match |
| `verified_by` | Role and session, or Mico |

## Claims
A claim points to a citation `id` and a locator (section, table, figure, or page). A number is copied as printed, with its units and conditions.

## Computed values
Each computed value records: `run_id`, inputs (IDs and versions), method and formula version, model name and version, device, and a UTC timestamp. The run's `manifest.json` holds the shared parts.

## Rules
- An identifier that was not opened this session is `UNVERIFIED`, however familiar it looks.
- Never fill a missing field with a guess. Leave it `UNVERIFIED`.
- Quotes stay under 15 words, one per source. Paraphrase the rest.
