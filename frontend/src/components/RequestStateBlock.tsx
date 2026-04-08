type RequestStateBlockProps = {
  title: string;
  message: string;
  tone?: "default" | "error";
};

export function RequestStateBlock({ title, message, tone = "default" }: RequestStateBlockProps) {
  return (
    <section className={`panel request-state request-state-${tone}`}>
      <h3>{title}</h3>
      <p>{message}</p>
    </section>
  );
}
