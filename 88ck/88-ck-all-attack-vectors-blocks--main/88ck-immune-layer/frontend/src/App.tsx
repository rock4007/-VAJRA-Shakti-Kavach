import { useMemo } from "react";

export function App() {
  const stability = useMemo(() => 0.982, []);

  return (
    <main className="page">
      <section className="hero">
        <h1>88/CK Immune Layer</h1>
        <p>Cross-pillar adaptive defense with stability-first orchestration.</p>
      </section>
      <section className="cards">
        <article>
          <h2>S(t)</h2>
          <p>{stability.toFixed(3)}</p>
        </article>
        <article>
          <h2>Gamma Coupling</h2>
          <p>0.420</p>
        </article>
        <article>
          <h2>PQ Safety</h2>
          <p>Enabled</p>
        </article>
      </section>
    </main>
  );
}
