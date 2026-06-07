import { useEffect, useMemo, useState } from "react";

type StabilityStatus = {
  s_value?: number;
  m_value?: number;
};

export function App() {
  const [status, setStatus] = useState<StabilityStatus | null>(null);
  const [connected, setConnected] = useState(false);
  const gatewayUrl = useMemo(() => import.meta.env.VITE_GATEWAY_URL || "http://localhost:8080", []);
  const stability = status?.s_value ?? 0;
  const gamma = status?.m_value ?? 0.42;

  useEffect(() => {
    const controller = new AbortController();

    fetch(`${gatewayUrl}/immune/status`, { signal: controller.signal })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`status ${response.status}`);
        }
        return response.json() as Promise<StabilityStatus>;
      })
      .then((payload) => {
        setStatus(payload);
        setConnected(true);
      })
      .catch(() => {
        setConnected(false);
      });

    return () => controller.abort();
  }, [gatewayUrl]);

  return (
    <main className="page">
      <section className="hero">
        <h1>88/CK Immune Layer</h1>
        <p>{connected ? "Gateway telemetry connected." : "Gateway telemetry awaiting connection."}</p>
      </section>
      <section className="cards">
        <article>
          <h2>S(t)</h2>
          <p>{connected ? stability.toFixed(3) : "Offline"}</p>
        </article>
        <article>
          <h2>Gamma Coupling</h2>
          <p>{connected ? gamma.toFixed(3) : "Pending"}</p>
        </article>
        <article>
          <h2>PQ Safety</h2>
          <p>{connected ? "Enabled" : "Unknown"}</p>
        </article>
      </section>
    </main>
  );
}
