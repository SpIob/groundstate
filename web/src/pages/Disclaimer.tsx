// P4 Disclaimer (#/disclaimer): top nav, title row, warning-triangle icon
// centered above the justified text column, then the version line taken from
// the copy file's `version` field (docs/web/PAGES.md P4). The triangle is
// the W-003 rect-SVG conversion of Mico's original (paper-matched fill with
// a green outline, as drawn; provenance in public/assets/ASSETS.md).
import { Nav } from "../components/Nav";
import { TitleRow } from "../components/TitleRow";
import { TextBlock } from "../components/TextBlock";
import { copyDisclaimer } from "../content/copy.disclaimer";

export function Disclaimer() {
  return (
    <main className="shell">
      <Nav />
      <TitleRow title="Disclaimer" />
      <div className="disclaimer-icon">
        <img
          src="/assets/icon-warning.svg"
          alt="Warning triangle icon"
          className="pixel-img warning-img"
          width="149"
          height="127"
        />
      </div>
      <div className="text-column">
        <TextBlock paragraphs={copyDisclaimer.paragraphs} />
        <p>Disclaimer version {copyDisclaimer.version}</p>
      </div>
    </main>
  );
}
