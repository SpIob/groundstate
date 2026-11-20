// P5-P9 Explore (#/explore...): top nav, title row, green rail, domain list,
// and the panel for the selected domain/child (docs/web/PAGES.md P5-P9).
// Panel by status: active leaf = the cathodes data panel (green; task W-008
// wires the promoted results/ data via components/CathodesPanel.tsx),
// planned = orange placeholder, exploring = gray placeholder.
import { Nav } from "../components/Nav";
import { TitleRow } from "../components/TitleRow";
import { DomainList } from "../components/DomainList";
import { PlaceholderPanel } from "../components/PlaceholderPanel";
import { CathodesPanel } from "../components/CathodesPanel";
import { DOMAINS, type DomainStatus } from "../content/domains";

export function Explore(props: { domain?: string; child?: string }) {
  const panel = panelFor(props.domain, props.child);
  return (
    <main className="shell">
      <Nav />
      <TitleRow title="Explore" />
      {/* Mico 2026-11-20: `with-panel` only gates the sidebar's height cap
          (see layout.css) - the margins are unconditional. It must NOT be
          applied when the flyout floats (P6): overflow on .explore-list
          clips the absolutely positioned flyout and hides it. */}
      <div className={`explore-body${panel ? " with-panel" : ""}`}>
        <div className="explore-rail" aria-hidden="true" />
        <div className="explore-list">
          <DomainList selectedDomain={props.domain} selectedChild={props.child} />
        </div>
        <div className="explore-panel-slot">{panel}</div>
      </div>
    </main>
  );
}

function panelFor(domain?: string, child?: string) {
  // No selection (P5): nothing but the list.
  if (!domain) {
    return null;
  }
  const d = DOMAINS.find((x) => x.id === domain);
  if (!d) {
    return null;
  }
  // Selected domain with children but no child chosen (P6): flyout only.
  if (!child) {
    return d.children.length > 0 ? null : placeholderFor(d.status);
  }
  const c = d.children.find((x) => x.id === child);
  if (!c) {
    return null;
  }
  if (c.status === "active") {
    return <CathodesPanel />;
  }
  return placeholderFor(c.status);
}

function placeholderFor(status: DomainStatus): ReturnType<typeof PlaceholderPanel> | null {
  if (status === "planned" || status === "exploring") {
    return <PlaceholderPanel kind={status} />;
  }
  return null;
}
