export type Citation = {
  doc_id: string;
  page: number;
  section: string;
  snippet_hash: string;
};

export type Requirement = {
  requirement_id: string;
  text: string;
  req_type: "MUST" | "SHOULD" | "NICE";
  category: string;
  acceptance_criteria: string;
  dependencies: string[];
  risk_if_not_met: string;
  citations: Citation[];
  approved: boolean;
  confidence: number;
};

export type Project = {
  project_id: string;
  name: string;
  client_notes: string;
  assumptions: string;
  status: string;
};
