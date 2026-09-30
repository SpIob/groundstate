# References

What agents read before acting. Nothing here counts as evidence until its status says `verified`.

| Path | What it holds | Status |
|---|---|---|
| `plan/initial-plan.md` | Mico's Initial Project Plan (Sept 25, 2026), transcribed. Source of truth for scope. | Authoritative |
| `CITATION_STANDARD.md` | How every source and every value is recorded. | Authoritative |
| `glossary.md` | Project terms, so agents use them the same way. | Draft |
| `data-sources.md` | Data sources for v1 and what each is for. | UNVERIFIED until T-002 |
| `science/method-notes.md` | Voltage, capacity, and stability methods, plus open research questions. | UNVERIFIED until T-002 |
| `science/benchmark-set.md` | The trust benchmark: known cathodes and their sourced reference voltages. | Blank until T-002 |
| `literature/` | One note per source read (`_template.md`). PDFs are gitignored. | Grows over time |

## Adding a reference
Run `/gs-lit-note`. Every new file needs a status line at the top: `authoritative`, `draft`, `UNVERIFIED`, or `verified`.
Promote `UNVERIFIED` to `verified` only after someone opens the primary source and checks it.
