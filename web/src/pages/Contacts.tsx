// P3 Contacts (#/contacts): top nav, title row, one row of six tiles.
// URLs come from src/content/contacts.ts (Mico, task W-004); a tile with no
// URL renders unlinked (docs/web/PAGES.md P3).
import { Nav } from "../components/Nav";
import { TitleRow } from "../components/TitleRow";
import { ContactTile } from "../components/ContactTile";
import { CONTACTS } from "../content/contacts";

export function Contacts() {
  return (
    <main className="shell">
      <Nav />
      <TitleRow title="Contacts" />
      <div className="contact-tiles">
        {CONTACTS.map((c) => (
          <ContactTile key={c.id} id={c.id} label={c.label} url={c.url} />
        ))}
      </div>
    </main>
  );
}
