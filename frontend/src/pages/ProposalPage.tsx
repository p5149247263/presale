import React, { useState } from "react";
import { generateProposal, getProposalFiles } from "../api/client";

export function ProposalPage({ projectId }: { projectId: string }) {
  const [proposal, setProposal] = useState<any>();
  const [files, setFiles] = useState<any>();
  const [error, setError] = useState("");
  const [showRaw, setShowRaw] = useState(false);

  return (
    <section className="card">
      <h2>Proposal Generator</h2>
      <button
        onClick={async () => {
          setError("");
          try {
            setProposal(await generateProposal(projectId));
          } catch (e: any) {
            setError(e?.message || "Failed to generate proposal.");
          }
        }}
      >
        Generate Proposal
      </button>
      <button
        onClick={async () => {
          setError("");
          try {
            setFiles(await getProposalFiles(projectId));
          } catch (e: any) {
            setError(e?.message || "Failed to load export paths.");
          }
        }}
      >
        Get Export Paths
      </button>
      {error && <p style={{ color: "#b00020" }}>{error}</p>}

      {proposal && (
        <article className="brief-card">
          <h3>{proposal.title}</h3>
          <p>
            <strong>Created:</strong> {proposal.created_at}
          </p>
          <h4>Sections</h4>
          <ul className="brief-list">
            {(proposal.sections || []).map((s: any, idx: number) => (
              <li key={`sec-${idx}`}>
                <strong>{s.title}</strong>
                <div className="muted-line">{(s.content || "").slice(0, 180)}...</div>
              </li>
            ))}
          </ul>
        </article>
      )}

      {files && (
        <article className="brief-card">
          <h3>Export Files</h3>
          <p>
            <strong>DOCX:</strong> {files.docx}
          </p>
          <p>
            <strong>PDF:</strong> {files.pdf}
          </p>
        </article>
      )}

      {(proposal || files) && (
        <label className="debug-toggle">
          <input type="checkbox" checked={showRaw} onChange={(e) => setShowRaw(e.target.checked)} />
          Show raw JSON
        </label>
      )}
      {showRaw && (
        <>
          {proposal && <pre>{JSON.stringify(proposal, null, 2)}</pre>}
          {files && <pre>{JSON.stringify(files, null, 2)}</pre>}
        </>
      )}
    </section>
  );
}
