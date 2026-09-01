import {
  GoogleLoginPayload,
  LoginPayload,
  SignupPayload,
  TokenResponse,
  User,
} from "@/types/auth";
import { ChatDetail, ChatSummary, DocumentUploadResult } from "@/types/chat";
import { Source } from "@/types/source";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

async function parseErrorDetail(res: Response): Promise<string> {
  try {
    const body = await res.json();
    return body.detail ?? res.statusText;
  } catch {
    return res.statusText;
  }
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export const authApi = {
  async signup(payload: SignupPayload): Promise<TokenResponse> {
    const res = await fetch(`${API_URL}/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new ApiError(await parseErrorDetail(res), res.status);
    return res.json();
  },

  async login(payload: LoginPayload): Promise<TokenResponse> {
    const res = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new ApiError(await parseErrorDetail(res), res.status);
    return res.json();
  },

  async loginWithGoogle(payload: GoogleLoginPayload): Promise<TokenResponse> {
    const res = await fetch(`${API_URL}/auth/google`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new ApiError(await parseErrorDetail(res), res.status);
    return res.json();
  },

  async me(token: string): Promise<User> {
    const res = await fetch(`${API_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new ApiError(await parseErrorDetail(res), res.status);
    return res.json();
  },

  /**
   * Permanently deletes the account and everything owned by it
   * (documents, chunks, chats, messages) — enforced server-side via
   * cascading foreign keys, not by this call doing multiple requests.
   */
  async deleteAccount(token: string): Promise<void> {
    const res = await fetch(`${API_URL}/auth/me`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok && res.status !== 204) {
      throw new ApiError(await parseErrorDetail(res), res.status);
    }
  },
};

// ---------------------------------------------------------------------------
// Chats (CRUD — persisted server-side in Postgres, see backend app/api/chats.py)
// ---------------------------------------------------------------------------

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

export const chatsApi = {
  async create(token: string, title?: string): Promise<ChatSummary> {
    const res = await fetch(`${API_URL}/chats`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders(token) },
      body: JSON.stringify({ title: title ?? null }),
    });
    if (!res.ok) throw new ApiError(await parseErrorDetail(res), res.status);
    return res.json();
  },

  async list(token: string): Promise<ChatSummary[]> {
    const res = await fetch(`${API_URL}/chats`, { headers: authHeaders(token) });
    if (!res.ok) throw new ApiError(await parseErrorDetail(res), res.status);
    return res.json();
  },

  async get(token: string, chatId: string): Promise<ChatDetail> {
    const res = await fetch(`${API_URL}/chats/${chatId}`, { headers: authHeaders(token) });
    if (!res.ok) throw new ApiError(await parseErrorDetail(res), res.status);
    return res.json();
  },

  async delete(token: string, chatId: string): Promise<void> {
    const res = await fetch(`${API_URL}/chats/${chatId}`, {
      method: "DELETE",
      headers: authHeaders(token),
    });
    if (!res.ok && res.status !== 204) {
      throw new ApiError(await parseErrorDetail(res), res.status);
    }
  },
};

// ---------------------------------------------------------------------------
// Documents
// ---------------------------------------------------------------------------

export const documentsApi = {
  /**
   * Upload a PDF with real upload-progress reporting. Uses XHR instead of
   * fetch because fetch has no cross-browser upload progress event.
   */
  upload(
    file: File,
    token: string,
    onProgress: (percent: number) => void
  ): Promise<DocumentUploadResult> {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      const formData = new FormData();
      formData.append("file", file);

      xhr.open("POST", `${API_URL}/documents/upload`);
      xhr.setRequestHeader("Authorization", `Bearer ${token}`);

      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          onProgress(Math.round((event.loaded / event.total) * 100));
        }
      };

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            resolve(JSON.parse(xhr.responseText));
          } catch {
            reject(new ApiError("Malformed response from server.", xhr.status));
          }
        } else {
          let detail = xhr.statusText;
          try {
            detail = JSON.parse(xhr.responseText).detail ?? detail;
          } catch {
            /* ignore parse failure, fall back to statusText */
          }
          reject(new ApiError(detail, xhr.status));
        }
      };

      xhr.onerror = () => reject(new ApiError("Network error during upload.", 0));
      xhr.send(formData);
    });
  },
};

// ---------------------------------------------------------------------------
// Chat (streaming)
// ---------------------------------------------------------------------------

export interface StreamCallbacks {
  onRoute: (route: string) => void;
  onToken: (token: string) => void;
  onCitations: (sources: Source[]) => void;
  onError: (message: string) => void;
  onDone: () => void;
}

/**
 * Streams /chat/query's Server-Sent Events. Implemented over a manual
 * fetch + ReadableStream reader (not the browser EventSource API) because
 * EventSource only supports GET requests with no custom headers, and this
 * endpoint needs POST + an Authorization bearer token.
 */
export async function streamChatQuery(
  query: string,
  chatId: string,
  token: string,
  callbacks: StreamCallbacks,
  signal?: AbortSignal
): Promise<void> {
  const res = await fetch(`${API_URL}/chat/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ query, chat_id: chatId }),
    signal,
  });

  if (!res.ok || !res.body) {
    callbacks.onError(await parseErrorDetail(res));
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // SSE messages are separated by a blank line ("\n\n").
      const messages = buffer.split("\n\n");
      buffer = messages.pop() ?? ""; // keep the last (possibly incomplete) chunk

      for (const raw of messages) {
        if (!raw.trim()) continue;

        const eventMatch = raw.match(/^event: (.+)$/m);
        const dataMatch = raw.match(/^data: (.+)$/m);
        if (!eventMatch || !dataMatch) continue;

        const eventName = eventMatch[1].trim();
        const data = JSON.parse(dataMatch[1]);

        if (eventName === "route") {
          callbacks.onRoute(data as string);
        } else if (eventName === "answer") {
          callbacks.onToken(data as string);
        } else if (eventName === "citations") {
          callbacks.onCitations(data as Source[]);
        }
      }
    }
  } catch (err) {
    if ((err as Error).name !== "AbortError") {
      callbacks.onError((err as Error).message || "Stream interrupted.");
    }
  } finally {
    callbacks.onDone();
  }
}
