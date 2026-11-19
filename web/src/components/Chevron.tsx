// Pixel chevrons (W-003): the site font JF Dot Shinonome Mincho 16 has no
// single-guillemet glyphs (U+2039/U+203A verified missing 2026-11-17), and
// DESIGN.md section 3 says missing arrow glyphs are drawn as pixel SVGs.
// The dot map below is the wireframe's own chevron, extracted 1px-exact from
// docs/web/design/wireframes/v3-05-explore-index.png (domain rows y169-185 /
// y208-226); the open variant is its mirror. Fill = currentColor, so the
// chevron takes the row's status color like the label text it belongs to.
const ROWS = [
  "##....",
  "###...",
  ".###..",
  "...##.",
  "....##",
  "....##",
  "...###",
  "..##..",
  ".##...",
  "##....",
];

function runs(row: string): Array<[number, number]> {
  const out: Array<[number, number]> = [];
  let x = 0;
  while (x < row.length) {
    if (row[x] === "#") {
      const start = x;
      while (x < row.length && row[x] === "#") x += 1;
      out.push([start, x - start]);
    } else {
      x += 1;
    }
  }
  return out;
}

export function Chevron(props: { open?: boolean }) {
  return (
    <svg
      className="chevron"
      viewBox="0 0 6 10"
      width="6"
      height="10"
      fill="currentColor"
      shapeRendering="crispEdges"
      aria-hidden="true"
    >
      {ROWS.flatMap((row, y) =>
        runs(row).map(([x, w]) => (
          <rect
            key={`${x}-${y}`}
            x={props.open ? 6 - x - w : x}
            y={y}
            width={w}
            height="1"
          />
        )),
      )}
    </svg>
  );
}
