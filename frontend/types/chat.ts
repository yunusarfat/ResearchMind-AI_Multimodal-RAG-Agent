import { Source } from "./source";

export type MessageRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  sources?: Source[];
  isStreaming?: boolean;
  createdAt: string; // ISO 8601 — matches backend MessageResponse.created_at
}

// Mirrors backend/app/api/schemas.py — chats are now persisted
// server-side in Postgres (see backend app/api/chats.py). Timestamps are
// ISO 8601 strings as returned by the API, not client-side numbers.
export interface ChatSummary {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ChatDetail extends ChatSummary {
  messages: ChatMessage[];
}

export type AgentRoute = "RETRIEVE" | "WEB_SEARCH" | "PAPER_SEARCH" | "DIRECT" | null;

export interface DocumentUploadResult {
  document_id: string;
  filename: string;
  num_pages: number;
  num_chunks: number;
  duplicate: boolean;
}

export interface UploadingFile {
  id: string;
  file: File;
  progress: number; // 0-100
  status: "uploading" | "processing" | "done" | "error";
  error?: string;
  result?: DocumentUploadResult;
}






