// Mirrors the citation objects streamed by backend/app/api/chat.py's
// "citations" SSE event.

export type SourceContentType = "text" | "table" | "image" | "chart" | "web" | "paper";

export interface Source {
  marker: string; // "[1]"
  chunk_id: string;
  document_id: string;
  page_number: number | null;
  section: string | null;
  content_type: SourceContentType;
  snippet: string;
  source_url?: string | null; // set for "web" / "paper" sources
}
