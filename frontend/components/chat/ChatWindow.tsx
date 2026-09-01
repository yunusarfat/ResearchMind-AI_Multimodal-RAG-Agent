"use client";

import { useEffect, useRef, ChangeEvent } from "react";
import { Sparkles } from "lucide-react";
import { Message } from "./Message";
import { StreamingMessage } from "./StreamingMessage";
import { ChatInput } from "./ChatInput";
import { UploadCard } from "./UploadCard";
import { AgentRoute, ChatMessage, UploadingFile } from "@/types/chat";

interface ChatWindowProps {
  messages: ChatMessage[];
  isStreaming: boolean;
  streamingContent: string;
  currentRoute: AgentRoute;
  uploads: UploadingFile[];
  onSend: (message: string) => void;
  onUploadFile: (file: File) => void;
}

export function ChatWindow({
  messages,
  isStreaming,
  streamingContent,
  currentRoute,
  uploads,
  onSend,
  onUploadFile,
}: ChatWindowProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Keep the conversation scrolled to the latest message/stream chunk.
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, streamingContent]);

  function handleFileSelected(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) onUploadFile(file);
    e.target.value = ""; // allow re-selecting the same file later
  }

  const isEmpty = messages.length === 0 && uploads.length === 0;

  return (
    <div className="flex h-full flex-1 flex-col">
      <div className="flex-1 overflow-y-auto px-4 py-2 md:px-8">
        {isEmpty ? (
          <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-accent/10">
              <Sparkles className="h-6 w-6 text-accent" />
            </div>
            <h2 className="text-lg font-semibold text-ink">Start your research</h2>
            <p className="max-w-sm text-sm text-muted">
              Upload a paper with the clip icon below, or just ask a question —
              ResearchMind will search the web or arXiv if it needs to.
            </p>
          </div>
        ) : (
          <div className="mx-auto flex max-w-3xl flex-col gap-5">
            {messages.map((message) => (
              <Message key={message.id} message={message} />
            ))}

            {isStreaming && (
              <StreamingMessage content={streamingContent} route={currentRoute} />
            )}

            {uploads.length > 0 && (
              <div className="flex flex-col gap-2">
                {uploads.map((upload) => (
                  <UploadCard key={upload.id} upload={upload} />
                ))}
              </div>
            )}

            <div ref={scrollRef} />
          </div>
        )}
      </div>

      <div className="mx-auto w-full max-w-3xl">
        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf"
          onChange={handleFileSelected}
          className="hidden"
        />
        <ChatInput
          onSend={onSend}
          onUploadClick={() => fileInputRef.current?.click()}
          disabled={isStreaming}
        />
      </div>
    </div>
  );
}
