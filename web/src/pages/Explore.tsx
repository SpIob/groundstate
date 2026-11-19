// P5-P9 Explore (#/explore...): top nav, title row, green rail, domain list,
// and the panel for the selected domain/child (docs/web/PAGES.md P5-P9).
// Panel by status: active leaf = content panel (green; the cathodes data
// panel is built by task W-008, so the shell shows the placeholder empty
// states), planned = orange placeholder, exploring = gray placeholder.
import { Nav } from "../components/Nav";
import { TitleRow } from "../components/TitleRow";
import { DomainList } from "../components/DomainList";
import { Panel } from "../components/Panel";
import { PlaceholderPanel } from "../components/PlaceholderPanel";
import { TextBlock } from "../components/TextBlock";
import { DOMAINS, type DomainStatus } from "../content/domains";
import { copyCathodes } from "../content/copy.cathodes";
import { copyDisclaimer } from "../content/copy.disclaimer";

export function Explore(props: { domain?: string; child?: string }) {
  return (
    <main className="shell">
      <Nav />
      <TitleRow title="Explore" />
      <div className="explore-body">
        <div className="explore-rail" aria-hidden="true" />
        <div className="explore-list">
          <DomainList selectedDomain={props.domain} selectedChild={props.child} />
        </div>
        <div className="explore-panel-slot">{panelFor(props.domain, props.child)}</div>
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

// P7 shell: the real benchmark/candidates tables arrive with W-008, which
// owns the data rules. Until then the panel renders the approved empty-state
// strings and the copy slots as pending-approval stubs.
function CathodesPanel() {
  return (
    <Panel kind="green">
      <TextBlock paragraphs={[copyCathodes.intro]} />
      <h2>Benchmark</h2>
      <p>Benchmark has not been run yet.</p>
      <h2>Candidates</h2>
      <p>No candidates have passed audit yet.</p>
      <h2>Method</h2>
      <TextBlock paragraphs={[copyCathodes.method]} />
      {/* P7 closing line (item 5): estimates statement + the disclaimer
          version from the copy file (P4 ties candidate data to it). The run
          id joins with the data in W-008 - until then the panel shows empty
          states, so there is no run to cite. */}
      <p>
        {copyCathodes.closingLine} Disclaimer version {copyDisclaimer.version}.
      </p>
    </Panel>
  );
}
