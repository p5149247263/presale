import React, { useState } from "react";
import { generateArchitecture } from "../api/client";

function cleanSummary(raw: string) {
  if (!raw) return "";
  let text = raw.trim();
  text = text.replace(/^\[MOCK-[^\]]+\]\s*/i, "");
  text = text.replace(/^\[(OPENAI|ANTHROPIC|LOCAL)[^\]]*\]\s*/i, "");
  text = text.split("Requirements context:")[0].trim();
  if (!text.endsWith(".")) {
    text = `${text}.`;
  }
  return text;
}

export function ArchitecturePage({ projectId }: { projectId: string }) {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function onGenerate() {
    setError("");
    setIsLoading(true);
    try {
      const out = await generateArchitecture(projectId);
      setData(out);
    } catch (e: any) {
      setError(e?.message || "Failed to generate architecture.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="card">
      <h2>Architecture Recommendation</h2>
      <button onClick={onGenerate} disabled={isLoading}>
        {isLoading ? "Generating..." : "Generate"}
      </button>
      {error && <p style={{ color: "#b00020" }}>{error}</p>}
      {data && (
        <div className="split architecture-grid">
          {data.options.map((o: any) => (
            <article key={o.name} className="architecture-card">
              <h3 className="architecture-title">{o.name}</h3>
              <p className="architecture-summary">{cleanSummary(o.summary)}</p>

              <div className="architecture-section">
                <h4>Components</h4>
                <div className="chip-wrap">
                  {(o.components || []).map((c: string) => (
                    <span className="chip" key={`${o.name}-${c}`}>
                      {c}
                    </span>
                  ))}
                </div>
              </div>

              <div className="architecture-section">
                <h4>Latency & Scalability</h4>
                <ul className="architecture-list">
                  {(o.latency_scalability_notes || []).map((n: string, idx: number) => (
                    <li key={`${o.name}-lat-${idx}`}>{n}</li>
                  ))}
                </ul>
              </div>

              <div className="architecture-section">
                <h4>Integration Plan</h4>
                <ul className="architecture-list">
                  {(o.integration_plan || []).map((n: string, idx: number) => (
                    <li key={`${o.name}-int-${idx}`}>{n}</li>
                  ))}
                </ul>
              </div>

              <div className="architecture-section">
                <h4>Mermaid</h4>
                <pre className="architecture-code">{o.mermaid}</pre>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
