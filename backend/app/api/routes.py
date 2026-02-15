from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.agents.brainstormer import Brainstormer
from app.agents.cloud_selector import CloudSelector
from app.agents.cost_estimator import CostEstimator
from app.agents.proposal_writer import ProposalWriter
from app.agents.requirement_extractor import RequirementExtractor
from app.agents.risk_assessor import RiskAssessor
from app.agents.solution_architect import SolutionArchitect
from app.core.audit import audit_logger
from app.core.config import settings
from app.core.llm_runtime import get_llm_config, set_llm_config
from app.core.security import UserContext, ensure_permission, get_user_context
from app.models.schemas import (
    BrainstormResponse,
    CloudRecommendation,
    CostEstimate,
    IngestResponse,
    Job,
    Project,
    ProposalDocument,
    RequirementMatrix,
    RiskRegister,
    LLMConfig,
)
from app.services.crypto_store import EncryptedFileStore
from app.services.evaluator import evaluate_output
from app.services.job_queue import JobQueue
from app.services.kb_service import KnowledgeBaseService
from app.services.parser import parse_file
from app.services.project_context import registry
from app.services.storage import LocalStorage
from app.utils.mermaid_export import mermaid_to_png, mermaid_to_svg

router = APIRouter()
storage = LocalStorage(settings.storage_path)
crypto_store = EncryptedFileStore(settings.encryption_key)
queue = JobQueue()
kb_service = KnowledgeBaseService()


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name}


@router.get("/config/llm", response_model=LLMConfig)
def get_llm_provider_config(user: UserContext = Depends(get_user_context)) -> LLMConfig:
    ensure_permission(user, "read")
    return get_llm_config()


@router.post("/config/llm", response_model=LLMConfig)
def set_llm_provider_config(config: LLMConfig, user: UserContext = Depends(get_user_context)) -> LLMConfig:
    ensure_permission(user, "write")
    updated = set_llm_config(config)
    audit_logger.log(user.user_id, "set_llm_config", updated.model_dump(mode="json"))
    return updated


@router.post("/projects", response_model=Project)
def create_project(
    name: Annotated[str, Form()],
    client_notes: Annotated[str, Form()] = "",
    assumptions: Annotated[str, Form()] = "",
    user: UserContext = Depends(get_user_context),
) -> Project:
    ensure_permission(user, "write")
    now = datetime.now(timezone.utc)
    project = Project(
        project_id=str(uuid4()),
        name=name,
        client_notes=client_notes,
        assumptions=assumptions,
        created_at=now,
        updated_at=now,
    )
    storage.save_project(project)
    audit_logger.log(user.user_id, "create_project", {"project_id": project.project_id})
    return project


@router.get("/projects", response_model=list[Project])
def list_projects(user: UserContext = Depends(get_user_context)) -> list[Project]:
    ensure_permission(user, "read")
    return storage.list_projects()


@router.post("/projects/{project_id}/ingest", response_model=IngestResponse)
async def ingest_documents(
    project_id: str,
    files: list[UploadFile] = File(...),
    user: UserContext = Depends(get_user_context),
) -> IngestResponse:
    ensure_permission(user, "write")
    project = storage.load_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    context = registry.get(project_id)
    doc_ids: list[str] = []
    all_chunks = []
    for file in files:
        data = await file.read()
        doc_id = f"{project_id}-{LocalStorage.hash_text(file.filename)}"
        doc_ids.append(doc_id)
        crypto_store.save(doc_id, data)
        chunks = parse_file(doc_id, file.filename, data, pii_redaction=settings.pii_redaction_enabled)
        all_chunks.extend(chunks)

    context.chunks.extend(all_chunks)
    context.vector_store.upsert(all_chunks)

    audit_logger.log(user.user_id, "ingest", {"project_id": project_id, "docs": doc_ids, "chunks": len(all_chunks)})
    return IngestResponse(project_id=project_id, documents=doc_ids, chunk_count=len(all_chunks))


