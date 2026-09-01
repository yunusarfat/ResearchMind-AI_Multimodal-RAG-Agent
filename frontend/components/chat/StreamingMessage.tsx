"use client";

import { Sparkles } from "lucide-react";
import { LoadingDots } from "@/components/ui/Loading";
import { AgentStatus } from "./AgentStatus";
import { AgentRoute } from "@/types/chat";

interface StreamingMessageProps {
  content: string;
  route: AgentRoute;
}

/**
 * Distinct from Message.tsx: this renders the *in-progress* answer as
 * plain text with a blinking cursor rather than full markdown, since
 * partial markdown (an unclosed "**" or list mid-stream) renders oddly.
 * Once streaming finishes, the final content is committed as a normal
 * Message and gets full markdown formatting.
 */
export function StreamingMessage({ content, route }: StreamingMessageProps) {
  return (
    <div className="flex animate-slide-up gap-3">
      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-accent text-accent-ink">
        <Sparkles className="h-4 w-4" />
      </div>

      <div className="flex max-w-[75%] flex-col gap-2">
        {route && <AgentStatus route={route} />}

        <div className="rounded-lg bg-surface px-4 py-2.5 text-ink">
          {content.length === 0 ? (
            <LoadingDots />
          ) : (
            <p className="whitespace-pre-wrap text-sm">
              {content}
              <span className="ml-0.5 inline-block h-4 w-1.5 animate-blink bg-accent align-text-bottom" />
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
