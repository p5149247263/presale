import React, { useState } from "react";
import { generateProposal, getProposalFiles, listOutputs, outputDownloadUrl } from "../api/client";

type OutputFile = {
  file_name: string;
  file_type: string;
  size_bytes: number;
  download_url: string;
};

export function ProposalPage({ projectId }: { projectId: string }) {
  const [proposal, setProposal] = useState<any>();
  const [files, setFiles] = useState<any>();
  const [outputs, setOutputs] = useState<OutputFile[]>([]);
  const [error, setError] = useState("");
  const [showRaw, setShowRaw] = useState(false);

  function sizeLabel(bytes: number) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  }

  return (
    <section className="card">
      <h2>Proposal Generator</h2>
      <button
        onClick={async () => {
          setError("");
          try {
            const data = await generateProposal(projectId);
            setProposal(data);
            const out = await listOutputs(projectId);
            setOutputs(out.files || []);
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
            const out = await listOutputs(projectId);
            setOutputs(out.files || []);
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

      {outputs.length > 0 && (
        <article className="brief-card">
          <h3>Output Center</h3>
          <p className="muted-line">Location: backend/app/output</p>
          <ul className="brief-list">
            {outputs.map((f) => (
              <li key={f.file_name} className="output-row">
                <div>
                  <strong>{f.file_name}</strong>
                  <div className="muted-line">
                    Type: {f.file_type.toUpperCase()} | Size: {sizeLabel(f.size_bytes)}
                  </div>
                </div>
                <a
                  className="download-btn"
                  href={outputDownloadUrl(projectId, f.file_name)}
                  download
                  target="_blank"
                  rel="noreferrer"
                >
                  Download
                </a>
              </li>
            ))}
          </ul>
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
