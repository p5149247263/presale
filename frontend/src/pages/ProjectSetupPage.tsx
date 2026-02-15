import React, { useState } from "react";
import { createProject } from "../api/client";

export function ProjectSetupPage({ onProject }: { onProject: (p: any) => void }) {
  const [name, setName] = useState("Healthcare AI Assistant RFP");
  const [clientNotes, setClientNotes] = useState("Client prefers Azure and SOC2-ready controls.");
  const [assumptions, setAssumptions] = useState("Pilot in US East with 500 daily active users.");
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState("");

  return (
    <section className="card">
      <h2>Create Project</h2>
      <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Project name" />
      <textarea value={clientNotes} onChange={(e) => setClientNotes(e.target.value)} rows={3} />
      <textarea value={assumptions} onChange={(e) => setAssumptions(e.target.value)} rows={3} />
      <button
        onClick={async () => {
          setIsCreating(true);
          setError("");
          try {
            const project = await createProject({ name, client_notes: clientNotes, assumptions });
            onProject(project);
          } catch (e: any) {
            setError(e?.message || "Failed to create project.");
          } finally {
            setIsCreating(false);
          }
        }}
        disabled={isCreating}
      >
        {isCreating ? "Creating..." : "Create"}
      </button>
      {error && <p style={{ color: "#b00020" }}>{error}</p>}
    </section>
  );
}
