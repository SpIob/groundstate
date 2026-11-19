// Plain data table (docs/web/DESIGN.md section 5): real table with th, 1px
// paper grid on the green panel, no zebra, no hover color. Values print
// exactly as stored - no formatting math in the table.

import type { ReactNode } from "react";

export interface TableColumn {
  key: string;
  label: string;
}

export function DataTable(props: { columns: TableColumn[]; rows: Record<string, ReactNode>[]; caption?: string }) {
  return (
    <table>
      {props.caption && <caption className="visually-hidden">{props.caption}</caption>}
      <thead>
        <tr>
          {props.columns.map((c) => (
            <th key={c.key} scope="col">
              {c.label}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {props.rows.map((row, i) => (
          <tr key={i}>
            {props.columns.map((c) => (
              <td key={c.key}>{row[c.key]}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
