import type { DashboardData } from "../lib/dashboard-data";

export default function Dashboard({ initialData }: { initialData: DashboardData }) {
  const { generatedAt, api, metrics, modules, notice } = initialData;

  return (
    <main className="container">
      <header>
        <h1>ZACMA Operations Dashboard</h1>
        <p>{notice}</p>
        <p style={{ fontSize: "0.9rem", opacity: 0.8 }}>Generated at: {generatedAt}</p>
        <p style={{ fontSize: "0.9rem", opacity: 0.9 }}>
          API status: {api.label} — {api.detail}
        </p>
      </header>

      <section style={{ marginTop: "1rem" }}>
        <h2>Metrics</h2>
        <ul>
          {metrics.map((m) => (
            <li key={m.label}>
              <strong>{m.label}:</strong> {m.value} <em>({m.detail})</em>
            </li>
          ))}
        </ul>
      </section>

      <section style={{ marginTop: "1rem" }}>
        <h2>Modules</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "0.75rem" }}>
          {modules.map((mod) => (
            <article key={mod.key} style={{ padding: "0.75rem", borderRadius: 8, background: "rgba(255,255,255,0.03)" }}>
              <div style={{ fontSize: "1.25rem" }}>{mod.symbol} {mod.label}</div>
              <div style={{ marginTop: "0.25rem" }}>{mod.description}</div>
              <div style={{ marginTop: "0.5rem", fontWeight: 700 }}>{mod.count} {mod.unit}</div>
              <div style={{ marginTop: "0.25rem", opacity: 0.9 }}>State: {mod.state}</div>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
