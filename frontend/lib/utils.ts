import { clsx, type ClassValue } from "clsx";

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export function generateId(): string {
  return crypto.randomUUID();
}

export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength).trimEnd() + "…";
}

/** Derive a short chat title from the first user message. */
export function titleFromMessage(content: string): string {
  const cleaned = content.trim().replace(/\s+/g, " ");
  return truncate(cleaned, 48) || "New chat";
}

const CONTENT_TYPE_LABELS: Record<string, string> = {
  text: "Text",
  table: "Table",
  image: "Image",
  chart: "Chart",
  web: "Web",
  paper: "Paper",
};

export function contentTypeLabel(type: string): string {
  return CONTENT_TYPE_LABELS[type] ?? type;
}

export function formatRelativeTime(isoTimestamp: string): string {
  const diffMs = Date.now() - new Date(isoTimestamp).getTime();
  const diffMin = Math.floor(diffMs / 60000);

  if (diffMin < 1) return "Just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  const diffDay = Math.floor(diffHr / 24);
  if (diffDay < 7) return `${diffDay}d ago`;
  return new Date(isoTimestamp).toLocaleDateString();
}
