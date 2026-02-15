from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Citation(BaseModel):
    doc_id: str
    page: int = Field(ge=1)
    section: str
    snippet_hash: str


class RequirementType(str, Enum):
    MUST = "MUST"
    SHOULD = "SHOULD"
    NICE = "NICE"


class RequirementCategory(str, Enum):
    DATA = "Data"
    MODEL = "Model"
    INFRA = "Infra"
    SECURITY = "Security"
    COMPLIANCE = "Compliance"
    INTEGRATION = "Integration"
    UI = "UI"
    SLA = "SLA"


class Requirement(BaseModel):
    requirement_id: str
    text: str
    req_type: RequirementType
    category: RequirementCategory
    acceptance_criteria: str
    dependencies: list[str] = Field(default_factory=list)
    risk_if_not_met: str
    citations: list[Citation] = Field(default_factory=list)
    approved: bool = False
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class RequirementMatrix(BaseModel):
    requirements: list[Requirement]


class ArchitectureOption(BaseModel):
    name: str
    summary: str
    components: list[str]
    data_flow: list[str]
    model_flow: list[str]
    latency_scalability_notes: list[str]
    integration_plan: list[str]
    mermaid: str
    citations: list[Citation] = Field(default_factory=list)


class CloudRecommendation(BaseModel):
    primary_cloud: Literal["AWS", "Azure", "GCP", "OnPrem"]
    rationale: str
    alternatives: list[str]
    constraints_considered: list[str]
    citations: list[Citation] = Field(default_factory=list)


class CostAssumption(BaseModel):
    key: str
    value: float
    unit: str
    editable: bool = True


class CostLineItem(BaseModel):
    category: str
    item: str
    monthly_cost_usd: float
    notes: str


class CostEstimate(BaseModel):
    assumptions: list[CostAssumption]
    line_items: list[CostLineItem]
    best_case_total: float
    expected_total: float
    worst_case_total: float
    citations: list[Citation] = Field(default_factory=list)


class RiskCategory(str, Enum):
    PRIVACY = "privacy"
    SECURITY = "security"
    HALLUCINATION = "hallucination"
    BIAS = "bias"
    REGULATORY = "regulatory"
    IP = "ip"
    OPS = "ops"


class RiskItem(BaseModel):
    risk_id: str
    category: RiskCategory
    description: str
    likelihood: Literal["Low", "Medium", "High"]
    impact: Literal["Low", "Medium", "High"]
    mitigations: list[str]
    owner: str
    residual_risk: Literal["Low", "Medium", "High"]
    citations: list[Citation] = Field(default_factory=list)


class RiskRegister(BaseModel):
    risks: list[RiskItem]


class ProposalSection(BaseModel):
    title: str
    content: str
    citations: list[Citation] = Field(default_factory=list)


class ProposalDocument(BaseModel):
    project_id: str
    title: str
    created_at: datetime
    sections: list[ProposalSection]
    appendix_requirements: RequirementMatrix
    appendix_risks: RiskRegister
    appendix_architecture_mermaid: str


class ClarificationItem(BaseModel):
    question: str
    reason: str


class BrainstormResponse(BaseModel):
    answer: str
    opportunities: list[str]
    differentiators: list[str]
    clarification_list: list[ClarificationItem]
    citations: list[Citation] = Field(default_factory=list)


class DocumentChunk(BaseModel):
    doc_id: str
    page: int
    section: str
    text: str
    snippet_hash: str


class IngestResponse(BaseModel):
    project_id: str
    documents: list[str]
    chunk_count: int


class Project(BaseModel):
    project_id: str
    name: str
    version: int = 1
    client_notes: str = ""
    assumptions: str = ""
    created_at: datetime
    updated_at: datetime
    status: str = "draft"


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(BaseModel):
    job_id: str
    project_id: str
    task: str
    status: JobStatus
    progress: int = Field(ge=0, le=100)
    message: str = ""
    result: dict | None = None


class GuardrailResult(BaseModel):
    pass_citation_check: bool
    pass_confidence_threshold: bool
    hallucination_risk_score: float = Field(ge=0.0, le=1.0)
    comments: list[str]


class LLMConfig(BaseModel):
    provider: Literal["openai", "anthropic", "local", "mock"] = "mock"
    model: str = "gpt-4o-mini"
    temperature: float = 0.2
    max_tokens: int = 1200
