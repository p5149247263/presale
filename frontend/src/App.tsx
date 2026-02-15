import React, { useState } from "react";
import { Stepper } from "./components/Stepper";
import { ArchitecturePage } from "./pages/ArchitecturePage";
import { BrainstormPage } from "./pages/BrainstormPage";
import { CloudCostRiskPage } from "./pages/CloudCostRiskPage";
import { IngestionPage } from "./pages/IngestionPage";
import { KnowledgeBasePage } from "./pages/KnowledgeBasePage";
import { ModelConfigPage } from "./pages/ModelConfigPage";
import { ProjectSetupPage } from "./pages/ProjectSetupPage";
import { ProposalPage } from "./pages/ProposalPage";
import { RequirementsPage } from "./pages/RequirementsPage";
import "./styles/app.css";

const steps = [
  "Project",
  "Ingestion",
  "Requirements",
  "Architecture",
  "Cloud/Cost/Risk",
  "Proposal",
  "Brainstorm",
  "Knowledge Base",
  "Model Config",
];

export default function App() {
  const [project, setProject] = useState<any>();
  const [step, setStep] = useState(0);
  const nextStep = project ? Math.min(step + 1, steps.length - 1) : 0;
  const canOpen = (idx: number) => idx === 0 || Boolean(project);

  const guideByStep: Record<number, string[]> = {
    0: [
      "Enter project name, client notes, and assumptions.",
      "Click Create to start your workflow.",
    ],
    1: [
      "Upload RFP/RFI/RFQ files (PDF, DOCX, TXT).",
      "Confirm ingestion summary shows document IDs and chunk count.",
    ],
    2: [
      "Run Extract Requirements.",
      "Edit Req Type and Category where needed.",
      "Click Approve All before proceeding to proposal generation.",
    ],
    3: [
      "Generate Plan A and Plan B architecture options.",
      "Review components, integration plan, and Mermaid diagram.",
    ],
    4: [
      "Generate cloud recommendation first.",
      "Run cost estimate and risk assessment.",
      "Review assumptions and top risk mitigations.",
    ],
    5: [
      "Generate proposal draft after requirements approval.",
      "Check export paths for DOCX and PDF artifacts.",
    ],
    6: [
      "Ask what-if questions and opportunity discovery prompts.",
      "Use clarifications list to prepare client follow-ups.",
    ],
    7: [
      "Upload reusable KB artifacts (past proposals/templates/case studies).",
      "Search KB to reuse proven language and evidence.",
    ],
    8: [
      "Select LLM provider/model for generation behavior.",
      "Use mock mode for demo; provider modes for real outputs.",
    ],
  };

  return (
    <main className="container">
      <header>
        <h1>AI Presales Copilot</h1>
        <p>Traceable proposal automation for AI/ML/GenAI presales.</p>
        <p className="byline">Designed & developed by Dr.P.Ramesh Babu</p>
      </header>

      <Stepper steps={steps} current={step} next={nextStep} />
      <nav className="row">
        {steps.map((s, i) => (
          <button
            key={s}
            className={`tab-btn ${i === step ? "active" : ""} ${i === nextStep ? "next" : ""}`}
            onClick={() => canOpen(i) && setStep(i)}
            disabled={!canOpen(i)}
            title={!canOpen(i) ? "Create a project first" : ""}
          >
            {s}
          </button>
        ))}
      </nav>
      <aside className="guide-card">
        <h3>First-Time Guide</h3>
        <p>
          Current Step: <strong>{steps[step]}</strong> | Recommended Next: <strong>{steps[nextStep]}</strong>
        </p>
        <ul className="brief-list">
          {(guideByStep[step] || []).map((g) => (
            <li key={g}>{g}</li>
          ))}
        </ul>
      </aside>

      {step === 0 && <ProjectSetupPage onProject={(p) => { setProject(p); setStep(1); }} />}
      {step > 0 && !project && <p>Create a project first.</p>}
      {step === 1 && project && <IngestionPage projectId={project.project_id} />}
      {step === 2 && project && <RequirementsPage projectId={project.project_id} />}
      {step === 3 && project && <ArchitecturePage projectId={project.project_id} />}
      {step === 4 && project && <CloudCostRiskPage projectId={project.project_id} />}
      {step === 5 && project && <ProposalPage projectId={project.project_id} />}
      {step === 6 && project && <BrainstormPage projectId={project.project_id} />}
      {step === 7 && <KnowledgeBasePage />}
      {step === 8 && <ModelConfigPage />}
    </main>
  );
}
