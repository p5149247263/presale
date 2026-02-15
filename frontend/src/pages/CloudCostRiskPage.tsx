import React, { useState } from "react";
import { assessRisks, estimateCost, recommendCloud } from "../api/client";

export function CloudCostRiskPage({ projectId }: { projectId: string }) {
  const [cloud, setCloud] = useState<any>();
  const [cost, setCost] = useState<any>();
  const [risk, setRisk] = useState<any>();
  const [error, setError] = useState("");
  const [showRaw, setShowRaw] = useState(false);

  return (
    <section className="card">
      <h2>Cloud, Cost, Risk</h2>
      <div className="row">
        <button
          onClick={async () => {
            setError("");
            try {
              setCloud(await recommendCloud(projectId));
            } catch (e: any) {
              setError(e?.message || "Failed to generate cloud recommendation.");
            }
          }}
        >
          Cloud Recommendation
        </button>
        <button
          onClick={async () => {
            setError("");
            try {
              setCost(await estimateCost(projectId));
            } catch (e: any) {
              setError(e?.message || "Failed to estimate cost.");
            }
          }}
        >
          Estimate Cost
        </button>
        <button
          onClick={async () => {
            setError("");
            try {
              setRisk(await assessRisks(projectId));
            } catch (e: any) {
              setError(e?.message || "Failed to assess risks.");
            }
          }}
        >
          Assess Risks
        </button>
      </div>
      {error && <p style={{ color: "#b00020" }}>{error}</p>}

      <div className="split brief-grid">
        {cloud && (
          <article className="brief-card">
            <h3>Cloud Recommendation</h3>
            <p>
              <strong>Primary:</strong> {cloud.primary_cloud}
            </p>
            <p>{cloud.rationale}</p>
            <h4>Constraints Considered</h4>
            <ul className="brief-list">
              {(cloud.constraints_considered || []).map((c: string, idx: number) => (
                <li key={`cc-${idx}`}>{c}</li>
              ))}
            </ul>
            {cloud.alternatives?.length > 0 && (
              <>
                <h4>Alternatives</h4>
                <div className="chip-wrap">
                  {cloud.alternatives.map((a: string) => (
                    <span className="chip" key={a}>
                      {a}
                    </span>
                  ))}
                </div>
              </>
            )}
          </article>
        )}

        {cost && (
          <article className="brief-card">
            <h3>Cost Estimate</h3>
            <p>
              <strong>Best:</strong> ${Number(cost.best_case_total || 0).toLocaleString()}
            </p>
            <p>
              <strong>Expected:</strong> ${Number(cost.expected_total || 0).toLocaleString()}
            </p>
            <p>
              <strong>Worst:</strong> ${Number(cost.worst_case_total || 0).toLocaleString()}
            </p>
            <h4>Top Line Items</h4>
            <ul className="brief-list">
              {(cost.line_items || []).slice(0, 6).map((i: any, idx: number) => (
                <li key={`li-${idx}`}>
                  {i.category}: {i.item} (${Number(i.monthly_cost_usd || 0).toLocaleString()}/mo)
                </li>
              ))}
            </ul>
          </article>
        )}

        {risk && (
          <article className="brief-card">
            <h3>Risk Register</h3>
            <ul className="brief-list">
              {(risk.risks || []).map((r: any) => (
                <li key={r.risk_id}>
                  <strong>{r.risk_id}</strong> ({r.category}) - {r.description}
                  <div className="muted-line">
                    Likelihood: {r.likelihood} | Impact: {r.impact} | Residual: {r.residual_risk}
                  </div>
                  <div className="muted-line">Owner: {r.owner}</div>
                </li>
              ))}
            </ul>
          </article>
        )}
      </div>

      {(cloud || cost || risk) && (
        <label className="debug-toggle">
          <input type="checkbox" checked={showRaw} onChange={(e) => setShowRaw(e.target.checked)} />
          Show raw JSON
        </label>
      )}
      {showRaw && (
        <>
          {cloud && <pre>{JSON.stringify(cloud, null, 2)}</pre>}
          {cost && <pre>{JSON.stringify(cost, null, 2)}</pre>}
          {risk && <pre>{JSON.stringify(risk, null, 2)}</pre>}
        </>
      )}
    </section>
  );
}
