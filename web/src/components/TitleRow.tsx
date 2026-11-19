// Title row: `<- | Title` (docs/web/PAGES.md, DESIGN.md section 4).
import { Link } from "./Link";

export function TitleRow({ title }: { title: string }) {
  return (
    <div className="title-row">
      <Link href="#/" className="back">
        &larr;
      </Link>
      <span aria-hidden="true">|</span>
      <h1>{title}</h1>
    </div>
  );
}
