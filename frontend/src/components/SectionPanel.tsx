import type { ReactNode } from "react";

type SectionPanelProps = {
  title?: string;
  description?: string;
  children: ReactNode;
};

export function SectionPanel({ title, description, children }: SectionPanelProps) {
  return (
    <section className="panel section-panel">
      {title ? <h3 className="font-ui">{title}</h3> : null}
      {description ? <p className="section-copy">{description}</p> : null}
      {children}
    </section>
  );
}
