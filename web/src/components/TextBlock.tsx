// Justified text column (About, Disclaimer, panel intros - DESIGN.md section 3).

export function TextBlock(props: { paragraphs: string[]; justified?: boolean }) {
  return (
    <div className={props.justified === false ? undefined : "justified"}>
      {props.paragraphs.map((p, i) => (
        <p key={i}>{p}</p>
      ))}
    </div>
  );
}