@router.post("/projects/{project_id}/requirements", response_model=Job)
def extract_requirements(project_id: str, user: UserContext = Depends(get_user_context)) -> Job:
    ensure_permission(user, "write")
    context = registry.get(project_id)

    def task(progress):
        progress(30, "Analyzing requirements")
        reqs = RequirementExtractor(context.vector_store).run(project_id)
        progress(80, "Saving requirement matrix")
        storage.save_json("requirements", project_id, reqs.model_dump(mode="json"))
        guardrail = evaluate_output(
            citation_count=sum(len(r.citations) for r in reqs.requirements),
            confidence=(sum(r.confidence for r in reqs.requirements) / max(1, len(reqs.requirements))),
        )
        return {"requirements": reqs.model_dump(mode="json"), "guardrail": guardrail.model_dump(mode="json")}

    job = queue.submit(project_id, "extract_requirements", task)
    audit_logger.log(user.user_id, "extract_requirements", {"project_id": project_id, "job_id": job.job_id})
    return job


@router.get("/projects/{project_id}/requirements", response_model=RequirementMatrix)
def get_requirements(project_id: str, user: UserContext = Depends(get_user_context)) -> RequirementMatrix:
    ensure_permission(user, "read")
    data = storage.load_json("requirements", project_id)
    if not data:
        raise HTTPException(status_code=404, detail="Requirements not generated")
    return RequirementMatrix.model_validate(data)


@router.post("/projects/{project_id}/requirements/approve", response_model=RequirementMatrix)
def approve_requirements(project_id: str, matrix: RequirementMatrix, user: UserContext = Depends(get_user_context)) -> RequirementMatrix:
    ensure_permission(user, "approve")
    approved = RequirementMatrix(requirements=[r.model_copy(update={"approved": True}) for r in matrix.requirements])
    storage.save_json("requirements", project_id, approved.model_dump(mode="json"))
    audit_logger.log(user.user_id, "approve_requirements", {"project_id": project_id, "count": len(approved.requirements)})
    return approved


@router.post("/projects/{project_id}/architecture")
def generate_architecture(project_id: str, user: UserContext = Depends(get_user_context)) -> dict:
    ensure_permission(user, "write")
    context = registry.get(project_id)
    reqs_data = storage.load_json("requirements", project_id)
    if not reqs_data:
        raise HTTPException(status_code=400, detail="Generate requirements first")
    reqs = RequirementMatrix.model_validate(reqs_data)

    options = SolutionArchitect(context.vector_store).run(reqs)
    svg_paths = []
    png_paths = []
    for idx, opt in enumerate(options, start=1):
        svg_paths.append(
            mermaid_to_svg(opt.mermaid, f"app/output/architecture_{project_id}_plan_{idx}.svg")
        )
        png_paths.append(
            mermaid_to_png(opt.mermaid, f"app/output/architecture_{project_id}_plan_{idx}.png")
        )
    storage.save_json("architecture", project_id, {"options": [o.model_dump(mode="json") for o in options]})
    guardrail = evaluate_output(citation_count=sum(len(o.citations) for o in options), confidence=0.78)
    return {
        "options": [o.model_dump(mode="json") for o in options],
        "diagram_exports": {"svg": svg_paths, "png": png_paths},
        "guardrail": guardrail.model_dump(mode="json"),
    }


@router.post("/projects/{project_id}/cloud", response_model=CloudRecommendation)
def recommend_cloud(project_id: str, user: UserContext = Depends(get_user_context)) -> CloudRecommendation:
    ensure_permission(user, "write")
    context = registry.get(project_id)
    project = storage.load_project(project_id)
    reqs_data = storage.load_json("requirements", project_id)
    if not project or not reqs_data:
        raise HTTPException(status_code=400, detail="Missing project or requirements")
    reqs = RequirementMatrix.model_validate(reqs_data)
    cloud = CloudSelector(context.vector_store).run(reqs, project.client_notes)
    storage.save_json("cloud", project_id, cloud.model_dump(mode="json"))
    return cloud


@router.post("/projects/{project_id}/cost", response_model=CostEstimate)
def estimate_cost(project_id: str, user: UserContext = Depends(get_user_context)) -> CostEstimate:
    ensure_permission(user, "write")
    context = registry.get(project_id)
    estimate = CostEstimator(context.vector_store).run()
    storage.save_json("cost", project_id, estimate.model_dump(mode="json"))
    return estimate


