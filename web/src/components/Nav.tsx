// Top nav on every page except Landing (docs/web/PAGES.md, DESIGN.md section 4).
import { Link } from "./Link";

const NAV_ITEMS: { label: string; href: string }[] = [
  { label: "Home", href: "#/" },
  { label: "Explore", href: "#/explore" },
  { label: "About", href: "#/about" },
  { label: "Contacts", href: "#/contacts" },
  { label: "Disclaimer", href: "#/disclaimer" },
];

export function Nav() {
  return (
    <nav className="top-nav" aria-label="Main">
      {NAV_ITEMS.map((item, i) => (
        <span key={item.label}>
          {i > 0 && <span className="nav-sep"> | </span>}
          <Link href={item.href}>{item.label}</Link>
        </span>
      ))}
    </nav>
  );
}
