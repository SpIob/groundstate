// P2 About (#/about): top nav, title row, justified copy slot `about`.
// Nothing else on the page (docs/web/PAGES.md P2).
import { Nav } from "../components/Nav";
import { TitleRow } from "../components/TitleRow";
import { TextBlock } from "../components/TextBlock";
import { copyAbout } from "../content/copy.about";

export function About() {
  return (
    <main className="shell">
      <Nav />
      <TitleRow title="About" />
      <div className="text-column">
        <TextBlock paragraphs={copyAbout.paragraphs} />
      </div>
    </main>
  );
}
