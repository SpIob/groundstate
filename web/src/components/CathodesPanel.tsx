// P7 Cathodes data panel (task W-008, skill gs-web-data-view): promoted
// results/ rendered exactly as stored. All values flow through
// src/data/display.ts verbatim - no math, rounding, or sorting anywhere.
// Empty states are part of the deliverable; the benchmark region shows its
// empty state today (results/index.json has benchmark_run_id: null; there is
// no results/ benchmark shape - PROPOSED D-014).
import { useEffect, useState } from "react";
import { Panel } from "./Panel";
import { TextBlock } from "./TextBlock";
import { DataTable, type TableColumn } from "./DataTable";
import { loadCandidate, loadCitations, loadIndex } from "../data/loaders";
import {
  EMPTY_CANDIDATES,
  LOAD_ERROR,
  benchmarkRegionText,
  candidateRows,
  closingLine,
  disclaimerMismatchNotes,
} from "../data/display";
import type { CandidateResult, CitationsFile, ResultsIndex } from "../data/types";
import { copyCathodes } from "../content/copy.cathodes";
import { copyDisclaimer } from "../content/copy.disclaimer";

type Loaded = { index: ResultsIndex; candidates: CandidateResult[]; citations: CitationsFile };

// Columns per docs/web/PAGES.md P7 item 3. Units in headers; the voltage
// header carries "Predicted" (skill: voltage is labeled predicted).
const candidateColumns: TableColumn[] = [
  { key: "formula", label: "Formula" },
  { key: "material_id", label: "Material id" },
  { key: "predicted_voltage_V", label: "Predicted voltage (V)" },
  { key: "capacity_mAh_g", label: "Capacity (mAh/g)" },
  { key: "e_above_hull_eV_atom", label: "Energy above hull (eV/atom)" },
  { key: "audit_status", label: "Audit status" },
  { key: "citations", label: "Citations" },
];

export function CathodesPanel() {
  const data = useCathodesData();
  return (
    <Panel kind="green">
      <TextBlock paragraphs={[copyCathodes.intro]} />
      {data === "loading" ? (
        // No fake empty states while loading: nothing prints but the copy.
        <p className="visually-hidden">Loading results.</p>
      ) : data === "error" ? (
        <p>{LOAD_ERROR}</p>
      ) : (
        <CathodesData data={data} />
      )}
    </Panel>
  );
}

function CathodesData({ data }: { data: Loaded }) {
  const { rows } = candidateRows(data.candidates, data.citations.citations);
  return (
    <>
      <h2>Benchmark</h2>
      <p>{benchmarkRegionText(data.index)}</p>
      <h2>Candidates</h2>
      {rows.length === 0 ? (
        <p>{EMPTY_CANDIDATES}</p>
      ) : (
        <DataTable
          columns={candidateColumns}
          caption="Promoted cathode candidates"
          rows={rows.map((r) => ({
            formula: r.formula,
            material_id: r.material_id,
            predicted_voltage_V: r.predicted_voltage_V,
            capacity_mAh_g: r.capacity_mAh_g,
            e_above_hull_eV_atom: r.e_above_hull_eV_atom,
            audit_status: r.audit_status,
            citations: (
              <>
                {r.citations.map((c, j) => (
                  <span key={j}>
                    {j > 0 && ", "}
                    {c.missing ? (
                      `${c.id} (UNVERIFIED)`
                    ) : c.href ? (
                      <a href={c.href}>{c.id}</a>
                    ) : (
                      c.id
                    )}
                  </span>
                ))}
              </>
            ),
          }))}
        />
      )}
      {rows.length > 0 &&
        disclaimerMismatchNotes(rows, copyDisclaimer.version).map((note) => (
          <p key={note}>{note}</p>
        ))}
      <h2>Method</h2>
      <TextBlock paragraphs={[copyCathodes.method]} />
      <p>
        {copyCathodes.closingLine} {closingLine(data.index, rows)} Disclaimer version{" "}
        {copyDisclaimer.version}.
      </p>
    </>
  );
}

function useCathodesData(): "loading" | "error" | Loaded {
  const [state, setState] = useState<"loading" | "error" | Loaded>("loading");
  useEffect(() => {
    let alive = true;
    Promise.all([loadIndex(), loadCitations()])
      .then(([index, citations]) =>
        Promise.all(index.candidates.map((id) => loadCandidate(id))).then((candidates) => ({
          index,
          citations,
          candidates,
        })),
      )
      .then((loaded) => {
        if (alive) setState(loaded);
      })
      .catch(() => {
        if (alive) setState("error");
      });
    return () => {
      alive = false;
    };
  }, []);
  return state;
}
