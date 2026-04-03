interface PlaceholderPageProps {
  title: string;
  description: string;
}

export function PlaceholderPage({ title, description }: PlaceholderPageProps) {
  return (
    <section className="panel placeholder-page">
      <p className="eyebrow">Scaffolded Route</p>
      <h2>{title}</h2>
      <p className="lede">{description}</p>
    </section>
  );
}
