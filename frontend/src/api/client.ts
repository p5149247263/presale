const API_BASE = import.meta.env.VITE_API_BASE || "/api";

const headers = {
  "x-user-id": "frontend-user",
  "x-role": "presales",
};

async function requestJSON(url: string, init?: RequestInit) {
  let resp: Response;
  try {
    resp = await fetch(url, init);
  } catch (err) {
    throw new Error(`Cannot reach backend at ${API_BASE}. Make sure FastAPI is running on port 8000.`);
  }

  const text = await resp.text();
  let data: any = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { raw: text };
    }
  }

  if (!resp.ok) {
    const detail = data?.detail || data?.raw || `${resp.status} ${resp.statusText}`;
    throw new Error(`API error: ${detail}`);
  }
  return data;
}

export async function createProject(payload: { name: string; client_notes: string; assumptions: string }) {
  const form = new FormData();
  form.set("name", payload.name);
  form.set("client_notes", payload.client_notes);
  form.set("assumptions", payload.assumptions);

  return requestJSON(`${API_BASE}/projects`, { method: "POST", body: form, headers });
}

export async function listProjects() {
  return requestJSON(`${API_BASE}/projects`, { headers });
}

export async function ingestFiles(projectId: string, files: File[]) {
  const form = new FormData();
  files.forEach((f) => form.append("files", f));
  return requestJSON(`${API_BASE}/projects/${projectId}/ingest`, { method: "POST", body: form, headers });
}

export async function createRequirementsJob(projectId: string) {
  return requestJSON(`${API_BASE}/projects/${projectId}/requirements`, { method: "POST", headers });
}

export async function getJob(jobId: string) {
  return requestJSON(`${API_BASE}/jobs/${jobId}`, { headers });
}

export async function getRequirements(projectId: string) {
  return requestJSON(`${API_BASE}/projects/${projectId}/requirements`, { headers });
}

export async function approveRequirements(projectId: string, matrix: unknown) {
  return requestJSON(`${API_BASE}/projects/${projectId}/requirements/approve`, {
    method: "POST",
    headers: { ...headers, "content-type": "application/json" },
    body: JSON.stringify(matrix),
  });
}

export async function generateArchitecture(projectId: string) {
  return requestJSON(`${API_BASE}/projects/${projectId}/architecture`, { method: "POST", headers });
}

export async function recommendCloud(projectId: string) {
  return requestJSON(`${API_BASE}/projects/${projectId}/cloud`, { method: "POST", headers });
}

export async function estimateCost(projectId: string) {
  return requestJSON(`${API_BASE}/projects/${projectId}/cost`, { method: "POST", headers });
}

export async function assessRisks(projectId: string) {
  return requestJSON(`${API_BASE}/projects/${projectId}/risks`, { method: "POST", headers });
}

export async function generateProposal(projectId: string) {
  return requestJSON(`${API_BASE}/projects/${projectId}/proposal`, { method: "POST", headers });
}

export async function getProposalFiles(projectId: string) {
  return requestJSON(`${API_BASE}/projects/${projectId}/proposal/files`, { headers });
}

export async function listOutputs(projectId: string) {
  return requestJSON(`${API_BASE}/projects/${projectId}/outputs`, { headers });
}

export function outputDownloadUrl(projectId: string, fileName: string) {
  return `${API_BASE}/projects/${projectId}/outputs/${encodeURIComponent(fileName)}`;
}

export async function brainstorm(projectId: string, prompt: string) {
  const form = new FormData();
  form.set("prompt", prompt);
  return requestJSON(`${API_BASE}/projects/${projectId}/brainstorm`, {
    method: "POST",
    headers,
    body: form,
  });
}

export async function kbUpload(file: File) {
  const form = new FormData();
  form.set("file", file);
  return requestJSON(`${API_BASE}/kb/upload`, {
    method: "POST",
    headers,
    body: form,
  });
}

export async function kbSearch(query: string) {
  const form = new FormData();
  form.set("query", query);
  return requestJSON(`${API_BASE}/kb/search`, {
    method: "POST",
    headers,
    body: form,
  });
}

export async function getLlmConfig() {
  return requestJSON(`${API_BASE}/config/llm`, { headers });
}

export async function setLlmConfig(payload: { provider: "openai" | "anthropic" | "local" | "mock"; model: string; temperature: number; max_tokens: number; }) {
  return requestJSON(`${API_BASE}/config/llm`, {
    method: "POST",
    headers: { ...headers, "content-type": "application/json" },
    body: JSON.stringify(payload),
  });
}
