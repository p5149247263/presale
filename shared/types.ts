export type Citation = {
  doc_id: string;
  page: number;
  section: string;
  snippet_hash: string;
};

export type Traceable<T> = {
  value: T;
  citations: Citation[];
  confidence: number;
};
