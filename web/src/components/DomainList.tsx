// Explore domain list (docs/web/PAGES.md P5-P9). Rows are real links,
// reachable by Tab, in registry order. Chevron `>` collapsed, `<` when the
// row is selected/open. Status is also exposed as visually hidden text.
// No dimming (D-011 DECIDED option B): non-selected rows keep their normal
// color; the selected row is marked by `<` and an underline.
import { DOMAINS, type DomainDef } from "../content/domains";
import { Link } from "./Link";
import { Flyout } from "./Flyout";
import { Chevron } from "./Chevron";

export function DomainList(props: { selectedDomain?: string; selectedChild?: string }) {
  return (
    <ul className="domain-list">
      {DOMAINS.map((d) => (
        <DomainRow
          key={d.id}
          domain={d}
          selected={props.selectedDomain === d.id}
          selectedChild={props.selectedDomain === d.id ? props.selectedChild : undefined}
        />
      ))}
    </ul>
  );
}

function DomainRow(props: { domain: DomainDef; selected: boolean; selectedChild?: string }) {
  const d = props.domain;
  const isOpen = props.selected;
  return (
    <li>
      <Link href={`#/explore/${d.id}`} className={`domain-row status-${d.status}${isOpen ? " selected" : ""}`}>
        {d.label} <Chevron open={isOpen} />
        <span className="visually-hidden">, {d.status}</span>
      </Link>
      {isOpen && d.children.length > 0 && (
        <Flyout
          domain={d}
          selectedChild={props.selectedChild}
          docked={props.selectedChild != null}
        />
      )}
    </li>
  );
}
