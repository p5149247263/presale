import React from "react";
import type { Citation } from "../types";

export function CitationTag({ c }: { c: Citation }) {
  return <span className="citation">{`${c.doc_id} p${c.page} ${c.section}`}</span>;
}
