"use client";

import ReactMarkdown from "react-markdown";
import { ChatMessage } from "@/types/chat";
import { cn } from "@/lib/utils";
import { User as UserIcon, Sparkles } from "lucide-react";

/**
 * Wraps citation markers like "[1]" in backticks before markdown parsing,
 * so they render as inline code — a small, distinct mono badge — without
 * needing a custom remark plugin. Skips markers already followed by "("
 * so real markdown links (e.g. "[text](url)") are left untouched.
 */
function citationizeMarkers(content: string): string {
  return content.replace(/\[(\d+)\](?!\()/g, "`[$1]`");
}

function AssistantContent({ content }: { content: string }) {
  return (
    <div className="prose-sm max-w-none text-ink [&_p]:my-2 [&_ul]:my-2 [&_ul]:list-disc [&_ul]:pl-5 [&_ol]:my-2 [&_ol]:list-decimal [&_ol]:pl-5">
      <ReactMarkdown
        components={{
          code: ({ children }) => (
            <span className="rounded bg-accent/10 px-1 py-0.5 font-mono text-xs font-medium text-accent">
              {children}
            </span>
          ),
          a: ({ href, children }) => (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-accent hover:underline"
            >
              {children}
            </a>
          ),
        }}
      >
        {citationizeMarkers(content)}
      </ReactMarkdown>
    </div>
  );
}

export function Message({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <div className={cn("flex gap-3 animate-slide-up", isUser && "flex-row-reverse")}>
      <div
        className={cn(
          "flex h-7 w-7 shrink-0 items-center justify-center rounded-full",
          isUser ? "bg-surface2 text-ink" : "bg-accent text-accent-ink"
        )}
      >
        {isUser ? <UserIcon className="h-4 w-4" /> : <Sparkles className="h-4 w-4" />}
      </div>

      <div
        className={cn(
          "max-w-[75%] rounded-lg px-4 py-2.5",
          isUser ? "bg-accent text-accent-ink" : "bg-surface text-ink"
        )}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap text-sm">{message.content}</p>
        ) : (
          <AssistantContent content={message.content} />
        )}
      </div>
    </div>
  );
}
