// One contact tile (docs/web/PAGES.md P3). A tile with no URL renders
// unlinked and the build prints UNSET (check-links) until Mico supplies
// URLs. Every tile shows its icon (flat token rect-SVGs converted in W-003,
// paper fill for the ink-green tile; provenance in public/assets/ASSETS.md):
// Mico, 2026-11-17 — the icons should be visible before the URLs land, so
// unset tiles render the icon too (dashed outline, not a link); the tile's
// aria-label is the accessible name and the icon is decorative.

export function ContactTile(props: { id: string; label: string; url: string | null }) {
  if (props.url) {
    return (
      <a className="contact-tile" href={props.url} aria-label={props.label}>
        <img src={`/assets/icon-${props.id}.svg`} alt="" className={`pixel-img tile-icon tile-${props.id}`} />
      </a>
    );
  }
  return (
    <div className="contact-tile unset" aria-label={`${props.label} (unset)`}>
      <img src={`/assets/icon-${props.id}.svg`} alt="" className={`pixel-img tile-icon tile-${props.id}`} />
    </div>
  );
}
