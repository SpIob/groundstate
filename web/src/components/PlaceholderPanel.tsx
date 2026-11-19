// Placeholder panel (docs/web/PAGES.md P8/P9): pixel icon centered, message
// centered under it. Icons are the W-003 rect-SVG conversions of Mico's
// originals (public/assets/, provenance in ASSETS.md), rendered in
// --ink-green per the D-011 amendment (panel text and icons).
import { STATUS_MESSAGES } from "../content/status-messages";

export function PlaceholderPanel(props: { kind: "planned" | "exploring" }) {
  return (
    <section className={`panel panel-${props.kind === "planned" ? "orange" : "gray"} placeholder-panel`}>
      {props.kind === "planned" ? (
        <img
          src="/assets/icon-lightbulb.svg"
          alt="Planned icon: pixel lightbulb"
          className="pixel-img panel-icon"
          width="156"
          height="166"
        />
      ) : (
        <img
          src="/assets/icon-question.svg"
          alt="Exploring icon: pixel question mark"
          className="pixel-img panel-icon"
          width="81"
          height="136"
        />
      )}
      <p>{STATUS_MESSAGES[props.kind]}</p>
    </section>
  );
}
