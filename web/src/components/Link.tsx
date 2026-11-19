// Internal link: plain <a> with the hash href. Kept as one component so the
// link rules (green, underline on hover/focus, focus outline) stay in CSS.

import type { ReactNode } from "react";

export function Link(props: { href: string; children: ReactNode; className?: string }) {
  return (
    <a href={props.href} className={props.className}>
      {props.children}
    </a>
  );
}