@router.post("/projects/{project_id}/risks", response_model=RiskRegister)
def assess_risks(project_id: str, user: UserContext = Depends(get_user_context)) -> RiskRegister:
    ensure_permission(user, "write")
    context = registry.get(project_id)
    reqs_data = storage.load_json("requirements", project_id)
    if not reqs_data:
        raise HTTPException(status_code=400, detail="Generate requirements first")
    reqs = RequirementMatrix.model_validate(reqs_data)
    risks = RiskAssessor(context.vector_store).run(reqs)
    storage.save_json("risks", project_id, risks.model_dump(mode="json"))
    return risks


@router.post("/projects/{project_id}/proposal", response_model=ProposalDocument)
def generate_proposal(project_id: str, user: UserContext = Depends(get_user_context)) -> ProposalDocument:
    ensure_permission(user, "export")
    project = storage.load_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    reqs = RequirementMatrix.model_validate(storage.load_json("requirements", project_id) or {"requirements": []})
    if not reqs.requirements:
        raise HTTPException(status_code=400, detail="Generate and approve requirements first")
    if any(not r.approved for r in reqs.requirements):
        raise HTTPException(status_code=400, detail="Human review checkpoint: approve requirements before proposal generation")
    arch_raw = storage.load_json("architecture", project_id) or {"options": []}
    options = arch_raw.get("options", [])
    if not options:
        raise HTTPException(status_code=400, detail="Generate architecture first")

    from app.models.schemas import ArchitectureOption

    architectures = [ArchitectureOption.model_validate(o) for o in options]
    cloud_data = storage.load_json("cloud", project_id)
    cost_data = storage.load_json("cost", project_id)
    if not cloud_data or not cost_data:
        raise HTTPException(status_code=400, detail="Generate cloud recommendation and cost estimate first")
    cloud = CloudRecommendation.model_validate(cloud_data)
    cost = CostEstimate.model_validate(cost_data)
    risks = RiskRegister.model_validate(storage.load_json("risks", project_id) or {"risks": []})

    writer = ProposalWriter()
    proposal = writer.build(project_id, project.name, reqs, architectures, cloud, cost, risks)
    storage.save_json("proposal", project_id, proposal.model_dump(mode="json"))

    out_dir = Path("app/output")
    docx_path = writer.export_docx(proposal, str(out_dir / f"proposal_{project_id}.docx"))
    pdf_path = writer.export_pdf(proposal, str(out_dir / f"proposal_{project_id}.pdf"))

    audit_logger.log(user.user_id, "generate_proposal", {"project_id": project_id, "docx": docx_path, "pdf": pdf_path})
    return proposal


@router.get("/projects/{project_id}/proposal/files")
def proposal_files(project_id: str, user: UserContext = Depends(get_user_context)) -> dict:
    ensure_permission(user, "read")
    out_dir = Path("app/output")
    return {
        "docx": str(out_dir / f"proposal_{project_id}.docx"),
        "pdf": str(out_dir / f"proposal_{project_id}.pdf"),
    }


@router.post("/projects/{project_id}/brainstorm", response_model=BrainstormResponse)
def brainstorm(project_id: str, prompt: str = Form(...), user: UserContext = Depends(get_user_context)) -> BrainstormResponse:
    ensure_permission(user, "read")
    context = registry.get(project_id)
    answer = Brainstormer(context.vector_store).run(prompt)
    audit_logger.log(user.user_id, "brainstorm", {"project_id": project_id, "prompt": prompt[:140]})
    return answer


@router.get("/jobs/{job_id}", response_model=Job)
def get_job(job_id: str, user: UserContext = Depends(get_user_context)) -> Job:
    ensure_permission(user, "read")
    job = queue.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/kb/upload")
async def kb_upload(file: UploadFile = File(...), user: UserContext = Depends(get_user_context)) -> dict:
    ensure_permission(user, "write")
    raw = await file.read()
    text = raw.decode("utf-8", errors="ignore")
    doc_id = kb_service.add_document(file.filename, text)
    audit_logger.log(user.user_id, "kb_upload", {"doc_id": doc_id, "file": file.filename})
    return {"doc_id": doc_id, "file": file.filename}


@router.post("/kb/search")
def kb_search(query: str = Form(...), user: UserContext = Depends(get_user_context)) -> dict:
    ensure_permission(user, "read")
    hits = kb_service.search(query, k=5)
    return {"query": query, "results": hits}
