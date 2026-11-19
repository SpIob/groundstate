// P1 Landing (#/): no top nav, centered column (docs/web/PAGES.md P1).
// The mark and wordmark are image assets ("not live text", PAGES.md P1),
// converted in W-003 to flat token rect-SVGs from Mico's originals
// (docs/web/design/assets-src/); provenance in public/assets/ASSETS.md.
import { Link } from "../components/Link";

const FOOTER_LINKS = [
  { label: "About", href: "#/about" },
  { label: "Contacts", href: "#/contacts" },
  { label: "Disclaimer", href: "#/disclaimer" },
];

export function Landing() {
  return (
    <main className="landing">
      <div className="landing-mark">
        <img
          src="/assets/logo-mark.svg"
          alt="Groundstate logo"
          className="pixel-img"
          width="306"
          height="233"
        />
      </div>
      {/* h1 per DESIGN.md section 8 (one h1 per page); resolves the W-002
          audit flag 2, accepted 2026-10-29 and carried into W-003. The
          wordmark is an image asset, so the h1 carries it with alt text. */}
      <h1 className="landing-wordmark">
        <img src="/assets/wordmark.svg" alt="Groundstate" className="pixel-img" width="895" height="139" />
      </h1>
      <p className="landing-cta">
        <Link href="#/explore">Explore &rarr;</Link>
      </p>
      <nav className="landing-links" aria-label="Footer">
        {FOOTER_LINKS.map((item, i) => (
          <span key={item.label}>
            {i > 0 && <span className="nav-sep"> | </span>}
            <Link href={item.href}>{item.label}</Link>
          </span>
        ))}
      </nav>
    </main>
  );
}
