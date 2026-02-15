import React, { useState } from "react";
import { approveRequirements, createRequirementsJob, getJob, getRequirements } from "../api/client";
import { CitationTag } from "../components/CitationTag";
import type { Requirement } from "../types";

const REQ_TYPE_OPTIONS: Array<Requirement["req_type"]> = ["MUST", "SHOULD", "NICE"];
const CATEGORY_OPTIONS = ["Data", "Model", "Infra", "Security", "Compliance", "Integration", "UI", "SLA"];

export function RequirementsPage({ projectId }: { projectId: string }) {
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [status, setStatus] = useState("idle");
  const [approveError, setApproveError] = useState("");
  const [approveMessage, setApproveMessage] = useState("");
  const [isApproving, setIsApproving] = useState(false);

  function updateRequirement(index: number, patch: Partial<Requirement>) {
    setRequirements((prev) => prev.map((r, i) => (i === index ? { ...r, ...patch } : r)));
  }

  async function generate() {
    setStatus("queueing");
    setApproveMessage("");
    setApproveError("");
    const job = await createRequirementsJob(projectId);
    let done = false;
    while (!done) {
      const poll = await getJob(job.job_id);
      setStatus(`${poll.status} ${poll.progress}%`);
      done = poll.status === "completed" || poll.status === "failed";
      if (!done) {
        await new Promise((r) => setTimeout(r, 500));
      }
    }
    const matrix = await getRequirements(projectId);
    setRequirements(matrix.requirements);
  }

  return (
    <section className="card">
      <h2>Requirements Matrix</h2>
      <button onClick={generate}>Extract Requirements</button>
      <span>{status}</span>
      <div className="list">
        {requirements.map((req, index) => (
          <article key={req.requirement_id}>
            <strong>{req.requirement_id}</strong> <em>{req.req_type}</em> <b>{req.category}</b>{" "}
            {req.approved && <span className="citation">Approved</span>}
            <p>{req.text}</p>
            <div className="row">
              <label>
                Req Type
                <select
                  value={req.req_type}
                  onChange={(e) => updateRequirement(index, { req_type: e.target.value as Requirement["req_type"] })}
                >
                  {REQ_TYPE_OPTIONS.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Category
                <select
                  value={req.category}
                  onChange={(e) => updateRequirement(index, { category: e.target.value })}
                >
                  {CATEGORY_OPTIONS.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <small>Acceptance: {req.acceptance_criteria}</small>
            <div className="citations-inline">
              {req.citations.map((c) => (
                <CitationTag key={c.snippet_hash} c={c} />
              ))}
            </div>
          </article>
        ))}
      </div>
      {requirements.length > 0 && (
        <>
          <button
            onClick={async () => {
              setApproveError("");
              setApproveMessage("");
              setIsApproving(true);
              try {
                const out = await approveRequirements(projectId, { requirements });
                if (out?.requirements) {
                  setRequirements(out.requirements);
                } else {
                  setRequirements((prev) => prev.map((r) => ({ ...r, approved: true })));
                }
                setApproveMessage("Requirements approved and saved.");
              } catch (e: any) {
                setApproveError(e?.message || "Failed to approve requirements.");
              } finally {
                setIsApproving(false);
              }
            }}
            disabled={isApproving}
          >
            {isApproving ? "Approving..." : "Approve All"}
          </button>
          {approveMessage && <p style={{ color: "#0a7f6f" }}>{approveMessage}</p>}
          {approveError && <p style={{ color: "#b00020" }}>{approveError}</p>}
        </>
      )}
    </section>
  );
}
