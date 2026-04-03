const apiBaseUrl: string = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

export default function App() {
  return (
    <main className="app-shell">
      <section className="hero">
        <p className="eyebrow">RPG GM Helper</p>
        <h1>Campaign data and note ingestion, with a typed frontend scaffold.</h1>
        <p className="lede">
          Backend and frontend scaffolding are in place. Next steps are entity CRUD, extraction
          review, and search.
        </p>
      </section>
      <section className="status-card">
        <h2>API Target</h2>
        <code>{apiBaseUrl}</code>
      </section>
    </main>
  );
}
