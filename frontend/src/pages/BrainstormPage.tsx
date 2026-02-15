import React, { useState } from "react";
import { brainstorm } from "../api/client";

type ClarificationItem = {
  question: string;
  reason: string;
};

type Citation = {
  doc_id: string;
  page: number;
  section: string;
  snippet_hash: string;
};

type BrainstormResult = {
  answer: string;
  opportunities: string[];
  differentiators: string[];
  clarification_list: ClarificationItem[];
  citations: Citation[];
};

export function BrainstormPage({ projectId }: { projectId: string }) {
  const [prompt, setPrompt] = useState("What upsell opportunities should we include?");
  const [result, setResult] = useState<BrainstormResult | null>(null);
  const [isAsking, setIsAsking] = useState(false);
  const [error, setError] = useState("");
  const [showRaw, setShowRaw] = useState(false);

  async function onAsk() {
    setError("");
    setIsAsking(true);
    try {
      const out = await brainstorm(projectId, prompt);
      setResult(out);
    } catch (e: any) {
      setError(e?.message || "Failed to get brainstorming response.");
    } finally {
      setIsAsking(false);
    }
  }

  const uniqueCitations = React.useMemo(() => {
    if (!result?.citations) return [];
    const seen = new Set<string>();
    const out: Citation[] = [];
    for (const c of result.citations) {
      const key = `${c.doc_id}|${c.page}|${c.section}`;
      if (seen.has(key)) continue;
      seen.add(key);
      out.push(c);
    }
    return out;
  }, [result]);

  return (
    <section className="card">
      <h2>Brainstorming Workspace</h2>
      <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} rows={3} />
      <button onClick={onAsk} disabled={isAsking}>
        {isAsking ? "Asking..." : "Ask"}
      </button>
      {error && <p style={{ color: "#b00020" }}>{error}</p>}

      {result && (
        <article className="brief-card">
          <h3>Brainstorm Brief</h3>

          <section className="brief-section">
            <h4>Recommended Direction</h4>
            <p>{result.answer}</p>
          </section>

          <section className="brief-section">
            <h4>Opportunities</h4>
            <ul className="brief-list">
              {result.opportunities.map((item, idx) => (
                <li key={`op-${idx}`}>{item}</li>
              ))}
            </ul>
          </section>

          <section className="brief-section">
            <h4>Differentiators</h4>
            <ul className="brief-list">
              {result.differentiators.map((item, idx) => (
                <li key={`df-${idx}`}>{item}</li>
              ))}
            </ul>
          </section>

          <section className="brief-section">
            <h4>Client Clarifications</h4>
            <ul className="brief-list">
              {result.clarification_list.map((item, idx) => (
                <li key={`cl-${idx}`}>
                  <strong>{item.question}</strong>
                  <div className="muted-line">Reason: {item.reason}</div>
                </li>
              ))}
            </ul>
          </section>

          {uniqueCitations.length > 0 && (
            <section className="brief-section">
              <h4>Traceability</h4>
              <div className="chip-wrap">
                {uniqueCitations.map((c) => (
                  <span className="chip" key={c.snippet_hash} title={`${c.doc_id} | ${c.snippet_hash}`}>
                    p{c.page} {c.section}
                  </span>
                ))}
              </div>
            </section>
          )}

          <label className="debug-toggle">
            <input type="checkbox" checked={showRaw} onChange={(e) => setShowRaw(e.target.checked)} />
            Show raw JSON
          </label>
          {showRaw && <pre>{JSON.stringify(result, null, 2)}</pre>}
        </article>
      )}
    </section>
  );
}
