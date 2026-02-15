import React, { useState } from "react";
import { kbSearch, kbUpload } from "../api/client";

type KbUploadResult = {
  doc_id: string;
  file: string;
};

type KbHit = {
  text: string;
  score: number;
  citation: {
    doc_id: string;
    page: number;
    section: string;
    snippet_hash: string;
  };
};

type KbSearchResult = {
  query: string;
  results: KbHit[];
};

export function KnowledgeBasePage() {
  const [file, setFile] = useState<File | null>(null);
  const [query, setQuery] = useState("citation grounded architecture accelerator");
  const [uploadResult, setUploadResult] = useState<KbUploadResult | null>(null);
  const [searchResult, setSearchResult] = useState<KbSearchResult | null>(null);
  const [error, setError] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [showRaw, setShowRaw] = useState(false);

  return (
    <section className="card">
      <h2>Knowledge Base</h2>
      <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
      <button
        onClick={async () => {
          setError("");
          if (!file) {
            setError("Select a file before upload.");
            return;
          }
          setIsUploading(true);
          try {
            setUploadResult(await kbUpload(file));
          } catch (e: any) {
            setError(e?.message || "Failed to upload KB artifact.");
          } finally {
            setIsUploading(false);
          }
        }}
        disabled={isUploading}
      >
        {isUploading ? "Uploading..." : "Upload KB Artifact"}
      </button>
      {error && <p style={{ color: "#b00020" }}>{error}</p>}
      {uploadResult && (
        <article className="brief-card">
          <h3>Upload Summary</h3>
          <p>
            <strong>File:</strong> {uploadResult.file}
          </p>
          <p>
            <strong>Document ID:</strong> {uploadResult.doc_id}
          </p>
        </article>
      )}

      <textarea value={query} onChange={(e) => setQuery(e.target.value)} rows={2} />
      <button
        onClick={async () => {
          setError("");
          setIsSearching(true);
          try {
            setSearchResult(await kbSearch(query));
          } catch (e: any) {
            setError(e?.message || "Failed to search KB.");
          } finally {
            setIsSearching(false);
          }
        }}
        disabled={isSearching}
      >
        {isSearching ? "Searching..." : "Search KB"}
      </button>

      {searchResult && (
        <article className="brief-card">
          <h3>Search Results</h3>
          <p>
            <strong>Query:</strong> {searchResult.query}
          </p>
          <ul className="brief-list">
            {(searchResult.results || []).map((hit, idx) => (
              <li key={`${hit.citation.snippet_hash}-${idx}`}>
                <div>{hit.text}</div>
                <div className="muted-line">Score: {Number(hit.score || 0).toFixed(3)}</div>
                <div className="chip-wrap">
                  <span className="chip" title={`${hit.citation.doc_id} | ${hit.citation.snippet_hash}`}>
                    p{hit.citation.page} {hit.citation.section}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        </article>
      )}

      {(uploadResult || searchResult) && (
        <label className="debug-toggle">
          <input type="checkbox" checked={showRaw} onChange={(e) => setShowRaw(e.target.checked)} />
          Show raw JSON
        </label>
      )}
      {showRaw && (
        <>
          {uploadResult && <pre>{JSON.stringify(uploadResult, null, 2)}</pre>}
          {searchResult && <pre>{JSON.stringify(searchResult, null, 2)}</pre>}
        </>
      )}
    </section>
  );
}
