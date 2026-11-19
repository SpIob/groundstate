// Flat content panel (docs/web/DESIGN.md section 5): flat fill, no border
// radius, no border, internal scroll when content is taller than the panel.

import type { ReactNode } from "react";

export function Panel(props: { kind: "green" | "orange" | "gray"; children: ReactNode }) {
  return (
    <section className={`panel panel-${props.kind}`}>{props.children}</section>
  );
}
