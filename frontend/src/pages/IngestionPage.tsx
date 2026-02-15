import React, { useState } from "react";
import { ingestFiles } from "../api/client";

export function IngestionPage({ projectId }: { projectId: string }) {
  const [files, setFiles] = useState<File[]>([]);
  const [result, setResult] = useState<any>();
  const [error, setError] = useState("");

  return (
    <section className="card">
      <h2>Upload RFP/RFI/RFQ</h2>
      <input type="file" multiple onChange={(e) => setFiles(Array.from(e.target.files || []))} />
      <button
        onClick={async () => {
          setError("");
          try {
            const out = await ingestFiles(projectId, files);
            setResult(out);
          } catch (e: any) {
            setError(e?.message || "Failed to ingest files.");
          }
        }}
      >
        Ingest
      </button>
      {error && <p style={{ color: "#b00020" }}>{error}</p>}
      {result && (
        <article className="brief-card">
          <h3>Ingestion Summary</h3>
          <p>
            <strong>Project:</strong> {result.project_id}
          </p>
          <p>
            <strong>Chunks Indexed:</strong> {result.chunk_count}
          </p>
          <h4>Documents</h4>
          <ul className="brief-list">
            {(result.documents || []).map((d: string) => (
              <li key={d}>{d}</li>
            ))}
          </ul>
        </article>
      )}
    </section>
  );
}
