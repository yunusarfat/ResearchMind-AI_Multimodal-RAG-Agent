"use client";

import { FormEvent, KeyboardEvent, useRef, useState } from "react";
import { Paperclip, Send } from "lucide-react";
import { Button } from "@/components/ui/Button";

interface ChatInputProps {
  onSend: (message: string) => void;
  onUploadClick: () => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, onUploadClick, disabled }: ChatInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  }

  function handleInput(e: React.ChangeEvent<HTMLTextAreaElement>) {
    setValue(e.target.value);
    // Auto-grow up to a reasonable cap, then scroll internally.
    e.target.style.height = "auto";
    e.target.style.height = `${Math.min(e.target.scrollHeight, 160)}px`;
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex py-16 items-end gap-2 border-t border-border bg-bg p-3"
    >
      <button
        type="button"
        onClick={onUploadClick}
        title="Upload a PDF"
        aria-label="Upload a PDF"
        className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md text-muted hover:bg-surface hover:text-ink"
      >
        <Paperclip className="h-5 w-5" />
      </button>

      <textarea
        ref={textareaRef}
        value={value}
        onChange={handleInput}
        onKeyDown={handleKeyDown}
        placeholder="Ask your research question…"
        rows={1}
        disabled={disabled}
        className="max-h-40 flex-1 resize-none rounded-md border border-border bg-bg px-3 py-2 text-sm text-ink placeholder:text-muted focus:outline-none focus-visible:outline-2 focus-visible:outline-accent focus-visible:outline-offset-1 disabled:opacity-50"
      />

      <Button type="submit" size="md" disabled={disabled || !value.trim()}>
        <Send className="h-4 w-4" />
        Send
      </Button>
    </form>
  );
}
