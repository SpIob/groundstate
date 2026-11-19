// Batteries flyout (docs/web/PAGES.md P6): green fill, panel text, one row
// per child. Status exposed as visually hidden text (`, planned`).
// Chevron on the active child only: PAGES.md P6/P7 list the flyout as
// "Cathodes › and Electrolytes" (and the v3 frames 6-7 draw it that way) -
// the planned child carries no chevron in any state; the active child's
// chevron flips › (closed) to ‹ (selected). A selected chevron-less row is
// marked by its underline alone.
// Position (W-003): on the domain route the flyout floats RIGHT of the
// Batteries row (DESIGN.md section 4; the W-002 delta audit called the
// in-flow rendering a defect). When a child is selected (P7, panel open) it
// docks below the row instead: the wireframe frame 7 draws no flyout beside
// the panel, and a floating flyout there would cover the panel's text; P7
// keeps the two rows visible, so they stay under the Batteries row.
import { type DomainDef } from "../content/domains";
import { Link } from "./Link";
import { Chevron } from "./Chevron";

export function Flyout(props: { domain: DomainDef; selectedChild?: string; docked?: boolean }) {
  return (
    <ul className={`flyout${props.docked ? " docked" : ""}`}>
      {props.domain.children.map((c) => (
        <li key={c.id}>
          <Link
            href={`#/explore/${props.domain.id}/${c.id}`}
            className={props.selectedChild === c.id ? "selected" : undefined}
          >
            {c.label}{" "}
            {c.status === "active" && <Chevron open={props.selectedChild === c.id} />}
            <span className="visually-hidden">, {c.status}</span>
          </Link>
        </li>
      ))}
    </ul>
  );
}
